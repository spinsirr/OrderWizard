# OrderWizard

OrderWizard is a desktop application for managing and tracking orders, built with Python and ttkbootstrap, offering a modern user interface and rich functionality.

## Core Features

### 1. Order Management
- Add New Orders: Quickly create orders from text
- Edit Orders: Modify order information
- Delete Orders: Remove unwanted orders
- Order Status Tracking:
  - Comment Status
  - Review Status
  - Reimbursement Status

### 2. Image Processing
- Drag-and-drop image upload
- Automatic order image association
- Support for comments with images

### 3. Search Functionality
- Order Number Search: Supports partial matching
- Amount Search: Matches within ±$2 range
- Real-time search result highlighting
- Search results marked with orange background

### 4. User Interface
- Modern interface design
- Completed orders highlighted in green
- Quick order number copy (click to copy)
- Double-click for quick order editing
- Right-click menu for edit and delete operations

## Usage Guide

### Adding Orders
1. Click "Add Order" button
2. Enter order information
3. Optional: Drag and drop image to designated area
4. If adding a comment, check "Comment with Picture"
5. Click save

### Searching Orders
1. Enter keywords in the search box
2. Select search type from dropdown menu:
   - Order Number: Search by order number
   - Amount: Search by amount (within ±$2 range)

### Editing Orders
- Method 1: Double-click order row
- Method 2: Right-click order and select "Edit"

### Copying Order Numbers
- Click on the order number column to copy to clipboard

## Technical Features
- Developed in Python
- Modern UI framework with ttkbootstrap
- SQLite database storage
- File drag-and-drop support
- Logging system

## System Requirements
- macOS / Windows / Linux
- Python 3.x
- Required Python packages (see requirements.txt)

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

## Project Structure

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

## Dependencies

- ttkbootstrap >= 1.10.1
- Pillow >= 10.0.0
- tkinterdnd2 >= 0.3.0

## Development

The project follows a clean architecture pattern with clear separation of concerns between the database layer, models, and UI components.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository.
