import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ui.viewmodel.order_list_viewmodel import OrderListViewModel
from typing import Callable

class OrderListView(ttk.Frame):
    def __init__(self, parent, viewmodel: OrderListViewModel, on_add_click: Callable):
        super().__init__(parent, padding="20")
        self.viewmodel = viewmodel
        self.on_add_click = on_add_click
        
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
            "Comment with Picture",
            "Commented",
            "Revealed",
            "Reimbursed"
        )
        self.tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            bootstyle="primary"
        )
        
        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col, anchor=W)  # W means West (left) alignment
            self.tree.column(col, anchor=W)  # Align the content to the left
        
        # Set column widths
        self.tree.column("ID", width=50)
        self.tree.column("Order Number", width=150)
        self.tree.column("Amount", width=100)
        self.tree.column("Comment with Picture", width=130)
        self.tree.column("Commented", width=100)
        self.tree.column("Revealed", width=100)
        self.tree.column("Reimbursed", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        self.tree.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)

    def update_ui(self):
        """Update the UI with current data"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Add orders to tree
        for order in self.viewmodel.orders:
            self.tree.insert("", END, values=(
                order[0],  # ID
                order[1],  # Order Number
                f"${order[2]:.2f}",  # Amount
                "Yes" if order[4] else "No",  # Comment with Picture
                "Yes" if order[5] else "No",  # Commented
                "Yes" if order[6] else "No",  # Revealed
                "Yes" if order[7] else "No"   # Reimbursed
            ))

    def refresh(self):
        """Refresh the order list"""
        self.viewmodel.refresh() 