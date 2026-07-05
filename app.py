import os
import re
import sqlite3
from flask import Flask, render_template, request

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

# Initialize Database on Start
init_db()

def extract_insights(text):
    # 1. Look for CGPA patterns (e.g., 8.5, 9.12, 3.8/4.0)
    cgpa_match = re.search(r'\b([0-9]\.[0-9]{1,2})\b', text)
    cgpa = cgpa_match.group(1) if cgpa_match else "Not Specified"
    
    # 2. Simple targeted keyword vocabulary scan
    skills_vocab = ["Python", "Java", "C++", "SQL", "Git", "Machine Learning", "OpenCV", "Flask", "HTML", "CSS"]
    found_skills = [skill for skill in skills_vocab if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE)]
    
    return found_skills, cgpa

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("resume_file")
        if file:
            # Read plaintext stream from file input directly
            text_content = file.read().decode("utf-8", errors="ignore")
            
            # Parse metrics
            skills, cgpa = extract_insights(text_content)
            
            # Save directly into database rows
            with sqlite3.connect(DB_FILE) as conn:
                conn.execute(
                    "INSERT INTO profiles (skills, cgpa) VALUES (?, ?)",
                    (", ".join(skills), cgpa)
                )
            
            return render_template("index.html", skills=skills, cgpa=cgpa)
            
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)