from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from devloper.models import Education, Project, Experience, TrainingCourse, Resume, Skill
from devloper.serializer import ResumeSerializer
import json
import re
import google.generativeai as genai


class ConvertResumeAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        if "pdf_file" not in request.FILES:
            return Response({"error": "No PDF file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        pdf_file = request.FILES["pdf_file"]

        if pdf_file.size == 0:
            return Response({"error": "Uploaded file is empty"}, status=status.HTTP_400_BAD_REQUEST)

        if pdf_file.content_type != "application/pdf":
            return Response({"error": "Uploaded file is not a valid PDF"}, status=status.HTTP_400_BAD_REQUEST)

        extracted_text = self.extract_text_from_pdf(pdf_file.read())

        if not extracted_text.strip():
            return Response({"error": "Failed to extract text from PDF"}, status=status.HTTP_400_BAD_REQUEST)

        parsed_data = self.parse_resume_with_gemini(extracted_text)

        if not isinstance(parsed_data, dict) or not parsed_data:
            return Response({"error": "Failed to parse resume data correctly"}, status=status.HTTP_400_BAD_REQUEST)

        resume = self.generate_ats_resume(parsed_data)

        ats_resume = {
            "personal_details": {
                "name": parsed_data.get("name", ""),
                "phone": parsed_data.get("phone", ""),
                "email": parsed_data.get("email", ""),
                "location": parsed_data.get("location", ""),
                "github_link": parsed_data.get("github_link", ""),
                "linkedin_link": parsed_data.get("linkedin_link", ""),
            },
            "summary": self.generate_summary(parsed_data),
            "skills": self.structure_skills(parsed_data.get("skills", [])),
            "education": self.structure_education(parsed_data.get("education", [])),
            "projects": parsed_data.get("projects", []),
            "experiences": parsed_data.get("experiences", []),
            "trainings_courses": parsed_data.get("trainings_courses", []),
        }

        return Response(ats_resume, status=status.HTTP_201_CREATED)

    def extract_text_from_pdf(self, pdf_data):
        import fitz
        try:
            doc = fitz.open(stream=pdf_data, filetype="pdf")
            text = "\n".join(page.get_text("text") for page in doc)
            return text.strip()
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""

    def parse_resume_with_gemini(self, resume_text):
        prompt = f"""
        Extract structured resume data from the following text:
        {resume_text}
        
        Provide the response in a structured JSON format with the following fields:
        - name, phone, location, email, github_link, linkedin_link, summary
        - skills (list), education (list), projects (list), experiences (list), trainings_courses (list)
        Ensure the response is in valid JSON format.
        """
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content([prompt])
            response_text = re.sub(r"```json|```", "", response.text.strip()).strip()
            return json.loads(response_text) if response_text.startswith("{") and response_text.endswith("}") else {}
        except Exception as e:
            print(f"Error in Gemini API response: {e}")
            return {}

    def generate_ats_resume(self, parsed_data):
        resume = Resume.objects.create(
            summary=self.generate_summary(parsed_data)
        )

        Skill.objects.bulk_create([
            Skill(resume=resume, skill=s if isinstance(s, str) else s.get("skill", ""))
            for s in parsed_data.get("skills", [])
        ])

        Education.objects.bulk_create([
            Education(
                resume=resume,
                degree=edu.get("degree", "Unknown"),
                institution=edu.get("university", "Unknown"),
                start_date=self.extract_date_range(edu.get("dates", ""))[0],
                end_date=self.extract_date_range(edu.get("dates", ""))[1]
            ) for edu in parsed_data.get("education", []) if isinstance(edu, dict)
        ])

        Project.objects.bulk_create([
            Project(
                resume=resume,
                title=proj.get("name", "Untitled"),
                github_link=proj.get("link", ""),
                description=proj.get("description", "")
            ) for proj in parsed_data.get("projects", []) if isinstance(proj, dict)
        ])

        Experience.objects.bulk_create([
            Experience(
                resume=resume,
                job_title=exp.get("title", "Unknown"),
                company=exp.get("location", "Unknown"),
                start_date=exp.get("years", "").split("-")[0].strip() if "years" in exp else "",
                end_date=exp.get("years", "").split("-")[1].strip() if "years" in exp else "",
                description=exp.get("description", "")
            ) for exp in parsed_data.get("experiences", []) if isinstance(exp, dict)
        ])

        TrainingCourse.objects.bulk_create([
            TrainingCourse(
                resume=resume,
                course_name=course.get("name", "Unknown"),
                institution=course.get("institution", "Unknown"),
                completion_date=course.get("completion_date", "")
            ) for course in parsed_data.get("trainings_courses", []) if isinstance(course, dict)
        ])

        return resume

    def extract_date_range(self, date_string):
        if "-" in date_string:
            parts = date_string.split("-")
            return parts[0].strip(), parts[1].strip()
        return "", ""

    def generate_summary(self, parsed_data):
        skills = parsed_data.get("skills", [])
        skill_names = [s.get("skill", "") if isinstance(s, dict) else str(s) for s in skills]
        skills_text = ", ".join(skill_names)

        education = parsed_data.get("education", [])
        education_text = "; ".join([
            f"{edu.get('degree', '')} at {edu.get('university', '')} ({edu.get('dates', '')})"
            for edu in education if isinstance(edu, dict)
        ])

        prompt = f"""
        Generate a professional and ATS-optimized resume summary based on:
        - Skills: {skills_text}
        - Education: {education_text}
        Keep it concise and impactful.
        """

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([prompt])
        return response.text.strip()

    def structure_skills(self, skills_list):
        structured = []
        for skill in skills_list:
            if isinstance(skill, str):
                match = re.match(r'^(.*?)\s*\((.*?)\)$', skill)
                if match:
                    structured.append({
                        "skill": match.group(1).strip(),
                        "level": match.group(2).strip()
                    })
                else:
                    structured.append({
                        "skill": skill.strip(),
                        "level": ""
                    })
            elif isinstance(skill, dict):
                structured.append(skill)
        return structured

    def structure_education(self, education_list):
        structured = []
        for edu in education_list:
            if isinstance(edu, dict):
                start, end = self.extract_date_range(edu.get("dates", ""))
                structured.append({
                    "degree": edu.get("degree", ""),
                    "institution": edu.get("university", ""),
                    "start_date": start,
                    "end_date": end,
                    "description": edu.get("description", "")
                })
        return structured
