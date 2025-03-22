import unittest
import os
from db.database import Database
from model.order import Order

class TestDatabase(unittest.TestCase):
    def setUp(self):
        """Set up test database before each test"""
        self.test_db_name = "test_orders.db"
        self.db = Database(self.test_db_name)
        self.sample_order = Order(
            order_number="123-4567890-1234567",
            amount=99.99,
            image_uri="path/to/test/image.jpg",
            comment_in_picture=True,
            commented=False,
            revealed=True,
            reimbursed=False,
            reimbursed_amount=0.0
        )

    def tearDown(self):
        """Clean up after each test"""
        self.db.close()
        if os.path.exists(self.test_db_name):
            os.remove(self.test_db_name)

    def test_database_initialization(self):
        """Test database initialization and structure verification"""
        self.assertTrue(os.path.exists(self.test_db_name))
        self.assertTrue(self.db._verify_database_structure())

    def test_insert_order(self):
        """Test inserting an order"""
        # Insert order
        order_id = self.db.insert_order(self.sample_order)
        
        # Verify insertion
        self.assertIsNotNone(order_id)
        
        # Retrieve and verify order
        order_data = self.db.get_order_by_id(order_id)
        self.assertIsNotNone(order_data)
        self.assertEqual(order_data[1], self.sample_order.order_number)
        self.assertEqual(float(order_data[2]), self.sample_order.amount)

    def test_update_order(self):
        """Test updating an order"""
        # First insert an order
        order_id = self.db.insert_order(self.sample_order)
        
        # Modify the order
        updated_order = Order(
            order_number=self.sample_order.order_number,
            amount=199.99,  # Changed amount
            image_uri=self.sample_order.image_uri,
            comment_in_picture=True,
            commented=True,  # Changed commented status
            revealed=True,
            reimbursed=True,  # Changed reimbursed status
            reimbursed_amount=199.99  # Changed reimbursed amount
        )
        
        # Update the order
        success = self.db.update_order(order_id, updated_order)
        self.assertTrue(success)
        
        # Verify update
        order_data = self.db.get_order_by_id(order_id)
        self.assertEqual(float(order_data[2]), updated_order.amount)
        self.assertTrue(order_data[5])  # commented
        self.assertTrue(order_data[7])  # reimbursed
        self.assertEqual(float(order_data[8]), updated_order.reimbursed_amount)

    def test_remove_order(self):
        """Test removing an order"""
        # First insert an order
        order_id = self.db.insert_order(self.sample_order)
        
        # Verify order exists
        self.assertIsNotNone(self.db.get_order_by_id(order_id))
        
        # Remove order
        success = self.db.remove_order(order_id)
        self.assertTrue(success)
        
        # Verify order no longer exists
        self.assertIsNone(self.db.get_order_by_id(order_id))

    def test_get_all_orders(self):
        """Test retrieving all orders"""
        # Insert multiple orders
        orders = [
            Order(order_number=f"ORDER-{i}", amount=float(i*10), 
                 image_uri=f"image_{i}.jpg")
            for i in range(1, 4)
        ]
        
        for order in orders:
            self.db.insert_order(order)
        
        # Retrieve all orders
        all_orders = self.db.get_all_orders()
        
        # Verify number of orders
        self.assertEqual(len(all_orders), len(orders))
        
        # Verify orders are returned in descending order of creation
        self.assertEqual(all_orders[0][1], "ORDER-1")
        self.assertEqual(all_orders[-1][1], "ORDER-3")

    def test_invalid_order_insert(self):
        """Test inserting invalid order data"""
        invalid_order = Order(
            order_number="",  # Invalid: empty order number
            amount=-10.0,  # Invalid: negative amount
            image_uri=None
        )
        
        # Attempt to insert invalid order should raise an exception
        with self.assertRaises(Exception):
            self.db.insert_order(invalid_order)

    def test_update_nonexistent_order(self):
        """Test updating an order that doesn't exist"""
        success = self.db.update_order(999, self.sample_order)
        self.assertFalse(success)

    def test_remove_nonexistent_order(self):
        """Test removing an order that doesn't exist"""
        success = self.db.remove_order(999)
        self.assertFalse(success)

if __name__ == '__main__':
    unittest.main() 