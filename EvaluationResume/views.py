from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
import json
import fitz  # PyMuPDF
import google.generativeai as genai

from EvaluationResume.serializer import ResumeEvaluationSerializer
from devloper.models import Resume, Skill, Education, Project, Experience, TrainingCourse
from .models import ResumeEvaluation


User = get_user_model()

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

        job_description = request.data.get("job_description", "")
        evaluation_result = self.evaluate_resume(parsed_data.get("summary", ""), job_description) if job_description else None

        if not evaluation_result:
            return Response({"error": "Evaluation failed"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(evaluation_result, status=status.HTTP_200_OK)

    def parse_resume_with_gemini(self, resume_text):
        prompt = f"""
        Extract ATS-friendly resume data from the following text:
        {resume_text}
        Ensure the output is structured in valid JSON format with the required fields.
        """
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content([prompt])
            response_text = response.text.strip().strip("```json").strip("```")
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            print("JSON Decode Error:", e)
            return {}

    def evaluate_resume(self, resume_summary, job_description):
        input_prompt = f'''
        Act as an ATS system and evaluate the resume based on the job description.
        Return the match percentage, missing keywords, and improvement tips in **valid JSON format ONLY**.
        Resume: {resume_summary}
        Job Description: {job_description}
        Ensure the response follows this structure:
        {{
            "match_percentage": 0.0,
            "missing_keywords": [],
            "improvement_tips": ""
        }}
        '''
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content([input_prompt])
            json_text = response.text.strip().strip("```json").strip("```")
            return json.loads(json_text)
        except json.JSONDecodeError:
            return {
                "match_percentage": 0.0,
                "missing_keywords": [],
                "improvement_tips": "Invalid JSON format received from the model"
            }