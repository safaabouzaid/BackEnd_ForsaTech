from django.urls import path
from . import views

urlpatterns = [
    path('recommend-job/', views.recommend_opportunities_view, name='recommend_opportunities_view'),
    path('recommend-user/', views.recommend_users_view, name='recommend_users_view'),
]