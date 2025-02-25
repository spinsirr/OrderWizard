import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ui.viewmodel.order_list_viewmodel import OrderListViewModel
from typing import Callable

class OrderListView(ttk.Frame):
    def __init__(self, parent, on_add_click: Callable):
        super().__init__(parent, padding="20")
        self.viewmodel = OrderListViewModel()
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
        columns = ("ID", "Order Number", "Amount", "Status", "Created At")
        self.tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            bootstyle="primary"
        )
        
        # Configure columns
        self.tree.heading("ID", text="ID")
        self.tree.heading("Order Number", text="Order Number")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Created At", text="Created At")
        
        self.tree.column("ID", width=50)
        self.tree.column("Order Number", width=200)
        self.tree.column("Amount", width=100)
        self.tree.column("Status", width=100)
        self.tree.column("Created At", width=150)
        
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
            status = "Reimbursed" if order[7] else "Pending"  # Index 7 is reimbursed status
            self.tree.insert("", END, values=(
                order[0],  # ID
                order[1],  # Order Number
                f"${order[2]:.2f}",  # Amount
                status,
                order[9]  # Created At
            ))

    def refresh(self):
        """Refresh the order list"""
        self.viewmodel.refresh() 