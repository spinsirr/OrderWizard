from dataclasses import dataclass
import re
from datetime import datetime
from typing import Optional

@dataclass
class Order:
    order_number: str
    amount: float
    image_uri: Optional[str] = None
    comment_with_picture: bool = False
    commented: bool = False
    revealed: bool = False
    reimbursed: bool = False
    reimbursed_amount: float = 0.0
    note: Optional[str] = None

    @staticmethod
    def parse_order_text(order_text: str) -> 'Order':
        """
        Parse Amazon order text and extract order number and amount.
        
        Args:
            order_text: Raw text from Amazon order
            
        Returns:
            Order instance with extracted information
        """
        # Extract order number
        order_number_match = re.search(r'Order #\s*([0-9-]+)', order_text)
        order_number = order_number_match.group(1) if order_number_match else ""

        # Extract amount
        amount_match = re.search(r'\$(\d+\.\d+)', order_text)
        amount = float(amount_match.group(1)) if amount_match else 0.0

        return Order(
            order_number=order_number,
            amount=amount
        )

    @staticmethod
    def create_from_text(text: str) -> 'Order':
        """Create an order from text input"""
        order = Order(
            order_number=None,
            amount=0.0
        )
        
        # Split text into lines and process each line
        lines = text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('Order #'):
                order.order_number = line.replace('Order #', '').strip()
            elif '$' in line:
                # Extract amount
                amount_str = line.split('$')[1].strip().replace(',', '')
                try:
                    order.amount = float(amount_str)
                except ValueError:
                    raise ValueError("Invalid amount format")
        
        if not order.order_number:
            raise ValueError("Order number not found in text")
        if order.amount <= 0:
            raise ValueError("Invalid or missing amount")
            
        return order