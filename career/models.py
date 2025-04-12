from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class SkillsAssessment(models.Model):
    """Model to store user's skills assessment results"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(default=timezone.now)
    technical_skills = models.JSONField()  # Store technical skills assessment
    soft_skills = models.JSONField()  # Store soft skills assessment
    interests = models.JSONField()  # Store career interests
    strengths = models.JSONField()  # Store identified strengths
    areas_to_improve = models.JSONField()  # Store areas for improvement

    def __str__(self):
        return f"Skills Assessment for {self.user.username} on {self.completed_at.strftime('%Y-%m-%d')}"


class CareerPath(models.Model):
    """Model to store recommended career paths for users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    primary_path = models.CharField(max_length=100)  # Primary career recommendation
    alternative_paths = models.JSONField()  # Alternative career paths as JSON
    required_skills = models.JSONField()  # Skills needed for recommended path
    growth_potential = models.TextField()  # Description of growth potential
    recommended_steps = models.JSONField()  # Recommended steps to pursue this path

    def __str__(self):
        return f"{self.primary_path} for {self.user.username}"


class JobMarketInsight(models.Model):
    """Model to store job market insights"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    generated_at = models.DateTimeField(default=timezone.now)
    industry = models.CharField(max_length=100)
    demand_score = models.FloatField()  # 0-10 score of demand
    salary_range = models.JSONField()  # JSON with min, max, average
    top_locations = models.JSONField()  # Top locations hiring
    trending_skills = models.JSONField()  # Skills in demand
    job_outlook = models.TextField()  # General outlook for the industry

    def __str__(self):
        return f"Job Market Insight for {self.industry}"


class ResumeAnalysis(models.Model):
    """Model to store resume analysis results"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    analyzed_at = models.DateTimeField(default=timezone.now)
    strength_score = models.FloatField()  # Overall resume strength (0-10)
    weaknesses = models.JSONField()  # Identified weaknesses
    suggestions = models.JSONField()  # Suggestions for improvement
    keyword_analysis = models.JSONField()  # Analysis of industry keywords
    improvement_plan = models.TextField()  # Plan for improving resume

    def __str__(self):
        return f"Resume Analysis for {self.user.username}"


class InterviewPrep(models.Model):
    """Model to store interview preparation data"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    job_title = models.CharField(max_length=100)
    common_questions = models.JSONField()  # Common interview questions
    suggested_answers = models.JSONField()  # Suggested answers based on profile
    preparation_tips = models.TextField()  # General interview preparation tips
    company_research = models.TextField(blank=True)  # Company-specific tips if provided

    def __str__(self):
        return f"Interview Prep for {self.job_title} - {self.user.username}"
