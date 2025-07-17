import fitz
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from GenerateResume.models import ResumeEvaluation
from devloper.models import Education, Project, Experience, TrainingCourse, Resume, Skill, Language
from .serializer import ResumeSerializer
# from .serializer import ResumeSerializer1
from decouple import config
import google.generativeai as genai
from rest_framework.views import APIView
User = get_user_model()
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes

import json
from .utils import extract_json
from human_resources.models import Opportunity

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




#========================================Generate Question===============================================#

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_opportunity_questions(request):
    title = request.data.get("title")
    required_skills = request.data.get("required_skills")
    description = request.data.get("description")

    if not title or not required_skills or not description:
        return Response(
            {"error": "title, required_skills, and description are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    opportunity = None
    try:
        opportunity = Opportunity.objects.get(
            opportunity_name=title,
            description=description,
            required_skills=required_skills
        )
    except Opportunity.DoesNotExist:
        pass  

    input_prompt = f'''
    You are an AI assistant specializing in job interview preparation. Generate exactly 5 multiple-choice questions (MCQs) 
    for a job interview based on the following job title, description, and required skills.
    
    The questions should:
    - Reflect real-world job interview scenarios.
    - Test problem-solving, debugging, and practical experience.
    - Include technical questions with real-world applications.
    - Contain at least one question that involves analyzing code.

    Job Title: {title}
    Job Description: {description}
    Required Skills: {required_skills}

    Each MCQ should have:
    - A question string.
    - Four options in an array, where each option is a string.
    - The correct answer as the index of the correct option (starting from 0).

    Strictly follow this format:
    {{
        "questions": [
            {{
                "question": "What is ...?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": 0
            }},
            {{
                "question": "Which of the following ...?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": 2
            }}
        ]
    }}
    '''

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_prompt])

    if not response or not response.text.strip():
        return Response(
            {"error": "No valid response received from the model"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    json_text = extract_json(response.text.strip())

    try:
        questions = json.loads(json_text) if json_text else None
    except json.JSONDecodeError:
        questions = None

    if not questions:
        return Response(
            {"error": "Invalid JSON format received from the model"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return Response(
        {
            "opportunity_id": opportunity.id if opportunity else None,
            "questions": questions["questions"]
        },
        status=status.HTTP_200_OK
    )


#======================================== ResumeEvaluation ===============================================#

class PDFProcessor:
    @staticmethod
    def extract_text_from_pdf(pdf_data):
        try:
            doc = fitz.open(stream=pdf_data, filetype="pdf")
            text = "\n".join(page.get_text("text") for page in doc)
            return text.strip()
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""


class ResumeEvaluationView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated] 

    def post(self, request):
        user = request.user

        if "pdf_file" not in request.FILES:
            return Response({"error": "No PDF file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        pdf_file = request.FILES["pdf_file"]

        if pdf_file.size == 0:
            return Response({"error": "Uploaded file is empty"}, status=status.HTTP_400_BAD_REQUEST)

        if pdf_file.content_type != "application/pdf":
            return Response({"error": "Uploaded file is not a valid PDF"}, status=status.HTTP_400_BAD_REQUEST)

        extracted_text = PDFProcessor.extract_text_from_pdf(pdf_file.read())

        if not extracted_text.strip():
            return Response({"error": "Failed to extract text from PDF"}, status=status.HTTP_400_BAD_REQUEST)

        parsed_data = self.parse_resume_with_gemini(extracted_text)

        if not isinstance(parsed_data, dict) or not parsed_data:
            return Response({"error": "Failed to parse resume data correctly"}, status=status.HTTP_400_BAD_REQUEST)
        
        user.username = parsed_data.get("name", user.username)
        user.first_name = parsed_data.get("name", "").split(" ")[0] if parsed_data.get("name") else user.first_name
        user.last_name = " ".join(parsed_data.get("name", "").split(" ")[1:]) if parsed_data.get("name") else user.last_name
        user.email = parsed_data.get("email", user.email)
        user.phone = parsed_data.get("phone", user.phone)
        user.location = parsed_data.get("location", user.location)
        user.github_link = parsed_data.get("github_link", user.github_link)
        user.linkedin_link = parsed_data.get("linkedin_link", user.linkedin_link)
        user.save()

        resume = Resume.objects.create(
            user=user,
            summary=parsed_data.get("summary", ""),
            pdf_file=pdf_file
        )

        skills = [Skill(resume=resume, skill=skill) for skill in parsed_data.get("skills", []) if isinstance(skill, str)]
        Skill.objects.bulk_create(skills)

        education_objects = []
        allowed_fields = {field.name for field in Education._meta.fields if field.name != "id"}
        for edu in parsed_data.get("education", []):
            if isinstance(edu, dict):
                filtered_edu = {key: value for key, value in edu.items() if key in allowed_fields}
                education_objects.append(Education(resume=resume, **filtered_edu))

        Education.objects.bulk_create(education_objects)

        allowed_fields = {field.name for field in Project._meta.fields if field.name != "id"}
        project_objects = []
        for proj in parsed_data.get("projects", []):
            if isinstance(proj, dict):
                filtered_proj = {key: value for key, value in proj.items() if key in allowed_fields}
                project_objects.append(Project(resume=resume, **filtered_proj))
        Project.objects.bulk_create(project_objects)  

        experiences = [Experience(resume=resume, **exp) for exp in parsed_data.get("experiences", []) if isinstance(exp, dict)]
        Experience.objects.bulk_create(experiences)

        training_courses = [TrainingCourse(resume=resume, **course) for course in parsed_data.get("trainings_courses", []) if isinstance(course, dict)]
        TrainingCourse.objects.bulk_create(training_courses)

        resume.save()
        serializer = ResumeSerializer(resume)

        job_description = request.data.get("job_description", "")
        evaluation_result = self.evaluate_resume(resume, job_description) if job_description else None
        evaluation_data = {}
        
        if evaluation_result:
            evaluation = ResumeEvaluation.objects.create(
                resume=resume,
                job_description=job_description,
                match_percentage=evaluation_result["JD Match"],
                missing_keywords=evaluation_result["MissingKeywords"],
               
            )
            
        return Response({
             "match_percentage": evaluation_result["JD Match"],
             "missing_keywords": evaluation_result["MissingKeywords"],
            
         }, status=status.HTTP_201_CREATED)


    def parse_resume_with_gemini(self, resume_text):
        prompt = f"""
        Extract ATS-friendly resume data from the following text:
        {resume_text}
        Ensure the output is structured in **valid JSON format** with the required fields.
        """
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content([prompt])
            response_text = response.text.strip().strip("```json").strip("```")
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            print("JSON Decode Error:", e)
            return {}

    def evaluate_resume(self, resume, job_description):
        input_prompt = f'''
        Act as an ATS system and evaluate the resume based on the job description.
        Return the match percentage, missing keywords, and improvement tips in **valid JSON format ONLY**.
        Resume: {resume.summary}
        Job Description: {job_description}
        Ensure the response follows this structure:
        {{
            "JD Match": 0.0,
            "MissingKeywords": [],
            
        }}
        '''
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([input_prompt])
        json_text = response.text.strip().strip("```json").strip("```")
        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            return {"JD Match": 0, "MissingKeywords": [],}
