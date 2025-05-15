import json
import re
import os
import logging
import spacy
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load spaCy model for NLP processing
try:
    nlp = spacy.load("en_core_web_sm")
except Exception as e:
    logger.error(f"Error loading spaCy model: {str(e)}")
    # Fallback to a simpler model if the main one isn't available
    try:
        nlp = spacy.load("en")
    except:
        logger.error("Could not load any spaCy model, basic skill extraction only will be available")
        nlp = None

# Load skills dictionary
def load_skills_dictionary():
    """Load the skills dictionary from the JSON file"""
    skills_file = os.path.join('static', 'data', 'skills_dictionary.json')
    try:
        if os.path.exists(skills_file):
            with open(skills_file, 'r') as f:
                return json.load(f)
        else:
            logger.warning(f"Skills dictionary file not found: {skills_file}")
            return generate_default_skills_dictionary()
    except Exception as e:
        logger.error(f"Error loading skills dictionary: {str(e)}")
        return generate_default_skills_dictionary()

def generate_default_skills_dictionary():
    """Generate a default skills dictionary if the file doesn't exist"""
    return {
        "technical": {
            "programming_languages": [
                "Python", "Java", "JavaScript", "C++", "C#", "PHP", "Ruby", "Swift", "Kotlin", "Go",
                "TypeScript", "R", "MATLAB", "Perl", "Scala", "Rust", "Dart", "Objective-C", "Bash",
                "PowerShell", "SQL", "HTML", "CSS", "XML", "JSON", "YAML", "Assembly"
            ],
            "frameworks_libraries": [
                "React", "Angular", "Vue.js", "Django", "Flask", "Spring", "ASP.NET", "Laravel",
                "Express.js", "Ruby on Rails", "TensorFlow", "PyTorch", "Keras", "Scikit-learn",
                "Pandas", "NumPy", "jQuery", "Bootstrap", "Tailwind CSS", "Node.js", "Redux",
                "Next.js", "Gatsby", "FastAPI", "Symfony", "Hibernate", "Mongoose", "Unity"
            ],
            "databases": [
                "MySQL", "PostgreSQL", "SQLite", "Oracle", "Microsoft SQL Server", "MongoDB",
                "Redis", "Cassandra", "DynamoDB", "Elasticsearch", "Firebase", "Neo4j", "MariaDB",
                "CouchDB", "Firestore"
            ],
            "cloud_services": [
                "AWS", "Azure", "Google Cloud", "Heroku", "DigitalOcean", "IBM Cloud", "Oracle Cloud",
                "Alibaba Cloud", "Linode", "Vultr", "EC2", "S3", "Lambda", "DynamoDB", "RDS",
                "CloudFront", "IAM", "Azure Functions", "App Engine", "GKE", "Azure DevOps"
            ],
            "tools": [
                "Git", "Docker", "Kubernetes", "Jenkins", "Travis CI", "CircleCI", "GitHub Actions",
                "Terraform", "Ansible", "Puppet", "Chef", "Vagrant", "JIRA", "Confluence", "Trello",
                "Slack", "VS Code", "IntelliJ IDEA", "Eclipse", "Xcode", "Android Studio", "PyCharm",
                "Postman", "Insomnia", "Figma", "Sketch", "Adobe XD"
            ],
            "methodologies": [
                "Agile", "Scrum", "Kanban", "Waterfall", "DevOps", "CI/CD", "TDD", "BDD", "XP",
                "Lean", "Six Sigma", "ITIL", "SAFe", "LeSS", "Design Thinking", "Microservices",
                "Serverless", "RESTful", "SOA"
            ]
        },
        "soft": [
            "Communication", "Leadership", "Teamwork", "Problem Solving", "Critical Thinking",
            "Adaptability", "Time Management", "Creativity", "Emotional Intelligence", "Negotiation",
            "Conflict Resolution", "Decision Making", "Empathy", "Active Listening", "Public Speaking",
            "Written Communication", "Collaboration", "Organization", "Project Management", "Attention to Detail",
            "Strategic Thinking", "Analytical Skills", "Customer Service", "Interpersonal Skills", "Flexibility"
        ],
        "industry_specific": {
            "finance": [
                "Financial Analysis", "Accounting", "Financial Reporting", "Budgeting", "Forecasting",
                "Risk Management", "Investment Banking", "Financial Modeling", "Valuation",
                "Portfolio Management", "Financial Planning", "Auditing", "Tax Preparation",
                "Mergers & Acquisitions", "Compliance", "Banking", "Insurance", "Equity Research"
            ],
            "healthcare": [
                "Patient Care", "Electronic Health Records (EHR)", "Medical Terminology", "Healthcare Compliance",
                "Clinical Research", "Medical Coding", "HIPAA", "Telemedicine", "Medical Billing",
                "Healthcare Administration", "Pharmacy", "Nursing", "Medical Devices", "Biotechnology"
            ],
            "marketing": [
                "Digital Marketing", "SEO", "SEM", "Social Media Marketing", "Content Marketing",
                "Email Marketing", "Market Research", "Brand Management", "Marketing Strategy",
                "Google Analytics", "CRM", "Growth Hacking", "Affiliate Marketing", "A/B Testing",
                "User Acquisition", "Conversion Rate Optimization", "Google Ads", "Facebook Ads"
            ],
            "data_science": [
                "Machine Learning", "Deep Learning", "Data Analysis", "Data Visualization", "Big Data",
                "Statistical Analysis", "Data Mining", "Natural Language Processing", "Computer Vision",
                "Predictive Modeling", "Feature Engineering", "Data Cleaning", "ETL", "BI Tools",
                "A/B Testing", "Hypothesis Testing", "Regression Analysis", "Clustering"
            ]
        }
    }

def extract_skills(resume_data):
    """
    Extract skills from resume data
    
    Args:
        resume_data (dict): Parsed resume data
        
    Returns:
        dict: Categorized skills
    """
    logger.debug("Extracting skills from resume data")
    
    # Load skills dictionary
    skills_dict = load_skills_dictionary()
    
    # Combine all text from various resume sections
    text = resume_data['raw_text']
    
    # Extract technical skills
    technical_skills = extract_technical_skills(text, skills_dict['technical'])
    
    # Extract soft skills
    soft_skills = extract_soft_skills(text, skills_dict['soft'])
    
    # Extract industry-specific skills
    industry_skills = extract_industry_skills(text, skills_dict['industry_specific'])
    
    # Combine all skills
    all_skills = defaultdict(list)
    
    # Add technical skills
    for category, skills in technical_skills.items():
        all_skills[category].extend(skills)
    
    # Add soft skills
    all_skills['soft_skills'] = soft_skills
    
    # Add industry skills
    for industry, skills in industry_skills.items():
        all_skills[f"industry_{industry}"] = skills
    
    # Add any skills already extracted from the resume
    if 'skills' in resume_data and resume_data['skills']:
        extracted_skills = resume_data['skills']
        if not any(all_skills.values()):
            # If no skills were extracted using the dictionary, use the ones from the resume
            all_skills['uncategorized'] = extracted_skills
        else:
            # Otherwise, add any skills that weren't caught by the dictionary
            all_known_skills = {skill.lower() for category in all_skills.values() for skill in category}
            new_skills = [skill for skill in extracted_skills if skill.lower() not in all_known_skills]
            if new_skills:
                all_skills['uncategorized'] = new_skills
    
    return dict(all_skills)

def extract_technical_skills(text, tech_skills_dict):
    """
    Extract technical skills from the text using the skills dictionary
    
    Args:
        text (str): The resume text
        tech_skills_dict (dict): Dictionary of technical skills categories
        
    Returns:
        dict: Extracted technical skills by category
    """
    extracted_skills = defaultdict(list)
    
    # Convert text to lowercase for case-insensitive matching
    text_lower = text.lower()
    
    # Check for each category of technical skills
    for category, skills in tech_skills_dict.items():
        for skill in skills:
            # Create pattern for whole word matching (with boundary check)
            # Also handle common variations (e.g., JavaScript vs Javascript)
            skill_pattern = r'\b' + re.escape(skill.lower()) + r'(?:\.js)?\b'
            
            # Check if skill exists in the text
            if re.search(skill_pattern, text_lower):
                extracted_skills[category].append(skill)
    
    return dict(extracted_skills)

def extract_soft_skills(text, soft_skills_list):
    """
    Extract soft skills from the text using the skills dictionary
    
    Args:
        text (str): The resume text
        soft_skills_list (list): List of soft skills
        
    Returns:
        list: Extracted soft skills
    """
    extracted_skills = []
    
    # Convert text to lowercase for case-insensitive matching
    text_lower = text.lower()
    
    # Check for each soft skill
    for skill in soft_skills_list:
        # Create pattern for whole word or phrase matching
        skill_pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        
        # Check if skill exists in the text
        if re.search(skill_pattern, text_lower):
            extracted_skills.append(skill)
    
    return extracted_skills

def extract_industry_skills(text, industry_skills_dict):
    """
    Extract industry-specific skills from the text
    
    Args:
        text (str): The resume text
        industry_skills_dict (dict): Dictionary of industry-specific skills
        
    Returns:
        dict: Extracted industry-specific skills by industry
    """
    extracted_skills = defaultdict(list)
    
    # Convert text to lowercase for case-insensitive matching
    text_lower = text.lower()
    
    # Check for each industry category
    for industry, skills in industry_skills_dict.items():
        for skill in skills:
            # Create pattern for whole word or phrase matching
            skill_pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            
            # Check if skill exists in the text
            if re.search(skill_pattern, text_lower):
                extracted_skills[industry].append(skill)
    
    return dict(extracted_skills)

def extract_skills_from_job_description(job_description):
    """
    Extract skills from a job description
    
    Args:
        job_description (str): Job description text
        
    Returns:
        list: Extracted skills
    """
    if not job_description:
        return []
        
    # Load skills dictionary
    skills_dict = load_skills_dictionary()
    
    # Flatten the technical skills dictionary
    all_technical_skills = []
    for category, skills in skills_dict['technical'].items():
        all_technical_skills.extend(skills)
    
    # Get soft skills
    soft_skills = skills_dict['soft']
    
    # Flatten the industry skills dictionary
    all_industry_skills = []
    for industry, skills in skills_dict['industry_specific'].items():
        all_industry_skills.extend(skills)
    
    # Combine all skills
    all_skills = all_technical_skills + soft_skills + all_industry_skills
    
    # Extract skills from job description
    extracted_skills = []
    job_description_lower = job_description.lower()
    
    for skill in all_skills:
        # Create pattern for whole word matching (with boundary check)
        skill_pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        
        # Check if skill exists in the job description
        if re.search(skill_pattern, job_description_lower):
            extracted_skills.append(skill)
    
    return extracted_skills
