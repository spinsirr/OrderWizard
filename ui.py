import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from order import Order
from PIL import Image, ImageTk
from tkinterdnd2 import DND_FILES, TkinterDnD
import os

class OrderWizardUI:
    def __init__(self, root):
        if not isinstance(root, TkinterDnD.Tk):
            raise TypeError("Root window must be an instance of TkinterDnD.Tk")
        
        self.root = root
        self.root.title("Order Wizard")
        self.root.geometry("1200x800")
        
        # Store the current image reference
        self.current_image = None
        self.current_image_path = None
        
        # Create main container with padding
        self.main_container = ttk.Frame(self.root, padding="20")
        self.main_container.pack(fill=BOTH, expand=YES)
        
        # Create title
        title = ttk.Label(
            self.main_container,
            text="Order Wizard",
            font=("Helvetica", 24, "bold"),
            bootstyle="primary"
        )
        title.pack(pady=(0, 20))
        
        # Create horizontal container for image and text sections
        self.content_container = ttk.Frame(self.main_container)
        self.content_container.pack(fill=BOTH, expand=YES)
        
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
        
        # Create a frame for buttons
        self.button_frame = ttk.Frame(self.main_container)
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
        file_path = event.data
        # Remove curly braces if present (Windows)
        file_path = file_path.strip('{}')
        
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            self.load_image(file_path)
        else:
            print("Please drop a valid image file")

    def load_image(self, file_path):
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
            self.current_image_path = file_path
            
        except Exception as e:
            print(f"Error loading image: {e}")
    
    def submit_order(self):
        order_text = self.text_area.get("1.0", tk.END).strip()
        if order_text:
            order = Order.create_from_text(order_text)
            if self.current_image_path:
                order.image_uri = self.current_image_path
                
            print("\n=== Order Details ===")
            print(f"Order Number: {order.order_number}")
            print(f"Amount: ${order.amount:.2f}")
            print(f"Image URI: {order.image_uri if hasattr(order, 'image_uri') else 'Not set'}")
            print(f"Comment in Picture: {order.comment_in_picture if hasattr(order, 'comment_in_picture') else False}")
            print(f"Commented: {order.commented}")
            print(f"Revealed: {order.revealed}")
            print(f"Reimbursed: {order.reimbursed}")
            print(f"Reimbursed Amount: ${order.reimbursed_amount:.2f}")
            print("==================\n")
    
    def clear_form(self):
        self.text_area.delete("1.0", tk.END)
        self.image_label.configure(image="", text="Drag and drop image here")
        self.current_image = None
        self.current_image_path = None

def main():
    root = TkinterDnD.Tk()
    root.style = ttk.Style(theme="cosmo")
    app = OrderWizardUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 