# Resume Analyzer Application

A web application that analyzes resumes, extracts key information, and provides scoring and improvement suggestions.

## Features

- **File Upload**: Support for PDF, DOCX, and TXT resume files
- **Resume Parsing**: Extract name, contact info, education, experience, skills, and more
- **Skill Extraction**: Identify technical and soft skills from resume content
- **Keyword Matching**: Compare resume with job descriptions to find matching and missing keywords
- **Resume Scoring**: Score resume based on content quality, keyword matches, structure, and more
- **Improvement Suggestions**: Get actionable suggestions to improve resume effectiveness
- **History Tracking**: Save and view history of analyzed resumes

## Technology Stack

- **Backend**: Python, Flask
- **Database**: PostgreSQL
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Data Visualization**: Chart.js
- **NLP**: Spacy (if installed)

## Installation and Setup

1. Clone the repository:
```
git clone <repository-url>
cd resume-analyzer
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Set up the environment variables:
```
DATABASE_URL=postgresql://username:password@localhost:5432/resume_analyzer
```

4. (Optional) Install spaCy model for improved name extraction and NLP capabilities:
```
python -m spacy download en_core_web_sm
```

5. Run the application:
```
python main.py
```

## Project Structure

- `app.py`: Main Flask application with routes and controllers
- `models.py`: Database models for PostgreSQL
- `resume_parser.py`: Resume parsing logic and extraction functions
- `skill_extractor.py`: Skill extraction from resume text
- `analyzer.py`: Analysis of resume structure, content, and match with job descriptions
- `templates/`: HTML templates for the web interface
- `static/`: CSS, JavaScript, and other static assets

## Usage

1. Start the application and navigate to http://localhost:5000
2. Upload a resume file (PDF, DOCX, or TXT format)
3. Optionally paste a job description for keyword matching
4. Click "Analyze Resume" to get detailed analysis
5. View the analysis and suggestions
6. Access previous analyses from the "History" page

## Database

The application uses PostgreSQL to store resume data and analysis results. The main tables are:

- `resumes`: Stores uploaded resume data and analysis results
- `users`: User information (for future authentication features)
- `user_resumes`: Association table linking users to resumes

## Future Improvements

- User authentication and login functionality
- PDF report generation for analysis results
- Email sharing of resume analysis
- AI-powered improvement suggestions
- Comparison between multiple resumes
- Resume anonymization for unbiased review