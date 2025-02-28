import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinterdnd2 import DND_FILES
from PIL import Image, ImageTk
from ui.viewmodel.order_list_viewmodel import OrderListViewModel
from model.order import Order
from ttkbootstrap.toast import ToastNotification
import re

class AddOrderView(ttk.Frame):
    def __init__(self, parent, viewmodel: OrderListViewModel):
        super().__init__(parent, padding="20")
        self.parent = parent
        self.viewmodel = viewmodel
        
        # Store current image for display
        self.current_image_display = None
        
        self._init_ui()
        self.pack(fill=BOTH, expand=YES)
        
    def _init_ui(self):
        """Initialize all UI components"""
        # Create title
        title = ttk.Label(
            self,
            text="Add New Order",
            font=("Helvetica", 24, "bold"),
            bootstyle="primary"
        )
        title.pack(pady=(0, 20))
        
        # Create horizontal container for image and text sections
        self.content_container = ttk.Frame(self)
        self.content_container.pack(fill=BOTH, expand=YES)
        
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
            padding="10"
        )
        self.image_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 10))
        
        # Image display label
        self.image_label = ttk.Label(
            self.image_frame,
            text="Drag and drop image here",
            bootstyle="secondary"
        )
        self.image_label.pack(fill=BOTH, expand=YES)
        
        # Configure drag and drop
        self.image_label.drop_target_register(DND_FILES)
        self.image_label.dnd_bind('<<Drop>>', self._handle_drop)
        
    def _init_text_section(self):
        """Initialize text section UI"""
        # Text section (right side)
        self.text_frame = ttk.LabelFrame(
            self.content_container,
            text="Order Details",
            padding="10"
        )
        self.text_frame.pack(side=LEFT, fill=BOTH, expand=YES)
        
        # Text area for order details
        self.text_area = tk.Text(
            self.text_frame,
            wrap=tk.WORD,
            font=("Helvetica", 11),
            height=10,  # Reduced height to make room for note
            width=50
        )
        self.text_area.pack(fill=BOTH, expand=YES, pady=(0, 10))
        
        # Note section
        note_label = ttk.Label(
            self.text_frame,
            text="Note (optional):",
            font=("Helvetica", 11)
        )
        note_label.pack(anchor=W, pady=(10, 5))
        
        self.note_area = tk.Text(
            self.text_frame,
            wrap=tk.WORD,
            font=("Helvetica", 11),
            height=5,
            width=50
        )
        self.note_area.pack(fill=BOTH, expand=YES)
        
    def _init_order_options(self):
        """Initialize order options section"""
        # Create options frame
        self.options_frame = ttk.Frame(self)
        self.options_frame.pack(fill=X, pady=(10, 0))
        
        # Add checkbox for comment with picture
        self.comment_var = tk.BooleanVar(value=False)
        self.comment_checkbox = ttk.Checkbutton(
            self.options_frame,
            text="Comment with Picture",
            variable=self.comment_var,
            command=self._on_comment_changed,
            bootstyle="primary-round-toggle"
        )
        self.comment_checkbox.pack(side=LEFT)
        
    def _init_buttons(self):
        """Initialize button section UI"""
        # Create a frame for buttons
        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(fill=X, pady=(20, 0))
        
        # Submit button
        self.submit_button = ttk.Button(
            self.button_frame,
            text="Submit Order",
            command=self.submit_order,
            bootstyle="primary"
        )
        self.submit_button.pack(side=RIGHT)
        
        # Clear button
        self.clear_button = ttk.Button(
            self.button_frame,
            text="Clear",
            command=self.clear_form,
            bootstyle="secondary"
        )
        self.clear_button.pack(side=RIGHT, padx=(0, 10))

    def _on_comment_changed(self):
        """Handle comment checkbox state change"""
        self.viewmodel.set_comment_with_picture(self.comment_var.get())
        self.viewmodel.refresh()

    def _handle_drop(self, event):
        """Handle file drop event"""
        try:
            # Get the dropped file path and remove curly braces if present (Windows)
            file_path = event.data.strip('{}')
            
            # Validate file type
            if not self._is_valid_image(file_path):
                self._show_error("Invalid file type. Please drop an image file (PNG, JPG, JPEG, GIF, BMP)")
                return
            
            # Set the image in viewmodel and get extracted text
            success, extracted_text = self.viewmodel.set_current_image(file_path)
            
            if success:
                # Update the image preview
                self._update_image_preview(file_path)
                
                # If text was extracted, update the order text
                if extracted_text:
                    # Try to clean up the text
                    cleaned_text = self._clean_ocr_text(extracted_text)
                    
                    # Clear existing text
                    self.text_area.delete(1.0, tk.END)
                    # Insert cleaned text
                    self.text_area.insert(tk.END, cleaned_text)
                    
                    # Show success toast
                    toast = ToastNotification(
                        title="OCR Success",
                        message="Text extracted from image. Please verify the order number and amount.",
                        duration=5000,  # Show for 5 seconds
                        bootstyle="success",
                        position=(80, 50, "se")
                    )
                    toast.show_toast()
                else:
                    self._show_error("No text could be extracted from the image")
            else:
                self._show_error("Failed to process the image")
                
        except Exception as e:
            self._show_error(f"Error processing dropped file: {str(e)}")

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
            print(f"Error cleaning OCR text: {e}")
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
            self._show_error(f"Error loading image preview: {str(e)}")
            
    def _show_error(self, message):
        """Show an error message"""
        toast = ToastNotification(
            title="Error",
            message=message,
            duration=3000,
            bootstyle="danger",
            position=(80, 50, "se")  # Bottom right corner
        )
        toast.show_toast()

    def submit_order(self):
        """Handle order submission"""
        order_text = self.text_area.get("1.0", tk.END).strip()
        note_text = self.note_area.get("1.0", tk.END).strip()
        
        if not order_text:
            self._show_error("Please enter order details")
            return
            
        try:
            # Create order from text
            order = self.viewmodel.add_order(order_text)
            
            if order:
                # Show success message
                toast = ToastNotification(
                    title="Success",
                    message="Order added successfully",
                    duration=3000,
                    bootstyle="success",
                    position=(80, 50, "se")
                )
                toast.show_toast()
                
                # Clear form
                self.clear_form()
            else:
                self._show_error("Failed to add order")
                
        except ValueError as e:
            # Show more specific error message for validation errors
            error_msg = str(e)
            if "Invalid amount format" in error_msg:
                self._show_error("Please ensure the amount is in the format: 123.45 or $123.45")
            elif "Order number not found" in error_msg:
                self._show_error("Please ensure the order number is included")
            else:
                self._show_error(f"Error adding order: {error_msg}")
        except Exception as e:
            self._show_error(f"Error adding order: {str(e)}")
    
    def clear_form(self):
        """Clear all form fields"""
        # Clear text areas
        self.text_area.delete("1.0", tk.END)
        self.note_area.delete("1.0", tk.END)
        
        # Clear image
        self.image_label.configure(image="", text="Drag and drop image here")
        self.current_image_display = None
        self.viewmodel.clear_current_image()
        
        # Clear comment with picture
        self.comment_var.set(False)
        self.viewmodel.clear_comment_with_picture() 