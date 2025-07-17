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


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['name', 'level']


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'skill', 'level', 'is_inferred', 'source_skill']


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ['id', 'degree', 'institution', 'start_date', 'end_date', 'description']


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'github_link']


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = ['id', 'job_title', 'company', 'start_date', 'end_date', 'description']


class TrainingCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingCourse
        fields = ['id', 'title', 'institution', 'start_date', 'end_date', 'description']


class ResumeSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)
    education = EducationSerializer(many=True, read_only=True)
    projects = ProjectSerializer(many=True, read_only=True)
    experiences = ExperienceSerializer(many=True, read_only=True)
    trainings_courses = TrainingCourseSerializer(many=True, read_only=True)

    class Meta:
        model = Resume
        fields = '__all__'\
            
            
            
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email'] 

class DeveloperSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True) 
    class Meta:
        model = Developer
        fields = ['id', 'gender', 'birth_date', 'bio', 'profile_picture', 'user']
        extra_kwargs = {
            'profile_picture': {'required': False}
        }


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ['id', 'resume', 'degree', 'institution', 'start_date', 'end_date', 'description']

class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = ['id', 'resume', 'job_title', 'company', 'start_date', 'end_date', 'description']
        
class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'        
        
# serializers.py
from rest_framework import serializers
from .models import (
    User, Resume, Skill, Education, Project,
    Experience, TrainingCourse, Language
)

class UserSerializer1(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'location', 'github_link', 'linkedin_link']


class SkillSerializer1(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['skill', 'level']


class EducationSerializer1(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ['degree', 'institution', 'start_date', 'end_date', 'description']


class ProjectSerializer1(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['title', 'description', 'github_link']


class ExperienceSerializer1(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = ['job_title', 'company', 'start_date', 'end_date', 'description']


class TrainingCourseSerializer1(serializers.ModelSerializer):
    class Meta:
        model = TrainingCourse
        fields = ['title', 'institution', 'start_date', 'end_date', 'description']


class LanguageSerializer1(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['name', 'level']


class ResumeSerializer1(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)
    location = serializers.CharField(source='user.location', read_only=True)
    github_link = serializers.CharField(source='user.github_link', read_only=True)
    linkedin_link = serializers.CharField(source='user.linkedin_link', read_only=True)

    skills = SkillSerializer1(many=True, read_only=True)
    education = EducationSerializer1(many=True, read_only=True)
    projects = ProjectSerializer1(many=True, read_only=True)
    experiences = ExperienceSerializer1(many=True, read_only=True)
    trainings_courses = TrainingCourseSerializer1(many=True, read_only=True)
    languages = LanguageSerializer1(many=True, read_only=True)

    class Meta:
        model = Resume
        fields = [
            'id',
            'username',
            'email',
            'phone',
            'location',
            'github_link',
            'linkedin_link',
            'summary',
            'skills',
            'education',
            'projects',
            'experiences',
            'trainings_courses',
            'languages',
            'pdf_file',
            'created_at'
        ]
