from db.database import Database, get_user_data_dir
from model.order import Order
from typing import List, Tuple, Optional, Callable
from PIL import Image
import os
import sys
import shutil
import threading
import logging
import time

# Lazy import pytesseract to improve startup speed
pytesseract = None

def load_pytesseract():
    """Lazy load pytesseract only when needed"""
    global pytesseract
    if pytesseract is None:
        try:
            import pytesseract as pt
            pytesseract = pt
        except ImportError as e:
            logging.error(f"Failed to import pytesseract: {e}")
            return False
    return True

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # Check if we should use user data directory for images
        if relative_path.startswith('images/'):
            return os.path.join(get_user_data_dir(), relative_path)
            
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
            # Check if we're in app bundle on macOS
            if sys.platform == 'darwin' and os.path.exists(os.path.join(os.path.dirname(sys.executable), '..', 'Resources')):
                resources_path = os.path.join(os.path.dirname(sys.executable), '..', 'Resources')
                return os.path.join(resources_path, relative_path)
            return os.path.join(base_path, relative_path)
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', relative_path)
    except Exception as e:
        logging.error(f"Error getting resource path: {e}")
        return relative_path

class OrderListViewModel:
    def __init__(self):
        self.db = Database()
        self._orders: List[Tuple] = []
        self._on_data_changed: Optional[Callable] = None
        self._current_image = None
        self._current_image_path = None
        self._comment_with_picture = False
        self._ocr_results = {}  # Cache for OCR results
        self._ocr_callbacks = {}  # Callbacks for when OCR completes
        self._ocr_lock = threading.Lock()
        
        # Ensure images directory exists in user data directory
        self.images_dir = os.path.join(get_user_data_dir(), 'images')
        os.makedirs(self.images_dir, exist_ok=True)
        
        # Start background thread to preload pytesseract
        threading.Thread(target=load_pytesseract, daemon=True).start()

    def load_orders(self):
        """Load orders from database"""
        try:
            self._orders = self.db.get_all_orders()
            self._notify_data_changed()
        except Exception as e:
            logging.error(f"Error loading orders: {e}")

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
                    logging.error(f"Error deleting image file: {e}")
            
            # Refresh the orders list
            self.load_orders()
            return True
            
        except Exception as e:
            logging.error(f"Error deleting order: {e}")
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
            logging.error(f"Error copying image: {e}")
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
            logging.error(f"Error adding order: {e}")
            return None

    def _perform_ocr(self, image_path: str, callback=None):
        """
        Perform OCR in a background thread
        
        Args:
            image_path: Path to the image file
            callback: Function to call with results
        """
        threading.Thread(
            target=self._ocr_thread,
            args=(image_path, callback),
            daemon=True
        ).start()
        
    def _ocr_thread(self, image_path: str, callback=None):
        """
        Thread function for OCR processing
        
        Args:
            image_path: Path to the image file
            callback: Function to call with results
        """
        if not load_pytesseract():
            if callback:
                callback(False, "Could not load OCR library")
            return
            
        try:
            # Check if we already have results for this image
            with self._ocr_lock:
                if image_path in self._ocr_results:
                    if callback:
                        callback(True, self._ocr_results[image_path])
                    return
                    
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
            
            # Extract text using pytesseract
            text = pytesseract.image_to_string(image)
            
            # Clean up the extracted text
            text = text.strip()
            
            # Cache the result
            with self._ocr_lock:
                self._ocr_results[image_path] = text
                
            # Log the result
            logging.info(f"OCR Result from {image_path}:")
            logging.info(text)
            
            # Call callback with result
            if callback:
                callback(True, text)
                
        except Exception as e:
            logging.error(f"Error extracting text from image: {e}")
            if callback:
                callback(False, str(e))

    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from image using OCR
        
        Args:
            image_path: Path to the image file
            
        Returns:
            str: Extracted text from the image
        """
        # For immediate return without waiting for threading
        if image_path in self._ocr_results:
            return self._ocr_results[image_path]
            
        # Synchronous fallback mode for rapid startup
        if not load_pytesseract():
            return ""
            
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
            
            # Extract text using pytesseract
            text = pytesseract.image_to_string(image)
            
            # Clean up the extracted text
            text = text.strip()
            
            # Cache the result
            with self._ocr_lock:
                self._ocr_results[image_path] = text
            
            # Log the result
            logging.info(f"OCR Result from {image_path}:")
            logging.info(text)
            
            return text
        except Exception as e:
            logging.error(f"Error extracting text from image: {e}")
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
            
            # If we already have OCR results for this image, return them immediately
            if image_path in self._ocr_results:
                return True, self._ocr_results[image_path]
                
            # Start OCR in background
            self._perform_ocr(image_path)
            
            # Return success but with empty text (the UI will be updated later)
            return True, ""
        except Exception as e:
            logging.error(f"Error setting image: {e}")
            return False, None

    def set_ocr_callback(self, image_path: str, callback: Callable):
        """
        Set a callback for when OCR completes
        
        Args:
            image_path: Path to the image file
            callback: Function to call with results
        """
        # If we already have results, call callback immediately
        if image_path in self._ocr_results:
            callback(True, self._ocr_results[image_path])
            return
            
        # Otherwise store callback and start OCR
        with self._ocr_lock:
            self._ocr_callbacks[image_path] = callback
            
        # Start OCR in background
        self._perform_ocr(image_path, callback)

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
            logging.info(f"Fetching order with ID: {order_id}")
            
            # Attempt to get from database
            order_data = self.db.get_order_by_id(order_id)
            
            if order_data:
                logging.info(f"Order found in database: {order_data[0]}, {order_data[1]}")
                return order_data
            
            # If not found, log detailed information and try refreshing
            logging.warning(f"Order {order_id} not found in database, refreshing orders list")
            self.refresh()  # Refresh orders from database
            
            # Try again after refresh
            order_data = self.db.get_order_by_id(order_id)
            if order_data:
                logging.info(f"Order found after refresh: {order_data[0]}, {order_data[1]}")
                return order_data
                
            # If still not found, check _orders list for debugging
            order_ids = [order[0] for order in self._orders]
            logging.error(f"Order {order_id} not found even after refresh. Available IDs: {order_ids}")
            
            # Final fallback: manually search in _orders list
            for order in self._orders:
                if order[0] == order_id:
                    logging.info(f"Order found in local cache: {order[0]}, {order[1]}")
                    return order
                    
            return None
        except Exception as e:
            logging.error(f"Error getting order: {e}", exc_info=True)
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
            logging.error(f"Error updating order: {e}")
            return False

    def __del__(self):
        """Cleanup database connection"""
        self.db.close() 