import re
import tempfile
import os
from typing import Dict, List
from docling.document_converter import DocumentConverter

def extract_pdf_data(pdf_content: bytes, filename: str) -> Dict:
    """Extract project data from PDF using Docling"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(pdf_content)
        tmp_path = tmp_file.name
    
    try:
        converter = DocumentConverter()
        result = converter.convert(tmp_path)
        markdown_text = result.document.export_to_markdown()
        
        project_name = extract_project_name(markdown_text)
        responsible_person = extract_responsible_person(markdown_text)
        budget_items = extract_budget_items(markdown_text)
        
        return {
            "project_name": project_name,
            "responsible_person": responsible_person,
            "budget_items": budget_items
        }
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def extract_project_name(text: str) -> str:
    """Extract ชื่อโครงการ"""
    patterns = [
        r'1\.\s*ชื่อโครงการ\s+(.+?)(?:\n|$)',
        r'ชื่อโครงการ[:\s]+(.+?)(?:\n|$)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return ""

def extract_responsible_person(text: str) -> str:
    """Extract ผู้รับผิดชอบ"""
    patterns = [
        r'2\.\s*ผู้รับผิดชอบ\s+(.+?)(?:\n|หลักสูตร)',
        r'ผู้รับผิดชอบ[:\s]+(.+?)(?:\n|หลักสูตร)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            name = match.group(1).strip()
            name = re.sub(r'\s*หลักสูตร.*', '', name)
            return name
    return ""

def extract_budget_items(text: str) -> List[Dict]:
    """Extract รายละเอียดงบประมาณ"""
    budget_items = []
    budget_section_match = re.search(
        r'14\.\s*รายละเอียดงบประมาณ\s*\n(.*?)(?:รวมทั้งหมด|15\.|$)',
        text,
        re.DOTALL | re.IGNORECASE
    )
    
    if not budget_section_match:
        return budget_items
    
    budget_text = budget_section_match.group(1)
    item_pattern = r'(\d+)\.\s*(.+?)\((.+?)\)\s+([\d,]+)'
    activity_matches = list(re.finditer(r'(\d+)\.\s*([A-Za-z\s]+(?:and|ERP)[^\n]*)', budget_text))
    
    if activity_matches:
        for activity_match in activity_matches:
            activity_name = activity_match.group(2).strip()
            activity_start = activity_match.end()
            next_activity = budget_text.find(f"{int(activity_match.group(1)) + 1}.", activity_start)
            activity_section = budget_text[activity_start:] if next_activity == -1 else budget_text[activity_start:next_activity]
            
            for item_match in re.finditer(item_pattern, activity_section):
                description = item_match.group(2).strip()
                calculation = item_match.group(3).strip()
                amount = float(item_match.group(4).replace(',', ''))
                budget_items.append({
                    "activity_name": activity_name,
                    "description": f"{description} ({calculation})",
                    "amount": amount
                })
    
    if not budget_items:
        for item_match in re.finditer(item_pattern, budget_text):
            description = item_match.group(2).strip()
            calculation = item_match.group(3).strip()
            amount = float(item_match.group(4).replace(',', ''))
            budget_items.append({
                "activity_name": "General",
                "description": f"{description} ({calculation})",
                "amount": amount
            })
    
    return budget_items

def validate_data(data: Dict) -> List[str]:
    """Validate extracted data"""
    errors = []
    if not data.get('project_name') or not data['project_name'].strip():
        errors.append("Project name is empty or not found")
    if not data.get('responsible_person') or not data['responsible_person'].strip():
        errors.append("Responsible person is empty or not found")
    budget_items = data.get('budget_items', [])
    if not budget_items:
        errors.append("No budget items found")
    else:
        for idx, item in enumerate(budget_items):
            if not item.get('activity_name'):
                errors.append(f"Budget item {idx + 1}: Activity name is missing")
            if item.get('amount', 0) <= 0:
                errors.append(f"Budget item {idx + 1}: Amount must be greater than 0")
    return errors
