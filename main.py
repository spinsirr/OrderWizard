import os
import sys
import logging
import traceback
from pathlib import Path
from tkinterdnd2 import TkinterDnD
import ttkbootstrap as ttk
from ui.view.add_order_view import AddOrderView
from ui.view.order_list_view import OrderListView
from ui.viewmodel.order_list_viewmodel import OrderListViewModel

# Configure logging
if getattr(sys, 'frozen', False):
    # we are running in a bundle
    bundle_dir = sys._MEIPASS
    # Use user's home directory for logs when bundled
    log_dir = os.path.expanduser('~/Library/Logs/OrderWizard')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'orderwizard.log')
else:
    # we are running in a normal Python environment
    bundle_dir = os.path.dirname(os.path.abspath(__file__))
    log_file = os.path.join(bundle_dir, 'orderwizard.log')

logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Add console handler for development
if not getattr(sys, 'frozen', False):
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    logging.getLogger().addHandler(console_handler)

def setup_tkdnd():
    """Setup tkdnd library paths"""
    try:
        logging.info("Setting up tkdnd paths")
        if getattr(sys, 'frozen', False):
            # If we're running in a bundle
            tkdnd_path = os.path.join(bundle_dir, 'tkinterdnd2', 'tkdnd')
            os.environ['TKDND_LIBRARY'] = tkdnd_path
            logging.info(f"Set TKDND_LIBRARY to: {tkdnd_path}")
            
            # Also set TCL/TK library paths
            tcl_lib = os.path.join(bundle_dir, 'lib', 'tcl8.6')
            tk_lib = os.path.join(bundle_dir, 'lib', 'tk8.6')
            os.environ['TCL_LIBRARY'] = tcl_lib
            os.environ['TK_LIBRARY'] = tk_lib
            logging.info(f"Set TCL_LIBRARY to: {tcl_lib}")
            logging.info(f"Set TK_LIBRARY to: {tk_lib}")
        else:
            # Running in development
            import tkinterdnd2
            tkdnd_path = os.path.join(os.path.dirname(tkinterdnd2.__file__), 'tkdnd')
            os.environ['TKDND_LIBRARY'] = tkdnd_path
            logging.info(f"Set TKDND_LIBRARY to: {tkdnd_path}")
    except Exception as e:
        logging.error(f"Error setting up tkdnd: {e}")
        logging.error(traceback.format_exc())
        raise

class MainApplication:
    def __init__(self, root):
        try:
            logging.info("Initializing MainApplication")
            self.root = root
            self.root.title("Order Wizard")
            self.root.geometry("1200x800")
            
            logging.info("Setting up ttkbootstrap style")
            self.root.style = ttk.Style(theme="cosmo")
            
            # Initialize shared ViewModel
            logging.info("Initializing OrderListViewModel")
            self.order_list_viewmodel = OrderListViewModel()
            
            self.current_screen = None
            logging.info("Showing initial order list screen")
            self.show_order_list()
            
        except Exception as e:
            logging.error(f"Error in MainApplication initialization: {e}")
            logging.error(traceback.format_exc())
            raise
        
    def show_order_list(self):
        """Show the order list screen"""
        try:
            logging.info("Showing order list screen")
            if self.current_screen:
                self.current_screen.destroy()
            self.current_screen = OrderListView(self.root, self.order_list_viewmodel, self.show_add_order)
        except Exception as e:
            logging.error(f"Error showing order list: {e}")
            logging.error(traceback.format_exc())
            raise
        
    def show_add_order(self):
        """Show the add order screen"""
        try:
            logging.info("Showing add order screen")
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
        except Exception as e:
            logging.error(f"Error showing add order screen: {e}")
            logging.error(traceback.format_exc())
            raise

def initialize_app():
    """Initialize the application and its dependencies"""
    try:
        logging.info("Starting application initialization")
        
        # Setup tkdnd
        setup_tkdnd()
        
        # Initialize root window
        logging.info("Creating root window")
        root = TkinterDnD.Tk()
        
        # Create main application
        logging.info("Creating main application")
        app = MainApplication(root)
        
        logging.info("Application initialized successfully")
        return root, app
    except Exception as e:
        logging.error(f"Failed to initialize application: {e}")
        logging.error(traceback.format_exc())
        sys.exit(1)

def main():
    try:
        logging.info("Starting main application")
        root, app = initialize_app()
        logging.info("Entering main event loop")
        root.mainloop()
    except Exception as e:
        logging.error(f"Application error: {e}")
        logging.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Fatal error in main: {e}")
        logging.error(traceback.format_exc())
        sys.exit(1) 