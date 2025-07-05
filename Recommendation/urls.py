from django.urls import path
from . import views

urlpatterns = [
    
    path('recommend-job/', views.recommend_opportunities_view, name='recommend_opportunities_view'),
    path('recommend-user/', views.recommend_users_view, name='recommend_users_view'),
    path('applicants/<int:opportunity_id>/', views.recommend_applicants_for_opportunity,name='recommend_applicants'),
    path('recommend-skills/', views.recommend_skills_view,name='recommend_skills_view'),
    path('update-embeddings/', views.update_embeddings),
    path('update-resumes-embeddings/', views.update_resumes_embeddings),


    ]

