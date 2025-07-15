from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from devloper.models import Education, Project, Experience, TrainingCourse, Resume, Skill, Language
from .serializer import ResumeSerializer
from decouple import config
import google.generativeai as genai
from rest_framework.views import APIView
User = get_user_model()
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class ResumeAPIView(APIView):
    permission_classes = [IsAuthenticated]  # ⬅️ مهم لاستخدام التوكن

    def post(self, request):
        user = request.user
        user_data = request.data

        try:
            summary = self.generate_summary(user_data)
            resume = Resume.objects.create(user=user, summary=summary)
        except Exception as e:
            return Response({
                "status": "Failed",
                "message": f"Couldn't create resume: {str(e)}",
                "code": status.HTTP_400_BAD_REQUEST,
            })

        try:
            # ✅ Skills
            skills = user_data.get("skills", [])
            if skills:
                Skill.objects.bulk_create([
                    Skill(resume=resume, skill=s["skill"], level=s.get("level"))
                    for s in skills if "skill" in s
                ])

            # ✅ Education
            education = user_data.get("education", [])
            if education:
                Education.objects.bulk_create([
                    Education(resume=resume, **e) for e in education
                ])

            # ✅ Projects
            projects = user_data.get("projects", [])
            if projects:
                Project.objects.bulk_create([
                    Project(resume=resume, **{k: v for k, v in p.items() if k != "technologies_used"})
                    for p in projects if isinstance(p, dict)
                ])

            # ✅ Experience
            experiences = user_data.get("experiences", [])
            if experiences:
                Experience.objects.bulk_create([
                    Experience(resume=resume, **e) for e in experiences
                ])

            # ✅ Training Courses
            trainings = user_data.get("trainings_courses", [])
            if trainings:
                TrainingCourse.objects.bulk_create([
                    TrainingCourse(resume=resume, **t) for t in trainings
                ])

            # ✅ Languages
            languages = user_data.get("languages", [])
            if languages:
                Language.objects.bulk_create([
                    Language(resume=resume, name=l["language"], level=l["level"])
                    for l in languages if "language" in l and "level" in l
                ])

        except Exception as e:
            return Response({
                "status": "Partial Success",
                "message": f"Resume created, but error in sections: {str(e)}",
                "code": status.HTTP_206_PARTIAL_CONTENT,
            })

        serializer = ResumeSerializer(resume)
        return Response({
            "status": "Success",
            "message": "Resume created successfully",
            "code": status.HTTP_201_CREATED,
            "data": serializer.data,
        }, status=status.HTTP_201_CREATED)

    def generate_summary(self, user_data):
        skills = ", ".join([s.get("skill", "") for s in user_data.get("skills", []) if "skill" in s])
        education = "; ".join([
            f"{e.get('degree')} at {e.get('institution')} ({e.get('start_date')} - {e.get('end_date')})"
            for e in user_data.get("education", []) if "degree" in e
        ])

        prompt = f"""
        Generate a first-person professional resume summary.
        Skills: {skills}
        Education: {education}
        """

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([prompt])
        return response.text.strip()


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
import google.generativeai as genai
from decouple import config
import pdfplumber
import docx

genai.configure(api_key=config("GOOGLE_API_KEY"))

class ATSResumeFromFileAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        file = request.FILES.get("resume_file")
        job_description = request.data.get("job_description", "")

        if not file:
            return Response({"message": "Resume file is required."}, status=400)

        try:
            if file.name.endswith(".pdf"):
                resume_text = self.extract_text_from_pdf(file)
            elif file.name.endswith(".docx"):
                resume_text = self.extract_text_from_docx(file)
            else:
                return Response({"message": "Unsupported file format. Use PDF or DOCX."}, status=400)
        except Exception as e:
            return Response({"message": f"Error extracting text: {str(e)}"}, status=500)

        try:
            ats_resume = self.generate_ats_resume(resume_text, job_description)
        except Exception as e:
            return Response({"message": f"Error generating ATS resume: {str(e)}"}, status=500)

        return Response({
            "status": "success",
            "message": "ATS resume generated successfully",
            "ats_resume": ats_resume
        }, status=200)

    def extract_text_from_pdf(self, file):
        with pdfplumber.open(file) as pdf:
            return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

    def extract_text_from_docx(self, file):
        doc = docx.Document(file)
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)

    def generate_ats_resume(self, resume_text, job_description=""):
        prompt = f"""
You are an expert in resume optimization. Convert the following resume into an ATS-friendly format:
- Focus on clear formatting, relevant keywords, and tailoring to job description (if any).
- Resume Tegenai.configure(api_key=config("GOOGLE_API_KEY"))

xt:
{resume_text}

Job Description:
{job_description}
        """
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
