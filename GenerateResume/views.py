from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from forsa.settings import GOOGLE_API_KEY
from devloper.models import Education, Project, Experience, TrainingCourse, Resume, Skill
from .serializer import ResumeSerializer, UserSerializer
from decouple import config
import google.generativeai as genai
from django.conf import settings  
from rest_framework.parsers import MultiPartParser, FormParser
import re

User = get_user_model()

genai.configure(api_key="AIzaSyAWfqk0NLuH3FV8BJgI1RtGQYoRxIR46sM")


class ResumeAPIView(APIView):
    def post(self, request):
        user_data = request.data
        try:
            user, created = User.objects.get_or_create(
                email=user_data.get("email"),
                defaults={
                    "username": user_data.get("username"),
                    "phone": user_data.get("phone"),
                    "location": user_data.get("location"),
                    "github_link": user_data.get("github_link"),
                    "linkedin_link": user_data.get("linkedin_link"),
                }
            )
            
        except:
            return Response({"status": "Faild", "message": "couldn't create user",
                             "code": status.HTTP_400_BAD_REQUEST,})
        try:
            if created:
                user.set_password(user_data.get("password", "default_password"))
                user.save()
        except:
                return Response({"status": "Faild", "message": "can't assign pasword to user",
                             "code": status.HTTP_400_BAD_REQUEST,})
        try:
            profile_summary = self.generate_summary(user_data)
            resume = Resume.objects.create(
                user=user,
                summary=profile_summary,
                
            )
        except:
            return Response({"status": "Faild", "message": "couldn't create summery",
                             "code": status.HTTP_400_BAD_REQUEST,})

        try:
            skill_objects = [Skill(resume=resume, skill=skill["skill"], level=skill.get("level")) for skill in user_data.get("skills", [])]
            Skill.objects.bulk_create(skill_objects)
            
            education_objects = [Education(resume=resume, **edu) for edu in user_data.get("education", [])]
            Education.objects.bulk_create(education_objects)
        except:
            return Response({"status": "Faild", "message": "couldn't make skills or education",
                             "code": status.HTTP_400_BAD_REQUEST,})
        
        try:
            
            project_objects = []
            for proj in user_data.get("projects", []):
                if isinstance(proj, dict):
                    proj.pop("technologies_used", None)
                project_objects.append(Project(resume=resume, **proj))
            
            Project.objects.bulk_create(project_objects)

            experience_objects = [Experience(resume=resume, **exp) for exp in user_data.get("experiences", [])]
            Experience.objects.bulk_create(experience_objects)
            
            training_objects = [TrainingCourse(resume=resume, **training) for training in user_data.get("trainings_courses", [])]
            TrainingCourse.objects.bulk_create(training_objects)
        except:
            return Response({"status": "Faild", "message": "couldn't Project or Experince or Training",
                             "code": status.HTTP_400_BAD_REQUEST,})
            
        serializer = ResumeSerializer(resume)
        return Response({
            "status": "success",
            "code": status.HTTP_201_CREATED,
            "message": "Resume created successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
            
    def generate_summary(self, user_data):
        skills_text = ", ".join([skill.get('skill', 'N/A') for skill in user_data.get('skills', [])])
        education_text = "; ".join(
            [f"{edu.get('degree', 'N/A')} at {edu.get('institution', 'N/A')} ({edu.get('start_date', 'N/A')} - {edu.get('end_date', 'N/A')})"
             for edu in user_data.get('education', [])]
        )

        prompt = f"""
        Generate a professional and impactful resume summary in the first person, emphasizing my problem-solving skills, leadership, and teamwork. Focus on the following:
        - My key technical skills: {skills_text}
        - My educational achievements and highlights: {education_text}
        Ensure the summary is concise, ATS-optimized, and aligned with software development roles.
        """

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([prompt])
        return response.text.strip()



