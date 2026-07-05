import os
import re
import sqlite3
from flask import Flask, render_template, request
# Import your original PDF library here (e.g., import pdfplumber or pypdf)

app = Flask(__name__)
DB_FILE = "database.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skills TEXT,
                cgpa TEXT
            )
        ''')
    conn.close()

init_db()

def extract_insights(text):
    # Regex to catch standard CGPA patterns (e.g., 8.5, 9.2, 3.8/4.0)
    cgpa_match = re.search(r'\b([0-9]\.[0-9]{1,2})\b', text)
    cgpa = cgpa_match.group(1) if cgpa_match else "Not Specified"
    
    # Simple core vocabulary matching
    skills_vocab = ["Python", "Java", "C++", "SQL", "Git", "Machine Learning", "OpenCV", "Flask", "HTML", "CSS"]
    found_skills = [skill for skill in skills_vocab if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE)]
    
    return found_skills, cgpa

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("resume_file")
        if file and file.filename != '':
            # --- RESTORE YOUR ORIGINAL PDF TEXT EXTRACTION HERE ---
            # Example if you used pdfplumber:
            # with pdfplumber.open(file) as pdf:
            #     text_content = "".join([page.extract_text() for page in pdf.pages])
            
            # Temporary fallback for plain text files:
            text_content = file.read().decode("utf-8", errors="ignore")
            
            skills, cgpa = extract_insights(text_content)
            
            with sqlite3.connect(DB_FILE) as conn:
                conn.execute(
                    "INSERT INTO profiles (skills, cgpa) VALUES (?, ?)",
                    (", ".join(skills), cgpa)
                )
            
            return render_template("index.html", skills=skills, cgpa=cgpa)
            
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)