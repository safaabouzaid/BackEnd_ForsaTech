from django.urls import path
from . import views  

urlpatterns = [
    path('companies/', views.listCompanies, name='company-list'), 
    path('companies/create/', views.createCompany, name='company-create'),  
    path('companies/<int:pk>/update/', views.updateCompany, name='company-update'),  
    path('companies/<int:pk>/delete/', views.deleteCompany, name='company-delete'),   
    path('ads/', views.list_create_ads, name='company-ads'),
    path('ads/<int:ad_id>/', views.suspend_ad, name='suspend_ad'), 
    path('company/<int:pk>/profile/', views.get_company_profile, name='company-profile'),
    path('dashboard/stats/', views.dashboard_stats, name='dashboard-stats'),
    path('complaints/', views.get_all_complaints, name='get_all_complaints'),
    path('complaints/<int:complaint_id>/update/', views.update_complaint_status, name='update_complaint_status'),
    path('plans/', views.list_subscription_plans, name='plan-list'),
    path('plans/create/', views.create_subscription_plan, name='plan-create'),
    path('plans/update/<plan_id>/', views.update_subscription_plan, name='plan-update'),
    path('plans/delete/<int:plan_id>/', views.delete_subscription_plan,name='plan-delete'), 
    path('list-subscription/', views.list_subscription_requests, name='list_subscription'),
    path('handle-subscription/', views.handle_subscription_request, name='handle_subscription'),
    path('request-registration/', views.request_company_registration, name='request_company_registration'),
    path('companies/by-opportunity/', views.companies_by_opportunity, name='companies_by_opportunity'),

]

