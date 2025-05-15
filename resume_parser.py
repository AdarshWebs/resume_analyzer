import logging
import re
import io
import pdfplumber
from docx import Document
import spacy

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Set nlp to None since spaCy model is not available
logger.warning("SpaCy model not available. Using basic parsing methods instead.")
nlp = None

def parse_resume(filepath, file_extension):
    """
    Parse a resume file and extract information
    
    Args:
        filepath (str): Path to the resume file
        file_extension (str): File extension (pdf, docx, txt)
        
    Returns:
        dict: Extracted resume data
    """
    logger.debug(f"Parsing resume: {filepath} with extension {file_extension}")
    
    text = ""
    
    try:
        if file_extension == 'pdf':
            text = extract_text_from_pdf(filepath)
        elif file_extension == 'docx':
            text = extract_text_from_docx(filepath)
        elif file_extension == 'txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            raise ValueError(f"Unsupported file extension: {file_extension}")
        
        # Extract resume information
        resume_data = extract_resume_data(text)
        return resume_data
        
    except Exception as e:
        logger.error(f"Error parsing resume: {str(e)}")
        raise

def extract_text_from_pdf(filepath):
    """Extract text from a PDF file"""
    logger.debug(f"Extracting text from PDF: {filepath}")
    text = ""
    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise

def extract_text_from_docx(filepath):
    """Extract text from a DOCX file"""
    logger.debug(f"Extracting text from DOCX: {filepath}")
    text = ""
    try:
        doc = Document(filepath)
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {str(e)}")
        raise

def extract_resume_data(text):
    """
    Extract structured data from resume text
    
    Args:
        text (str): The raw text from the resume
        
    Returns:
        dict: Structured resume data
    """
    logger.debug("Extracting structured data from resume text")
    
    resume_data = {
        'raw_text': text,
        'name': extract_name(text),
        'email': extract_email(text),
        'phone': extract_phone(text),
        'education': extract_education(text),
        'experience': extract_experience(text),
        'skills': extract_skills_from_text(text),
        'projects': extract_projects(text),
        'certifications': extract_certifications(text),
        'languages': extract_languages(text),
        'sections': identify_sections(text)
    }
    
    return resume_data

def extract_name(text):
    """Extract name from text using spaCy if available, or regex patterns"""
    if nlp:
        # Use spaCy for named entity recognition
        doc = nlp(text.split('\n')[0])  # Assume name is in the first line
        for ent in doc.ents:
            if ent.label_ == 'PERSON':
                return ent.text
    
    # Fallback to first line if no name entity was found
    lines = text.split('\n')
    for line in lines[:3]:  # Check first 3 lines
        line = line.strip()
        if line and len(line) > 3 and len(line.split()) <= 5:
            return line
    
    return "Name not detected"

def extract_email(text):
    """Extract email address from text"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else "Email not found"

def extract_phone(text):
    """Extract phone number from text"""
    # Remove non-numeric characters for matching
    text_clean = re.sub(r'[^0-9+()-]', ' ', text)
    
    # Common phone patterns
    patterns = [
        r'\+\d{1,3}\s*\(\d{1,4}\)\s*\d{3,4}[-\s]?\d{3,4}',  # +1 (123) 456-7890
        r'\+\d{1,3}\s*\d{1,4}\s*\d{3,4}[-\s]?\d{3,4}',       # +1 123 456 7890
        r'\(\d{3,4}\)\s*\d{3,4}[-\s]?\d{3,4}',               # (123) 456-7890
        r'\d{3,4}[-\s]?\d{3,4}[-\s]?\d{3,4}',                # 123-456-7890
        r'\d{10,12}'                                          # 1234567890
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text_clean)
        if matches:
            return matches[0]
    
    return "Phone not found"

def extract_education(text):
    """Extract education information from text"""
    education = []
    
    # Identify education section
    education_section = extract_section(text, ['EDUCATION', 'ACADEMIC BACKGROUND'])
    if education_section:
        # Look for common degree patterns
        degree_patterns = [
            r'(Bachelor|Master|PhD|Doctorate|BSc|BA|MS|MSc|MBA|BBA|B\.Tech|M\.Tech|B\.E|M\.E)\.?\s+(of|in|on)?\s+([A-Za-z\s,]+)',
            r'([A-Za-z\s]+)(University|College|Institute|School)',
            r'(19|20)\d{2}\s*(-|–|to)\s*(19|20)\d{2}|Present',
            r'GPA\s*:?\s*\d+\.\d+',
        ]
        
        lines = education_section.split('\n')
        current_edu = {}
        
        for line in lines:
            if not line.strip():
                continue
                
            if current_edu and (any(re.search(pattern, line, re.IGNORECASE) for pattern in degree_patterns) or 
                               line.strip().endswith(':')):
                education.append(current_edu)
                current_edu = {}
            
            # Extract degree information
            for pattern in degree_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    if 'degree' not in current_edu:
                        current_edu['degree'] = line.strip()
                    else:
                        current_edu['details'] = current_edu.get('details', '') + line.strip() + '\n'
        
        if current_edu:
            education.append(current_edu)
    
    # If no structured education found, return the entire education section
    if not education and education_section:
        education = [{'details': education_section}]
    
    return education if education else [{"details": "Education section not found"}]

def extract_experience(text):
    """Extract work experience information from text"""
    experience = []
    
    # Identify experience section
    experience_section = extract_section(text, ['EXPERIENCE', 'WORK EXPERIENCE', 'EMPLOYMENT', 'WORK HISTORY'])
    if experience_section:
        # Split by date patterns or company names
        date_pattern = r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\.?[\s,]*\d{4}|[\d]{1,2}/[\d]{4}|[\d]{4})\s*(-|–|to)\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\.?[\s,]*\d{4}|[\d]{1,2}/[\d]{4}|[\d]{4}|Present|Current|Now)'
        
        # First try to split by date patterns
        chunks = re.split(date_pattern, experience_section)
        if len(chunks) > 1:
            for i in range(0, len(chunks)-3, 4):
                start_date = chunks[i+1]
                end_date = chunks[i+3]
                description = chunks[i+4].strip() if i+4 < len(chunks) else ""
                
                # Find the company/title line, usually right before the date
                previous_text = chunks[i].strip().split('\n')
                title_company = previous_text[-1] if previous_text else ""
                
                experience.append({
                    'title_company': title_company,
                    'date': f"{start_date} - {end_date}",
                    'description': description
                })
        else:
            # Fallback to splitting by new paragraphs
            paragraphs = re.split(r'\n\s*\n', experience_section)
            for para in paragraphs:
                if not para.strip():
                    continue
                
                date_match = re.search(date_pattern, para)
                if date_match:
                    date_str = f"{date_match.group(1)} - {date_match.group(3)}"
                    para_without_date = para.replace(date_match.group(0), '')
                    lines = para_without_date.split('\n')
                    
                    title_company = lines[0].strip() if lines else ""
                    description = '\n'.join(lines[1:]).strip() if len(lines) > 1 else ""
                    
                    experience.append({
                        'title_company': title_company,
                        'date': date_str,
                        'description': description
                    })
                else:
                    experience.append({
                        'description': para.strip()
                    })
    
    # If no structured experience found, return the entire experience section
    if not experience and experience_section:
        experience = [{'description': experience_section}]
    
    return experience if experience else [{"description": "Experience section not found"}]

def extract_skills_from_text(text):
    """Extract skills from text (basic version, more comprehensive in skill_extractor.py)"""
    skills_section = extract_section(text, ['SKILLS', 'TECHNICAL SKILLS', 'CORE COMPETENCIES'])
    if skills_section:
        # Simple extraction: split by commas, bullets, or new lines
        skills_text = re.sub(r'•|·|\*|›|✓|✔|▪|▫|-|\|', ',', skills_section)
        skills_list = [skill.strip() for skill in re.split(r',|\n', skills_text) if skill.strip()]
        return skills_list
    
    return []

def extract_projects(text):
    """Extract project information from text"""
    projects_section = extract_section(text, ['PROJECTS', 'PROJECT EXPERIENCE', 'ACADEMIC PROJECTS'])
    if projects_section:
        # Split by project titles or bullet points
        projects = []
        current_project = {}
        
        lines = projects_section.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # New project likely starts with a title (often with date)
            if (re.match(r'^[A-Z]', line) and len(line) < 100) or re.search(r'\(\d{4}\)', line):
                if current_project:
                    projects.append(current_project)
                current_project = {'title': line}
            elif current_project:
                # Add to description
                if 'description' not in current_project:
                    current_project['description'] = line
                else:
                    current_project['description'] += '\n' + line
        
        if current_project:
            projects.append(current_project)
            
        return projects
    
    return []

def extract_certifications(text):
    """Extract certification information from text"""
    cert_section = extract_section(text, ['CERTIFICATIONS', 'CERTIFICATES', 'PROFESSIONAL CERTIFICATIONS'])
    if cert_section:
        # Split by new lines and bullet points
        cert_text = re.sub(r'•|·|\*|›|✓|✔|▪|▫|-', '\n', cert_section)
        certs = [cert.strip() for cert in cert_text.split('\n') if cert.strip()]
        return certs
    
    return []

def extract_languages(text):
    """Extract language information from text"""
    lang_section = extract_section(text, ['LANGUAGES', 'LANGUAGE SKILLS'])
    if lang_section:
        # Split by commas and new lines
        lang_text = re.sub(r'•|·|\*|›|✓|✔|▪|▫|-', ',', lang_section)
        langs = [lang.strip() for lang in re.split(r',|\n', lang_text) if lang.strip()]
        return langs
    
    return []

def extract_section(text, section_headers):
    """
    Extract a section from the text based on section headers
    
    Args:
        text (str): Full resume text
        section_headers (list): Possible section header names
        
    Returns:
        str: The extracted section text or empty string if not found
    """
    section_pattern = '|'.join(f"({header})" for header in section_headers)
    regex_pattern = fr"(?:{section_pattern})[:\s]*(?:\n|\r\n?)(.*?)(?:\n\s*(?:[A-Z][A-Z\s]+[A-Z])[:\s]*(?:\n|\r\n?)|$)"
    
    try:
        match = re.search(regex_pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            # Return the content of the section (capturing group after the header)
            return match.group(len(section_headers) + 1).strip()
    except Exception as e:
        logger.error(f"Error extracting section {section_headers}: {str(e)}")
    
    return ""

def identify_sections(text):
    """
    Identify the main sections present in the resume
    
    Args:
        text (str): Full resume text
        
    Returns:
        dict: Dictionary of section names and their presence
    """
    common_sections = {
        'contact': ['CONTACT', 'CONTACT INFORMATION'],
        'summary': ['SUMMARY', 'PROFESSIONAL SUMMARY', 'PROFILE'],
        'education': ['EDUCATION', 'ACADEMIC BACKGROUND'],
        'experience': ['EXPERIENCE', 'WORK EXPERIENCE', 'EMPLOYMENT', 'WORK HISTORY'],
        'skills': ['SKILLS', 'TECHNICAL SKILLS', 'CORE COMPETENCIES'],
        'projects': ['PROJECTS', 'PROJECT EXPERIENCE', 'ACADEMIC PROJECTS'],
        'certifications': ['CERTIFICATIONS', 'CERTIFICATES', 'PROFESSIONAL CERTIFICATIONS'],
        'languages': ['LANGUAGES', 'LANGUAGE SKILLS'],
        'interests': ['INTERESTS', 'HOBBIES'],
        'references': ['REFERENCES']
    }
    
    sections = {}
    for section_key, headers in common_sections.items():
        section_text = extract_section(text, headers)
        sections[section_key] = bool(section_text)
    
    return sections
