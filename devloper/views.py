from django.shortcuts import render
from devloper.models import Resume
from human_resources.models import JobApplication, Opportunity
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import status
from .serializer import LoginSerializer, SingUpSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

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

        return Response({'details': 'Your account registered successfully'}, status=status.HTTP_201_CREATED)
    
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







##############complaint################

@api_view(['POST'])
def add_complaint(request):
    if request.method == 'POST':
        serializer = ComplaintSerializer(data=request.data)
        

        if serializer.is_valid():

            user = request.user


            if user.is_authenticated:

                serializer.save(user=user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "User is not authenticated."}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
   #### apply opp 
   ##
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_for_opportunity(request, opportunity_id):
    user = request.user

   
    try:
        opportunity = Opportunity.objects.get(id=opportunity_id)
    except Opportunity.DoesNotExist:
        return Response({"error": "Opportunity not found."}, status=status.HTTP_404_NOT_FOUND)

    # Check if the user has a resume
    try:
        resume = Resume.objects.get(user=user)
    except Resume.DoesNotExist:
        return Response({
            "error": "missing_resume",
            "title": "Please create a resume first."
        }, status=status.HTTP_400_BAD_REQUEST)

    # Check if the user has experience or education
    has_experience = resume.experiences.exists()
    has_education = resume.education.exists()

    # Check if any of the required information is missing
    if not has_experience and not has_education:
        return Response({
            "error": "missing_info",
            "title": "Please complete the following information",
            "missing_experience": True,
            "missing_education": True
        }, status=status.HTTP_400_BAD_REQUEST)

    if not has_experience:
        return Response({
            "error": "missing_experience",
            "title": "Please complete the experience section."
        }, status=status.HTTP_400_BAD_REQUEST)

    if not has_education:
        return Response({
            "error": "missing_education",
            "title": "Please complete the education section."
        }, status=status.HTTP_400_BAD_REQUEST)

    # Check if the user has already applied for this opportunity
    if JobApplication.objects.filter(user=user, opportunity=opportunity).exists():
        return Response({
            "error": "already_applied",
            "message": "You have already applied for this job."
        }, status=status.HTTP_400_BAD_REQUEST)

    # Create the job application
    JobApplication.objects.create(user=user, opportunity=opportunity, status="pending")
    return Response({
        "message": "Application submitted successfully."
    }, status=status.HTTP_201_CREATED)
    