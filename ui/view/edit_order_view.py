import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
from ui.viewmodel.order_list_viewmodel import OrderListViewModel
from model.order import Order

class EditOrderView(ttk.Frame):
    def __init__(self, parent, viewmodel: OrderListViewModel, order_id: int, on_close: callable):
        super().__init__(parent, padding="20")
        self.parent = parent
        self.viewmodel = viewmodel
        self.order_id = order_id
        self.on_close = on_close
        self.current_image_display = None
        
        # Get order data
        self.order_data = self.viewmodel.get_order_by_id(order_id)
        if not self.order_data:
            raise ValueError(f"Order {order_id} not found")
            
        self._init_ui()
        self.pack(fill=BOTH, expand=YES)
        
    def _init_ui(self):
        """Initialize all UI components"""
        # Create title
        title = ttk.Label(
            self,
            text=f"Edit Order #{self.order_data[1]}",  # order number
            font=("Helvetica", 24, "bold"),
            bootstyle="primary"
        )
        title.pack(pady=(0, 20))
        
        # Create main container
        main_container = ttk.Frame(self)
        main_container.pack(fill=BOTH, expand=YES)
        
        # Left side - Order details and status
        details_frame = self._init_details_frame(main_container)
        details_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 10))
        
        # Right side - Image display (if exists)
        if self.order_data[3]:  # image_uri
            image_frame = self._init_image_frame(main_container)
            image_frame.pack(side=LEFT, fill=BOTH, expand=YES)
        
        # Bottom - Buttons
        self._init_buttons()
        
    def _init_details_frame(self, parent):
        """Initialize order details and status section"""
        frame = ttk.LabelFrame(parent, text="Order Details", padding="10")
        
        # Order info
        info_text = f"Order Number: {self.order_data[1]}\nAmount: ${self.order_data[2]:.2f}"
        info_label = ttk.Label(
            frame,
            text=info_text,
            font=("Helvetica", 11),
            justify=LEFT
        )
        info_label.pack(anchor=W, pady=(0, 20))
        
        # Status checkboxes
        self.status_vars = {
            'comment_with_picture': tk.BooleanVar(value=self.order_data[4]),
            'commented': tk.BooleanVar(value=self.order_data[5]),
            'revealed': tk.BooleanVar(value=self.order_data[6]),
            'reimbursed': tk.BooleanVar(value=self.order_data[7])
        }
        
        # Create checkboxes with labels
        status_labels = {
            'comment_with_picture': "Comment with Picture",
            'commented': "Commented",
            'revealed': "Revealed",
            'reimbursed': "Reimbursed"
        }
        
        for key, label in status_labels.items():
            checkbox = ttk.Checkbutton(
                frame,
                text=label,
                variable=self.status_vars[key],
                bootstyle="primary-round-toggle"
            )
            checkbox.pack(anchor=W, pady=5)
            
        # Note section
        note_label = ttk.Label(
            frame,
            text="Note:",
            font=("Helvetica", 11)
        )
        note_label.pack(anchor=W, pady=(20, 5))
        
        self.note_area = tk.Text(
            frame,
            wrap=tk.WORD,
            font=("Helvetica", 11),
            height=5,
            width=40
        )
        self.note_area.pack(fill=X, expand=NO)
        
        # Set initial note text
        if self.order_data[9]:  # note
            self.note_area.insert("1.0", self.order_data[9])
        
        return frame
        
    def _init_image_frame(self, parent):
        """Initialize image display section"""
        frame = ttk.LabelFrame(parent, text="Order Image", padding="10")
        
        try:
            # Load and display image
            image = Image.open(self.order_data[3])
            # Calculate resize dimensions while maintaining aspect ratio
            display_width = 400
            display_height = 400
            
            # Calculate aspect ratio
            aspect_ratio = image.width / image.height
            
            if aspect_ratio > 1:
                new_width = display_width
                new_height = int(display_width / aspect_ratio)
            else:
                new_height = display_height
                new_width = int(display_height * aspect_ratio)
            
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            # Create and pack image label
            image_label = ttk.Label(frame, image=photo)
            image_label.image = photo  # Keep a reference
            image_label.pack(fill=BOTH, expand=YES)
            
        except Exception as e:
            error_label = ttk.Label(
                frame,
                text="Error loading image",
                bootstyle="danger"
            )
            error_label.pack(fill=BOTH, expand=YES)
            print(f"Error loading image: {e}")
            
        return frame
        
    def _init_buttons(self):
        """Initialize button section"""
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=X, pady=(20, 0))
        
        # Save button
        save_button = ttk.Button(
            button_frame,
            text="Save Changes",
            command=self._save_changes,
            bootstyle="success"
        )
        save_button.pack(side=RIGHT, padx=(10, 0))
        
        # Cancel button
        cancel_button = ttk.Button(
            button_frame,
            text="Cancel",
            command=self._handle_cancel,
            bootstyle="secondary"
        )
        cancel_button.pack(side=RIGHT)
        
    def _save_changes(self):
        """Save changes to the order"""
        try:
            # Create updated order object
            updated_order = Order(
                order_number=self.order_data[1],
                amount=self.order_data[2],
                image_uri=self.order_data[3],
                comment_with_picture=self.status_vars['comment_with_picture'].get(),
                commented=self.status_vars['commented'].get(),
                revealed=self.status_vars['revealed'].get(),
                reimbursed=self.status_vars['reimbursed'].get(),
                reimbursed_amount=self.order_data[8],
                note=self.note_area.get("1.0", tk.END).strip()
            )
            
            # Update through viewmodel
            if self.viewmodel.update_order(self.order_id, updated_order):
                self.viewmodel.refresh()  # Refresh the list view
                self._handle_cancel()  # Close the edit window
            else:
                ttk.Messagebox.show_error(
                    message="Failed to update order",
                    title="Error",
                    parent=self
                )
                
        except Exception as e:
            ttk.Messagebox.show_error(
                message=f"Error updating order: {e}",
                title="Error",
                parent=self
            )
            
    def _handle_cancel(self):
        """Handle cancel button click"""
        self.destroy()
        if self.on_close:
            self.on_close() 