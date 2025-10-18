from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models, schemas, database, extractor
from database import engine, get_db
from typing import List

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="PDF Extractor API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "PDF Extractor API is running"}

@app.post("/extract", response_model=schemas.ExtractedDataResponse)
async def extract_pdf(file: UploadFile = File(...)):
    """
    Extract data from uploaded PDF
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        # Read file content
        content = await file.read()
        
        # Extract data using Docling
        extracted_data = extractor.extract_pdf_data(content, file.filename)
        
        # Validate data
        validation_errors = extractor.validate_data(extracted_data)
        
        return {
            **extracted_data,
            "validation_errors": validation_errors
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@app.post("/save")
def save_to_database(data: schemas.ExtractedData, db: Session = next(get_db())):
    """
    Save extracted data to database
    """
    try:
        # Validate before saving
        validation_errors = extractor.validate_data(data.dict())
        if validation_errors:
            raise HTTPException(status_code=400, detail={"errors": validation_errors})
        
        # Create project
        db_project = models.Project(
            project_name=data.project_name,
            responsible_person=data.responsible_person
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        
        # Create budget items
        for item in data.budget_items:
            db_budget = models.BudgetItem(
                project_id=db_project.id,
                activity_name=item.activity_name,
                description=item.description,
                amount=item.amount
            )
            db.add(db_budget)
        
        db.commit()
        
        return {
            "message": "Data saved successfully",
            "project_id": db_project.id
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving to database: {str(e)}")

@app.get("/projects", response_model=List[schemas.ProjectResponse])
def get_all_projects(db: Session = next(get_db())):
    """
    Get all projects with their budget items
    """
    projects = db.query(models.Project).all()
    return projects

@app.get("/projects/{project_id}", response_model=schemas.ProjectResponse)
def get_project(project_id: int, db: Session = next(get_db())):
    """
    Get specific project by ID
    """
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
