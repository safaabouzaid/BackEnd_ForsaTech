from django.shortcuts import render
from devloper.models import Resume
from human_resources.models import JobApplication, Opportunity
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import status
from .serializer import *
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from admin.serializers import ComplaintSerializer

from django.shortcuts import redirect
from social_django.utils import psa
from social_django.utils import load_strategy, load_backend
from social_core.exceptions import AuthException
# from django.contrib.auth import get_user_model

User = get_user_model()  


@api_view(['POST'])
def register(request):
    data = request.data
    serializer = SingUpSerializer(data=data)
    if serializer.is_valid():
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')

        if User.objects.filter(email=email).exists():
            return Response({'error': 'This email already exists!'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create(
            email=email,
            username=username,
            password=make_password(password),
        )

        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Your account registered successfully',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def login(request):
    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(password):  
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
###
# add lan

# views.py




@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def language_list_create(request):
    user = request.user

    resume = Resume.objects.filter(user=user).first()
    if not resume:
        resume = Resume.objects.create(user=user)

    if request.method == 'GET':
        languages = Language.objects.filter(resume=resume)
        serializer = LanguageSerializer(languages, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        languages_data = request.data if isinstance(request.data, list) else [request.data]

        existing_languages = Language.objects.filter(resume=resume)
        added_languages = []
        errors = []

        for lang_data in languages_data:
            lang_data['resume'] = resume.id

            exists = existing_languages.filter(
                name=lang_data.get('name')
            ).exists()

            if not exists:
                serializer = LanguageSerializer(data=lang_data)
                if serializer.is_valid():
                    serializer.save()
                    added_languages.append(serializer.data)
                else:
                    errors.append(serializer.errors)
            else:
                # تحديث اللغة الموجودة
                language_obj = existing_languages.get(name=lang_data.get('name'))
                serializer = LanguageSerializer(language_obj, data=lang_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    added_languages.append(serializer.data)
                else:
                    errors.append(serializer.errors)

        if errors:
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response(added_languages, status=status.HTTP_201_CREATED)



## add  profile 

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_developer(request):
    user = request.user
    try:
        developer_profile = user.developer_profile
        serializer = DeveloperSerializer(developer_profile)
        return Response({'detail': 'Developer profile retrieved successfully.', 'data': serializer.data}, status=status.HTTP_200_OK)
    except Developer.DoesNotExist:
        return Response({'detail': 'Developer profile not found.', 'data': None}, status=status.HTTP_200_OK)



@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_developer(request):
    user = request.user
    partial = request.method == 'PATCH'

    try:
        developer_profile = user.developer_profile
        serializer = DeveloperSerializer(developer_profile, data=request.data, partial=partial)
    except Developer.DoesNotExist:
        serializer = DeveloperSerializer(data=request.data)

    if serializer.is_valid():
        if hasattr(user, 'developer_profile'):
            serializer.save()
            return Response({'detail': 'Developer profile updated successfully.', 'data': serializer.data}, status=status.HTTP_200_OK)
        else:
            serializer.save(user=user)
            return Response({'detail': 'Developer profile created successfully.', 'data': serializer.data}, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

### delet profile 

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_developer(request):
    try:
        developer = request.user.developer_profile
    except Developer.DoesNotExist:
        return Response({'detail': 'Developer profile not found.'}, status=404)

    developer.delete()
    return Response({'detail': 'Developer profile deleted successfully.'}, status=204)


### for sava resume 

from .models import Resume, Skill, Education, Experience, Language, User

@api_view(['POST'])
def create_resume_from_parser(request):
    try:
        user_id = request.data.get('user_id')
        user = User.objects.get(id=user_id)

        resume = Resume.objects.create(
            user=user,
            summary=request.data.get("summary", ""),
        )

        # skills
        for skill in request.data.get("skills", []):
            Skill.objects.create(resume=resume, skill=skill)

        # education
        for edu in request.data.get("education", []):
            Education.objects.create(resume=resume, degree=edu, institution="")

        # experience
        for exp in request.data.get("experiences", []):
            Experience.objects.create(
                resume=resume,
                job_title=exp.get("job_title", ""),
                company=exp.get("company", ""),
                start_date=exp.get("start_date", ""),
                end_date=exp.get("end_date", ""),
                description=exp.get("description", "")
            )

        # languages
        for lang in request.data.get("languages", []):
         Language.objects.create(
          resume=resume,
          name=lang.get("name", "English"),
          level=lang.get("level", "1")
    )

        return Response({"message": "Resume saved successfully"}, status=status.HTTP_201_CREATED)

    except Exception as e:  
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



## update FCM-token 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_fcm_token(request):
    fcm_token = request.data.get('fcm_token')
    
    if not fcm_token:
        return Response({"error": "FCM token is required."}, status=status.HTTP_400_BAD_REQUEST)

    user = request.user
    user.fcm_token = fcm_token
    user.save()

    return Response({"message": "FCM token updated successfully."}, status=status.HTTP_200_OK)



@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def experience_list_create(request):
    user = request.user
    resume = Resume.objects.filter(user=user).last()  # أو .first() حسب الحاجة

    if not resume:
        return Response({'error': 'No resume found for this user.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        experiences = Experience.objects.filter(resume=resume)
        serializer = ExperienceSerializer(experiences, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        experiences_data = request.data if isinstance(request.data, list) else [request.data]

        existing_experiences = Experience.objects.filter(resume=resume)
        added_experiences = []
        errors = []

        for exp_data in experiences_data:
            exp_data['resume'] = resume.id

            exists = existing_experiences.filter(
                job_title=exp_data.get('job_title'),
                company=exp_data.get('company'),
                start_date=exp_data.get('start_date'),
            ).exists()

            if not exists:
                serializer = ExperienceSerializer(data=exp_data)
                if serializer.is_valid():
                    serializer.save()
                    added_experiences.append(serializer.data)
                else:
                    errors.append(serializer.errors)
            else:
                # يمكنك تجاهل التكرار أو تعديله هنا
                pass

        if errors:
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response(added_experiences, status=status.HTTP_201_CREATED)

    
    
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def education_list_create(request):
    user = request.user
    resume = Resume.objects.filter(user=user).first()
    
    # إذا لم يوجد Resume، أنشئ واحدًا
    if not resume:
        resume = Resume.objects.create(user=user)

    if request.method == 'GET':
        educations = Education.objects.filter(resume=resume)
        serializer = EducationSerializer(educations, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        educations_data = request.data if isinstance(request.data, list) else [request.data]

        existing_educations = Education.objects.filter(resume=resume)
        added_educations = []
        errors = []

        for edu_data in educations_data:
            edu_data['resume'] = resume.id

            exists = existing_educations.filter(
                degree=edu_data.get('degree'),
                institution=edu_data.get('institution'),
                start_date=edu_data.get('start_date'),
            ).exists()

            if not exists:
                serializer = EducationSerializer(data=edu_data)
                if serializer.is_valid():
                    serializer.save()
                    added_educations.append(serializer.data)
                else:
                    errors.append(serializer.errors)

        if errors:
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response(added_educations, status=status.HTTP_201_CREATED)


# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Resume



class LatestResumeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            latest_resume = Resume.objects.filter(user=request.user).last()
            if not latest_resume:
                return Response({
                    "status": "Empty",
                    "message": "No resume found",
                    "code": 200,
                    "data": {}
                })

            serializer = ResumeSerializer1(latest_resume)
            return Response({
                "status": "Success",
                "message": "Resume fetched successfully",
                "code": 200,
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": "Failed",
                "message": f"Couldn't fetch resume: {str(e)}",
                "code": 400
            }, status=status.HTTP_400_BAD_REQUEST)















#======================================================================================#


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from human_resources.models import Complaint
from admin.serializers import ComplaintSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_complaint(request):
    user = request.user
    data = request.data.copy()
    serializer = ComplaintSerializer(data=data)
    if serializer.is_valid():
        serializer.save(user=user)
        return Response(
            {"detail": "Complaint submitted successfully.", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )
    return Response(
        {"detail": "Invalid data.", "errors": serializer.errors},
        status=status.HTTP_400_BAD_REQUEST
    )
