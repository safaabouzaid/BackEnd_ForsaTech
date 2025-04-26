from django.urls import path
from . import views

urlpatterns = [
    path('SignUp/',views.register,name='register'),
    path('LogIn/',views.login,name='login'),
    path('complaints/', views.add_complaint, name='add_complaint'),
    
]