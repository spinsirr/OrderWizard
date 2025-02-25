from order import Order

def main():
    sample_text = """Order placed
February 24, 2025
Total
$16.15
Ship to
Amazon Locker - Cicero 
Order # 113-2089298-0236240
View order details  View invoice
Arriving tomorrow
Track package

2 Pack 30 OZ Flip Straw Lid for Stanley Quencher, Leak Proof Lid Replacement for 30 OZ Stanley H2.0 FlowState Tumbler, Reusable Spill Proof Lid for Tumbler Cup (White, 30 OZ)
Buy it again
View or edit order
Archive order"""
    
    order = Order.create_from_text(sample_text)
    print(f"Order Number: {order.order_number}")
    print(f"Amount: ${order.amount:.2f}")
    print(order)

if __name__ == "__main__":
    main() 