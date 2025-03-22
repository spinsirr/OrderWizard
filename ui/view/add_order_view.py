import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import sys
import logging
from ui.viewmodel.order_list_viewmodel import OrderListViewModel
from model.order import Order
import re
import threading

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    logging.warning("tkinterdnd2 not available, drag and drop will be disabled")
    DND_FILES = None
    TkinterDnD = tk.Tk

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
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

class AddOrderView(ttk.Frame):
    def __init__(self, parent, viewmodel: OrderListViewModel):
        super().__init__(parent, padding=20)
        self.parent = parent
        self.viewmodel = viewmodel
        
        # Store current image for display
        self.current_image_display = None
        self.current_image_path = None
        self.ocr_in_progress = False
        
        # Set up drop target registration
        self.drop_target_register = self.register_drop_target if hasattr(self, 'register_drop_target') else None
        
        self._init_ui()
        self.pack(fill=tk.BOTH, expand=True)
        
        # Setup drag and drop if available
        if DND_FILES:
            self.image_label.drop_target_register(DND_FILES)
            self.image_label.dnd_bind('<<Drop>>', self._on_drop)
        
    def _init_ui(self):
        """Initialize all UI components"""
        # Create title
        title = ttk.Label(
            self,
            text="Add New Order",
            font=("Helvetica", 24, "bold")
        )
        title.pack(pady=(0, 20))
        
        # Create horizontal container for image and text sections
        self.content_container = ttk.Frame(self)
        self.content_container.pack(fill=tk.BOTH, expand=True)
        
        self._init_image_section()
        self._init_text_section()
        self._init_order_options()
        self._init_buttons()
        
    def _init_image_section(self):
        """Initialize image section UI"""
        # Image section (left side)
        self.image_frame = ttk.LabelFrame(
            self.content_container,
            text="Order Image (Optional)",
            padding=10
        )
        self.image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Status label for feedback
        self.status_label = ttk.Label(
            self.image_frame,
            text="",
            foreground="blue",
            wraplength=300  # Allow text to wrap
        )
        self.status_label.pack(fill=tk.X, pady=(0, 10))
        
        # Image display label with drag and drop support
        if DND_FILES:
            from tkinterdnd2 import DND_TEXT
            self.image_label = ttk.Label(
                self.image_frame,
                text="Drop an image here or click 'Browse'",
                padding=10
            )
        else:
            self.image_label = ttk.Label(
                self.image_frame,
                text="Click 'Browse' to select an image",
                padding=10
            )
        self.image_label.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # OCR processing indicator
        self.ocr_indicator = ttk.Label(
            self.image_frame,
            text="",
            foreground="blue"
        )
        self.ocr_indicator.pack(fill=tk.X, expand=False)
        
        # Add browse button
        self.browse_button = ttk.Button(
            self.image_frame,
            text="Browse",
            command=self._browse_image
        )
        self.browse_button.pack(pady=(0, 10))
        
    def _init_text_section(self):
        """Initialize text section UI"""
        # Text section (right side)
        self.text_frame = ttk.LabelFrame(
            self.content_container,
            text="Order Details",
            padding=10
        )
        self.text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Text area for order details
        self.text_area = tk.Text(
            self.text_frame,
            wrap=tk.WORD,
            font=("Helvetica", 11),
            height=10,  # Reduced height to make room for note
            width=50
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Note section
        note_label = ttk.Label(
            self.text_frame,
            text="Note (optional):",
            font=("Helvetica", 11)
        )
        note_label.pack(anchor=tk.W, pady=(10, 5))
        
        self.note_area = tk.Text(
            self.text_frame,
            wrap=tk.WORD,
            font=("Helvetica", 11),
            height=5,
            width=50
        )
        self.note_area.pack(fill=tk.BOTH, expand=True)
        
    def _init_order_options(self):
        """Initialize order options section"""
        # Create options frame
        self.options_frame = ttk.Frame(self)
        self.options_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Add checkbox for comment with picture
        self.comment_var = tk.BooleanVar(value=False)
        self.comment_checkbox = ttk.Checkbutton(
            self.options_frame,
            text="Comment with Picture",
            variable=self.comment_var,
            command=self._on_comment_changed
        )
        self.comment_checkbox.pack(side=tk.LEFT)
        
    def _init_buttons(self):
        """Initialize button section UI"""
        # Create a frame for buttons
        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Submit button
        self.submit_button = ttk.Button(
            self.button_frame,
            text="Submit Order",
            command=self.submit_order
        )
        self.submit_button.pack(side=tk.RIGHT)
        
        # Clear button
        self.clear_button = ttk.Button(
            self.button_frame,
            text="Clear",
            command=self.clear_form
        )
        self.clear_button.pack(side=tk.RIGHT, padx=(0, 10))

    def _on_comment_changed(self):
        """Handle comment checkbox state change"""
        self.viewmodel.set_comment_with_picture(self.comment_var.get())

    def _browse_image(self):
        """Open file browser to select an image"""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self._process_image(file_path)
    
    def _update_ocr_status(self, message, is_done=False):
        """Update OCR status indicator"""
        if is_done:
            self.ocr_in_progress = False
            
        # Use after to ensure thread safety
        self.after(0, lambda: self.ocr_indicator.configure(text=message))
            
    def _on_ocr_complete(self, success, result):
        """Callback for when OCR completes"""
        if success:
            # Try to clean up the text
            cleaned_text = self._clean_ocr_text(result)
            
            # Update UI in the main thread
            self.after(0, lambda: self._update_text_area(cleaned_text))
            self._update_ocr_status("Text extraction complete", True)
        else:
            self._update_ocr_status(f"OCR failed: {result}", True)
            
    def _update_text_area(self, text):
        """Update text area with extracted text"""
        # Clear existing text
        self.text_area.delete(1.0, tk.END)
        # Insert cleaned text
        self.text_area.insert(tk.END, text)
        # Show success message in status
        self._show_status("Text extracted from image. Please verify the order details.")
    
    def _process_image(self, file_path):
        """Process the selected image file"""
        try:
            # Validate file type
            if not self._is_valid_image(file_path):
                self._show_status("Invalid file type. Please select an image file (PNG, JPG, JPEG, GIF, BMP)", True)
                return
            
            # Store the image path
            self.current_image_path = file_path
            
            # Update the image preview immediately
            self._update_image_preview(file_path)
            
            # Show processing indicator
            self.ocr_in_progress = True
            self._update_ocr_status("Extracting text from image...")
            
            # Set the image in viewmodel and start OCR
            success, extracted_text = self.viewmodel.set_current_image(file_path)
            
            if not success:
                self._update_ocr_status("Failed to process image", True)
                self._show_status("Failed to process image", True)
                return
                
            # If we got text back immediately (from cache), update UI
            if extracted_text:
                cleaned_text = self._clean_ocr_text(extracted_text)
                self._update_text_area(cleaned_text)
                self._update_ocr_status("Text extraction complete", True)
                return
                
            # Otherwise register for callback when OCR completes
            self.viewmodel.set_ocr_callback(file_path, self._on_ocr_complete)
                
        except Exception as e:
            logging.error(f"Error processing image: {e}")
            self._update_ocr_status("", True)
            self._show_status(f"Error processing image: {str(e)}", True)

    def _clean_ocr_text(self, text: str) -> str:
        """
        Clean up OCR text to better match expected format
        Order number format: ORDER # xxx-xxxxxxx-xxxxxxx
        Amount format: $xx.xx or $xxx.xx or $xxxx.xx
        """
        try:
            # Split into lines
            lines = text.split('\n')
            
            order_number = None
            amount = None
            
            # First pass: look for amount and order number
            for line in lines:
                line = line.strip().replace("'", "")  # Remove single quotes
                if not line:
                    continue
                
                # Try to find amount first (it's more reliable)
                if '$' in line:
                    # Extract amount using regex
                    amount_match = re.search(r'\$(\d{2,4}\.\d{2}(?!\d))', line)
                    if amount_match:
                        amount = amount_match.group(0)  # Include the $ sign
                
                # Try to find order number with flexible matching
                if 'ORDER' in line.upper() and '#' in line:
                    # Extract order number using regex
                    # More flexible pattern matching
                    order_match = re.search(r'(?:ORDER.*?#|#)\s*(\d{3}-\d{7}-\d{7})', line.upper())
                    if order_match:
                        order_number = order_match.group(1)
            
            # If we found both order number and amount, combine them
            if order_number and amount:
                return f"{order_number} {amount}"
            
            # If we only found order number, do another pass for amount
            if order_number:
                for line in lines:
                    amount_match = re.search(r'\$(\d{2,4}\.\d{2}(?!\d))', line)
                    if amount_match:
                        amount = amount_match.group(0)
                        return f"{order_number} {amount}"
            
            # If we only found amount, do another pass for order number
            if amount:
                for line in lines:
                    line = line.strip().replace("'", "")
                    if 'ORDER' in line.upper() and '#' in line:
                        order_match = re.search(r'(?:ORDER.*?#|#)\s*(\d{3}-\d{7}-\d{7})', line.upper())
                        if order_match:
                            order_number = order_match.group(1)
                            return f"{order_number} {amount}"
            
            # If we couldn't process it, return original text
            return text
            
        except Exception as e:
            logging.error(f"Error cleaning OCR text: {e}")
            # If cleaning fails, return original text
            return text

    def _is_valid_image(self, file_path):
        """Check if the file is a valid image"""
        return file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))
        
    def _update_image_preview(self, file_path):
        """Update the image preview"""
        try:
            # Open and resize image
            image = Image.open(file_path)
            
            # Calculate resize dimensions while maintaining aspect ratio
            display_width = 300  # Maximum width for display
            display_height = 300  # Maximum height for display
            
            # Calculate aspect ratio
            aspect_ratio = image.width / image.height
            
            if aspect_ratio > 1:
                # Width is greater than height
                new_width = display_width
                new_height = int(display_width / aspect_ratio)
            else:
                # Height is greater than width
                new_height = display_height
                new_width = int(display_height * aspect_ratio)
            
            # Resize image
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # Update label with image
            self.image_label.configure(image=photo, text="")
            self.current_image_display = photo  # Keep a reference
            
        except Exception as e:
            logging.error(f"Error loading image preview: {e}")
            self._show_status(f"Error loading image preview: {str(e)}", True)

    def submit_order(self):
        """Handle order submission"""
        # If OCR is still in progress, show warning in status
        if self.ocr_in_progress:
            self._show_status("Text extraction is still in progress. Please wait.", True)
            return
        
        order_text = self.text_area.get("1.0", tk.END).strip()
        note_text = self.note_area.get("1.0", tk.END).strip()
        
        if not order_text:
            self._show_status("Please enter order details", True)
            return
            
        try:
            # Create order from text
            order = self.viewmodel.add_order(order_text)
            
            if order:
                # Show success message in status
                self._show_status("Order added successfully")
                
                # Clear form
                self.clear_form()
            else:
                self._show_status("Failed to add order", True)
                
        except ValueError as e:
            # Show more specific error message in status
            error_msg = str(e)
            if "Invalid amount format" in error_msg:
                self._show_status("Please ensure the amount is in the format: 123.45 or $123.45", True)
            elif "Order number not found" in error_msg:
                self._show_status("Please ensure the order number is included", True)
            else:
                self._show_status(f"Error: {error_msg}", True)
        except Exception as e:
            logging.error(f"Error adding order: {e}")
            self._show_status(f"Error adding order: {str(e)}", True)
    
    def clear_form(self):
        """Clear all form fields"""
        # Clear text areas
        self.text_area.delete("1.0", tk.END)
        self.note_area.delete("1.0", tk.END)
        
        # Clear image
        self.image_label.configure(image="", text="Click 'Browse' to select an image or drop an image here")
        self.current_image_display = None
        self.current_image_path = None
        self.viewmodel.clear_current_image()
        
        # Clear OCR status
        self.ocr_indicator.configure(text="")
        self.ocr_in_progress = False
        
        # Clear comment with picture
        self.comment_var.set(False)
        self.viewmodel.clear_comment_with_picture()

    def _on_drop(self, event):
        """Handle drag and drop events"""
        try:
            # Get the file path from the event
            file_path = event.data
            
            # Remove curly braces if present (Windows)
            if file_path.startswith('{') and file_path.endswith('}'):
                file_path = file_path[1:-1]
            
            # Process the dropped image
            if self._is_valid_image(file_path):
                self._process_image(file_path)
            else:
                self._show_status("Please drop a valid image file (PNG, JPG, JPEG, GIF, BMP)", True)
        except Exception as e:
            logging.error(f"Error handling dropped file: {e}")
            self._show_status(f"Error processing file: {str(e)}", True)

    def _show_status(self, message, is_error=False):
        """Show status message"""
        self.status_label.configure(
            text=message,
            foreground="red" if is_error else "blue"
        )
        # Clear status after 3 seconds
        self.after(3000, lambda: self.status_label.configure(text="")) 