from django.urls import path
from . import views

urlpatterns = [
    path('HR/Login', views.loginHumanResource, name='login'),
    path('HR/createOpportunity', views.createOpportunity, name='opportunity'),
    path('HR/deleteOpportunity/<int:pk>', views.deleteOpportunity, name='opportunity'),
    path('HR/getByIdOpportunity/<int:pk>', views.getByIdOpportunity, name='opportunity'),
    path('HR/updateOpportunity/<int:pk>', views.updateOpportunity, name='opportunity'),



]
