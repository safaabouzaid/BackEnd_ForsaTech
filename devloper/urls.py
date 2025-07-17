from django.urls import path
from . import views

urlpatterns = [
    path('SignUp/',views.register,name='register'),
    path('LogIn/',views.login,name='register'),
  #  path('languages/save/', views.save_languages, name='save_languages'),
    path('developer/get/', views.get_developer, name='get-developer'),
    path('developer/update/', views.update_developer, name='update-developer'),
    path('resumes/', views.create_resume_from_parser),
    path('update-fcm-token/', views.update_fcm_token),
    path('education/', views.education_list_create, name='education_list_create'),
    path('experience/', views.experience_list_create, name='experience_list_create'),
    path("get-latest-resume/", views.LatestResumeAPIView.as_view()),
    path('languages/', views.language_list_create, name='language-list-create'),
    path('experiences/', views.experience_list_create, name='experience-list-create'),
  


    path('complaints/', views.submit_complaint, name='submit_complaint'),

]
    # path('apply/<int:opportunity_id>/', views.apply_for_opportunity, name='apply-for-opportunity'),


    
