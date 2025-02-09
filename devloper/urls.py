from django.urls import path
from . import views

urlpatterns = [
    path('signUp/',views.register,name='register'),
    path('signIn/',views.login,name='register'),
    
]