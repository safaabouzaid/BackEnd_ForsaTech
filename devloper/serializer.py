from rest_framework import serializers
from .models import *

class SingUpSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}} 


class LoginSerializer(serializers.Serializer): 
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ('username', 'password', 'email')
        
        
        
# serializers.py


<<<<<<< HEAD
class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['name', 'level']
        
      

=======

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['skill', 'level', 'is_inferred', 'source_skill']

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ['degree', 'institution', 'start_date', 'end_date', 'description']

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['title', 'description', 'github_link']

class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = ['job_title', 'company', 'start_date', 'end_date', 'description']

class TrainingCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingCourse
        fields = ['title', 'institution', 'start_date', 'end_date', 'description']

class ResumeSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)
    education = EducationSerializer(many=True, read_only=True)
    projects = ProjectSerializer(many=True, read_only=True)
    experiences = ExperienceSerializer(many=True, read_only=True)
    trainings_courses = TrainingCourseSerializer(many=True, read_only=True)

    class Meta:
        model = Resume
        fields = ['id', 'summary', 'pdf_file', 'created_at', 'skills', 'education', 'projects', 'experiences', 'trainings_courses']
>>>>>>> 08f25b5669300c126e3f778ddc14c109b7d6a5d8
