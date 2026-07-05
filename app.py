from flask import Flask, render_template, request, redirect, url_for, flash
import fitz  # PyMuPDF
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "super_secret_key_for_flash_messages"
DB_PATH = "database.db"

# 1. Initialize SQLite Database Schema
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT UNIQUE,
            candidate_name TEXT,
            extracted_text TEXT,
            matched_skills TEXT
        )
    ''')
    conn.commit()
    conn.close()

# 2. Extract Text using PyMuPDF
def extract_text_from_pdf(stream):
    doc = fitz.open(stream=stream, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Simple dictionary-based keyword matching algorithm
def identify_skills(text):
    SKILL_KEYWORDS = ["python", "flask", "django", "html", "css", "javascript", 
                      "sqlite", "react", "sql", "java", "c++", "git", "docker"]
    found_skills = []
    text_lower = text.lower()
    for skill in SKILL_KEYWORDS:
        if skill in text_lower:
            found_skills.append(skill.capitalize())
    return ", ".join(found_skills) if found_skills else "None Identified"

@app.route("/", methods=["GET", "POST"])
def index():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if request.method == "POST":
        # Handle file uploads
        if 'resume_files' not in request.files:
            return redirect(request.url)
        
        files = request.files.getlist('resume_files')
        
        for file in files:
            if file.filename == '':
                continue
            
            if file and file.filename.endswith('.pdf'):
                try:
                    file_stream = file.read()
                    raw_text = extract_text_from_pdf(file_stream)
                    skills = identify_skills(raw_text)
                    
                    # Basic extraction for Candidate Name (uses first line of document)
                    first_line = raw_text.split('\n')[0].strip()
                    name = first_line if len(first_line) < 50 else "Unknown Profile"

                    # Save to SQLite Database
                    cursor.execute('''
                        INSERT OR IGNORE INTO resumes (filename, candidate_name, extracted_text, matched_skills)
                        VALUES (?, ?, ?, ?)
                    ''', (file.filename, name, raw_text, skills))
                except Exception as e:
                    print(f"Error parsing file {file.filename}: {e}")
        
        conn.commit()
    
    # Check for search filtering
    search_query = request.args.get('search', '').strip()
    if search_query:
        cursor.execute("SELECT filename, candidate_name, matched_skills FROM resumes WHERE matched_skills LIKE ?", (f'%{search_query}%',))
    else:
        cursor.execute("SELECT filename, candidate_name, matched_skills FROM resumes")
        
    records = cursor.fetchall()
    conn.close()
    
    return render_template("index.html", records=records, search_query=search_query)

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)