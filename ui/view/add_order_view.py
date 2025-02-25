import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinterdnd2 import DND_FILES
from PIL import Image, ImageTk
from model.order import Order
from db.database import Database

class AddOrderView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding="20")
        self.parent = parent
        
        # Store current state
        self.current_image = None
        self.current_image_path = None
        
        # Initialize database
        self.db = Database()
        
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
        self._init_buttons()
        
    def _init_image_section(self):
        """Initialize image section UI"""
        # Image section (left side)
        self.image_frame = ttk.LabelFrame(
            self.content_container,
            text="Order Image (Drag & Drop)",
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
        self.image_label.dnd_bind('<<Drop>>', self.handle_drop)
        
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
            height=20,
            width=50
        )
        self.text_area.pack(fill=BOTH, expand=YES)
        
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

    def handle_drop(self, event):
        """Handle image file drop event"""
        file_path = event.data
        # Remove curly braces if present (Windows)
        file_path = file_path.strip('{}')
        
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            self.load_image(file_path)
            self.current_image_path = file_path
        else:
            print("Please drop a valid image file")

    def load_image(self, file_path):
        """Load and display image"""
        try:
            # Open and resize image
            image = Image.open(file_path)
            # Calculate resize dimensions while maintaining aspect ratio
            display_width = 500  # Maximum width for display
            display_height = 500  # Maximum height for display
            
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
            
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            # Update label with image
            self.image_label.configure(image=photo, text="")
            self.current_image = photo  # Keep a reference
            
        except Exception as e:
            print(f"Error loading image: {e}")
    
    def submit_order(self):
        """Handle order submission"""
        order_text = self.text_area.get("1.0", tk.END).strip()
        if order_text:
            order = Order.create_from_text(order_text)
            if self.current_image_path:
                order.image_uri = self.current_image_path
                
            # Insert order into database
            self.db.insert_order(order)
            
            print("\n=== Order Details ===")
            print(f"Order Number: {order.order_number}")
            print(f"Amount: ${order.amount:.2f}")
            print(f"Image URI: {order.image_uri if order.image_uri else 'Not set'}")
            print(f"Comment in Picture: {order.comment_in_picture}")
            print(f"Commented: {order.commented}")
            print(f"Revealed: {order.revealed}")
            print(f"Reimbursed: {order.reimbursed}")
            print(f"Reimbursed Amount: ${order.reimbursed_amount:.2f}")
            print("==================\n")
            
            # Clear form after successful submission
            self.clear_form()
    
    def clear_form(self):
        """Clear all form fields"""
        self.text_area.delete("1.0", tk.END)
        self.image_label.configure(image="", text="Drag and drop image here")
        self.current_image = None
        self.current_image_path = None

    def __del__(self):
        """Ensure database connection is closed on destruction"""
        self.db.close() 