from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_page, name='chat_page'),     # this handles /chat/
    path("api/chat/", views.chat_api, name="chat_api"),
]
