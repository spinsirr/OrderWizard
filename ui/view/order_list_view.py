import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.toast import ToastNotification
from ui.viewmodel.order_list_viewmodel import OrderListViewModel
from ui.view.edit_order_view import EditOrderView
from typing import Callable
import platform

class OrderListView(ttk.Frame):
    def __init__(self, parent, viewmodel: OrderListViewModel, on_add_click: Callable):
        super().__init__(parent, padding="20")
        self.parent = parent  # Store parent for toast notifications
        self.viewmodel = viewmodel
        self.on_add_click = on_add_click
        self.edit_window = None
        
        self._init_ui()
        self.viewmodel.set_data_changed_callback(self.update_ui)
        self.viewmodel.load_orders()
        
    def _init_ui(self):
        """Initialize the UI components"""
        # Configure grid
        self.pack(fill=BOTH, expand=YES)
        
        # Header frame
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=X, pady=(0, 20))
        
        # Title
        title = ttk.Label(
            header_frame,
            text="Order List",
            font=("Helvetica", 24, "bold"),
            bootstyle="primary"
        )
        title.pack(side=LEFT)
        
        # Add Order button
        add_button = ttk.Button(
            header_frame,
            text="Add Order",
            command=self.on_add_click,
            bootstyle="success"
        )
        add_button.pack(side=RIGHT)
        
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
            bootstyle="primary",
            height=15  # Show 15 rows at a time
        )
        
        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col, anchor=W)  # W means West (left) alignment
            self.tree.column(col, anchor=W)  # Align the content to the left
        
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
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        self.tree.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)
        
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

    def _show_toast(self, message: str, bootstyle: str = "success"):
        """Show a toast notification"""
        toast = ToastNotification(
            message=message,
            duration=1000,  # 1 second
            bootstyle=bootstyle,
            position=(80, 50, "se")  # Bottom right corner
        )
        toast.show_toast()

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
            
            # Show toast notification
            self._show_toast("✓ Order number copied to clipboard", "success")

    def _delete_selected_order(self):
        """Delete the selected order"""
        selected_items = self.tree.selection()
        if not selected_items:
            return
            
        # Get the order data
        values = self.tree.item(selected_items[0])["values"]
        order_id = values[0]
        order_number = values[1]
        
        # Calculate center position for dialog
        window_x = self.winfo_rootx() + (self.winfo_width() // 2)
        window_y = self.winfo_rooty() + (self.winfo_height() // 2)
        
        # Create custom confirmation dialog
        dialog = Messagebox.show_question(
            message=f"Are you sure you want to delete order #{order_number}?",
            title="Confirm Delete",
            buttons=['No:secondary', 'Yes:danger'],  # Format: text:bootstyle
            alert=True,
            parent=self,  # This ensures the dialog is modal to the main window
            position=(window_x, window_y)  # Center the dialog
        )
        
        if dialog == "Yes":
            # Delete the order
            if self.viewmodel.delete_order(order_id):
                self._show_toast(f"✓ Order #{order_number} successfully deleted", "success")
            else:
                Messagebox.show_error(
                    message=f"Failed to delete order #{order_number}",
                    title="Error",
                    alert=True,
                    parent=self,
                    position=(window_x, window_y)
                )

    def _edit_selected_order(self):
        """Edit the selected order"""
        selected_items = self.tree.selection()
        if not selected_items:
            return
            
        # Get the order ID
        order_id = self.tree.item(selected_items[0])["values"][0]
        
        # Create edit window if not exists
        if not self.edit_window or not tk.Toplevel.winfo_exists(self.edit_window):
            self.edit_window = tk.Toplevel(self)
            self.edit_window.title("Edit Order")
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
            EditOrderView(
                self.edit_window,
                self.viewmodel,
                order_id,
                self._on_edit_window_close
            )
            
            # Make window modal
            self.edit_window.grab_set()
            
            # Show the window in its final position
            self.edit_window.deiconify()

    def _on_edit_window_close(self):
        """Handle edit window closing"""
        if self.edit_window:
            self.edit_window.grab_release()
            self.edit_window.destroy()
            self.edit_window = None

    def update_ui(self):
        """Update the UI with current data"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Add orders to tree
        for order in self.viewmodel.orders:
            note_display = order[9] if order[9] else ""  # Display empty string if note is None
            
            # Check if all status flags are True
            is_completed = all([
                order[5],  # Commented
                order[6],  # Revealed
                order[7]   # Reimbursed
            ])
            
            # Insert with appropriate tag if completed
            item = self.tree.insert("", END, values=(
                order[0],  # ID
                order[1],  # Order Number
                f"${order[2]:.2f}",  # Amount
                note_display,  # Note
                "Yes" if order[4] else "No",  # Comment with Picture
                "Yes" if order[5] else "No",  # Commented
                "Yes" if order[6] else "No",  # Revealed
                "Yes" if order[7] else "No"   # Reimbursed
            ), tags=('completed',) if is_completed else ())

    def refresh(self):
        """Refresh the order list"""
        self.viewmodel.refresh() 