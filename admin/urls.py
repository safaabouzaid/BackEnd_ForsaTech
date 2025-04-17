from django.urls import path
from . import views  

urlpatterns = [
    path('companies/', views.listCompanies, name='company-list'), 
    path('companies/create/', views.createCompany, name='company-create'),  
    path('companies/<int:pk>/update/', views.updateCompany, name='company-update'),  
    path('companies/<int:pk>/delete/', views.deleteCompany, name='company-delete'),   
    path('ads/', views.list_create_ads, name='company-ads'),
    path('ads/<int:ad_id>/', views.delete_ad, name='delete_ad'), 
]