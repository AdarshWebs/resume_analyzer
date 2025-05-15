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

# Configure database - use SQLite instead of PostgreSQL for simplicity
database_url = os.environ.get("DATABASE_URL", "sqlite:///resume_analyzer.db")
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
    
    if file and file.filename and allowed_file(file.filename):
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
            
            # Save to database
            try:
                # Create a new Resume record
                resume_record = Resume()
                resume_record.filename = file.filename
                resume_record.name = resume_data.get('name', 'Unknown')
                resume_record.email = resume_data.get('email', '')
                resume_record.phone = resume_data.get('phone', '')
                resume_record.raw_text = resume_data.get('raw_text', '')
                resume_record.job_description = job_description
                resume_record.skills = skills
                resume_record.sections_analysis = analysis.get('sections_analysis', {})
                resume_record.keyword_match = analysis.get('keyword_match', {})
                resume_record.action_verbs_analysis = analysis.get('action_verbs', {})
                resume_record.word_count_analysis = analysis.get('word_count', {})
                resume_record.common_issues = analysis.get('common_resume_issues', [])
                resume_record.overall_score = scores.get('overall', 0)
                resume_record.sections_score = scores.get('sections', 0)
                resume_record.keywords_score = scores.get('keywords', 0)
                resume_record.action_verbs_score = scores.get('action_verbs', 0)
                resume_record.word_count_score = scores.get('word_count', 0)
                resume_record.issues_score = scores.get('issues', 0)
                resume_record.grade = scores.get('grade', 'F')
                resume_record.suggestions = suggestions
                
                # Save to database
                db.session.add(resume_record)
                db.session.commit()
                
                # Store the resume ID in session for future reference
                session['resume_id'] = resume_record.id
                logger.debug(f"Resume saved to database with ID: {resume_record.id}")
            except Exception as e:
                logger.error(f"Error saving to database: {str(e)}")
                db.session.rollback()
                # Continue even if database save fails
            
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

@app.route('/history')
def history():
    """Display resume analysis history"""
    # Get all resumes from database
    resumes = Resume.query.order_by(Resume.upload_date.desc()).all()
    
    return render_template('history.html', resumes=resumes)

@app.route('/view_resume/<int:resume_id>')
def view_resume(resume_id):
    """View a specific resume analysis from history"""
    # Get the resume from database
    resume = Resume.query.get_or_404(resume_id)
    
    # Set session data
    session['resume_data'] = {
        'name': resume.name,
        'email': resume.email,
        'phone': resume.phone,
        'raw_text': resume.raw_text
    }
    session['skills'] = resume.skills
    session['analysis'] = {
        'sections_analysis': resume.sections_analysis,
        'keyword_match': resume.keyword_match,
        'action_verbs': resume.action_verbs_analysis,
        'word_count': resume.word_count_analysis,
        'common_resume_issues': resume.common_issues
    }
    session['scores'] = {
        'overall': resume.overall_score,
        'sections': resume.sections_score,
        'keywords': resume.keywords_score,
        'action_verbs': resume.action_verbs_score,
        'word_count': resume.word_count_score,
        'issues': resume.issues_score,
        'grade': resume.grade
    }
    session['suggestions'] = resume.suggestions
    
    return redirect(url_for('results'))

# Error handler for 405 Method Not Allowed
@app.errorhandler(405)
def method_not_allowed(e):
    logger.error(f"Method Not Allowed Error: {request.method} request to {request.path}")
    flash(f'Method Not Allowed: The {request.method} method is not allowed for the requested URL. Please use the form on the homepage.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
