import json
from docx import Document  # Add this import for handling .docx files
import spacy
nlp = spacy.load("en_core_web_sm")
from django.conf import settings
import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import (
    SkillsAssessment, 
    CareerPath, 
    JobMarketInsight,
    ResumeAnalysis,
    InterviewPrep
)
from .forms import (
    SkillsAssessmentForm,
    ResumeAnalysisForm,
    InterviewPrepForm,
    ResumeUploadForm  # Import ResumeUploadForm
)
from .recommendation_engine import (
    analyze_resume,
    generate_career_paths,
    get_job_market_insights,
    generate_interview_questions,
    load_job_market_data
)


@login_required
def dashboard(request):
    """Main dashboard view displaying career insights"""
    # Get recent assessment data for the user if available
    try:
        recent_assessment = SkillsAssessment.objects.filter(user=request.user).latest('completed_at')
    except SkillsAssessment.DoesNotExist:
        recent_assessment = None

    # Get career path recommendations if available
    try:
        career_paths = CareerPath.objects.filter(user=request.user).latest('created_at')
    except CareerPath.DoesNotExist:
        career_paths = None

    # Get job market insights if available
    job_insights = JobMarketInsight.objects.filter(user=request.user).order_by('-generated_at')[:3]

    # Get resume analysis if available
    try:
        resume_analysis = ResumeAnalysis.objects.filter(user=request.user).latest('analyzed_at')
    except ResumeAnalysis.DoesNotExist:
        resume_analysis = None

    context = {
        'recent_assessment': recent_assessment,
        'career_paths': career_paths,
        'job_insights': job_insights,
        'resume_analysis': resume_analysis,
        'profile_completion': calculate_profile_completion(request.user),
    }
    return render(request, 'career/dashboard.html', context)


def calculate_profile_completion(user):
    """Calculate profile completion percentage"""
    profile = user.profile
    
    # Define fields to check and their weights
    total_fields = 11  # Total number of fields we're checking
    completed_fields = 0
    
    # Check basic user data
    if user.first_name and user.last_name:
        completed_fields += 1
    if user.email:
        completed_fields += 1
    
    # Check profile fields
    if profile.bio:
        completed_fields += 1
    if profile.birth_date:
        completed_fields += 1
    if profile.location:
        completed_fields += 1
    if profile.current_position:
        completed_fields += 1
    if profile.desired_position:
        completed_fields += 1
    if profile.resume:
        completed_fields += 1
    
    # Check for social links
    if profile.linkedin_url or profile.github_url or profile.portfolio_url:
        completed_fields += 1
    
    # Check if user has added education
    if profile.education.exists():
        completed_fields += 1
    
    # Check if user has added work experience
    if profile.work_experience.exists():
        completed_fields += 1
    
    # Calculate percentage
    completion_percentage = int((completed_fields / total_fields) * 100)
    
    return completion_percentage


@login_required
def skills_assessment(request):
    """Handle the skills assessment quiz and results"""
    # Check if user has already completed an assessment
    existing_assessment = SkillsAssessment.objects.filter(user=request.user).order_by('-completed_at').first()
    
    if request.method == 'POST':
        form = SkillsAssessmentForm(request.POST)
        if form.is_valid():
            # Process the form data
            technical_skills = {
                'programming': int(form.cleaned_data['programming']),
                'data_analysis': int(form.cleaned_data['data_analysis']),
                'design': int(form.cleaned_data['design']),
                'writing': int(form.cleaned_data['writing']),
                'project_management': int(form.cleaned_data['project_management']),
            }
            
            soft_skills = {
                'communication': int(form.cleaned_data['communication']),
                'teamwork': int(form.cleaned_data['teamwork']),
                'leadership': int(form.cleaned_data['leadership']),
                'problem_solving': int(form.cleaned_data['problem_solving']),
                'adaptability': int(form.cleaned_data['adaptability']),
            }
            
            interests = {
                'technology': int(form.cleaned_data['interest_technology']),
                'business': int(form.cleaned_data['interest_business']),
                'arts': int(form.cleaned_data['interest_arts']),
                'sciences': int(form.cleaned_data['interest_sciences']),
                'helping_others': int(form.cleaned_data['interest_helping']),
            }
            
            # Calculate strengths and areas to improve
            strengths = {skill: score for skill, score in technical_skills.items() if score >= 4}
            strengths.update({skill: score for skill, score in soft_skills.items() if score >= 4})
            
            areas_to_improve = {skill: score for skill, score in technical_skills.items() if score <= 2}
            areas_to_improve.update({skill: score for skill, score in soft_skills.items() if score <= 2})
            
            # Save the assessment
            assessment = SkillsAssessment(
                user=request.user,
                technical_skills=technical_skills,
                soft_skills=soft_skills,
                interests=interests,
                strengths=strengths,
                areas_to_improve=areas_to_improve
            )
            assessment.save()
            
            # Generate career path recommendations based on assessment
            generate_career_paths(request.user, assessment)
            
            messages.success(request, 'Skills assessment completed successfully!')
            return redirect('dashboard')
    else:
        # If there's an existing assessment, initialize the form with those values
        if existing_assessment:
            initial_data = {}
            
            # Map stored values back to form fields
            for skill, value in existing_assessment.technical_skills.items():
                initial_data[skill] = value
                
            for skill, value in existing_assessment.soft_skills.items():
                initial_data[skill] = value
                
            for area, value in existing_assessment.interests.items():
                initial_data[f'interest_{area}'] = value
                
            form = SkillsAssessmentForm(initial=initial_data)
        else:
            form = SkillsAssessmentForm()
    
    context = {
        'form': form,
        'existing_assessment': existing_assessment
    }
    return render(request, 'career/skills_assessment.html', context)


def analyze_resume(resume_text):
    """
    Analyze the resume for strengths, weaknesses, and general tips using NLP.
    """
    tips = []
    strengths = []
    weaknesses = []
    doc = nlp(resume_text)  # Process the resume text with spaCy

    # Debugging log to ensure resume_text is valid
    print(f"Debug: Inside analyze_resume, type of resume_text: {type(resume_text)}, content: {resume_text[:100]}")

    # Extract skills and technologies mentioned in the resume
    skill_keywords = ['python', 'java', 'sql', 'aws', 'javascript', 'react', 'angular', 'django', 'flask']
    found_skills = [skill for skill in skill_keywords if skill in resume_text.lower()]
    if found_skills:
        strengths.extend([skill.capitalize() for skill in found_skills])
        for skill in found_skills:
            tips.append(f"Your {skill.upper()} skills are valuable. Consider enhancing them further with advanced projects or certifications.")
    else:
        weaknesses.append("No technical skills detected.")
        tips.append("Consider adding technical skills relevant to your field, such as programming languages or tools.")

    # Analyze work experience
    experience_phrases = ['years of experience', 'worked at', 'managed', 'led', 'developed']
    if any(phrase in resume_text.lower() for phrase in experience_phrases):
        strengths.append("Work experience")
        tips.append("Your work experience is noted. Highlighting specific achievements with metrics can make your resume stand out.")
    else:
        weaknesses.append("No work experience mentioned.")
        tips.append("Consider adding details about your work experience or internships to showcase your practical skills.")

    # Analyze education background
    education_keywords = ['bachelor', 'master', 'phd', 'degree', 'certification']
    if any(keyword in resume_text.lower() for keyword in education_keywords):
        strengths.append("Educational qualifications")
        tips.append("Your educational background is noted. Highlighting relevant projects or honors can further boost your resume.")
    else:
        weaknesses.append("No educational details provided.")
        tips.append("Consider including your educational background or certifications to provide a fuller picture of your qualifications.")

    # Extract soft skills
    soft_skill_keywords = ['communication', 'teamwork', 'leadership', 'problem-solving', 'critical thinking']
    found_soft_skills = [skill for skill in soft_skill_keywords if skill in resume_text.lower()]
    if found_soft_skills:
        strengths.extend([skill.capitalize() for skill in found_soft_skills])
        tips.append("Your soft skills are valuable. Provide examples where these skills have contributed to your success.")
    else:
        weaknesses.append("No soft skills mentioned.")
        tips.append("Consider mentioning soft skills to give a well-rounded view of your abilities.")

    # Use NLP to identify named entities (e.g., organizations, roles)
    for ent in doc.ents:
        if ent.label_ == "ORG":
            strengths.append(f"Experience with {ent.text}")
        elif ent.label_ in ["JOB_TITLE", "PERSON"]:
            strengths.append(f"Role: {ent.text}")

    return {
        'tips': tips,
        'strengths': list(set(strengths)),  # Remove duplicates
        'weaknesses': list(set(weaknesses)),  # Remove duplicates
    }


@login_required
def resume_analysis(request):
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume_file = request.FILES.get('resume_file')  # Safely retrieve the uploaded file
            if not resume_file:
                messages.error(request, 'No file uploaded. Please upload a valid resume file.')
                return redirect('resume_analysis')

            try:
                resume_text = extract_text_from_file(resume_file)  # Extract text from the uploaded file
                if not isinstance(resume_text, str) or not resume_text.strip():
                    raise ValueError("Extracted resume text is empty or invalid.")
            except Exception as e:
                messages.error(request, f"Error processing the file: {str(e)}")
                return redirect('resume_analysis')

            # Analyze the resume for strengths, weaknesses, and tips
            try:
                print(f"Debug: Type of resume_text: {type(resume_text)}")  # Debugging log
                analysis_results = analyze_resume(resume_text)  # Pass the extracted text to analyze_resume
                print(f"Debug: Analysis results: {analysis_results}")  # Debugging log
            except Exception as e:
                messages.error(request, f"Error analyzing the resume: {str(e)}")
                return redirect('resume_analysis')

            context = {
                'tips_title': "Your Personalized Resume Analysis",
                'tips': analysis_results.get('tips', []),
                'strengths': analysis_results.get('strengths', []),
                'weaknesses': analysis_results.get('weaknesses', []),
            }
            return render(request, 'resume_tips/tips_results.html', context)
        else:
            messages.error(request, 'Invalid form submission. Please try again.')
    else:
        form = ResumeUploadForm()
    return render(request, 'resume_tips/upload_resume.html', {'form': form})


def extract_text_from_file(file):
    """Extract text from an uploaded file (e.g., .docx or .pdf)."""
    # Example for .docx files
    document = Document(file)
    return '\n'.join([paragraph.text for paragraph in document.paragraphs])


@login_required
def interview_prep(request):
    """Handle interview preparation and question generation"""
    # Get user's previous interview prep sessions
    previous_sessions = InterviewPrep.objects.filter(user=request.user).order_by('-created_at')
    
    if request.method == 'POST':
        form = InterviewPrepForm(request.POST)
        if form.is_valid():
            job_title = form.cleaned_data['job_title']
            company_name = form.cleaned_data['company_name']
            
            # Generate interview questions and suggestions
            interview_data = generate_interview_questions(
                request.user, 
                job_title, 
                company_name
            )
            
            # Save the interview prep data
            interview_prep = InterviewPrep(
                user=request.user,
                job_title=job_title,
                common_questions=interview_data['common_questions'],
                suggested_answers=interview_data['suggested_answers'],
                preparation_tips=interview_data['preparation_tips'],
                company_research=interview_data['company_research'] if company_name else ''
            )
            interview_prep.save()
            
            messages.success(request, 'Interview preparation guide generated successfully!')
            return redirect('interview_prep')
    else:
        # Pre-populate form with user's desired position if available
        initial_data = {}
        if request.user.profile.desired_position:
            initial_data['job_title'] = request.user.profile.desired_position
            
        form = InterviewPrepForm(initial=initial_data)
    
    # If there's a session_id in the GET parameters, show that specific session
    session_id = request.GET.get('session_id')
    if session_id:
        try:
            current_session = InterviewPrep.objects.get(id=session_id, user=request.user)
        except InterviewPrep.DoesNotExist:
            current_session = previous_sessions.first() if previous_sessions.exists() else None
    else:
        current_session = previous_sessions.first() if previous_sessions.exists() else None
    
    context = {
        'form': form,
        'current_session': current_session,
        'previous_sessions': previous_sessions
    }
    return render(request, 'career/interview_prep.html', context)


@login_required
def career_paths(request):
    """Display career path recommendations"""
    # Get user's career path recommendations
    try:
        career_path = CareerPath.objects.filter(user=request.user).latest('created_at')
    except CareerPath.DoesNotExist:
        career_path = None
    
    # Check if the user has completed a skills assessment
    has_assessment = SkillsAssessment.objects.filter(user=request.user).exists()
    
    if not has_assessment:
        messages.warning(request, 'Please complete a skills assessment first to receive career path recommendations.')
        return redirect('skills_assessment')
    
    # If no career path exists but user has assessment, generate one
    if not career_path and has_assessment:
        assessment = SkillsAssessment.objects.filter(user=request.user).latest('completed_at')
        career_path = generate_career_paths(request.user, assessment)
    
    # Get job market insights for the primary career path
    if career_path:
        try:
            job_market = JobMarketInsight.objects.get(
                user=request.user,
                industry=career_path.primary_path
            )
        except JobMarketInsight.DoesNotExist:
            # Generate job market insights if none exists
            job_market = get_job_market_insights(request.user, career_path.primary_path)
    else:
        job_market = None
    
    context = {
        'career_path': career_path,
        'job_market': job_market
    }
    return render(request, 'career/career_paths.html', context)


@login_required
def trending_jobs(request):
    jobs = []
    error = None

    if request.method == 'POST':
        keyword = request.POST.get('keyword', '')
        location = request.POST.get('location', '')

        # Replace 'in' with 'us' if you're not getting results
        country_code = 'in'  # or 'us', 'gb', etc.
        url = f'https://api.adzuna.com/v1/api/jobs/{country_code}/search/1'
        params = {
            'app_id': '5d1b0e47',  # Replace with your App ID
            'app_key': '72066aeb38655102d452923521a16046	',  # Replace with your App Key
            'results_per_page': 100,
            'what': keyword,
            'where': location,
        }

        try:
            response = requests.get(url, params=params)
            print("Request URL:", response.url)
            print("Status Code:", response.status_code)

            if response.status_code == 200:
                data = response.json()
                jobs = data.get('results', [])
                if not jobs:
                    error = "No jobs found for the given query."
            else:
                # Show full error message from Adzuna
                print("Error Response:", response.text)
                error = f"Error fetching data: {response.status_code} - {response.reason}"

        except Exception as e:
            print("Exception occurred:", e)
            error = f"An error occurred: {str(e)}"

    return render(request, 'career/trending_jobs.html', {'jobs': jobs, 'error': error})

@login_required
def network_analysis(request):
    """Display network analysis visualization"""
    # Get user's career path for network visualization context
    try:
        career_path = CareerPath.objects.filter(user=request.user).latest('created_at')
    except CareerPath.DoesNotExist:
        career_path = None
    
    # Sample node structure for network visualization
    if career_path:
        # Build network nodes based on career path and skills
        network_data = {
            'nodes': [],
            'links': []
        }
        
        # Add primary path as central node
        network_data['nodes'].append({
            'id': 'primary',
            'name': career_path.primary_path,
            'group': 1,
            'size': 20
        })
        
        # Add required skills as connected nodes
        for idx, skill in enumerate(career_path.required_skills):
            node_id = f'skill_{idx}'
            network_data['nodes'].append({
                'id': node_id,
                'name': skill,
                'group': 2,
                'size': 10
            })
            network_data['links'].append({
                'source': 'primary',
                'target': node_id,
                'value': 5
            })
        
        # Add alternative paths as connected nodes
        for idx, path in enumerate(career_path.alternative_paths):
            node_id = f'alt_{idx}'
            network_data['nodes'].append({
                'id': node_id,
                'name': path,
                'group': 3,
                'size': 15
            })
            network_data['links'].append({
                'source': 'primary',
                'target': node_id,
                'value': 3
            })
    else:
        network_data = None
    
    context = {
        'network_data': json.dumps(network_data) if network_data else None,
        'career_path': career_path
    }
    return render(request, 'career/network_analysis.html', context)


# recommendations/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Example career data for recommendation
CAREER_DATA = [
    {"career": "Data Scientist", "skills": "machine learning, data analysis, python, statistics"},
    {"career": "Web Developer", "skills": "html, css, javascript, react, frontend development"},
    {"career": "Backend Developer", "skills": "python, django, databases, api development"},
    {"career": "AI Engineer", "skills": "deep learning, neural networks, python, nlp"},
    {"career": "Cybersecurity Analyst", "skills": "network security, penetration testing, cryptography, risk assessment"},
    {"career": "Cloud Engineer", "skills": "aws, azure, cloud computing, devops, kubernetes"},
    {"career": "Mobile App Developer", "skills": "android, ios, flutter, react native, mobile development"},
    {"career": "Game Developer", "skills": "unity, unreal engine, c++, game design, 3d modeling"},
    {"career": "Digital Marketing Specialist", "skills": "seo, social media marketing, content creation, google ads, analytics"},
    {"career": "Product Manager", "skills": "product strategy, agile, user research, roadmaps, stakeholder management"},
    {"career": "UI/UX Designer", "skills": "user interface design, user experience, wireframing, prototyping, figma"},
    {"career": "DevOps Engineer", "skills": "ci/cd, docker, kubernetes, linux, automation"},
    {"career": "Blockchain Developer", "skills": "blockchain, solidity, smart contracts, ethereum, cryptography"},
    {"career": "Machine Learning Engineer", "skills": "tensorflow, pytorch, machine learning, data preprocessing, algorithms"},
    {"career": "Data Engineer", "skills": "big data, hadoop, spark, sql, data pipelines"},
    {"career": "Business Analyst", "skills": "business analysis, requirements gathering, process improvement, data visualization"},
    {"career": "Technical Writer", "skills": "technical documentation, writing, editing, api documentation, communication"},
    {"career": "Network Engineer", "skills": "networking, cisco, routing, switching, network troubleshooting"},
    {"career": "IT Support Specialist", "skills": "technical support, troubleshooting, hardware, software, customer service"},
    {"career": "E-commerce Specialist", "skills": "e-commerce platforms, online sales, digital marketing, inventory management"},
    {"career": "Robotics Engineer", "skills": "robotics, automation, c++, embedded systems, mechanical design"},
    {"career": "Healthcare Data Analyst", "skills": "healthcare analytics, data visualization, sql, python, statistics"},
    {"career": "Environmental Scientist", "skills": "environmental science, data analysis, gis, sustainability, research"},
    {"career": "Financial Analyst", "skills": "financial modeling, excel, data analysis, accounting, investment research"},
    {"career": "Content Creator", "skills": "video editing, social media, content strategy, storytelling, graphic design"},
    {"career": "Salesforce Developer", "skills": "salesforce, crm, apex, lightning, integration"},
    {"career": "AI Researcher", "skills": "artificial intelligence, deep learning, research, algorithms, python"},
    {"career": "Operations Manager", "skills": "operations management, process optimization, leadership, logistics, planning"},
    {"career": "HR Specialist", "skills": "recruitment, employee relations, hr policies, payroll, training"},
]

def recommendations_view(request):
    # Example context data
    context = {
        'title': 'Recommendations',
        'recommendations': [],  # Add dynamic recommendations here
    }
    return render(request, 'career/career_paths.html', context)

def career_paths(request):
    """
    View to generate and display recommendations.
    """
    context = {
        'title': 'Recommendations',
        'recommendations': ['Example Recommendation 1', 'Example Recommendation 2'],  # Replace with dynamic logic
    }
    return render(request, 'career/career_paths.html', context)

@csrf_exempt
def skill_based_recommendation(request):
    """
    View to generate recommendations based on user-entered skills.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_skills = data.get("skills", "")

            if not user_skills:
                return JsonResponse({"error": "No skills provided."}, status=400)

            # Use TF-IDF and cosine similarity for skill matching
            vectorizer = TfidfVectorizer()
            all_skills = [career["skills"] for career in CAREER_DATA] + [user_skills]
            tfidf_matrix = vectorizer.fit_transform(all_skills)
            similarity_scores = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()

            # Get top recommendations (increase the number of top indices)
            top_indices = similarity_scores.argsort()[-6:][::-1]  # Adjust the number here (e.g., 5 for more recommendations)
            recommendations = [CAREER_DATA[i]["career"] for i in top_indices]

            return JsonResponse({"recommendations": recommendations})
        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)

from django.shortcuts import render, redirect
from .models import QuizQuestion
import random

def select_subject(request):
    subjects = ['Python', 'Web Development', 'Soft Skills']
    return render(request, 'career/select_subject.html', {'subjects': subjects})

def start_quiz(request, subject):
    questions = list(QuizQuestion.objects.filter(subject=subject))
    random.shuffle(questions)
    selected_questions = questions[:5]  # Pick 5 random questions
    return render(request, 'career/quiz.html', {'questions': selected_questions, 'subject': subject})

def submit_quiz(request, subject):
    if request.method == 'POST':
        questions = QuizQuestion.objects.filter(subject=subject)
        score = 0
        total = 0
        feedback = []

        for i, question in enumerate(questions[:5], 1):
            user_answer = request.POST.get(f'q{i}')
            correct = question.correct_option
            if user_answer == correct:
                score += 1
            feedback.append({
                'question': question.question,
                'your_answer': user_answer,
                'correct_answer': correct,
                'is_correct': user_answer == correct,
            })
            total += 1

        return render(request, 'career/feedback.html', {
            'score': score,
            'total': total,
            'feedback': feedback,
            'subject': subject
        })
    return redirect('select_subject')
