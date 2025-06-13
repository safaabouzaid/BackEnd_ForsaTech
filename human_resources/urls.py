from django.urls import path
from . import views


urlpatterns = [
    path('HR/Login', views.loginHumanResource, name='login'),
    path('HR/createOpportunity', views.createOpportunity, name='opportunity'),
    path('HR/deleteOpportunity/<int:pk>', views.deleteOpportunity, name='opportunity'),
    path('HR/getByIdOpportunity/<int:pk>', views.getByIdOpportunity, name='opportunity'),
    path('HR/updateOpportunity/<int:pk>', views.updateOpportunity, name='opportunity'),
    path('opportunities/',views.getJobCard, name='opportunityCard'),
     path('opportunityById/<int:pk>/',views.opportunityById, name='opportunityCard'),
    path('Forsa/', views.opportunity_list, name='opportunity-list'),
#    path('HR/getAllOpportunity/', views.getAllOpportunity, name='opportunity'),
    path('apply/<int:opportunity_id>/', views.apply_for_opportunity, name='apply-for-opportunity'),



]
