import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
import tempfile
import uuid
from flask_sqlalchemy import SQLAlchemy

# Import the resume processing modules
from resume_parser import parse_resume
from skill_extractor import extract_skills
from analyzer import analyze_resume, score_resume, generate_suggestions

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "resume-analyzer-secret")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure database
database_url = os.environ.get("DATABASE_URL", "postgresql://neondb_owner:npg_C85gcGiRjvwl@ep-noisy-morning-a6w9ifir.us-west-2.aws.neon.tech/neondb?sslmode=require")
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import and initialize database models
from models import db, Resume, User
db.init_app(app)

# Configure upload settings
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
TEMP_FOLDER = tempfile.gettempdir()
app.config['UPLOAD_FOLDER'] = TEMP_FOLDER

# Create database tables if they don't exist
with app.app_context():
    db.create_all()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle resume file upload"""
    # Check if file part exists in the request
    if 'resume' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['resume']
    job_description = request.form.get('job_description', '')
    
    # If user does not select file
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        try:
            # Generate a unique filename with the original extension
            original_extension = file.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{original_extension}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            # Save the file
            file.save(filepath)
            logger.debug(f"File saved to {filepath}")
            
            # Parse the resume
            resume_data = parse_resume(filepath, original_extension)
            logger.debug("Resume parsed successfully")
            
            # Extract skills
            skills = extract_skills(resume_data)
            logger.debug(f"Extracted skills: {skills}")
            
            # Analyze the resume
            analysis = analyze_resume(resume_data, job_description)
            logger.debug("Resume analysis completed")
            
            # Score the resume
            scores = score_resume(resume_data, analysis, job_description)
            logger.debug(f"Resume scores: {scores}")
            
            # Generate improvement suggestions
            suggestions = generate_suggestions(resume_data, analysis, scores, job_description)
            logger.debug("Generated suggestions")
            
            # Store results in session
            session['resume_data'] = resume_data
            session['skills'] = skills
            session['analysis'] = analysis
            session['scores'] = scores
            session['suggestions'] = suggestions
            
            # Clean up the file
            os.remove(filepath)
            
            return redirect(url_for('results'))
            
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            flash(f'Error processing file: {str(e)}')
            return redirect(request.url)
    else:
        flash('File type not allowed. Please upload a PDF, DOCX, or TXT file.')
        return redirect(request.url)

@app.route('/results')
def results():
    """Display the analysis results"""
    # Check if we have results in the session
    if not all(key in session for key in ['resume_data', 'skills', 'analysis', 'scores', 'suggestions']):
        flash('No analysis data found. Please upload a resume first.')
        return redirect(url_for('index'))
    
    return render_template('results.html',
                          resume_data=session['resume_data'],
                          skills=session['skills'],
                          analysis=session['analysis'],
                          scores=session['scores'],
                          suggestions=session['suggestions'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
