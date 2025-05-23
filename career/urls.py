from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('skills-assessment/', views.skills_assessment, name='skills_assessment'),
    path('resume-analysis/', views.resume_analysis, name='resume_analysis'),
    path('interview-prep/', views.interview_prep, name='interview_prep'),
    path('career-paths/', views.career_paths, name='career_paths'),
    path('network-analysis/', views.network_analysis, name='network_analysis'),
    path('trending-jobs/', views.trending_jobs, name='trending_jobs'),
    path('skill-based-recommendation/', views.skill_based_recommendation, name='skill_based_recommendation'),
    path('quiz/', views.select_subject, name='select_subject'),
    path('quiz/start/<str:subject>/', views.start_quiz, name='start_quiz'),
    path('quiz/submit/<str:subject>/', views.submit_quiz, name='submit_quiz'),
]
