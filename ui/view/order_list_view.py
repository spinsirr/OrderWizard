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
from typing import Callable, List

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

def detect_dark_mode():
    """检测系统是否处于暗色模式"""
    try:
        if platform.system() == "Darwin":  # macOS
            import subprocess
            result = subprocess.run(
                ['defaults', 'read', '-g', 'AppleInterfaceStyle'],
                capture_output=True, text=True
            )
            return result.stdout.strip() == "Dark"
        elif platform.system() == "Windows":  # Windows
            import winreg
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return value == 0
        else:  # Linux 和其他系统，默认为光模式
            return False
    except Exception as e:
        logging.error(f"Error detecting dark mode: {e}")
        return False

class OrderListView(ttk.Frame):
    def __init__(self, parent, viewmodel: OrderListViewModel, on_add_click: Callable):
        super().__init__(parent, padding=20)
        self.parent = parent
        self.viewmodel = viewmodel
        self.on_add_click = on_add_click
        self.edit_window = None
        self.original_orders = []  # Store original orders for search filtering
        
        # 检测当前系统主题
        self.is_dark_mode = detect_dark_mode()
        self.colors = self._get_theme_colors()
        
        # 监听系统主题变化
        if platform.system() == "Darwin":  # macOS
            parent.bind("<<ThemeChanged>>", self._update_theme)
        
        self._init_ui()
        self.viewmodel.set_data_changed_callback(self.update_ui)
        self.viewmodel.load_orders()
        
        # Initialize search field as empty to show all orders
        self.search_var.set("")
        
    def _get_theme_colors(self):
        """获取基于当前主题的颜色方案"""
        if self.is_dark_mode:
            return {
                'selection_bg': '#2A4D69',  # 深蓝色
                'selection_fg': 'white',
                'completed_bg': '#2E7D32',  # 深绿色
                'completed_fg': 'white',
                'match_bg': '#8B5A2B',  # 深棕色
                'match_fg': 'white',
                'text_color': 'white'
            }
        else:
            return {
                'selection_bg': '#4A6984',  # 浅蓝色
                'selection_fg': 'white',
                'completed_bg': '#90EE90',  # 浅绿色
                'completed_fg': 'black',
                'match_bg': '#FFE5B4',  # 浅橙色
                'match_fg': 'black',
                'text_color': 'black'
            }
    
    def _update_theme(self, event=None):
        """更新主题颜色"""
        # 重新检测当前主题
        self.is_dark_mode = detect_dark_mode()
        self.colors = self._get_theme_colors()
        
        # 更新样式
        style = ttk.Style()
        
        # 配置选中项颜色
        style.map('Treeview', 
                 foreground=[('selected', self.colors['selection_fg'])],
                 background=[('selected', self.colors['selection_bg'])])
        
        # 配置标签颜色
        self.tree.tag_configure('completed', 
                               background=self.colors['completed_bg'], 
                               foreground=self.colors['completed_fg'])
        
        self.tree.tag_configure('match', 
                               background=self.colors['match_bg'], 
                               foreground=self.colors['match_fg'])
        
        # 重绘UI
        self.update_ui()

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
        
        # Create custom style before creating Treeview
        style = ttk.Style()
        
        # Configure selection colors 
        style.map('Treeview', 
                 foreground=[('selected', self.colors['selection_fg'])],
                 background=[('selected', self.colors['selection_bg'])])
        
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
            height=15,  # Show 15 rows at a time
            selectmode="extended"  # Allow multiple selection
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
        
        # Configure tags for special styling
        self.tree.tag_configure('completed', 
                               background=self.colors['completed_bg'], 
                               foreground=self.colors['completed_fg'])
        
        self.tree.tag_configure('match', 
                               background=self.colors['match_bg'], 
                               foreground=self.colors['match_fg'])
        
        # Override text color for tagged items even when not focused
        style.map('completed.Treeview.Item', foreground=[('!focus', self.colors['completed_fg'])])
        style.map('match.Treeview.Item', foreground=[('!focus', self.colors['match_fg'])])
        
        # Add event handler for window focus changes to reapply tag styling
        self.parent.bind("<FocusIn>", self._on_focus_change)
        self.parent.bind("<FocusOut>", self._on_focus_change)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create right-click menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Edit", command=self._edit_selected_order)
        self.context_menu.add_command(label="Delete", command=self._delete_single_order)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete Selected", command=self._delete_selected_orders)
        
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
            # Check if the clicked item is already selected
            currently_selected = self.tree.selection()
            
            # If clicked on an item that's not in the current selection, 
            # make it the only selected item
            if item not in currently_selected:
                self.tree.selection_set(item)
            # Otherwise, keep the current selection (including multiple items)
            
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
            order_number = self.tree.item(item)["values"][1]  # Index 1 for Order Number
            # Copy to clipboard
            self.clipboard_clear()
            self.clipboard_append(order_number)
            
            # Show notification
            self._show_message("Order number copied to clipboard", "Notification", "info")

    def _delete_single_order(self):
        """Delete a single selected order (via right-click)"""
        selected_items = self.tree.selection()
        if not selected_items:
            return
            
        # If multiple items are selected but user chose "Delete" (not "Delete Selected"),
        # only delete the most recently clicked item
        if len(selected_items) > 1:
            # Ask for confirmation if they want to delete just one or all selected items
            confirm = messagebox.askyesnocancel(
                title="Multiple Items Selected",
                message="Multiple items are selected. Do you want to delete all selected items?\n\n"
                        "Yes - Delete all selected items\n"
                        "No - Delete only the right-clicked item\n"
                        "Cancel - Do nothing"
            )
            
            if confirm is None:  # Cancel was clicked
                return
            elif confirm:  # Yes was clicked - delete all selected
                self._delete_selected_orders()
                return
            # If No was clicked, continue with deleting just the one item
            
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
            logging.error(f"Error in _delete_single_order: {e}", exc_info=True)
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def _delete_selected_orders(self):
        """Delete all selected orders"""
        # Get all selected orders
        selected_items = self.tree.selection()
        
        # Check if any orders are selected
        if not selected_items:
            self._show_message("No orders selected for deletion", "Notice", "info")
            return
            
        # Get order objects for selected items
        selected_orders = []
        for item_id in selected_items:
            order_id = int(item_id)  # Convert item_id to order_id
            order = self.viewmodel.get_order_by_id(order_id)
            if order:
                selected_orders.append(order)
        
        # Confirm deletion
        confirm = messagebox.askyesno(
            title="Confirm Delete",
            message=f"Are you sure you want to delete {len(selected_orders)} selected orders?"
        )
        
        if not confirm:
            return
            
        # Delete orders
        success_count = 0
        failed_orders = []
        
        for order in selected_orders:
            if self.viewmodel.delete_order(order.id):
                success_count += 1
            else:
                failed_orders.append(order.order_number)
                
        # Show results
        if failed_orders:
            self._show_message(
                f"Deleted {success_count} orders. Failed to delete {len(failed_orders)} orders.",
                "Partial Success",
                "warning"
            )
        else:
            self._show_message(
                f"Successfully deleted {success_count} orders",
                "Success",
                "info"
            )

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
        search_text = self.search_var.get().strip().lower()
        search_type = self.search_type.get()
        
        if not search_text:
            # If search is empty, show all orders
            self._display_orders(self.original_orders)
            return
        
        # Filter orders based on search text
        filtered_orders = []
        for order in self.original_orders:
            if search_type == "Order Number" and search_text in str(order.order_number).lower():
                filtered_orders.append(order)
            elif search_type == "Amount":
                try:
                    search_amount = float(search_text)
                    if abs(search_amount - order.amount) <= 2:  # Allow small differences
                        filtered_orders.append(order)
                except ValueError:
                    pass
        
        # Display filtered orders
        self._display_orders(filtered_orders, True)  # True for highlight matches

    def _display_orders(self, orders=None, highlight_search=False):
        """Display orders in the treeview"""
        # Clear the treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Use provided orders or current orders
        if orders is None:
            orders = self.viewmodel.orders
            
        # Update original_orders for search filtering if not already set
        if not self.original_orders:
            self.original_orders = self.viewmodel.orders
            
        # Calculate total amount
        total_amount = sum(order.amount for order in orders)
            
        # Update total amount label
        self.total_amount_label.configure(text=f"Total Amount: ${total_amount:.2f}")
            
        # Add orders to treeview
        for index, order in enumerate(orders, 1):  # Start enumeration from 1
            # Determine if order should be highlighted
            tags = ()
            if order.commented and order.revealed and order.reimbursed:
                tags = ('completed',)  # Use 'completed' tag for styling
                
            # Add 'match' tag if search is active and should highlight
            if highlight_search:
                tags = tags + ('match',)
                
            # Format values for display
            comment_status = "Yes" if order.comment_with_picture else "No"
            commented_status = "Yes" if order.commented else "No"
            revealed_status = "Yes" if order.revealed else "No"
            reimbursed_status = "Yes" if order.reimbursed else "No"
            
            # Add row
            self.tree.insert(
                "",
                tk.END,
                iid=str(order.id),  # Use order.id as the tree item identifier
                values=(
                    index,  # Sequential ID starting from 1
                    order.order_number,
                    f"${order.amount:.2f}",
                    order.note or "",
                    comment_status,
                    commented_status,
                    revealed_status,
                    reimbursed_status
                ),
                tags=tags
            )

    def update_ui(self):
        """Update the UI with current data"""
        # Update original_orders with latest data from viewmodel
        self.original_orders = self.viewmodel.orders
        
        # Get current search text
        search_text = self.search_var.get().strip().lower()
        
        # If search is empty, show all orders
        if not search_text:
            self._display_orders(self.viewmodel.orders)
        else:
            # Re-apply search filter
            self._on_search_change()

    def refresh(self):
        """Refresh the order list"""
        self.viewmodel.load_orders()

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

    def _on_focus_change(self, event):
        """Handle window focus changes to maintain tag styling"""
        # Reapply tag styling for all items with tags
        for item_id in self.tree.get_children():
            tags = self.tree.item(item_id, 'tags')
            if 'completed' in tags or 'match' in tags:
                # Force re-render by setting the same tags again
                self.tree.item(item_id, tags=tags) 