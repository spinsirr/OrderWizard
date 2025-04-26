import logging
import os
import sys
from datetime import datetime, timedelta
import random

# Add parent directory to path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.database import Database
from model.order import Order

def seed_test_database():
    """Seed the test database with sample data"""
    logging.info("Seeding test database with sample data...")
    
    # Make sure we're not in production mode
    if os.environ.get('ORDERWIZARD_PROD_MODE', '0') == '1':
        logging.error("Cannot seed test database in production mode!")
        return
    
    # Initialize database
    db = Database()
    
    # Clear existing data
    conn = db._pool.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM orders")
        conn.commit()
        logging.info("Cleared existing test data")
    except Exception as e:
        logging.error(f"Error clearing test database: {e}")
    finally:
        db._pool.return_connection(conn)
    
    # Sample order data
    sample_orders = [
        # Order Number, Amount, Has Comment, Commented, Revealed, Reimbursed, Note
        ("112-4567890-1234567", 25.99, True, True, True, True, "Computer accessories"),
        ("113-1234567-8901234", 75.50, True, True, True, False, "Kitchen appliance"),
        ("114-9876543-2109876", 12.99, True, True, False, False, "Office supplies"),
        ("115-4567890-0987654", 149.99, True, False, False, False, "Monitor stand"),
        ("116-7890123-4567890", 8.75, False, False, False, False, "Desk lamp"),
        ("117-3456789-0123456", 199.99, False, False, False, False, "Wireless headphones"),
        ("118-9012345-6789012", 35.50, False, False, False, False, "Keyboard"),
        ("119-5678901-2345678", 19.95, False, False, False, False, "Mouse pad"),
        ("120-1234567-8901234", 299.99, False, False, False, False, "Smart watch"),
        ("121-9876543-2109876", 15.75, False, False, False, False, "USB cables")
    ]
    
    # Create and insert orders
    for i, (order_number, amount, has_comment, commented, revealed, reimbursed, note) in enumerate(sample_orders):
        try:
            # Create order
            order = Order(
                order_number=order_number,
                amount=amount,
                comment_with_picture=has_comment,
                commented=commented,
                revealed=revealed,
                reimbursed=reimbursed,
                note=note
            )
            
            # Insert order
            order_id = db.insert_order(order)
            logging.info(f"Added test order: {order_number} (ID: {order_id})")
            
        except Exception as e:
            logging.error(f"Error adding test order {order_number}: {e}")
    
    # Verify seeded data
    conn = db._pool.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM orders")
        count = cursor.fetchone()[0]
        logging.info(f"Test database seeded with {count} orders")
    except Exception as e:
        logging.error(f"Error verifying test data: {e}")
    finally:
        db._pool.return_connection(conn)

if __name__ == "__main__":
    # Configure basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    seed_test_database() 