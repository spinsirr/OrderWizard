import sqlite3
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class DatabaseError(Exception):
    """Custom exception for database errors"""
    pass

class Database:
    def __init__(self, db_name="orders.db"):
        self.db_name = db_name
        self.initialize_database()

    def initialize_database(self):
        """Initialize the database and verify its structure"""
        try:
            # Check if database file exists
            db_exists = os.path.exists(self.db_name)
            
            # Create tables
            self._create_table()
            
            if not db_exists:
                logging.info(f"New database created: {self.db_name}")
            
            # Verify database structure
            if self._verify_database_structure():
                logging.info("Database structure verified successfully")
            else:
                logging.error("Database structure verification failed")
                
        except Exception as e:
            logging.error(f"Database initialization failed: {e}")
            raise

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
            with sqlite3.connect(self.db_name) as conn:
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
                    'reimbursed', 'reimbursed_amount', 'created_at'
                }
                
                if not expected_columns.issubset(columns):
                    logging.error(f"Missing columns: {expected_columns - columns}")
                    return False
                
                return True
                
        except sqlite3.Error as e:
            logging.error(f"Database verification failed: {e}")
            return False

    def _create_table(self):
        """Create the orders table if it doesn't exist"""
        with sqlite3.connect(self.db_name) as conn:
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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create index on order_number for faster lookups
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_order_number 
                ON orders(order_number)
            ''')
            
            conn.commit()

    def insert_order(self, order):
        """Insert a new order after validation"""
        try:
            self._validate_order(order)
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO orders (
                        order_number, amount, image_uri, comment_with_picture, 
                        commented, revealed, reimbursed, reimbursed_amount
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    order.order_number, order.amount, order.image_uri, order.comment_with_picture,
                    order.commented, order.revealed, order.reimbursed, order.reimbursed_amount
                ))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")
            raise DatabaseError(str(e))
        except Exception as e:
            logging.error(f"Exception in insert_order: {e}")
            raise

    def remove_order(self, order_id):
        """Remove an order by ID"""
        try:
            with sqlite3.connect(self.db_name) as conn:
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

    def update_order(self, order_id, order):
        """Update an existing order after validation"""
        try:
            self._validate_order(order)
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE orders SET
                        order_number = ?,
                        amount = ?,
                        image_uri = ?,
                        comment_with_picture = ?,
                        commented = ?,
                        revealed = ?,
                        reimbursed = ?,
                        reimbursed_amount = ?
                    WHERE id = ?
                ''', (
                    order.order_number, order.amount, order.image_uri, order.comment_with_picture,
                    order.commented, order.revealed, order.reimbursed, order.reimbursed_amount,
                    order_id
                ))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")
            raise DatabaseError(str(e))
        except Exception as e:
            logging.error(f"Exception in update_order: {e}")
            raise

    def get_order_by_id(self, order_id):
        """Retrieve an order by its ID"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
                return cursor.fetchone()
        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")
            raise DatabaseError(str(e))
        except Exception as e:
            logging.error(f"Exception in get_order_by_id: {e}")
            raise

    def get_all_orders(self):
        """Retrieve all orders sorted by creation time (newest first)"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM orders ORDER BY created_at ASC')  # Changed to ASC
                return cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")
            raise DatabaseError(str(e))
        except Exception as e:
            logging.error(f"Exception in get_all_orders: {e}")
            raise

    def close(self):
        # No need to explicitly close connections when using context managers
        pass 