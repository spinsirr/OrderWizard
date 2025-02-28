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
    def create_from_text(text: str):
        """
        Create an order from text
        Expected format: Order number followed by amount
        Example: "123-456-789 $12.34" or "123-456-789 12.34"
        """
        order = Order(
            order_number=None,
            amount=0.0
        )
        try:
            # Split text into lines and get the first non-empty line
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            if not lines:
                raise ValueError("No valid text found")
                
            # Get the first line
            first_line = lines[0]
            
            # Try to find order number and amount
            parts = first_line.split()
            if len(parts) < 2:
                raise ValueError("Text must contain both order number and amount")
            
            # Get order number (first part)
            order.order_number = parts[0]
            
            # Get amount (last part)
            amount_str = parts[-1].strip('$')  # Remove $ if present
            # Remove any commas in the number
            amount_str = amount_str.replace(',', '')
            # Convert to float
            try:
                order.amount = float(amount_str)
            except ValueError:
                raise ValueError("Invalid amount format")
            
            # If there are additional lines, use them as note
            if len(lines) > 1:
                order.note = '\n'.join(lines[1:])
            
            return order
        except Exception as e:
            raise ValueError(f"Error creating order: {str(e)}")

    def to_tuple(self):
        """Convert order to tuple for database storage"""
        return (
            self.order_number,
            self.amount,
            self.image_uri,
            self.comment_with_picture,
            self.commented,
            self.revealed,
            self.reimbursed,
            self.note
        )