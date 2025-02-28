from db.database import Database
from model.order import Order
from typing import List, Tuple, Optional, Callable
from PIL import Image
import os
import shutil
import pytesseract

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

    def delete_order(self, order_id: int) -> bool:
        """
        Delete an order from the database
        
        Args:
            order_id: The ID of the order to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get the order before deleting (to get image path)
            order = next((o for o in self._orders if o[0] == order_id), None)
            
            # Delete from database
            if not self.db.remove_order(order_id):
                return False
                
            # If order had an image, delete it
            if order and order[3]:  # image_uri
                try:
                    if os.path.exists(order[3]):
                        os.remove(order[3])
                except Exception as e:
                    print(f"Error deleting image file: {e}")
            
            # Refresh the orders list
            self.load_orders()
            return True
            
        except Exception as e:
            print(f"Error deleting order: {e}")
            return False

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

    def add_order(self, order_text: str) -> Optional[Order]:
        """
        Add a new order to the database and update the orders list
        
        Args:
            order_text: The raw order text to parse
            
        Returns:
            Order: The created order object if successful, None otherwise
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
            order_id = self.db.insert_order(order)
            if order_id:
                order.id = order_id
                # Refresh orders list
                self.load_orders()
                return order
                
            return None
        except Exception as e:
            print(f"Error adding order: {e}")
            return None

    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from image using OCR
        
        Args:
            image_path: Path to the image file
            
        Returns:
            str: Extracted text from the image
        """
        try:
            # Open the image
            image = Image.open(image_path)
            
            # Convert PNG with transparency to RGB
            if image.mode == 'RGBA':
                # Create a white background image
                background = Image.new('RGB', image.size, (255, 255, 255))
                # Paste the image on the background
                background.paste(image, mask=image.split()[3])  # 3 is the alpha channel
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Optionally enhance image for better OCR results
            # image = image.filter(ImageFilter.SHARPEN)
            
            # Extract text using pytesseract
            text = pytesseract.image_to_string(image)
            
            # Clean up the extracted text
            text = text.strip()
            
            # Log the result
            print(f"OCR Result from {image_path}:")
            print(text)
            
            return text
        except Exception as e:
            print(f"Error extracting text from image: {e}")
            return ""

    def set_current_image(self, image_path: str) -> Tuple[bool, Optional[str]]:
        """
        Set the current image for the next order and extract text
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Tuple[bool, Optional[str]]: (success, extracted_text)
        """
        try:
            self._current_image_path = image_path
            # Extract text from the image
            extracted_text = self.extract_text_from_image(image_path)
            return True, extracted_text
        except Exception as e:
            print(f"Error setting image: {e}")
            return False, None

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

    def get_order_by_id(self, order_id: int) -> Optional[tuple]:
        """
        Get order data by ID
        
        Args:
            order_id: The ID of the order to retrieve
            
        Returns:
            tuple: Order data if found, None otherwise
        """
        try:
            return self.db.get_order_by_id(order_id)
        except Exception as e:
            print(f"Error getting order: {e}")
            return None
            
    def update_order(self, order_id: int, order: Order) -> bool:
        """
        Update an existing order
        
        Args:
            order_id: The ID of the order to update
            order: The updated order data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.db.update_order(order_id, order):
                self.refresh()
                return True
            return False
        except Exception as e:
            print(f"Error updating order: {e}")
            return False

    def __del__(self):
        """Cleanup database connection"""
        self.db.close() 