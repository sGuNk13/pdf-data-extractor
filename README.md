# PDF Data Extractor

Automated data extraction tool for Thai academic project documents. Built with Python, FastAPI, Docling, and React.

## Features

- 📄 Extract data from Thai PDF documents (text + scanned)
- 🤖 Powered by Docling for advanced PDF understanding
- ✏️ Edit extracted data before saving
- 💾 Store in SQLite/MySQL database
- ✅ Data validation
- 🎨 Modern React UI with Tailwind CSS

## Extracted Fields

- **ชื่อโครงการ** (Project Name)
- **ผู้รับผิดชอบ** (Responsible Person)
- **รายละเอียดงบประมาณ** (Budget Breakdown)

## Tech Stack

**Backend:**
- Python 3.10+
- FastAPI
- Docling
- SQLAlchemy
- Pydantic

**Frontend:**
- React
- Vite
- Tailwind CSS
- Lucide Icons

**Database:**
- SQLite (development)
- MySQL (production ready)

## Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs on: `http://localhost:8000`

API docs: `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend runs on: `http://localhost:5173`

## Usage

1. Open `http://localhost:5173` in your browser
2. Click "Choose PDF file" and select a Thai academic PDF
3. Click "Extract Data"
4. Review and edit the extracted information
5. Click "Save to Database"

## Database Configuration

### SQLite (Default)
No configuration needed. Database file created automatically.

### MySQL (Production)

1. Create database:
```sql
CREATE DATABASE pdf_extractor;
CREATE USER 'pdf_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON pdf_extractor.* TO 'pdf_user'@'localhost';
```

2. Update `backend/database.py`:
```python
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://pdf_user:your_password@localhost:3306/pdf_extractor"
```

## API Endpoints

- `POST /extract` - Upload and extract PDF data
- `POST /save` - Save extracted data to database
- `GET /projects` - Get all projects
- `GET /projects/{id}` - Get specific project

## Project Structure

```
pdf-data-extractor/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Database models
│   ├── schemas.py           # Pydantic schemas
│   ├── database.py          # Database configuration
│   ├── extractor.py         # PDF extraction logic
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Main React component
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── .gitignore
└── README.md
```

## Screenshots

*(Add screenshots here after deployment)*

## Roadmap

- [ ] Batch PDF processing
- [ ] Export to Excel/CSV
- [ ] User authentication
- [ ] Dashboard with statistics
- [ ] Docker containerization
- [ ] Cloud deployment guide

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Acknowledgments

- [Docling](https://github.com/docling-project/docling) - PDF processing
- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
- [React](https://react.dev/) - Frontend framework

## Contact
Project Link: [https://github.com/sGuNk13/pdf-data-extractor](https://github.com/yourusername/pdf-data-extractor)
