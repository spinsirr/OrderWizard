from db.database import Database
from typing import List, Tuple, Optional, Callable

class OrderListViewModel:
    def __init__(self):
        self.db = Database()
        self._orders: List[Tuple] = []
        self._on_data_changed: Optional[Callable] = None

    def load_orders(self):
        """Load orders from database"""
        try:
            self._orders = self.db.get_all_orders()
            if self._on_data_changed:
                self._on_data_changed()
        except Exception as e:
            print(f"Error loading orders: {e}")

    @property
    def orders(self) -> List[Tuple]:
        """Get current orders"""
        return self._orders

    def set_data_changed_callback(self, callback: Callable):
        """Set callback for data changes"""
        self._on_data_changed = callback

    def refresh(self):
        """Refresh order data"""
        self.load_orders()

    def __del__(self):
        """Cleanup database connection"""
        self.db.close() 