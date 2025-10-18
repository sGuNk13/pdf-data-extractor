import streamlit as st
import sqlite3
import json
from datetime import datetime
import PyPDF2
import io
from groq import Groq

# Page config
st.set_page_config(page_title="PDF Data Extractor", page_icon="📄", layout="wide")

# Initialize database
def init_db():
    conn = sqlite3.connect('pdf_extractor.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS projects
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  project_name TEXT NOT NULL,
                  responsible_person TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS budget_items
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  project_id INTEGER,
                  activity_name TEXT,
                  description TEXT,
                  amount REAL,
                  FOREIGN KEY (project_id) REFERENCES projects (id))''')
    conn.commit()
    return conn

# Extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Extract data using Groq LLM
def extract_with_groq(pdf_text, api_key):
    client = Groq(api_key=api_key)
    
    prompt = f"""Extract the following information from this Thai academic PDF text and return ONLY a valid JSON object with no additional text:

PDF Text:
{pdf_text[:4000]}

Extract:
1. project_name (from "1. ชื่อโครงการ")
2. responsible_person (from "2. ผู้รับผิดชอบ")
3. budget_items (from "14. รายละเอียดงบประมาณ") as an array of objects with: activity_name, description, amount

Return format (JSON only, no markdown, no explanation):
{{
  "project_name": "extracted name",
  "responsible_person": "extracted person",
  "budget_items": [
    {{"activity_name": "activity", "description": "desc", "amount": 1000}}
  ]
}}"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=2000
        )
        
        response_text = completion.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        
        data = json.loads(response_text.strip())
        return data, None
    except Exception as e:
        return None, str(e)

# Save to database
def save_to_db(conn, data):
    c = conn.cursor()
    c.execute("INSERT INTO projects (project_name, responsible_person) VALUES (?, ?)",
              (data['project_name'], data['responsible_person']))
    project_id = c.lastrowid
    
    for item in data['budget_items']:
        c.execute("INSERT INTO budget_items (project_id, activity_name, description, amount) VALUES (?, ?, ?, ?)",
                  (project_id, item['activity_name'], item['description'], item['amount']))
    
    conn.commit()
    return project_id

# Main app
def main():
    st.title("📄 PDF Data Extractor")
    st.markdown("Extract project information from Thai academic PDFs using AI")
    
    # Sidebar for API key
    with st.sidebar:
        st.header("⚙️ Settings")
        api_key = st.text_input("Groq API Key", type="password", help="Get free API key from https://console.groq.com")
        st.markdown("---")
        st.markdown("### 📊 Extracted Fields")
        st.markdown("- ชื่อโครงการ (Project Name)")
        st.markdown("- ผู้รับผิดชอบ (Responsible Person)")
        st.markdown("- รายละเอียดงบประมาณ (Budget)")
        
        if st.button("🗄️ View All Projects"):
            st.session_state.show_projects = True
    
    # Initialize database
    conn = init_db()
    
    # Show all projects
    if st.session_state.get('show_projects', False):
        st.header("📋 All Projects")
        projects = conn.execute("SELECT * FROM projects ORDER BY created_at DESC").fetchall()
        
        if projects:
            for proj in projects:
                with st.expander(f"🗂️ {proj[1]} (ID: {proj[0]})"):
                    st.write(f"**Responsible:** {proj[2]}")
                    st.write(f"**Created:** {proj[3]}")
                    
                    budget = conn.execute("SELECT * FROM budget_items WHERE project_id = ?", (proj[0],)).fetchall()
                    if budget:
                        st.write("**Budget Items:**")
                        total = 0
                        for item in budget:
                            st.write(f"- {item[2]}: {item[3]} - ฿{item[4]:,.2f}")
                            total += item[4]
                        st.write(f"**Total: ฿{total:,.2f}**")
        else:
            st.info("No projects yet. Upload a PDF to get started!")
        
        if st.button("⬅️ Back to Upload"):
            st.session_state.show_projects = False
            st.rerun()
        return
    
    # File upload
    st.header("1️⃣ Upload PDF")
    uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'])
    
    if uploaded_file is not None:
        if not api_key:
            st.warning("⚠️ Please enter your Groq API key in the sidebar")
            st.info("Get a free API key from: https://console.groq.com")
            return
        
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        # Extract text
        with st.spinner("📖 Reading PDF..."):
            pdf_text = extract_text_from_pdf(uploaded_file)
        
        st.success(f"✅ Extracted {len(pdf_text)} characters from PDF")
        
        # Extract with Groq
        if st.button("🤖 Extract Data with AI", type="primary"):
            with st.spinner("🧠 AI is analyzing your PDF..."):
                data, error = extract_with_groq(pdf_text, api_key)
            
            if error:
                st.error(f"❌ Error: {error}")
                return
            
            if data:
                st.session_state.extracted_data = data
                st.success("✅ Data extracted successfully!")
    
    # Show extracted data
    if 'extracted_data' in st.session_state:
        st.header("2️⃣ Review & Edit Extracted Data")
        data = st.session_state.extracted_data
        
        col1, col2 = st.columns(2)
        
        with col1:
            data['project_name'] = st.text_input("Project Name (ชื่อโครงการ)", value=data.get('project_name', ''))
        
        with col2:
            data['responsible_person'] = st.text_input("Responsible Person (ผู้รับผิดชอบ)", value=data.get('responsible_person', ''))
        
        st.subheader("Budget Items (รายละเอียดงบประมาณ)")
        
        budget_items = data.get('budget_items', [])
        
        if budget_items:
            for idx, item in enumerate(budget_items):
                with st.expander(f"Item {idx + 1}: {item.get('activity_name', 'Unnamed')}", expanded=True):
                    col1, col2, col3 = st.columns([2, 3, 1])
                    with col1:
                        item['activity_name'] = st.text_input(f"Activity {idx+1}", value=item.get('activity_name', ''), key=f"act_{idx}")
                    with col2:
                        item['description'] = st.text_input(f"Description {idx+1}", value=item.get('description', ''), key=f"desc_{idx}")
                    with col3:
                        item['amount'] = st.number_input(f"Amount {idx+1}", value=float(item.get('amount', 0)), key=f"amt_{idx}")
            
            total = sum(item.get('amount', 0) for item in budget_items)
            st.metric("Total Budget", f"฿{total:,.2f}")
        else:
            st.warning("No budget items found")
        
        # Save button
        st.header("3️⃣ Save to Database")
        if st.button("💾 Save to Database", type="primary"):
            if not data.get('project_name'):
                st.error("❌ Project name is required")
            elif not data.get('responsible_person'):
                st.error("❌ Responsible person is required")
            elif not budget_items:
                st.error("❌ At least one budget item is required")
            else:
                try:
                    project_id = save_to_db(conn, data)
                    st.success(f"✅ Saved successfully! Project ID: {project_id}")
                    del st.session_state.extracted_data
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Error saving: {e}")

if __name__ == "__main__":
    main()
