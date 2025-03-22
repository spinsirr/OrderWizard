import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import sys
import logging
from ui.viewmodel.order_list_viewmodel import OrderListViewModel
from model.order import Order

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

class EditOrderView(ttk.Frame):
    def __init__(self, parent, viewmodel: OrderListViewModel, order_id: int, on_close: callable):
        super().__init__(parent, padding=20)
        self.parent = parent
        self.viewmodel = viewmodel
        self.order_id = order_id
        self.on_close = on_close
        self.current_image_display = None
        
        logging.info(f"Initializing EditOrderView for order ID: {order_id}")
        
        # Get order data
        self.order = self.viewmodel.get_order_by_id(order_id)
        if not self.order:
            error_msg = f"Order {order_id} not found"
            logging.error(error_msg)
            # Add a small delay and then close the window
            self.after(100, self.on_close)
            raise ValueError(error_msg)
        
        logging.info(f"Successfully retrieved order data: {self.order.id}, {self.order.order_number}")
        
        try:
            self._init_ui()
            self.pack(fill=tk.BOTH, expand=True)
        except Exception as e:
            logging.error(f"Error initializing EditOrderView UI: {e}", exc_info=True)
            self.after(100, self.on_close)
            raise
        
    def _init_ui(self):
        """Initialize all UI components"""
        # Create title
        title = ttk.Label(
            self,
            text=f"Edit Order #{self.order.order_number}",  # order number
            font=("Helvetica", 24, "bold")
        )
        title.pack(pady=(0, 20))
        
        # Status label for feedback
        self.status_label = ttk.Label(
            self,
            text="",
            foreground="blue",
            wraplength=300  # Allow text to wrap
        )
        self.status_label.pack(fill=tk.X, pady=(0, 10))
        
        # Create main container
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left side - Order details and status
        details_frame = self._init_details_frame(main_container)
        details_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Right side - Image display and LLM chatbox
        right_frame = ttk.Frame(main_container)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        if self.order.image_uri:  # image_uri
            # If image exists, show image frame
            image_frame = self._init_image_frame(right_frame)
            image_frame.pack(fill=tk.BOTH, expand=True)
        else:
            # If no image, just show the LLM chatbox
            chat_frame = ttk.LabelFrame(right_frame, text="AI Assistant", padding=10)
            chat_frame.pack(fill=tk.BOTH, expand=True)
            self._init_llm_chatbox_content(chat_frame)
        
        # Bottom - Buttons
        self._init_buttons()
        
    def _init_details_frame(self, parent):
        """Initialize the order details frame"""
        frame = ttk.LabelFrame(parent, text="Order Details", padding=10)
        
        # Order info
        info_text = f"Order Number: {self.order.order_number}\nAmount: ${self.order.amount:.2f}"
        info_label = ttk.Label(
            frame,
            text=info_text,
            font=("Helvetica", 12)
        )
        info_label.pack(fill=tk.X, pady=(0, 10))
        
        # Status checkboxes
        self.status_vars = {
            'comment_with_picture': tk.BooleanVar(value=self.order.comment_with_picture),
            'commented': tk.BooleanVar(value=self.order.commented),
            'revealed': tk.BooleanVar(value=self.order.revealed),
            'reimbursed': tk.BooleanVar(value=self.order.reimbursed)
        }
        
        # Create checkboxes
        for status, var in self.status_vars.items():
            # Convert status name to display text
            display_text = ' '.join(word.capitalize() for word in status.split('_'))
            cb = ttk.Checkbutton(
                frame,
                text=display_text,
                variable=var,
                command=lambda s=status: self._on_status_change(s)
            )
            cb.pack(fill=tk.X, pady=2)
        
        # Note area
        note_label = ttk.Label(frame, text="Notes:")
        note_label.pack(fill=tk.X, pady=(10, 2))
        
        self.note_area = tk.Text(frame, height=5, wrap=tk.WORD)
        self.note_area.pack(fill=tk.BOTH, expand=True)
        
        # Set initial note text
        if self.order.note:  # note
            self.note_area.insert("1.0", self.order.note)
        
        return frame
        
    def _init_image_frame(self, parent):
        """Initialize the image display frame"""
        frame = ttk.LabelFrame(parent, text="Image", padding=10)
        
        try:
            # Load and display image
            image_path = self.order.image_uri
            logging.info(f"Loading image: {image_path}")
            
            if os.path.exists(image_path):
                # Open and resize image
                image = Image.open(image_path)
                
                # Calculate new size while maintaining aspect ratio
                display_width = 400  # Desired width
                ratio = display_width / image.width
                display_height = int(image.height * ratio)
                
                image = image.resize((display_width, display_height), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                
                # Create and pack image label
                self.current_image_display = ttk.Label(frame, image=photo)
                self.current_image_display.image = photo  # Keep a reference
                self.current_image_display.pack(pady=10)
                
                # Add chat frame below image
                chat_frame = ttk.LabelFrame(frame, text="AI Assistant", padding=10)
                chat_frame.pack(fill=tk.BOTH, expand=True)
                self._init_llm_chatbox_content(chat_frame)
            else:
                logging.error(f"Image file not found: {image_path}")
                error_label = ttk.Label(
                    frame,
                    text="Image file not found",
                    foreground="red"
                )
                error_label.pack(pady=10)
        except Exception as e:
            logging.error(f"Error loading image: {e}")
            error_label = ttk.Label(
                frame,
                text=f"Error loading image: {str(e)}",
                foreground="red"
            )
            error_label.pack(pady=10)
        
        return frame
        
    def _init_llm_chatbox(self, parent):
        """Initialize LLM chatbox UI"""
        # Create a frame for the chatbox
        chat_frame = ttk.LabelFrame(parent, text="AI Assistant", padding=10)
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self._init_llm_chatbox_content(chat_frame)
        
    def _init_llm_chatbox_content(self, chat_frame):
        """Initialize the content of the LLM chatbox"""
        # Chat history display area
        self.chat_history = tk.Text(
            chat_frame,
            wrap=tk.WORD,
            font=("Helvetica", 10),
            height=8,
            width=40,
            state=tk.DISABLED,  # Read-only initially
            background="#f0f0f0"
        )
        self.chat_history.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Add scrollbar to chat history
        chat_scrollbar = ttk.Scrollbar(self.chat_history, command=self.chat_history.yview)
        chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_history.configure(yscrollcommand=chat_scrollbar.set)
        
        # Input area frame
        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill=tk.X, expand=False)
        
        # Chat input field
        self.chat_input = ttk.Entry(
            input_frame,
            font=("Helvetica", 10),
            width=40
        )
        self.chat_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Bind Enter key to send message
        self.chat_input.bind("<Return>", self._on_send_message)
        
        # Send button
        send_button = ttk.Button(
            input_frame,
            text="Send",
            width=8,
            command=self._on_send_message
        )
        send_button.pack(side=tk.RIGHT)
        
        # Add placeholder text to chat history
        self._update_chat_history("AI Assistant: How can I help you with this order?")
        
    def _on_send_message(self, event=None):
        """Handle sending a message (placeholder for future implementation)"""
        message = self.chat_input.get().strip()
        if message:
            # Display user message
            self._update_chat_history(f"You: {message}")
            
            # Clear input field
            self.chat_input.delete(0, tk.END)
            
            # Placeholder for future LLM integration
            self._update_chat_history("AI Assistant: This feature will be implemented soon.")
            
        return "break"  # Prevent default behavior for Enter key
        
    def _update_chat_history(self, message):
        """Update chat history with new message"""
        self.chat_history.configure(state=tk.NORMAL)
        self.chat_history.insert(tk.END, message + "\n\n")
        self.chat_history.see(tk.END)  # Scroll to bottom
        self.chat_history.configure(state=tk.DISABLED)
        
    def _init_buttons(self):
        """Initialize button section"""
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Save button
        save_button = ttk.Button(
            button_frame,
            text="Save Changes",
            command=self._save_changes
        )
        save_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Cancel button
        cancel_button = ttk.Button(
            button_frame,
            text="Cancel",
            command=self._handle_cancel
        )
        cancel_button.pack(side=tk.RIGHT)
        
    def _show_status(self, message, is_error=False):
        """Show status message"""
        self.status_label.configure(
            text=message,
            foreground="red" if is_error else "blue"
        )
        # Clear status after 3 seconds
        self.after(3000, lambda: self.status_label.configure(text=""))

    def _save_changes(self):
        """Save changes to the order"""
        try:
            # Create updated order object
            updated_order = Order(
                order_number=self.order.order_number,
                amount=self.order.amount,
                image_uri=self.order.image_uri,
                comment_with_picture=self.status_vars['comment_with_picture'].get(),
                commented=self.status_vars['commented'].get(),
                revealed=self.status_vars['revealed'].get(),
                reimbursed=self.status_vars['reimbursed'].get(),
                reimbursed_amount=self.order.reimbursed_amount,
                note=self.note_area.get("1.0", tk.END).strip()
            )
            
            # Update in database
            if self.viewmodel.update_order(self.order_id, updated_order):
                self.status_label.config(
                    text="Changes saved successfully",
                    foreground="green"
                )
                # Close window after a short delay
                self.after(500, self._handle_cancel)
            else:
                self.status_label.config(
                    text="Failed to save changes",
                    foreground="red"
                )
        except Exception as e:
            logging.error(f"Error saving changes: {e}")
            self.status_label.config(
                text=f"Error: {str(e)}",
                foreground="red"
            )
            
    def _handle_cancel(self):
        """Handle cancel button click"""
        if self.on_close:
            self.on_close()

    def _on_status_change(self, status: str):
        """
        Handle status checkbox changes
        
        Args:
            status: The status that changed
        """
        try:
            # Get the new value
            new_value = self.status_vars[status].get()
            logging.info(f"Status change - {status}: {new_value}")
            
            # Create updated order with new status
            updated_order = Order(
                order_number=self.order.order_number,
                amount=self.order.amount,
                image_uri=self.order.image_uri,
                comment_with_picture=self.status_vars['comment_with_picture'].get(),
                commented=self.status_vars['commented'].get(),
                revealed=self.status_vars['revealed'].get(),
                reimbursed=self.status_vars['reimbursed'].get(),
                reimbursed_amount=self.order.reimbursed_amount,
                note=self.note_area.get("1.0", tk.END).strip()
            )
            
            # Update in database
            if self.viewmodel.update_order(self.order_id, updated_order):
                self.status_label.config(
                    text=f"{status.replace('_', ' ').title()} status updated",
                    foreground="green"
                )
                # Schedule status message to clear after 3 seconds
                self.after(3000, lambda: self.status_label.config(text=""))
            else:
                self.status_label.config(
                    text=f"Failed to update {status}",
                    foreground="red"
                )
                # Revert checkbox if update failed
                self.status_vars[status].set(not new_value)
        except Exception as e:
            logging.error(f"Error updating status: {e}")
            self.status_label.config(
                text=f"Error: {str(e)}",
                foreground="red"
            )
            # Revert checkbox on error
            self.status_vars[status].set(not new_value) 