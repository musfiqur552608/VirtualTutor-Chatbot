from unicodedata import name
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='index'),
    path('chatbot', views.chatbot, name='chatbot'),
]