from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from devloper.models import Education, Project, Experience, TrainingCourse, Resume, Skill, Language
from .serializer import ResumeSerializer
from decouple import config
import google.generativeai as genai

User = get_user_model()
genai.configure(api_key=config("GOOGLE_API_KEY"))

class ResumeAPIView(APIView):
    def post(self, request):
        user_data = request.data

        # إنشاء أو جلب المستخدم
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
            return Response({
                "status": "Failed",
                "message": "Couldn't create or get user",
                "code": status.HTTP_400_BAD_REQUEST,
            })

        try:
            if created:
                user.set_password(user_data.get("password", "default_password"))
                user.save()
        except:
            return Response({
                "status": "Failed",
                "message": "Couldn't assign password to user",
                "code": status.HTTP_400_BAD_REQUEST,
            })

      
        try:
            profile_summary = self.generate_summary(user_data)
            resume = Resume.objects.create(
                user=user,
                summary=profile_summary,
            )
        except:
            return Response({
                "status": "Failed",
                "message": "Couldn't create resume summary",
                "code": status.HTTP_400_BAD_REQUEST,
            })

       
        try:
            Skill.objects.bulk_create([
                Skill(resume=resume, skill=skill["skill"], level=skill.get("level"))
                for skill in user_data.get("skills", [])
            ])

            Education.objects.bulk_create([
                Education(resume=resume, **edu)
                for edu in user_data.get("education", [])
            ])
        except:
            return Response({
                "status": "Failed",
                "message": "Couldn't create skills or education",
                "code": status.HTTP_400_BAD_REQUEST,
            })
        try:
           
            project_objects = []
            for proj in user_data.get("projects", []):
                if isinstance(proj, dict):
                    proj.pop("technologies_used", None)
                    project_objects.append(Project(resume=resume, **proj))
            Project.objects.bulk_create(project_objects)

            Experience.objects.bulk_create([
                Experience(resume=resume, **exp)
                for exp in user_data.get("experiences", [])
            ])

            TrainingCourse.objects.bulk_create([
                TrainingCourse(resume=resume, **course)
                for course in user_data.get("trainings_courses", [])
            ])

            Language.objects.bulk_create([
                Language(resume=resume, name=lang["language"], level=lang["level"])
                for lang in user_data.get("languages", [])
            ])

        except Exception as e:
            return Response({
                "status": "Failed",
                "message": f"Couldn't create project/experience/training/language: {str(e)}",
                "code": status.HTTP_400_BAD_REQUEST,
            })

        # إرجاع النتيجة
        serializer = ResumeSerializer(resume)
        return Response({
            "status": "success",
            "code": status.HTTP_201_CREATED,
            "message": "Resume created successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    def generate_summary(self, user_data):
        skills_text = ", ".join([s.get("skill", "") for s in user_data.get("skills", [])])
        education_text = "; ".join([
            f"{e.get('degree')} at {e.get('institution')} ({e.get('start_date')} - {e.get('end_date')})"
            for e in user_data.get("education", [])
        ])

        prompt = f"""
        Generate a professional and impactful resume summary in the first person, emphasizing my problem-solving skills, leadership, and teamwork. Focus on the following:
        - My key technical skills: {skills_text}
        - My educational achievements and highlights: {education_text}
        Ensure the summary is concise, ATS-optimized, and aligned with software development roles.
        """

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([prompt])
        return response.text.strip()
