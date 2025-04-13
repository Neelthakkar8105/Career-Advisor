from django.contrib import admin
from .models import (
    SkillsAssessment, 
    CareerPath, 
    JobMarketInsight,
    ResumeAnalysis,
    InterviewPrep
)

admin.site.register(SkillsAssessment)
admin.site.register(CareerPath)
admin.site.register(JobMarketInsight)
admin.site.register(ResumeAnalysis)
admin.site.register(InterviewPrep)
# career/admin.py
from django.contrib import admin
from .models import QuizQuestion

admin.site.register(QuizQuestion)

