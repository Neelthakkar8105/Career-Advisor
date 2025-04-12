from django.contrib import admin
from .models import Profile, Education, WorkExperience, Skill

admin.site.register(Profile)
admin.site.register(Education)
admin.site.register(WorkExperience)
admin.site.register(Skill)
