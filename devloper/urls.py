from django.urls import path
from . import views

urlpatterns = [
    path('SignUp/',views.register,name='register'),
    path('LogIn/',views.login,name='register'),
    path('languages/save/', views.save_languages, name='save_languages'),
    path('developer/add/', views.add_developer, name='add-developer'),
    path('developer/update/', views.update_developer, name='update-developer'),
    path('developer/delete/', views.delete_developer, name='delete-developer'),
    path('resumes/', views.create_resume_from_parser),
    path('update-fcm-token/', views.update_fcm_token),
    path('education/', views.education_list_create, name='education_list_create'),
    path('experience/', views.experience_list_create, name='experience_list_create'),
     #
]
    # path('apply/<int:opportunity_id>/', views.apply_for_opportunity, name='apply-for-opportunity'),


    
