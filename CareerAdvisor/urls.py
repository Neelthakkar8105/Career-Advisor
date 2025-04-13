"""
URL Configuration for CareerAdvisor project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('users/', include('users.urls')),
    path('career/', include('career.urls')),
    
    path("chat/", include("chatbot.urls")),
]
