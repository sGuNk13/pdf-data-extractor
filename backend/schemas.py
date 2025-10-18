from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import datetime

class BudgetItemBase(BaseModel):
    activity_name: str
    description: Optional[str] = ""
    amount: float

class BudgetItemCreate(BudgetItemBase):
    pass

class BudgetItem(BudgetItemBase):
    id: int
    project_id: int
    
    class Config:
        from_attributes = True

class ProjectBase(BaseModel):
    project_name: str
    responsible_person: str

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    budget_items: List[BudgetItem] = []
    
    class Config:
        from_attributes = True

class ExtractedData(BaseModel):
    project_name: str
    responsible_person: str
    budget_items: List[BudgetItemBase]
    
    @validator('project_name', 'responsible_person')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip()
    
    @validator('budget_items')
    def validate_budget_items(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one budget item is required')
        return v

class ExtractedDataResponse(ExtractedData):
    validation_errors: List[str] = []
