import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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
    InterviewPrepForm
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


@login_required
def resume_analysis(request):
    """Handle resume analysis and improvement suggestions"""
    # Check if user has already had a resume analysis
    try:
        existing_analysis = ResumeAnalysis.objects.filter(user=request.user).latest('analyzed_at')
    except ResumeAnalysis.DoesNotExist:
        existing_analysis = None
    
    if request.method == 'POST':
        form = ResumeAnalysisForm(request.POST)
        if form.is_valid():
            resume_text = form.cleaned_data['resume_text'] or request.user.profile.resume
            job_title = form.cleaned_data['job_title']
            
            # Analyze the resume for the specific job title
            analysis_results = analyze_resume(resume_text, job_title)
            
            # Save the analysis results
            analysis = ResumeAnalysis(
                user=request.user,
                strength_score=analysis_results['strength_score'],
                weaknesses=analysis_results['weaknesses'],
                suggestions=analysis_results['suggestions'],
                keyword_analysis=analysis_results['keyword_analysis'],
                improvement_plan=analysis_results['improvement_plan']
            )
            analysis.save()
            
            # Update the user's resume in their profile if provided
            if form.cleaned_data['resume_text']:
                request.user.profile.resume = form.cleaned_data['resume_text']
                request.user.profile.save()
            
            messages.success(request, 'Resume analysis completed successfully!')
            return redirect('resume_analysis')
    else:
        # Pre-populate form with user's existing resume if available
        initial_data = {}
        if request.user.profile.resume:
            initial_data['resume_text'] = request.user.profile.resume
        
        # If user has a desired position, use that as default job title
        if request.user.profile.desired_position:
            initial_data['job_title'] = request.user.profile.desired_position
            
        form = ResumeAnalysisForm(initial=initial_data)
    
    context = {
        'form': form,
        'analysis': existing_analysis
    }
    return render(request, 'career/resume_analysis.html', context)


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
    """Display trending jobs and their insights"""
    # Load job market data
    job_market_data = load_job_market_data()
    
    # Sort jobs by demand score to get trending jobs
    trending_jobs = sorted(job_market_data, key=lambda x: x['demand_score'], reverse=True)
    
    context = {
        'trending_jobs': trending_jobs[:5],  # Top 5 trending jobs
    }
    return render(request, 'career/trending_jobs.html', context)

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
