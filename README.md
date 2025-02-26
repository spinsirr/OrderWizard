# OrderWizard

OrderWizard is a desktop application for managing Amazon orders with a modern, user-friendly interface. Built with Python and Tkinter, it provides an efficient way to track, manage, and monitor the status of your Amazon orders.

## Features

- **Order Management**
  - Add new orders with order numbers and amounts
  - Track order status (commented, revealed, reimbursed)
  - Attach images to orders
  - Add notes to orders
  - Double-click orders to edit them

- **User Interface**
  - Modern and intuitive interface using ttkbootstrap
  - Drag-and-drop support for images
  - Quick copy order numbers with a single click
  - Sort and filter orders
  - Status indicators for order progress

- **Data Management**
  - SQLite database for reliable data storage
  - Automatic data validation
  - Image management system
  - Data persistence between sessions

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/OrderWizard.git
cd OrderWizard
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

To run the application:
```bash
python main.py
```

## Usage

1. **Adding Orders**
   - Click "Add Order" button
   - Paste order details from Amazon
   - Optionally drag and drop an image
   - Add any additional notes
   - Click "Submit Order"

2. **Managing Orders**
   - View all orders in the main list
   - Double-click an order to edit
   - Right-click for additional options
   - Click order numbers to copy them
   - Track status with checkboxes

3. **Order Status**
   - Comment with Picture: Order has an image attached
   - Commented: Order has been commented on
   - Revealed: Order details have been revealed
   - Reimbursed: Order has been reimbursed

## System Requirements

- Python 3.12 or higher
- Operating Systems:
  - macOS 10.13 or higher
  - Windows 10 or higher
  - Linux (major distributions)

## Dependencies

- ttkbootstrap >= 1.10.1
- Pillow >= 10.0.0
- tkinterdnd2 >= 0.3.0

## Development

The project structure follows a clean architecture pattern:

```
OrderWizard/
├── main.py              # Application entry point
├── db/                  # Database layer
├── model/              # Data models
├── ui/                 # User interface
│   ├── view/          # UI views
│   └── viewmodel/     # View models
├── images/            # Stored images
└── requirements.txt   # Project dependencies
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Support

For support, please open an issue in the GitHub repository.
