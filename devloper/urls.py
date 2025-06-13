from django.urls import path
from . import views

urlpatterns = [
    # path('SignUp/',views.register,name='register'),
    path('LogIn/',views.login,name='register'),
    path('languages/save/', views.save_languages, name='save_languages'),
]
    # path('apply/<int:opportunity_id>/', views.apply_for_opportunity, name='apply-for-opportunity'),


    
