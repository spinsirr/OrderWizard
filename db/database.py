import sqlite3
import logging
import os
import sys
import time
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_user_data_dir():
    """Get the user-specific data directory"""
    if sys.platform == 'darwin':
        data_dir = os.path.expanduser('~/Library/Application Support/OrderWizard')
    elif sys.platform == 'win32':
        data_dir = os.path.join(os.environ['APPDATA'], 'OrderWizard')
    else:  # Linux and other Unix-like
        data_dir = os.path.expanduser('~/.orderwizard')
    
    # Create directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # First check if we should use user data directory
        if relative_path.startswith('db/') and relative_path.endswith('.db'):
            # Always store database files in user data directory
            return os.path.join(get_user_data_dir(), os.path.basename(relative_path))
            
        # For other resources, use standard resource path logic
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
            # Check if we're in app bundle on macOS
            if sys.platform == 'darwin' and os.path.exists(os.path.join(os.path.dirname(sys.executable), '..', 'Resources')):
                resources_path = os.path.join(os.path.dirname(sys.executable), '..', 'Resources')
                return os.path.join(resources_path, relative_path)
            return os.path.join(base_path, relative_path)
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', relative_path)
    except Exception as e:
        logging.error(f"Error getting resource path: {e}")
        return relative_path

class DatabaseError(Exception):
    """Custom exception for database errors"""
    pass

class ConnectionPool:
    """A simple SQLite connection pool"""
    def __init__(self, db_path, max_connections=5):
        self.db_path = db_path
        self.max_connections = max_connections
        self.connections = []
        self.lock = threading.Lock()
        self.connection_locks = {}  # Lock per connection
        
    def get_connection(self):
        """Get a connection from the pool or create a new one"""
        with self.lock:
            if self.connections:
                conn = self.connections.pop()
            else:
                # Ensure the database directory exists
                os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
                conn = sqlite3.connect(self.db_path, check_same_thread=False)
                self.connection_locks[id(conn)] = threading.Lock()
            return conn
                
    def get_lock(self, conn):
        """Get the lock for a specific connection"""
        return self.connection_locks.get(id(conn))
                
    def return_connection(self, conn):
        """Return a connection to the pool"""
        with self.lock:
            if len(self.connections) < self.max_connections:
                self.connections.append(conn)
            else:
                lock = self.connection_locks.pop(id(conn), None)
                conn.close()
                
    def close_all(self):
        """Close all connections in the pool"""
        with self.lock:
            for conn in self.connections:
                conn.close()
            self.connections.clear()
            self.connection_locks.clear()

class Database:
    _instance = None
    _pool = None
    _initialized = False
    _init_lock = threading.Lock()
    
    def __new__(cls, db_name="db/orders.db"):
        """Singleton pattern to ensure only one Database instance"""
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.db_name = resource_path(db_name)
            # Ensure database directory exists
            os.makedirs(os.path.dirname(cls._instance.db_name), exist_ok=True)
        return cls._instance
        
    def __init__(self, db_name="db/orders.db"):
        # Avoid re-initialization
        if self._initialized:
            return
            
        with self._init_lock:
            if self._initialized:
                return
                
            self.db_name = resource_path(db_name)
            
            # Create connection pool
            if self._pool is None:
                self._pool = ConnectionPool(self.db_name)
            
            # Initialize in a lighter way
            self._create_table()
            
            # Schedule full verification for later
            threading.Thread(target=self._delayed_verification, daemon=True).start()
            
            self._initialized = True
            
    def _delayed_verification(self):
        """Perform full database verification in background"""
        time.sleep(1)  # Wait for app to start
        try:
            # Verify database structure
            if self._verify_database_structure():
                logging.info("Database structure verified successfully")
            else:
                logging.error("Database structure verification failed")
        except Exception as e:
            logging.error(f"Database delayed verification failed: {e}")

    def initialize_database(self):
        """Initialize the database (light version)"""
        # Tables are already created in __init__
        pass

    def _validate_order(self, order):
        """Validate order data before database operations"""
        if not order.order_number or not order.order_number.strip():
            raise DatabaseError("Order number cannot be empty")
        if order.amount <= 0:
            raise DatabaseError("Amount must be greater than 0")
        return True

    def _verify_database_structure(self):
        """Verify that the database has the correct structure"""
        try:
            conn = self._pool.get_connection()
            try:
                cursor = conn.cursor()
                
                # Get table info
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='orders'
                """)
                if not cursor.fetchone():
                    logging.error("Orders table not found")
                    return False
                
                # Get column info
                cursor.execute('PRAGMA table_info(orders)')
                columns = {row[1] for row in cursor.fetchall()}
                
                # Expected columns
                expected_columns = {
                    'id', 'order_number', 'amount', 'image_uri',
                    'comment_with_picture', 'commented', 'revealed',
                    'reimbursed', 'reimbursed_amount', 'note', 'created_at'
                }
                
                if not expected_columns.issubset(columns):
                    logging.error(f"Missing columns: {expected_columns - columns}")
                    return False
                
                return True
            finally:
                self._pool.return_connection(conn)
                
        except sqlite3.Error as e:
            logging.error(f"Database verification failed: {e}")
            return False

    def _create_table(self):
        """Create the orders table if it doesn't exist"""
        conn = self._pool.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_number TEXT NOT NULL,
                    amount REAL NOT NULL CHECK (amount > 0),
                    image_uri TEXT,
                    comment_with_picture BOOLEAN DEFAULT FALSE,
                    commented BOOLEAN DEFAULT FALSE,
                    revealed BOOLEAN DEFAULT FALSE,
                    reimbursed BOOLEAN DEFAULT FALSE,
                    reimbursed_amount REAL DEFAULT 0.0,
                    note TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create index on order_number for faster lookups
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_order_number 
                ON orders(order_number)
            ''')
            
            conn.commit()
        finally:
            self._pool.return_connection(conn)

    def _execute_with_lock(self, operation, *args, **kwargs):
        """Execute a database operation with proper locking"""
        conn = self._pool.get_connection()
        try:
            lock = self._pool.get_lock(conn)
            if lock:
                with lock:
                    return operation(conn, *args, **kwargs)
            return operation(conn, *args, **kwargs)
        finally:
            self._pool.return_connection(conn)

    def get_order_by_id(self, order_id):
        """Retrieve an order by its ID"""
        def _operation(conn):
            try:
                logging.info(f"Database: Getting order with ID {order_id}")
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
                result = cursor.fetchone()
                
                if result:
                    logging.info(f"Database: Found order {order_id} - {result[1]}")
                else:
                    logging.warning(f"Database: Order {order_id} not found in database")
                    
                    # Debug: Get a count of all orders
                    cursor.execute('SELECT COUNT(*) FROM orders')
                    count = cursor.fetchone()[0]
                    logging.info(f"Database: Total order count: {count}")
                    
                    # Debug: Get the highest order ID
                    cursor.execute('SELECT MAX(id) FROM orders')
                    max_id = cursor.fetchone()[0]
                    logging.info(f"Database: Highest order ID: {max_id}")
                
                return result
            except sqlite3.Error as e:
                logging.error(f"Database error in get_order_by_id: {e}", exc_info=True)
                raise DatabaseError(f"Failed to get order {order_id}: {str(e)}")
            except Exception as e:
                logging.error(f"Exception in get_order_by_id: {e}", exc_info=True)
                raise
        
        return self._execute_with_lock(_operation)

    def get_all_orders(self):
        """Retrieve all orders sorted by creation time (newest first)"""
        def _operation(conn):
            try:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM orders ORDER BY created_at ASC')
                return cursor.fetchall()
            except sqlite3.Error as e:
                logging.error(f"Database error: {e}")
                raise DatabaseError(str(e))
            except Exception as e:
                logging.error(f"Exception in get_all_orders: {e}")
                raise
        
        return self._execute_with_lock(_operation)

    def insert_order(self, order):
        """Insert a new order after validation"""
        def _operation(conn):
            try:
                self._validate_order(order)
                cursor = conn.cursor()
                # Get tuple values and remove the id (it's auto-generated)
                values = order.to_tuple()[1:]  # Skip the id field
                cursor.execute('''
                    INSERT INTO orders (
                        order_number, amount, image_uri, comment_with_picture, 
                        commented, revealed, reimbursed, reimbursed_amount, note
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', values)
                conn.commit()
                return cursor.lastrowid
            except sqlite3.Error as e:
                logging.error(f"Database error: {e}")
                raise DatabaseError(str(e))
            except Exception as e:
                logging.error(f"Exception in insert_order: {e}")
                raise
        
        return self._execute_with_lock(_operation)

    def remove_order(self, order_id):
        """Remove an order by ID"""
        def _operation(conn):
            try:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM orders WHERE id = ?', (order_id,))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                logging.error(f"Database error: {e}")
                raise DatabaseError(str(e))
            except Exception as e:
                logging.error(f"Exception in remove_order: {e}")
                raise
        
        return self._execute_with_lock(_operation)

    def update_order(self, order_id, order):
        """Update an existing order after validation"""
        def _operation(conn):
            try:
                self._validate_order(order)
                cursor = conn.cursor()
                # Get the tuple values (now includes id as first element)
                values = order.to_tuple()
                # Remove the id from the start and add it to the end for the WHERE clause
                values = values[1:] + (order_id,)
                cursor.execute('''
                    UPDATE orders SET
                        order_number = ?,
                        amount = ?,
                        image_uri = ?,
                        comment_with_picture = ?,
                        commented = ?,
                        revealed = ?,
                        reimbursed = ?,
                        reimbursed_amount = ?,
                        note = ?
                    WHERE id = ?
                ''', values)
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                logging.error(f"Database error: {e}")
                raise DatabaseError(str(e))
            except Exception as e:
                logging.error(f"Exception in update_order: {e}")
                raise
        
        return self._execute_with_lock(_operation)

    def get_order_by_number(self, order_number: str):
        """Get an order by its order number"""
        def _operation(conn):
            try:
                logging.info(f"Database: Getting order with number {order_number}")
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM orders WHERE order_number = ?', (order_number,))
                result = cursor.fetchone()
                
                if result:
                    logging.info(f"Database: Found order {order_number} - ID: {result[0]}")
                else:
                    logging.warning(f"Database: Order {order_number} not found in database")
                    
                    # Debug: Get a count of all orders
                    cursor.execute('SELECT COUNT(*) FROM orders')
                    count = cursor.fetchone()[0]
                    logging.info(f"Database: Total order count: {count}")
                    
                    # Debug: Get all order numbers
                    cursor.execute('SELECT order_number FROM orders')
                    all_orders = cursor.fetchall()
                    logging.info(f"Database: Available order numbers: {[o[0] for o in all_orders]}")
                
                return result
            except sqlite3.Error as e:
                logging.error(f"Database error in get_order_by_number: {e}", exc_info=True)
                raise DatabaseError(f"Failed to get order {order_number}: {str(e)}")
            except Exception as e:
                logging.error(f"Exception in get_order_by_number: {e}", exc_info=True)
                raise
        
        return self._execute_with_lock(_operation)

    def close(self):
        """Close all database connections"""
        if self._pool:
            self._pool.close_all() 