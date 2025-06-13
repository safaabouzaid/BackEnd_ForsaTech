from django.urls import path
from . import views


urlpatterns = [
    path('HR/Login', views.loginHumanResource, name='login'),
    path('HR/createOpportunity', views.createOpportunity, name='opportunity'),
    path('HR/deleteOpportunity/<int:pk>', views.deleteOpportunity, name='opportunity'),
    path('HR/getByIdOpportunity/<int:pk>', views.getByIdOpportunity, name='opportunity'),
    path('HR/updateOpportunity/<int:pk>', views.updateOpportunity, name='opportunity'),
    path('opportunities/',views.getJobCard, name='opportunityCard'),
    #path('opportunity-details/', views.opportunity_details_view, name='opportunity-details'),
    path('user-resume/<int:user_id>/', views.user_resume, name='user-resume'),
    path('create-ad/', views.create_company_ad, name='create_company_ad'),
    path('getopportunitynames/', views.get_opportunity_names, name='get_opportunity_names'),
    path('Forsa/', views.opportunity_list, name='opportunity-list'),
    path('opportunities/my-company/', views.get_opportunities_for_hr_company, name='hr-company-opportunities'),
    path('opportunityById/<int:pk>/',views.opportunityById, name='opportunityCard'),






#    path('HR/getAllOpportunity/', views.getAllOpportunity, name='opportunity'),
    path('apply/<int:opportunity_id>/', views.apply_for_opportunity, name='apply-for-opportunity'),



]
