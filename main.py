from tkinterdnd2 import TkinterDnD
import ttkbootstrap as ttk
from ui.view.add_order_view import AddOrderView
from ui.view.order_list_view import OrderListView
from ui.viewmodel.order_list_viewmodel import OrderListViewModel
import logging
import sys

class MainApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("Order Wizard")
        self.root.geometry("1200x800")
        self.root.style = ttk.Style(theme="cosmo")
        
        # Initialize shared ViewModel
        self.order_list_viewmodel = OrderListViewModel()
        
        self.current_screen = None
        self.show_order_list()
        
    def show_order_list(self):
        """Show the order list screen"""
        if self.current_screen:
            self.current_screen.destroy()
        self.current_screen = OrderListView(self.root, self.order_list_viewmodel, self.show_add_order)
        
    def show_add_order(self):
        """Show the add order screen"""
        if self.current_screen:
            self.current_screen.destroy()
        self.current_screen = AddOrderView(self.root, self.order_list_viewmodel)
        # Add back button
        back_button = ttk.Button(
            self.current_screen.button_frame,
            text="Back to List",
            command=self.show_order_list,
            bootstyle="secondary"
        )
        back_button.pack(side="left")

def initialize_app():
    """Initialize the application and its dependencies"""
    try:
        root = TkinterDnD.Tk()
        app = MainApplication(root)
        return root, app
    except Exception as e:
        logging.error(f"Failed to initialize application: {e}")
        sys.exit(1)

def main():
    root, app = initialize_app()
    try:
        root.mainloop()
    except Exception as e:
        logging.error(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 