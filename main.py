import os
import sys
import logging
import traceback
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from pathlib import Path
import threading
import argparse

# Default to development mode when not frozen
IS_FROZEN = getattr(sys, 'frozen', False)

# Parse command line arguments
parser = argparse.ArgumentParser(description='OrderWizard Application')
parser.add_argument('--prod', action='store_true', help='Run in production mode with real database')
parser.add_argument('--seed', action='store_true', help='Seed the test database with sample data (only in dev mode)')
args = parser.parse_args()

# Set mode environment variables based on arguments
if args.prod:
    os.environ['ORDERWIZARD_PROD_MODE'] = '1'
    print("Running in PRODUCTION mode with real database")
elif not IS_FROZEN:
    print("Running in DEVELOPMENT mode with test database")
    # Check if seed flag is set
    if args.seed:
        print("Seeding test database with sample data...")
        from db.seed_test_data import seed_test_database
        seed_test_database()

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    logging.warning("tkinterdnd2 not available, drag and drop will be disabled")
    DND_FILES = None
    TkinterDnD = tk.Tk

from ui.view.add_order_view import AddOrderView
from ui.view.order_list_view import OrderListView
from ui.viewmodel.order_list_viewmodel import OrderListViewModel

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
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)
    except Exception as e:
        logging.error(f"Error getting resource path: {e}")
        return relative_path

# Configure logging
if getattr(sys, 'frozen', False):
    # we are running in a bundle
    # Use user's home directory for logs when bundled
    log_dir = os.path.expanduser('~/Library/Logs/OrderWizard')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'orderwizard.log')
else:
    # we are running in a normal Python environment
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'orderwizard.log')

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

class MainApplication:
    def __init__(self, root):
        try:
            logging.info("Initializing MainApplication")
            self.root = root
            self.root.title("Order Wizard")
            self.root.geometry("1200x800")
            
            # Log resource paths
            logging.info(f"DB Path: {resource_path('db/orders.db')}")
            logging.info(f"Images Path: {resource_path('images')}")
            
            # Add a loading label
            self.loading_label = ttk.Label(
                self.root,
                text="Loading...",
                font=("Helvetica", 18)
            )
            self.loading_label.pack(expand=True)
            
            # Initialize ViewModel in a separate thread
            self.order_list_viewmodel = None
            self.current_screen = None
            threading.Thread(target=self._initialize_viewmodel, daemon=True).start()
            
        except Exception as e:
            logging.error(f"Error in MainApplication initialization: {e}")
            logging.error(traceback.format_exc())
            messagebox.showerror("Initialization Error", f"Error initializing application: {e}")
            raise
    
    def _initialize_viewmodel(self):
        """Initialize the ViewModel in a background thread"""
        try:
            # Initialize shared ViewModel
            logging.info("Initializing OrderListViewModel")
            self.order_list_viewmodel = OrderListViewModel()
            
            # Schedule UI update on the main thread
            self.root.after(100, self._finish_initialization)
        except Exception as e:
            logging.error(f"Error initializing ViewModel: {e}")
            self.root.after(0, lambda: messagebox.showerror("Initialization Error", f"Error initializing application: {e}"))
    
    def _finish_initialization(self):
        """Complete initialization on the main thread"""
        if self.order_list_viewmodel:
            # Remove loading label
            self.loading_label.pack_forget()
            
            # Show the initial screen
            logging.info("Showing initial order list screen")
            self.show_order_list()
            
            # Load orders in background after UI is shown
            threading.Thread(target=self._load_orders_background, daemon=True).start()
        else:
            # Check again in 100ms
            self.root.after(100, self._finish_initialization)
    
    def _load_orders_background(self):
        """Load orders in the background and update UI when done"""
        try:
            self.order_list_viewmodel.load_orders()
        except Exception as e:
            logging.error(f"Error loading orders: {e}")
        
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
            messagebox.showerror("View Error", f"Error showing order list: {e}")
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
                command=self.show_order_list
            )
            back_button.pack(side="left")
        except Exception as e:
            logging.error(f"Error showing add order screen: {e}")
            logging.error(traceback.format_exc())
            messagebox.showerror("View Error", f"Error showing add order screen: {e}")
            raise

def main():
    try:
        logging.info("Starting application")
        logging.info("Creating root window")
        root = TkinterDnD.Tk()  # Use TkinterDnD instead of tk.Tk
        root.withdraw()  # Hide the window initially
        
        # Set app icon (faster loading)
        if sys.platform == 'darwin':
            # Skip setting icon on macOS to speed up startup
            pass
        
        # Show a basic splash screen first
        splash = tk.Toplevel(root)
        splash.title("Loading OrderWizard")
        splash.geometry("400x200")
        splash.overrideredirect(True)  # Remove window decorations
        
        # Center splash screen
        screen_width = splash.winfo_screenwidth()
        screen_height = splash.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 200) // 2
        splash.geometry(f"400x200+{x}+{y}")
        
        splash_label = ttk.Label(
            splash,
            text="OrderWizard",
            font=("Helvetica", 24, "bold")
        )
        splash_label.pack(pady=(50, 20))
        
        splash_sublabel = ttk.Label(
            splash,
            text="Starting...",
            font=("Helvetica", 12)
        )
        splash_sublabel.pack()
        
        # Force update to show splash
        splash.update()
        
        # Check database connection
        try:
            logging.info("Initializing application")
            app = MainApplication(root)
            
            # Close splash and show main window
            splash.destroy()
            root.deiconify()  # Show the window after initialization
            
            logging.info("Entering main event loop")
            root.mainloop()
        except Exception as e:
            splash.destroy()  # Ensure splash is closed on error
            logging.error(f"Application initialization error: {e}")
            logging.error(traceback.format_exc())
            messagebox.showerror("Initialization Error", f"Failed to initialize application: {e}")
            sys.exit(1)
    except Exception as e:
        logging.error(f"Application startup error: {e}")
        logging.error(traceback.format_exc())
        try:
            messagebox.showerror("Startup Error", f"Application failed to start: {e}")
        except:
            pass
        sys.exit(1)

# Improve startup speed by avoiding slow module imports until needed
if __name__ == "__main__":
    main() 