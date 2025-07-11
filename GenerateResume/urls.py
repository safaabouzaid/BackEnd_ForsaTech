from django.urls import path
from .views import  ResumeAPIView

# ATSResumeConverterAPIView,

urlpatterns = [
    path('generate-resume/', ResumeAPIView.as_view(), name='generate_resume'),
    # path('convert-ats-resume/', ATSResumeConverterAPIView.as_view(), name='convert-ats-resume'),


]