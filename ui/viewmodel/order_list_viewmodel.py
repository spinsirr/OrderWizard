from db.database import Database
from model.order import Order
from typing import List, Tuple, Optional, Callable
from PIL import Image
import os
import shutil

class OrderListViewModel:
    def __init__(self):
        self.db = Database()
        self._orders: List[Tuple] = []
        self._on_data_changed: Optional[Callable] = None
        self._current_image = None
        self._current_image_path = None
        self._comment_with_picture = False
        
        # Ensure images directory exists
        self.images_dir = "images"
        os.makedirs(self.images_dir, exist_ok=True)

    def load_orders(self):
        """Load orders from database"""
        try:
            self._orders = self.db.get_all_orders()
            self._notify_data_changed()
        except Exception as e:
            print(f"Error loading orders: {e}")

    @property
    def orders(self) -> List[Tuple]:
        """Get current orders"""
        return self._orders

    def set_data_changed_callback(self, callback: Callable):
        """Set callback for data changes"""
        self._on_data_changed = callback

    def _notify_data_changed(self):
        """Notify observers of data changes"""
        if self._on_data_changed:
            self._on_data_changed()

    def refresh(self):
        """Refresh order data"""
        self.load_orders()

    def _copy_image_for_order(self, order_number: str, source_path: str) -> Optional[str]:
        """
        Copy image to images directory with order number as name
        
        Args:
            order_number: The order number to use as filename
            source_path: Path to the source image
            
        Returns:
            str: Path to the copied image, or None if copy failed
        """
        try:
            # Get file extension from source
            _, ext = os.path.splitext(source_path)
            
            # Create destination path
            dest_filename = f"{order_number}{ext}"
            dest_path = os.path.join(self.images_dir, dest_filename)
            
            # Copy the file
            shutil.copy2(source_path, dest_path)
            
            return dest_path
        except Exception as e:
            print(f"Error copying image: {e}")
            return None

    def add_order(self, order_text: str) -> bool:
        """
        Add a new order to the database and update the orders list
        
        Args:
            order_text: The raw order text to parse
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create order from text
            order = Order.create_from_text(order_text)
            
            # Set image path if available
            if self._current_image_path:
                # Copy image to images directory with order number as name
                new_image_path = self._copy_image_for_order(
                    order.order_number,
                    self._current_image_path
                )
                if new_image_path:
                    order.image_uri = new_image_path
                
            # Set comment with picture flag
            order.comment_with_picture = self._comment_with_picture
                
            # Add to database
            self.db.insert_order(order)
            
            # Refresh orders list
            self.load_orders()
            
            return True
        except Exception as e:
            print(f"Error adding order: {e}")
            return False

    def set_current_image(self, image_path: str) -> bool:
        """
        Set the current image for the next order
        
        Args:
            image_path: Path to the image file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self._current_image_path = image_path
            return True
        except Exception as e:
            print(f"Error setting image: {e}")
            return False

    def set_comment_with_picture(self, has_comment: bool):
        """Set whether the current order has a comment with the picture"""
        self._comment_with_picture = has_comment

    def get_comment_with_picture(self) -> bool:
        """Get whether the current order has a comment with the picture"""
        return self._comment_with_picture

    def clear_current_image(self):
        """Clear the current image data"""
        self._current_image = None
        self._current_image_path = None

    def clear_comment_with_picture(self):
        """Clear the comment with picture flag"""
        self._comment_with_picture = False

    def get_current_image_path(self) -> Optional[str]:
        """Get the current image path"""
        return self._current_image_path

    def __del__(self):
        """Cleanup database connection"""
        self.db.close() 