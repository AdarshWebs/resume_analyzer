import re
import logging
from collections import Counter
from skill_extractor import extract_skills_from_job_description

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def analyze_resume(resume_data, job_description):
    """
    Analyze the resume for completeness, quality, and match with job description
    
    Args:
        resume_data (dict): Parsed resume data
        job_description (str): Job description text
        
    Returns:
        dict: Analysis results
    """
    logger.debug("Analyzing resume")
    
    analysis = {
        'sections_analysis': analyze_sections(resume_data),
        'word_count': analyze_word_count(resume_data),
        'action_verbs': analyze_action_verbs(resume_data),
        'keyword_match': analyze_keyword_match(resume_data, job_description),
        'common_resume_issues': identify_common_issues(resume_data)
    }
    
    return analysis

def analyze_sections(resume_data):
    """
    Analyze which sections are present or missing in the resume
    
    Args:
        resume_data (dict): Parsed resume data
        
    Returns:
        dict: Section analysis
    """
    sections = resume_data.get('sections', {})
    
    # Define essential sections
    essential_sections = ['summary', 'education', 'experience', 'skills']
    
    # Define recommended sections
    recommended_sections = ['projects', 'certifications']
    
    # Check for missing essential sections
    missing_essential = [section for section in essential_sections if not sections.get(section, False)]
    
    # Check for missing recommended sections
    missing_recommended = [section for section in recommended_sections if not sections.get(section, False)]
    
    return {
        'present': [section for section, present in sections.items() if present],
        'missing_essential': missing_essential,
        'missing_recommended': missing_recommended,
        'has_all_essential': len(missing_essential) == 0
    }

def analyze_word_count(resume_data):
    """
    Analyze word count for different sections of the resume
    
    Args:
        resume_data (dict): Parsed resume data
        
    Returns:
        dict: Word count analysis
    """
    word_counts = {}
    
    # Count words in the raw text
    raw_text = resume_data.get('raw_text', '')
    word_counts['total'] = len(re.findall(r'\b\w+\b', raw_text))
    
    # Count words in summary section (if present)
    summary_section = ''
    if resume_data.get('sections', {}).get('summary', False):
        # Extract summary section from raw text (simplified)
        summary_section = re.search(r'(?:SUMMARY|PROFESSIONAL SUMMARY|PROFILE)[:\s]*(?:\n|\r\n?)(.*?)(?:\n\s*(?:[A-Z][A-Z\s]+[A-Z])[:\s]*(?:\n|\r\n?)|$)', raw_text, re.IGNORECASE | re.DOTALL)
        if summary_section:
            summary_text = summary_section.group(1)
            word_counts['summary'] = len(re.findall(r'\b\w+\b', summary_text))
    
    # Count words in experience descriptions
    experience_words = 0
    for exp in resume_data.get('experience', []):
        if 'description' in exp:
            experience_words += len(re.findall(r'\b\w+\b', exp['description']))
    word_counts['experience'] = experience_words
    
    # Analyze if word count is within recommended ranges
    word_count_assessment = {}
    
    # Total word count assessment (ideally 400-800 words)
    if word_counts['total'] < 300:
        word_count_assessment['total'] = 'too_short'
    elif word_counts['total'] > 1000:
        word_count_assessment['total'] = 'too_long'
    else:
        word_count_assessment['total'] = 'good'
    
    # Summary word count assessment (ideally 50-200 words)
    if 'summary' in word_counts:
        if word_counts['summary'] < 30:
            word_count_assessment['summary'] = 'too_short'
        elif word_counts['summary'] > 250:
            word_count_assessment['summary'] = 'too_long'
        else:
            word_count_assessment['summary'] = 'good'
    
    word_counts['assessment'] = word_count_assessment
    
    return word_counts

def analyze_action_verbs(resume_data):
    """
    Analyze the usage of action verbs in experience descriptions
    
    Args:
        resume_data (dict): Parsed resume data
        
    Returns:
        dict: Action verb analysis
    """
    # Common action verbs for resumes
    common_action_verbs = [
        'achieved', 'improved', 'developed', 'created', 'implemented', 'managed', 'led', 'designed',
        'established', 'coordinated', 'conducted', 'organized', 'directed', 'launched', 'spearheaded',
        'delivered', 'generated', 'reduced', 'increased', 'negotiated', 'supervised', 'trained',
        'analyzed', 'built', 'streamlined', 'produced', 'resolved', 'executed', 'maintained',
        'collaborated', 'influenced', 'optimized', 'authored', 'initiated', 'transformed'
    ]
    
    # Extract all experience descriptions
    experience_descriptions = []
    for exp in resume_data.get('experience', []):
        if 'description' in exp:
            experience_descriptions.append(exp['description'])
    
    combined_description = ' '.join(experience_descriptions).lower()
    
    # Count action verbs
    action_verb_count = 0
    unique_action_verbs = set()
    
    for verb in common_action_verbs:
        verb_pattern = r'\b' + re.escape(verb) + r'\b'
        matches = re.findall(verb_pattern, combined_description)
        
        if matches:
            action_verb_count += len(matches)
            unique_action_verbs.add(verb)
    
    # Calculate action verb density
    total_words = len(re.findall(r'\b\w+\b', combined_description))
    action_verb_density = action_verb_count / total_words if total_words > 0 else 0
    
    # Extract most used action verbs (top 5)
    verb_counter = Counter()
    for verb in common_action_verbs:
        verb_pattern = r'\b' + re.escape(verb) + r'\b'
        matches = re.findall(verb_pattern, combined_description)
        
        if matches:
            verb_counter[verb] = len(matches)
    
    most_used_verbs = verb_counter.most_common(5)
    
    return {
        'action_verb_count': action_verb_count,
        'unique_action_verbs': len(unique_action_verbs),
        'action_verb_density': action_verb_density,
        'most_used_verbs': most_used_verbs,
        'assessment': 'good' if action_verb_density >= 0.05 else 'needs_improvement'
    }

def analyze_keyword_match(resume_data, job_description):
    """
    Analyze how well the resume matches keywords from the job description
    
    Args:
        resume_data (dict): Parsed resume data
        job_description (str): Job description text
        
    Returns:
        dict: Keyword match analysis
    """
    if not job_description:
        return {
            'match_percentage': None,
            'matched_keywords': [],
            'missing_keywords': [],
            'assessment': 'no_job_description'
        }
    
    # Extract skills from job description
    job_skills = extract_skills_from_job_description(job_description)
    
    # Get resume skills (flattened)
    resume_skills = []
    for skill_category, skills in resume_data.get('skills', {}).items():
        if isinstance(skills, list):
            resume_skills.extend(skills)
        elif isinstance(skills, dict):
            for subcategory, subskills in skills.items():
                resume_skills.extend(subskills)
    
    # Normalize skills (lowercase)
    resume_skills_lower = [skill.lower() for skill in resume_skills]
    job_skills_lower = [skill.lower() for skill in job_skills]
    
    # Find matching and missing skills
    matched_skills = [skill for skill in job_skills if skill.lower() in resume_skills_lower]
    missing_skills = [skill for skill in job_skills if skill.lower() not in resume_skills_lower]
    
    # Calculate match percentage
    match_percentage = len(matched_skills) / len(job_skills) * 100 if job_skills else 0
    
    # Assess the match
    if match_percentage >= 80:
        assessment = 'excellent'
    elif match_percentage >= 60:
        assessment = 'good'
    elif match_percentage >= 40:
        assessment = 'fair'
    else:
        assessment = 'poor'
    
    return {
        'match_percentage': match_percentage,
        'matched_keywords': matched_skills,
        'missing_keywords': missing_skills,
        'assessment': assessment
    }

def identify_common_issues(resume_data):
    """
    Identify common issues in the resume
    
    Args:
        resume_data (dict): Parsed resume data
        
    Returns:
        list: Common issues identified
    """
    issues = []
    
    # Check for missing contact information
    if resume_data.get('email') == "Email not found":
        issues.append("Missing email address")
    
    if resume_data.get('phone') == "Phone not found":
        issues.append("Missing phone number")
    
    # Check for missing essential sections
    sections = resume_data.get('sections', {})
    if not sections.get('summary', False):
        issues.append("Missing professional summary section")
    
    if not sections.get('experience', False):
        issues.append("Missing work experience section")
    
    if not sections.get('education', False):
        issues.append("Missing education section")
    
    if not sections.get('skills', False):
        issues.append("Missing skills section")
    
    # Check for potentially weak experience descriptions
    weak_experience = False
    for exp in resume_data.get('experience', []):
        if 'description' in exp:
            description = exp['description']
            # Check if description is too short
            if len(re.findall(r'\b\w+\b', description)) < 15:
                weak_experience = True
                break
            
            # Check if description lacks action verbs
            if not any(re.search(r'\b' + re.escape(verb) + r'\b', description.lower()) for verb in [
                'achieved', 'improved', 'developed', 'created', 'implemented', 'managed', 'led',
                'designed', 'established', 'coordinated', 'analyzed', 'built'
            ]):
                weak_experience = True
                break
    
    if weak_experience:
        issues.append("Weak experience descriptions (too short or lacking action verbs)")
    
    # Check for potential formatting issues (based on raw text)
    raw_text = resume_data.get('raw_text', '')
    
    # Check for excessive line breaks
    if raw_text.count('\n\n\n') > 5:
        issues.append("Potential formatting issues: excessive line breaks")
    
    # Check for potential inconsistent date formats
    date_formats = re.findall(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\.?[\s,]*\d{4}|[\d]{1,2}/[\d]{4}|[\d]{4}', raw_text)
    if len(set(len(date) for date in date_formats)) > 1:
        issues.append("Inconsistent date formats")
    
    return issues

def score_resume(resume_data, analysis, job_description):
    """
    Score the resume based on various factors
    
    Args:
        resume_data (dict): Parsed resume data
        analysis (dict): Analysis results
        job_description (str): Job description text
        
    Returns:
        dict: Resume scores
    """
    scores = {}
    
    # Score based on sections (30 points)
    section_score = 0
    sections_analysis = analysis.get('sections_analysis', {})
    
    # Each essential section is worth 5 points
    essential_sections = ['summary', 'education', 'experience', 'skills']
    for section in essential_sections:
        if section in sections_analysis.get('present', []):
            section_score += 5
    
    # Each recommended section is worth 2.5 points
    recommended_sections = ['projects', 'certifications']
    for section in recommended_sections:
        if section in sections_analysis.get('present', []):
            section_score += 2.5
    
    # Bonus for having contact information (5 points)
    if resume_data.get('email') != "Email not found" and resume_data.get('phone') != "Phone not found":
        section_score += 5
    
    scores['sections'] = min(section_score, 30)
    
    # Score based on keyword matching (25 points)
    keyword_score = 0
    keyword_match = analysis.get('keyword_match', {})
    
    if keyword_match.get('match_percentage') is not None:
        keyword_score = keyword_match.get('match_percentage') * 0.25
    else:
        # If no job description provided, give default score
        keyword_score = 15
    
    scores['keywords'] = min(keyword_score, 25)
    
    # Score based on action verbs usage (20 points)
    action_verb_score = 0
    action_verbs = analysis.get('action_verbs', {})
    
    if action_verbs.get('assessment') == 'good':
        action_verb_score = 15
        
        # Bonus for having many unique action verbs
        if action_verbs.get('unique_action_verbs', 0) >= 10:
            action_verb_score += 5
    else:
        # Base score based on action verb density
        action_verb_density = action_verbs.get('action_verb_density', 0)
        action_verb_score = min(action_verb_density * 200, 15)
    
    scores['action_verbs'] = min(action_verb_score, 20)
    
    # Score based on word count (15 points)
    word_count_score = 0
    word_count = analysis.get('word_count', {})
    
    # Score based on total word count
    if word_count.get('assessment', {}).get('total') == 'good':
        word_count_score += 10
    elif word_count.get('assessment', {}).get('total') == 'too_short':
        word_count_score += 5
    elif word_count.get('assessment', {}).get('total') == 'too_long':
        word_count_score += 7
    
    # Score based on summary word count (if present)
    if 'summary' in word_count.get('assessment', {}):
        if word_count.get('assessment', {}).get('summary') == 'good':
            word_count_score += 5
        elif word_count.get('assessment', {}).get('summary') == 'too_short':
            word_count_score += 2
        elif word_count.get('assessment', {}).get('summary') == 'too_long':
            word_count_score += 3
    
    scores['word_count'] = min(word_count_score, 15)
    
    # Score based on lack of common issues (10 points)
    issues_score = 10
    common_issues = analysis.get('common_resume_issues', [])
    
    # Deduct 2 points per issue, up to 10 points
    issues_score -= min(len(common_issues) * 2, 10)
    
    scores['issues'] = max(issues_score, 0)
    
    # Calculate overall score (out of 100)
    scores['overall'] = (
        scores['sections'] +
        scores['keywords'] +
        scores['action_verbs'] +
        scores['word_count'] +
        scores['issues']
    )
    
    # Determine score grade
    if scores['overall'] >= 90:
        scores['grade'] = 'A'
    elif scores['overall'] >= 80:
        scores['grade'] = 'B'
    elif scores['overall'] >= 70:
        scores['grade'] = 'C'
    elif scores['overall'] >= 60:
        scores['grade'] = 'D'
    else:
        scores['grade'] = 'F'
    
    return scores

def generate_suggestions(resume_data, analysis, scores, job_description):
    """
    Generate improvement suggestions based on analysis
    
    Args:
        resume_data (dict): Parsed resume data
        analysis (dict): Analysis results
        scores (dict): Resume scores
        job_description (str): Job description text
        
    Returns:
        dict: Improvement suggestions
    """
    suggestions = {
        'high_priority': [],
        'medium_priority': [],
        'low_priority': []
    }
    
    # Suggestions based on missing sections
    sections_analysis = analysis.get('sections_analysis', {})
    
    for section in sections_analysis.get('missing_essential', []):
        formatted_section = section.replace('_', ' ').title()
        suggestions['high_priority'].append(f"Add a {formatted_section} section to your resume")
    
    for section in sections_analysis.get('missing_recommended', []):
        formatted_section = section.replace('_', ' ').title()
        suggestions['medium_priority'].append(f"Consider adding a {formatted_section} section to strengthen your resume")
    
    # Suggestions based on keyword matching
    keyword_match = analysis.get('keyword_match', {})
    
    if keyword_match.get('assessment') == 'poor' or keyword_match.get('assessment') == 'fair':
        missing_keywords = keyword_match.get('missing_keywords', [])
        if missing_keywords:
            if len(missing_keywords) <= 5:
                suggestions['high_priority'].append(f"Add these missing keywords from the job description: {', '.join(missing_keywords)}")
            else:
                top_keywords = missing_keywords[:5]
                suggestions['high_priority'].append(f"Add these important keywords from the job description: {', '.join(top_keywords)} and others")
    
    # Suggestions based on action verbs
    action_verbs = analysis.get('action_verbs', {})
    
    if action_verbs.get('assessment') == 'needs_improvement':
        suggestions['medium_priority'].append("Use more action verbs in your experience descriptions (e.g., Achieved, Improved, Developed, Implemented, Led)")
    
    # Suggestions based on word count
    word_count = analysis.get('word_count', {})
    
    if word_count.get('assessment', {}).get('total') == 'too_short':
        suggestions['medium_priority'].append("Your resume is too short. Add more detailed information about your experience, skills, and achievements")
    
    if word_count.get('assessment', {}).get('total') == 'too_long':
        suggestions['medium_priority'].append("Your resume is quite long. Consider condensing it to be more concise and focused")
    
    if word_count.get('assessment', {}).get('summary') == 'too_short':
        suggestions['low_priority'].append("Expand your professional summary to better highlight your qualifications")
    
    if word_count.get('assessment', {}).get('summary') == 'too_long':
        suggestions['low_priority'].append("Shorten your professional summary to be more concise and impactful")
    
    # Suggestions based on common issues
    common_issues = analysis.get('common_resume_issues', [])
    
    for issue in common_issues:
        if "Missing email" in issue or "Missing phone" in issue:
            suggestions['high_priority'].append("Add your contact information (email and phone number)")
        elif "Weak experience descriptions" in issue:
            suggestions['high_priority'].append("Strengthen your experience descriptions by adding specific achievements and using action verbs")
        elif "Inconsistent date formats" in issue:
            suggestions['low_priority'].append("Use consistent date formats throughout your resume")
        elif "Potential formatting issues" in issue:
            suggestions['medium_priority'].append("Fix formatting issues to improve readability")
    
    # General suggestions based on overall score
    if scores.get('overall', 0) < 70:
        suggestions['high_priority'].append("Consider a complete resume overhaul to better highlight your qualifications")
    elif scores.get('overall', 0) < 80:
        suggestions['medium_priority'].append("Make several key improvements to strengthen your resume's impact")
    
    return suggestions
