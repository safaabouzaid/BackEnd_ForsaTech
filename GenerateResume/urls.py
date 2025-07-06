from django.urls import path
from .views import ResumeAPIView

urlpatterns = [
    path('generate-resume/', ResumeAPIView.as_view(), name='generate_resume'),


]