from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import JSON

db = SQLAlchemy()

class Resume(db.Model):
    """Resume model for storing uploaded resume data and analysis results"""
    __tablename__ = 'resumes'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Basic resume data
    name = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    
    # Raw text and job description
    raw_text = db.Column(db.Text, nullable=True)
    job_description = db.Column(db.Text, nullable=True)
    
    # Analysis results stored as JSON
    skills = db.Column(JSON, nullable=True)
    sections_analysis = db.Column(JSON, nullable=True)
    keyword_match = db.Column(JSON, nullable=True)
    action_verbs_analysis = db.Column(JSON, nullable=True)
    word_count_analysis = db.Column(JSON, nullable=True)
    common_issues = db.Column(JSON, nullable=True)
    
    # Scores
    overall_score = db.Column(db.Float, nullable=True)
    sections_score = db.Column(db.Float, nullable=True)
    keywords_score = db.Column(db.Float, nullable=True)
    action_verbs_score = db.Column(db.Float, nullable=True)
    word_count_score = db.Column(db.Float, nullable=True)
    issues_score = db.Column(db.Float, nullable=True)
    grade = db.Column(db.String(2), nullable=True)
    
    # Suggestions
    suggestions = db.Column(JSON, nullable=True)
    
    def __repr__(self):
        return f'<Resume {self.id}: {self.name or "Unknown"}>'

class User(db.Model):
    """User model for authentication and resume ownership"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to resumes
    resumes = db.relationship('Resume', secondary='user_resumes', backref='users')
    
    def __repr__(self):
        return f'<User {self.username}>'

# Association table for user-resume relationship (many-to-many)
user_resumes = db.Table('user_resumes',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('resume_id', db.Integer, db.ForeignKey('resumes.id'), primary_key=True)
)