# Installation Guide for Resume Analyzer

This document provides detailed instructions for setting up and running the Resume Analyzer application.

## Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- pip (Python package manager)

## Required Packages

The following Python packages are required:

```
flask==2.3.3
flask-sqlalchemy==3.1.1
gunicorn==23.0.0
docx==0.2.4
email-validator==2.1.0
pdfplumber==0.10.3
psycopg2-binary==2.9.9
python-docx==1.0.1
werkzeug==2.3.7
spacy==3.7.2
```

## Installation Steps

1. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install the required packages**:
   ```bash
   pip install flask flask-sqlalchemy gunicorn docx email-validator pdfplumber psycopg2-binary python-docx werkzeug spacy
   ```

3. **Install spaCy model** (optional, for improved NLP capabilities):
   ```bash
   python -m spacy download en_core_web_sm
   ```

4. **Set up the PostgreSQL database**:
   - Create a database for the application
   - Set the DATABASE_URL environment variable to point to your database:
     ```bash
     # On Linux/Mac
     export DATABASE_URL=postgresql://username:password@localhost:5432/resume_analyzer
     
     # On Windows
     set DATABASE_URL=postgresql://username:password@localhost:5432/resume_analyzer
     ```

5. **Run the application**:
   ```bash
   python main.py
   ```
   
   The application will start on http://localhost:5000

## Docker Installation (Alternative)

If you prefer using Docker:

1. **Create a Dockerfile** with the following content:
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   
   COPY . .
   
   RUN pip install --no-cache-dir -r requirements.txt
   
   EXPOSE 5000
   
   CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]
   ```

2. **Build and run the Docker container**:
   ```bash
   docker build -t resume-analyzer .
   docker run -p 5000:5000 -e DATABASE_URL=postgresql://username:password@host:5432/resume_analyzer resume-analyzer
   ```

## Troubleshooting

- **Database Connection Issues**: Ensure your PostgreSQL server is running and that the DATABASE_URL environment variable is set correctly.
  
- **File Upload Issues**: Make sure the UPLOAD_FOLDER path exists and has proper permissions.
  
- **spaCy Model Missing**: If you get warnings about missing spaCy models, install the recommended model using the command in step 3.

## Running in Production

For production deployment, consider:

1. Using a production WSGI server like Gunicorn:
   ```bash
   gunicorn --bind 0.0.0.0:5000 main:app
   ```

2. Setting up a reverse proxy with Nginx or Apache

3. Using environment variables for all configuration and secrets

4. Enabling proper logging and monitoring