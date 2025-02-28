# OrderWizard

OrderWizard is a desktop application for managing and tracking orders, built with Python and ttkbootstrap, offering a modern user interface and rich functionality.

## Core Features

### 1. Order Management
- **Add New Orders**: 
  - Manual input or OCR from screenshots
  - Automatic text extraction from order images
  - Smart parsing of order numbers and amounts
- **Edit Orders**: Modify order information with ease
- **Delete Orders**: Remove unwanted orders
- **Order Status Tracking**:
  - Comment Status
  - Review Status
  - Reimbursement Status

### 2. Image Processing & OCR
- Drag-and-drop image upload
- Automatic OCR text extraction
- Smart parsing of Amazon order format:
  - Order number (format: xxx-xxxxxxx-xxxxxxx)
  - Amount (format: $xx.xx, $xxx.xx, or $xxxx.xx)
- Support for PNG, JPG, JPEG, GIF, BMP formats
- Automatic image association with orders

### 3. Search Functionality
- **Order Number Search**: 
  - Supports partial matching
  - Real-time search results
- **Amount Search**: 
  - Matches within ±$2 range
  - Supports decimal amounts
- Search results highlighted in orange
- Instant visual feedback

### 4. User Interface
- Modern and clean design
- Completed orders highlighted in green
- Quick order number copy (click to copy)
- Double-click for quick order editing
- Right-click context menu
- Toast notifications for user feedback

## Usage Guide

### Adding Orders
1. Click "Add Order" button
2. Choose input method:
   - Manual text entry
   - Drag and drop order screenshot
3. For image upload:
   - System automatically extracts order number and amount
   - Verify extracted information
   - Add optional notes
4. For manual entry:
   - Enter order number (xxx-xxxxxxx-xxxxxxx)
   - Enter amount ($xx.xx format)
5. Optional: Check "Comment with Picture" if needed
6. Click "Submit"

### Searching Orders
1. Enter search term in search box
2. Select search type:
   - Order Number: Partial matches supported
   - Amount: Matches within ±$2 range
3. Results update in real-time
4. Matching items highlighted in orange

### Managing Orders
- **Copy Order Number**: Click on order number
- **Edit Order**: 
  - Double-click order row, or
  - Right-click and select "Edit"
- **Delete Order**: Right-click and select "Delete"
- **View Status**: Check status columns in list view

## Technical Features
- Built with Python
- Modern UI using ttkbootstrap
- SQLite database for data storage
- OCR capabilities with pytesseract
- Drag-and-drop support via tkinterdnd2
- Comprehensive logging system

## System Requirements
- macOS / Windows / Linux
- Python 3.x
- Tesseract OCR engine
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/OrderWizard.git
cd OrderWizard
```

2. Create virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Tesseract OCR:
- macOS: `brew install tesseract`
- Windows: Download installer from GitHub
- Linux: `sudo apt-get install tesseract-ocr`

## Running the Application

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
- pytesseract >= 0.3.10

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository.
