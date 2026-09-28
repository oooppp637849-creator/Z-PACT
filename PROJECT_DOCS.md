# WebPDF Elite — Technical Documentation

## 1. Project Overview
**WebPDF Elite** is a secure platform for selling and protecting PDF documents. It uses dynamic stamping, digital watermarking, and steganography (hidden marks) to prevent leaks and track unauthorized distribution.

## 2. Technology Stack
- **Backend**: FastAPI (Python 3.10+)
- **Database**: SQLite (SQLAlchemy ORM)
- **Security**: JWT Authentication, Bcrypt password hashing
- **PDF Processing**: `pypdf`, `reportlab` (for stamping and encryption)
- **Frontend**: Vanilla HTML5, CSS3, JavaScript (ES6+)
- **Libraries**: PDF.js (Secure preview), Fabric.js (Stamp designer)

## 3. Directory Structure
```text
/webpdf_elite
├── /app                # Backend Core Logic
│   ├── /routers        # API Endpoints (Auth, Materials, Purchases, etc.)
│   ├── auth.py         # Security & JWT logic
│   ├── crud.py         # Database Operations (Create, Read, Update, Delete)
│   ├── database.py     # Database Connection & Session Management
│   ├── models.py       # SQLAlchemy Database Models
│   ├── schemas.py      # Pydantic Data Validation Schemas
│   └── stamper.py      # PDF Stamping & Security Engine
├── /frontend           # User Interface
│   ├── /css            # Global & Component Styles
│   ├── /js             # API Client & Frontend Logic
│   └── /pages          # HTML Pages (Admin, Store, Login)
├── /storage            # Uploaded and Processed Files
│   ├── /materials      # Original PDF files
│   └── /stamped        # Processed & Secured files for customers
├── main.py             # Application Entry Point
└── migrate.py          # Database Migration Script
```

## 4. Database Architecture (Models)
The system uses several interlinked tables to manage users, files, and security:

1.  **User**: Stores accounts (Admin vs. Customer) and their balances (Coins).
2.  **Material**: Stores original PDF files, titles, descriptions, and prices.
3.  **StampLayout**: Stores the design of how stamps (Name, Phone) are placed on the PDF.
4.  **Purchase**: Records every sale, payment status, and links the customer to the secured file.
5.  **HiddenMark**: Records invisible tracking codes (Steganography) embedded in each page.
6.  **PreviewToken**: Manages secure, time-limited browser previews without allowing downloads.
7.  **BackgroundJob**: Tracks long-running tasks like PDF processing.

## 5. Core Features & Security Logic

### A. Dynamic PDF Stamping
When a customer buys a file, the system automatically generates a unique version of the PDF. It "stamps" the buyer's Name and Phone Number on every page at coordinates specified by the Admin.

### B. PDF Encryption
Each customer's PDF is encrypted using their phone number as a password. This ensures that even if the file is shared, it cannot be opened without the owner's credentials.

### C. Steganography (Hidden Marks)
In addition to visible stamps, the system embeds "Invisible Marks" (white text, 1px size) containing unique tracking IDs. If a file is leaked online, the Admin can extract this code to find exactly which customer leaked the document.

### D. Secure Preview
Customers can preview the first few pages of a PDF before buying. The system sends a partial, secured binary stream to the browser using PDF.js, making it extremely difficult to download the original file during preview.

### E. Coins (Credits) System
A flexible balance system where Admins can assign "Coins" to users. Users can then purchase materials using these coins as a digital currency within the platform.

## 6. How to Run the Project

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the Server**:
   ```bash
   uvicorn main:app --reload
   ```
3. **Access the App**:
   - Store: `http://localhost:8000/frontend/pages/store.html`
   - Admin: `http://localhost:8000/frontend/pages/admin.html`
