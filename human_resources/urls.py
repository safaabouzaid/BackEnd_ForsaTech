from django.urls import path
from . import views


urlpatterns = [
    path('HR/Login', views.loginHumanResource, name='login'),
    path('HR/createOpportunity', views.createOpportunity, name='opportunity'),
    path('HR/deleteOpportunity/<int:pk>', views.deleteOpportunity, name='opportunity'),
    path('HR/getByIdOpportunity/<int:pk>', views.getByIdOpportunity, name='opportunity'),
    path('HR/updateOpportunity/<int:pk>', views.updateOpportunity, name='opportunity'),
    path('opportunities/',views.getJobCard, name='opportunityCard'),
    path('opportunity-details/', views.opportunity_details_view, name='opportunity-details'),
    path('user-resume/', views.user_resume, name='user-resume'),
    path('create-ad/', views.create_company_ad, name='create_company_ad'),
    path('getopportunitynames/', views.get_opportunity_names, name='get_opportunity_names'),
    path('Forsa/', views.opportunity_list, name='opportunity-list'),
    path('opportunities/my-company/', views.get_opportunities_for_hr_company, name='hr-company-opportunities'),
    path('opportunityById/<int:pk>/',views.opportunityById, name='opportunityCard'),
    path('request-subscription/',views.request_subscription_change, name='request_subscription'),
    path('job-applications/', views.list_job_applications, name='list_job_applications'),
    path('job-applications/update-status/', views.update_job_application_status, name='update_job_status'),
    path('check-status/', views.check_application_status, name='check_application_status'),
    path('dashboard-status/', views.hr_dashboard_stats, name='hr_dashboard_stats'),
    path('check-subscription-status/', views.check_subscription_status, name='check_subscription_status'),
#    path('HR/getAllOpportunity/', views.getAllOpportunity, name='opportunity'),
    path('apply/<int:opportunity_id>/', views.apply_for_opportunity, name='apply-for-opportunity'),
    path('company_ads/', views.company_ads_list, name='company_ads_list'),
    path('schedule-interview/', views.create_interview_schedule, name='create_interview'),
    path('get-interviews/',views.get_interview_schedules, name='get_interviews'),
    path('company-profile/',views.get_hr_company_profile, name='get_hr_company_profile'),
]
