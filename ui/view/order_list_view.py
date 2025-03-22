import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os
import sys
import logging
import platform
import datetime
from ui.viewmodel.order_list_viewmodel import OrderListViewModel
from ui.view.edit_order_view import EditOrderView
from ui.view.add_order_view import AddOrderView
from typing import Callable

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

class OrderListView(ttk.Frame):
    def __init__(self, parent, viewmodel: OrderListViewModel, on_add_click: Callable):
        super().__init__(parent, padding=20)
        self.parent = parent
        self.viewmodel = viewmodel
        self.on_add_click = on_add_click
        self.edit_window = None
        self.original_orders = []  # Store original orders for search filtering
        
        self._init_ui()
        self.viewmodel.set_data_changed_callback(self.update_ui)
        self.viewmodel.load_orders()
        
    def _init_ui(self):
        """Initialize the UI components"""
        # Configure grid
        self.pack(fill=tk.BOTH, expand=True)
        
        # Header frame
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Left section frame (for title and total amount)
        left_section = ttk.Frame(header_frame)
        left_section.pack(side=tk.LEFT)
        
        # Title
        title = ttk.Label(
            left_section,
            text="Order List",
            font=("Helvetica", 24, "bold")
        )
        title.pack(side=tk.TOP, anchor=tk.W)
        
        # Total amount label
        self.total_amount_label = ttk.Label(
            left_section,
            text="Total Amount: $0.00",
            font=("Helvetica", 12)
        )
        self.total_amount_label.pack(side=tk.TOP, anchor=tk.W, pady=(5, 0))
        
        # Search frame (new)
        search_frame = ttk.Frame(header_frame)
        search_frame.pack(side=tk.LEFT, padx=20)
        
        # Search entry
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self._on_search_change)
        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=30
        )
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Search type combobox
        self.search_type = ttk.Combobox(
            search_frame,
            values=["Order Number", "Amount"],
            width=15,
            state="readonly"
        )
        self.search_type.set("Order Number")
        self.search_type.pack(side=tk.LEFT, padx=5)
        self.search_type.bind("<<ComboboxSelected>>", lambda e: self._on_search_change())
        
        # Add Order button
        add_button = ttk.Button(
            header_frame,
            text="Add Order",
            command=self.on_add_click
        )
        add_button.pack(side=tk.RIGHT)
        
        # Create Treeview
        columns = (
            "ID", 
            "Order Number", 
            "Amount", 
            "Note",
            "Comment with Picture",
            "Commented",
            "Revealed",
            "Reimbursed"
        )
        self.tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            height=15  # Show 15 rows at a time
        )
        
        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col, anchor=tk.W)  # W means West (left) alignment
            self.tree.column(col, anchor=tk.W)  # Align the content to the left
        
        # Set column widths
        self.tree.column("ID", width=50)
        self.tree.column("Order Number", width=150)
        self.tree.column("Amount", width=100)
        self.tree.column("Note", width=200)  # Wider column for notes
        self.tree.column("Comment with Picture", width=130)
        self.tree.column("Commented", width=100)
        self.tree.column("Revealed", width=100)
        self.tree.column("Reimbursed", width=100)
        
        # Configure tag for completed orders
        self.tree.tag_configure('completed', background='#90EE90')  # Light green color
        self.tree.tag_configure('match', background='#FFE5B4')  # Light orange for search matches
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create right-click menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Edit", command=self._edit_selected_order)
        self.context_menu.add_command(label="Delete", command=self._delete_selected_order)
        
        # Bind events
        if platform.system() == "Darwin":  # macOS
            self.tree.bind("<Button-2>", self._show_context_menu)  # Right click
            self.tree.bind("<Control-Button-1>", self._show_context_menu)  # Control+click
        else:  # Windows/Linux
            self.tree.bind("<Button-3>", self._show_context_menu)  # Right click
            
        self.tree.bind("<Button-1>", self._handle_click)  # Left click
        self.tree.bind("<Double-Button-1>", self._handle_double_click)  # Double click

    def _show_context_menu(self, event):
        """Show the context menu on right click"""
        # Get the item under cursor
        item = self.tree.identify_row(event.y)
        
        if item:
            # Select the item
            self.tree.selection_set(item)
            # Show context menu
            self.context_menu.tk_popup(event.x_root, event.y_root)
        
        return "break"  # Prevent propagation

    def _show_message(self, message: str, title: str = "Notification", message_type: str = "info"):
        """Show a message dialog"""
        if message_type == "info":
            messagebox.showinfo(title, message)
        elif message_type == "warning":
            messagebox.showwarning(title, message)
        elif message_type == "error":
            messagebox.showerror(title, message)

    def _handle_click(self, event):
        """Handle left click events"""
        # Get the clicked item and column
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        
        if item and column == "#2":  # Order Number column
            # Get the order number value
            order_number = self.tree.item(item)["values"][1]
            # Copy to clipboard
            self.clipboard_clear()
            self.clipboard_append(order_number)
            
            # Show notification
            self._show_message("Order number copied to clipboard", "Notification", "info")

    def _delete_selected_order(self):
        """Delete the selected order"""
        selected_items = self.tree.selection()
        if not selected_items:
            return
            
        try:
            # Get the actual order_id from the tree item's iid
            order_id = int(selected_items[0])  # selected_items[0] is the iid we set earlier
            logging.info(f"Deleting order - Selected Tree IID: {selected_items[0]}, Parsed Database ID: {order_id}")
            
            # Get order data using order ID directly
            order = self.viewmodel.get_order_by_id(order_id)
            if not order:
                error_msg = f"Order ID {order_id} not found in database"
                logging.error(error_msg)
                messagebox.showerror("Error", error_msg)
                return
                
            logging.info(f"Retrieved order for deletion - Database ID: {order.id}, Order Number: {order.order_number}")
            
            # Create confirmation dialog
            confirm = messagebox.askyesno(
                title="Confirm Delete",
                message=f"Are you sure you want to delete order #{order.order_number}?"
            )
            
            if confirm:
                # Delete the order
                if self.viewmodel.delete_order(order_id):
                    logging.info(f"Successfully deleted order - Database ID: {order_id}, Order Number: {order.order_number}")
                    self._show_message(f"Order #{order.order_number} successfully deleted", "Success", "info")
                else:
                    logging.error(f"Failed to delete order - Database ID: {order_id}, Order Number: {order.order_number}")
                    self._show_message(f"Failed to delete order #{order.order_number}", "Error", "error")
        except Exception as e:
            logging.error(f"Error in _delete_selected_order: {e}", exc_info=True)
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def _edit_selected_order(self):
        """Edit the selected order"""
        selected_items = self.tree.selection()
        if not selected_items:
            return
        
        try:
            # Get the actual order_id from the tree item's iid
            order_id = int(selected_items[0])  # selected_items[0] is the iid we set earlier
            logging.info(f"Editing order - Selected Tree IID: {selected_items[0]}, Parsed Database ID: {order_id}")
            
            # Get order data using order ID directly
            order = self.viewmodel.get_order_by_id(order_id)
            if not order:
                error_msg = f"Order ID {order_id} not found in database"
                logging.error(error_msg)
                messagebox.showerror("Error", error_msg)
                return
                
            logging.info(f"Retrieved order for editing - Database ID: {order.id}, Order Number: {order.order_number}")
            
            # If we already have an edit window open, close it
            if hasattr(self, 'edit_window') and self.edit_window:
                self.edit_window.destroy()
            
            # Create a new window for editing
            self.edit_window = tk.Toplevel(self.parent)
            self.edit_window.title(f"Edit Order #{order.order_number}")  # Use order number for title
            self.edit_window.geometry("800x600")
            
            # Make it modal
            self.edit_window.transient(self.parent)
            
            # Withdraw the window until it's positioned
            self.edit_window.withdraw()
            
            # Calculate center position
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            x = (screen_width - 800) // 2
            y = (screen_height - 600) // 2
            self.edit_window.geometry(f"800x600+{x}+{y}")
            
            # Create edit view
            try:
                EditOrderView(
                    self.edit_window,
                    self.viewmodel,
                    order_id,  # Pass the actual order_id
                    self._on_edit_window_close
                )
                logging.info(f"Created EditOrderView for order - Database ID: {order_id}, Order Number: {order.order_number}")
                
                # Make window modal
                self.edit_window.grab_set()
                
                # Show the window in its final position
                self.edit_window.deiconify()
            except Exception as e:
                logging.error(f"Failed to create EditOrderView: {e}", exc_info=True)
                messagebox.showerror("Error", f"Failed to open edit window: {str(e)}")
                if self.edit_window:
                    self.edit_window.destroy()
                    self.edit_window = None
        except Exception as e:
            logging.error(f"Error in _edit_selected_order: {e}", exc_info=True)
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def _on_edit_window_close(self):
        """Handle edit window closing"""
        if self.edit_window:
            self.edit_window.grab_release()
            self.edit_window.destroy()
            self.edit_window = None

    def _on_search_change(self, *args):
        """Handle search input changes"""
        search_text = self.search_var.get().strip()
        search_type = self.search_type.get()
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not search_text:
            # If search is empty, show all orders
            self._display_orders()
            return
            
        filtered_orders = []
        for order in self.viewmodel.orders:
            if search_type == "Order Number":
                # Search in order number (partial match)
                if search_text.lower() in str(order.order_number).lower():
                    filtered_orders.append(order)
            else:  # Amount search
                try:
                    search_amount = float(search_text)
                    # Match if amount is within ±2
                    if abs(search_amount - order.amount) <= 2:
                        filtered_orders.append(order)
                except ValueError:
                    continue
        
        # Log search results
        logging.info(f"Search found {len(filtered_orders)} orders matching '{search_text}' in {search_type}")
        
        self._display_orders(filtered_orders, highlight_search=True)

    def _display_orders(self, orders=None, highlight_search=False):
        """Display orders in the treeview"""
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Get orders from ViewModel
            if orders is None:
                orders = self.viewmodel.orders
            logging.info(f"Displaying {len(orders)} orders in the list")
            
            search_text = self.search_var.get().strip().lower()
            search_type = self.search_type.get()
            
            # Display orders
            for index, order in enumerate(orders, 1):  # Start enumeration from 1
                logging.info(f"Processing order - Database ID: {order.id}, Display Index: {index}, Order Number: {order.order_number}")
                
                # Create tags for highlighting
                tags = []
                if search_text:
                    if search_type == "Order Number" and search_text in str(order.order_number).lower():
                        tags.append('match')
                    elif search_type == "Amount":
                        try:
                            search_amount = float(search_text)
                            if abs(search_amount - order.amount) <= 2:
                                tags.append('match')
                        except ValueError:
                            pass
                
                # Add 'completed' tag if all status flags are true
                if order.commented and order.revealed and order.reimbursed:
                    tags.append('completed')
                
                note_display = order.note if order.note else ""
                
                # Insert item with iid explicitly set to order_id as string
                self.tree.insert("", tk.END, 
                    iid=str(order.id),  # Use the actual order_id as the iid
                    values=(
                        index,     # Display ID (sequential from 1)
                        order.order_number, # Order Number
                        f"${order.amount:.2f}",  # Amount
                        note_display,  # Note
                        "Yes" if order.comment_with_picture else "No",  # Comment with Picture
                        "Yes" if order.commented else "No",  # Commented
                        "Yes" if order.revealed else "No",  # Revealed
                        "Yes" if order.reimbursed else "No"   # Reimbursed
                    ), 
                    tags=tuple(tags)
                )
                
                logging.info(f"Added tree item - Database ID: {order.id}, Display Index: {index}, Order Number: {order.order_number}")
            
            # Calculate total amount
            total_amount = sum(order.amount for order in orders)
            self.total_amount_label.configure(text=f"Total Amount: ${total_amount:.2f}")
            
        except Exception as e:
            logging.error(f"Error displaying orders: {e}", exc_info=True)
            messagebox.showerror("Error", f"Failed to load orders: {str(e)}")

    def update_ui(self):
        """Update the UI with current data"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Display orders with current search filter
        self._on_search_change()

    def refresh(self):
        """Refresh the order list"""
        self.viewmodel.refresh()

    def _handle_double_click(self, event):
        """Handle double click events"""
        try:
            item_id = self.tree.identify_row(event.y)
            if item_id:
                logging.info(f"Double-clicked on item: {item_id}")
                self._edit_selected_order()
                return "break"  # Prevent event propagation
        except Exception as e:
            logging.error(f"Error handling double click: {e}", exc_info=True)
            messagebox.showerror("Error", f"Error processing double click: {str(e)}") 