# OrderWizard

OrderWizard is a desktop application for managing and tracking Amazon orders, featuring OCR capabilities, status tracking, and a modern user interface.

![OrderWizard Icon](static/amazon-icon-1024x1024-l9mz6jgt.png)

## Installation

### macOS

#### Option 1: DMG Installation (Recommended)
1. Download the latest `OrderWizard.dmg` from [Releases](https://github.com/yourusername/OrderWizard/releases)
2. Double-click the DMG file to open it
3. Drag OrderWizard.app to your Applications folder
4. Launch OrderWizard from Applications

#### Option 2: From Source
1. Clone the repository:
```bash
git clone https://github.com/yourusername/OrderWizard.git
cd OrderWizard
```

2. Create virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Tesseract OCR:
```bash
brew install tesseract
```

5. Run the application:
```bash
python main.py
```

### Windows/Linux Installation
Currently optimizing for Windows and Linux platforms. Stay tuned for updates.

## Core Features

### 1. Order Management
- **Add New Orders**: 
  - OCR from screenshots with automatic text extraction
  - Manual input option
  - Smart parsing of order numbers and amounts
- **Edit Orders**: Modify order details and track status
- **Delete Orders**: Remove orders with confirmation
- **Status Tracking**:
  - Comment Status
  - Review Status
  - Reimbursement Status
  - Visual status indicators

### 2. Smart OCR Processing
- Drag-and-drop image support
- Automatic text extraction
- Intelligent parsing of Amazon order format
- Support for common image formats (PNG, JPG, JPEG)
- Automatic image organization

### 3. Advanced Search
- **Order Number Search**: 
  - Real-time partial matching
  - Highlighted results
- **Amount Search**: 
  - Flexible range matching (±$2)
  - Decimal support
- Visual search feedback

### 4. Modern Interface
- Clean, intuitive design
- Status-based color coding
- Quick actions (copy, edit, delete)
- Context menus
- Toast notifications

## Usage Guide

### Managing Orders
1. **Adding Orders**
   - Click "Add Order" or drag a screenshot
   - Verify extracted information
   - Add optional notes
   - Set status flags as needed

2. **Searching**
   - Use the search box
   - Choose search type (Order Number/Amount)
   - Results update instantly

3. **Order Actions**
   - Click order number to copy
   - Double-click to edit
   - Right-click for more options

4. **Status Tracking**
   - Toggle status flags in edit view
   - Visual status indicators in list
   - Track comments, reviews, reimbursements

## Technical Details
- Built with Python 3.12
- Modern UI using ttkbootstrap
- SQLite database
- OCR via Tesseract
- Comprehensive logging

## Project Structure
```
OrderWizard/
├── main.py              # Entry point
├── db/                  # Database management
├── model/              # Data models
├── ui/                 # User interface
│   ├── view/          # Views
│   └── viewmodel/     # View models
├── static/            # Static resources
├── images/            # Order images
└── requirements.txt   # Dependencies
```

## Dependencies
- Python 3.12+
- ttkbootstrap >= 1.10.1
- Pillow >= 10.0.0
- tkinterdnd2 >= 0.3.0
- pytesseract >= 0.3.10

## Contributing
1. Fork the repository
2. Create feature branch (`git checkout -b feature/NewFeature`)
3. Commit changes (`git commit -m 'Add NewFeature'`)
4. Push to branch (`git push origin feature/NewFeature`)
5. Open a Pull Request

## License
This project is licensed under the MIT License.

## Support
For support:
- Open an issue in the GitHub repository
- Check existing issues for solutions
- Include logs and screenshots when reporting issues
