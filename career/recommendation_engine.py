import json
import os
import random
from django.conf import settings
from .models import CareerPath, JobMarketInsight, ResumeAnalysis

# Load career data from JSON file
def load_career_data():
    """Load career data from JSON file"""
    data_file = os.path.join(os.path.dirname(__file__), 'career_data.json')
    with open(data_file, 'r') as f:
        return json.load(f)

# Load job market data from JSON file
def load_job_market_data():
    """Load job market data from JSON file"""
    data_file = os.path.join(os.path.dirname(__file__), 'job_market_data.json')
    with open(data_file, 'r') as f:
        return json.load(f)

def analyze_resume(resume_text, job_title):
    """
    Analyze resume for a specific job title
    Returns: dict with analysis results
    """
    # Initialize results dictionary
    results = {
        'strength_score': 0.0,
        'weaknesses': [],
        'suggestions': [],
        'keyword_analysis': {},
        'improvement_plan': ''
    }
    
    # Load career data for keyword matching
    career_data = load_career_data()
    
    # Find the job in our career data
    job_data = None
    for career in career_data:
        for job in career['jobs']:
            if job['title'].lower() == job_title.lower():
                job_data = job
                break
        if job_data:
            break
    
    # If job not found, use generic analysis
    if not job_data:
        # Generic analysis
        results['strength_score'] = 6.5  # Average score
        results['weaknesses'] = [
            "Missing specific keywords for this job title",
            "Resume may not be tailored to this position",
            "Work experience section might need more detail"
        ]
        results['suggestions'] = [
            "Research more about this job title and include relevant keywords",
            "Quantify your achievements with metrics when possible",
            "Include a strong summary section at the top"
        ]
        results['keyword_analysis'] = {
            "present": [],
            "missing": ["specific", "relevant", "keywords", "for", "this", "position"]
        }
        results['improvement_plan'] = (
            "1. Research the job title more thoroughly\n"
            "2. Find 5-10 key skills mentioned in job descriptions\n"
            "3. Incorporate those skills in your resume\n"
            "4. Add quantifiable achievements\n"
            "5. Create a targeted summary section"
        )
        return results
    
    # Perform keyword analysis
    keywords = job_data.get('keywords', [])
    skills = job_data.get('skills', [])
    
    # Check which keywords are present in the resume
    present_keywords = []
    missing_keywords = []
    
    for keyword in keywords + skills:
        if keyword.lower() in resume_text.lower():
            present_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)
    
    # Calculate strength score based on keywords presence
    keyword_score = len(present_keywords) / (len(keywords) + len(skills)) * 10
    
    # Analyze resume sections (simplified)
    has_summary = "summary" in resume_text.lower() or "objective" in resume_text.lower()
    has_education = "education" in resume_text.lower() or "degree" in resume_text.lower()
    has_experience = "experience" in resume_text.lower() or "work" in resume_text.lower()
    has_skills = "skills" in resume_text.lower() or "expertise" in resume_text.lower()
    
    section_score = sum([has_summary, has_education, has_experience, has_skills]) / 4 * 10
    
    # Calculate final strength score (weighted average)
    results['strength_score'] = round((keyword_score * 0.7 + section_score * 0.3), 1)
    
    # Generate weaknesses
    if not has_summary:
        results['weaknesses'].append("Missing a strong summary/objective section")
    if not has_skills:
        results['weaknesses'].append("Skills section not clearly defined")
    if len(missing_keywords) > len(keywords) / 2:
        results['weaknesses'].append("Missing important keywords for this position")
    if results['strength_score'] < 5:
        results['weaknesses'].append("Resume needs significant tailoring for this position")
    
    # Generate suggestions
    results['suggestions'].append(f"Add these missing keywords: {', '.join(missing_keywords[:5])}")
    if not has_summary:
        results['suggestions'].append("Add a concise summary highlighting your value proposition")
    results['suggestions'].append("Quantify your achievements with measurable results")
    results['suggestions'].append("Tailor your experience to highlight relevant accomplishments")
    
    # Keyword analysis
    results['keyword_analysis'] = {
        "present": present_keywords,
        "missing": missing_keywords
    }
    
    # Generate improvement plan
    results['improvement_plan'] = (
        f"1. Add these key missing terms: {', '.join(missing_keywords[:5])}\n"
        f"2. {'Add a summary section at the top of your resume' if not has_summary else 'Enhance your summary section with more targeted language'}\n"
        f"3. {'Create a clear skills section' if not has_skills else 'Expand your skills section to include more technical abilities'}\n"
        "4. Quantify at least 3 achievements with specific metrics\n"
        "5. Remove irrelevant experience or reframe it to highlight transferable skills"
    )
    
    return results


def generate_career_paths(user, assessment):
    """
    Generate career path recommendations based on skills assessment
    Returns: CareerPath object
    """
    # Load career data
    career_data = load_career_data()
    
    # Calculate scores for each career path based on assessment
    career_scores = {}
    
    for career in career_data:
        score = 0
        
        # Match technical skills
        for skill, required_level in career['technical_skills'].items():
            if skill in assessment.technical_skills:
                user_level = assessment.technical_skills[skill]
                # Add points based on how close the user's skill level is to required
                score += max(0, 5 - abs(required_level - user_level)) * 2
        
        # Match soft skills
        for skill, required_level in career['soft_skills'].items():
            if skill in assessment.soft_skills:
                user_level = assessment.soft_skills[skill]
                # Add points based on how close the user's skill level is to required
                score += max(0, 5 - abs(required_level - user_level)) * 1.5
        
        # Match interests
        for interest, importance in career['interests'].items():
            interest_key = f"interest_{interest}" if interest in ["technology", "business", "arts", "sciences", "helping_others"] else interest
            if interest_key in assessment.interests:
                user_interest = assessment.interests[interest_key]
                # Add points based on interest alignment
                score += user_interest * importance
        
        career_scores[career['path']] = score
    
    # Sort careers by score
    sorted_careers = sorted(career_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Get primary career path (highest score)
    primary_path = sorted_careers[0][0]
    
    # Get alternative career paths (next 3 highest scores)
    alternative_paths = [career[0] for career in sorted_careers[1:4]]
    
    # Get primary career data
    primary_career_data = next((c for c in career_data if c['path'] == primary_path), None)
    
    # Extract required skills for primary path
    required_skills = []
    if primary_career_data:
        for skill, level in primary_career_data['technical_skills'].items():
            if level >= 3:  # Only include skills with importance of 3 or higher
                required_skills.append(skill)
        for skill, level in primary_career_data['soft_skills'].items():
            if level >= 3:  # Only include skills with importance of 3 or higher
                required_skills.append(skill)
    
    # Generate growth potential description
    growth_potential = (
        f"The {primary_path} field has strong growth potential over the next 5-10 years. "
        f"With your skills in {', '.join(assessment.strengths.keys())}, you're well-positioned to advance. "
        f"To maximize growth, consider developing expertise in {', '.join(required_skills[:3])}."
    )
    
    # Generate recommended steps
    recommended_steps = [
        "Complete relevant certifications or training programs",
        f"Build portfolio showcasing your {', '.join(list(assessment.strengths.keys())[:2])} skills",
        "Connect with professionals in the field for mentorship",
        "Develop specific technical skills through hands-on projects",
        "Join industry associations and attend networking events"
    ]
    
    # Create and save the career path
    career_path = CareerPath(
        user=user,
        primary_path=primary_path,
        alternative_paths=alternative_paths,
        required_skills=required_skills,
        growth_potential=growth_potential,
        recommended_steps=recommended_steps
    )
    career_path.save()
    
    return career_path


def get_job_market_insights(user, career_path):
    """
    Get job market insights for a specific career path
    Returns: JobMarketInsight object
    """
    # Load job market data
    job_market_data = load_job_market_data()
    
    # Find data for the specific career path
    career_data = None
    for career in job_market_data:
        if career['career_path'].lower() == career_path.lower():
            career_data = career
            break
    
    # If no data found, use default data
    if not career_data:
        career_data = {
            'career_path': career_path,
            'demand_score': 7.5,
            'salary_range': {
                'min': 50000,
                'max': 100000,
                'average': 75000
            },
            'top_locations': [
                'San Francisco, CA',
                'New York, NY',
                'Austin, TX',
                'Seattle, WA',
                'Boston, MA'
            ],
            'trending_skills': [
                'Data Analysis',
                'Project Management',
                'Cloud Computing',
                'Communication',
                'Problem Solving'
            ],
            'job_outlook': (
                "This field is expected to grow at an above-average rate over the next decade. "
                "Increasing digital transformation across industries is creating steady demand "
                "for qualified professionals. Remote work opportunities are abundant."
            )
        }
    
    # Create and save job market insight
    job_insight = JobMarketInsight(
        user=user,
        industry=career_path,
        demand_score=career_data['demand_score'],
        salary_range=career_data['salary_range'],
        top_locations=career_data['top_locations'],
        trending_skills=career_data['trending_skills'],
        job_outlook=career_data['job_outlook']
    )
    job_insight.save()
    
    return job_insight


def generate_interview_questions(user, job_title, company_name=None):
    """
    Generate interview questions and preparation tips
    Returns: dict with interview preparation data
    """
    # Load career data to find job-specific questions
    career_data = load_career_data()
    
    # Find relevant career path for the job title
    relevant_career = None
    for career in career_data:
        for job in career.get('jobs', []):
            if job_title.lower() in job['title'].lower():
                relevant_career = career
                relevant_job = job
                break
        if relevant_career:
            break
    
    # General behavioral questions (always included)
    behavioral_questions = [
        "Tell me about yourself.",
        "Why are you interested in this position?",
        "What are your greatest strengths and weaknesses?",
        "Describe a challenging situation you faced at work and how you handled it.",
        "Where do you see yourself in five years?",
        "Why do you want to leave your current job?",
        "Describe your ideal work environment.",
        "How do you handle stress and pressure?",
        "Tell me about a time when you had to work as part of a team.",
        "How do you prioritize your work?"
    ]
    
    # Technical or job-specific questions based on career path
    technical_questions = []
    if relevant_career:
        # Get technical questions based on job skills
        for skill in relevant_job.get('skills', []):
            if skill.lower() == "programming":
                technical_questions.append("What programming languages are you proficient in?")
                technical_questions.append("Describe a complex coding project you completed.")
            elif skill.lower() == "project management":
                technical_questions.append("What project management methodologies are you familiar with?")
                technical_questions.append("How do you handle scope creep?")
            elif skill.lower() == "data analysis":
                technical_questions.append("What data analysis tools have you used?")
                technical_questions.append("Explain how you'd approach analyzing a large dataset.")
            elif skill.lower() == "design":
                technical_questions.append("What design software are you proficient in?")
                technical_questions.append("Walk me through your design process.")
            elif skill.lower() == "communication":
                technical_questions.append("How do you tailor your communication style to different audiences?")
            else:
                technical_questions.append(f"Tell me about your experience with {skill}.")
    
    # If we don't have enough technical questions, add generic ones
    generic_technical = [
        f"What specific skills do you believe are most important for a {job_title} role?",
        "How do you stay current with industry trends and developments?",
        "Describe a time when you had to learn a new skill quickly.",
        "What tools or software are you most experienced with?",
        "How do you approach problem-solving in your work?"
    ]
    
    while len(technical_questions) < 5:
        # Add a random question from generic list that's not already in technical_questions
        available = [q for q in generic_technical if q not in technical_questions]
        if not available:
            break
        technical_questions.append(random.choice(available))
    
    # Combine question types
    all_questions = behavioral_questions + technical_questions
    
    # Generate suggested answers based on user profile
    suggested_answers = {}
    
    # Get user profile data for personalized answers
    user_profile = user.profile
    user_skills = [skill.name for skill in user_profile.skills.all()]
    
    # Generate basic answer suggestions for common questions
    suggested_answers["Tell me about yourself."] = (
        f"As a {user_profile.current_position or 'professional'} with expertise in "
        f"{', '.join(user_skills[:3] if user_skills else ['your key skills'])}, I have developed "
        f"strong abilities in problem-solving and collaboration. "
        f"{'I am currently seeking opportunities in ' + user_profile.desired_position if user_profile.desired_position else 'I am looking for new challenges'} "
        f"where I can apply my skills and continue to grow professionally."
    )
    
    suggested_answers["What are your greatest strengths and weaknesses?"] = (
        f"My strengths include {', '.join(user_skills[:2] if user_skills else ['your top skills'])}. "
        f"For example, [include a specific achievement]. "
        f"As for weaknesses, I'm working on improving my {user_skills[-1] if user_skills else 'specific skill'} "
        f"by [describe specific action you're taking]."
    )
    
    # Preparation tips
    preparation_tips = (
        "Before the interview:\n"
        "1. Research the company thoroughly - review their website, recent news, and social media\n"
        "2. Practice your answers to common questions out loud\n"
        "3. Prepare specific examples that demonstrate your skills and achievements\n"
        "4. Research typical salary ranges for this position\n"
        "5. Prepare thoughtful questions to ask the interviewer\n\n"
        "During the interview:\n"
        "1. Make a strong first impression with professional attire and positive body language\n"
        "2. Use the STAR method (Situation, Task, Action, Result) when answering behavioral questions\n"
        "3. Be specific about your achievements, using numbers when possible\n"
        "4. Show enthusiasm for the role and company\n"
        "5. Listen carefully and ask clarifying questions if needed"
    )
    
    # Company research if company name provided
    company_research = ""
    if company_name:
        company_research = (
            f"Research points for {company_name}:\n"
            "1. Review the company's mission, vision, and values from their website\n"
            "2. Understand their products/services and target market\n"
            "3. Research recent news, press releases, and financial performance\n"
            "4. Look up the backgrounds of key executives on LinkedIn\n"
            "5. Check reviews on sites like Glassdoor for insights into company culture\n"
            "6. Explore their competitors and market position\n"
            "7. Prepare to explain why you're interested specifically in this company"
        )
    
    return {
        'common_questions': all_questions,
        'suggested_answers': suggested_answers,
        'preparation_tips': preparation_tips,
        'company_research': company_research
    }
