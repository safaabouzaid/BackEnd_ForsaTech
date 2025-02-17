from django.urls import path
from . import views  

urlpatterns = [
    path('companies/', views.CompanyListView.as_view(), name='company-list'), 
    path('companies/create/', views.CompanyCreateView.as_view(), name='company-create'),  
    path('companies/<int:pk>/update/', views.CompanyUpdateView.as_view(), name='company-update'),  
    path('companies/<int:pk>/delete/', views.CompanyDeleteView.as_view(), name='company-delete'),   
]
