from django.urls import path
from .views import  ATSResumeFromFileAPIView, ResumeAPIView
from . import views
# ATSResumeConverterAPIView,

urlpatterns = [
    path('generate-resume/', ResumeAPIView.as_view(), name='generate_resume'),
    path('convert-from-file/', ATSResumeFromFileAPIView.as_view(), name='convert-from-file'),
    path('generate-questions/', views.generate_opportunity_questions, name='generate_opportunity_questions'),

]