# A Simple Flask API
# Step 1 is pip install flask
 
# Render Template will tell flask to look in templates folder for exact .html file
from flask import Flask, render_template, request, jsonify
# This will protect us from injections 
from markupsafe import escape
# For handling cross-origin requests from your MERN application
from flask_cors import CORS
# Regular expressions for pattern matching
import re
# For natural language processing tasks
import nltk
import spacy
# For handling JSON data
import json
# For PDF processing
import io
import PyPDF2
# For handling file uploads
from werkzeug.utils import secure_filename
import os
import sys

# Initialize Flask app
app = Flask(__name__)
# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})
# Configure upload folder - use absolute path based on app location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'txt'}

# Download necessary NLTK data (run once)
try:
    # These are common NLTK packages needed
    for package in ['punkt', 'stopwords']:
        try:
            nltk.data.find(f'tokenizers/{package}' if package == 'punkt' else f'corpora/{package}')
        except LookupError:
            nltk.download(package)
except Exception as e:
    print(f"Warning: NLTK data download issue: {e}")
    # Continue even if NLTK data download fails

# Load spaCy English model with proper error handling
nlp = None
try:
    nlp = spacy.load("en_core_web_sm")
except:
    try:
        # Try to install if not found (this might work in some environments)
        import subprocess
        print("Attempting to download spaCy model...")
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        nlp = spacy.load("en_core_web_sm")
    except:
        # Final fallback - continue without spaCy
        print("spaCy model not available. Using basic extraction methods only.")

# List of common technical skills (this is a small sample - in production you would have a much larger dataset)
TECH_SKILLS = [
    # Programming Languages
    "javascript", "python", "java", "c++", "c#", "ruby", "php", "swift", "go", "rust",
    "typescript", "kotlin", "scala", "perl", "r", "matlab", "dart", "groovy", "bash",
    
    # Web Technologies
    "html", "css", "sass", "less", "bootstrap", "tailwind", "jquery", "ajax", "xml",
    
    # Frameworks & Libraries
    "react", "angular", "vue", "node.js", "express", "django", "flask", "spring", 
    "laravel", "asp.net", "rails", "symfony", "flutter", "react native",
    
    # Databases
    "sql", "mongodb", "mysql", "postgresql", "oracle", "sqlite", "firebase", 
    "dynamodb", "cassandra", "redis", "couchdb", "mariadb", "neo4j",
    
    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "terraform", "ansible",
    "git", "github", "gitlab", "bitbucket", "ci/cd", "prometheus", "grafana",
    
    # AI & Data Science
    "machine learning", "deep learning", "nlp", "computer vision", "tensorflow", 
    "pytorch", "keras", "scikit-learn", "pandas", "numpy", "hadoop", "spark",
    
    # MERN Specific
    "mern", "mongodb", "express", "react", "node"
]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_file):
    """Extract text from a PDF file"""
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    return text

@app.route('/')
def base():
    return render_template('Home.html')

@app.route('/about')
def about():
    return render_template('About.html')

@app.route('/contact')
def contact():
    return render_template('Contact.html')

# New API endpoint for skill extraction
@app.route('/api/extract-skills', methods=['POST'])
def extract_skills():
    try:
        resume_text = ""
        # Check if the request is a file upload
        if 'resume' in request.files:
            file = request.files['resume']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                try:
                    file.save(file_path)
                    
                    # Extract text based on file type
                    if filename.endswith('.pdf'):
                        with open(file_path, 'rb') as pdf_file:
                            resume_text = extract_text_from_pdf(pdf_file)
                    elif filename.endswith('.txt'):
                        with open(file_path, 'r', encoding='utf-8') as txt_file:
                            resume_text = txt_file.read()
                    
                    # Clean up the file after processing
                    try:
                        os.remove(file_path)
                    except:
                        pass  # Don't let cleanup failures break the API
                        
                except Exception as e:
                    return jsonify({"error": f"Error processing file: {str(e)}"}), 500
            else:
                return jsonify({"error": "Invalid file format. Allowed formats: PDF, TXT"}), 400
        
        # Check if the request contains JSON data with text
        elif request.json and 'text' in request.json:
            resume_text = request.json['text']
        else:
            return jsonify({
                "error": "No resume content provided. Please send either text data or upload a file."
            }), 400
        
        if not resume_text:
            return jsonify({"error": "Failed to extract text from the provided content"}), 400
            
        # Convert to lowercase for processing
        resume_text = resume_text.lower()
        
        # Extract skills using both methods if possible
        skills_from_regex = extract_skills_regex(resume_text)
        skills_from_nlp = extract_skills_nlp(resume_text) if nlp else []
        
        # Combine skills from both methods and remove duplicates
        all_skills = list(set(skills_from_regex + skills_from_nlp))
        
        # Sort skills alphabetically for consistent responses
        all_skills.sort()
        
        # Return the extracted skills as JSON
        return jsonify({
            "skills": all_skills,
            "count": len(all_skills)
        })
    except Exception as e:
        # Catch-all error handler
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

def extract_skills_regex(text):
    """
    Extract skills using regex pattern matching.
    This is a simple approach that looks for exact matches of skills in the text.
    """
    found_skills = []
    for skill in TECH_SKILLS:
        # Look for the skill as a whole word
        if re.search(r'\b' + re.escape(skill) + r'\b', text):
            found_skills.append(skill)
    return found_skills

def extract_skills_nlp(text):
    """
    Extract skills using NLP techniques.
    This is a more advanced approach that uses spaCy for entity recognition.
    In a production system, you would train a custom NER model for better results.
    """
    if not nlp:
        return []
        
    try:
        found_skills = []
        doc = nlp(text)
        
        # Extract noun phrases as potential skills
        noun_phrases = [chunk.text.lower() for chunk in doc.noun_chunks]
        
        # Check if any noun phrases match our skills list
        for phrase in noun_phrases:
            phrase = phrase.strip()
            for skill in TECH_SKILLS:
                if skill == phrase or skill in phrase.split():
                    found_skills.append(skill)
        
        return found_skills
    except Exception as e:
        print(f"Error in NLP processing: {e}")
        return []  # Fall back to empty list if NLP fails

if __name__=="__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)

