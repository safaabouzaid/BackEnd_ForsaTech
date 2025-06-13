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

    
###
# add lan

# views.py



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_languages(request):
    
    resume = Resume.objects.filter(user=request.user).order_by('created_at').first()

    if not resume:
        return Response({"error": "No resume found for the user."}, status=status.HTTP_404_NOT_FOUND)

    languages_data = request.data  

    for item in languages_data:
        serializer = LanguageSerializer(data=item)
        if serializer.is_valid():
            name = serializer.validated_data['name']
            level = serializer.validated_data['level']

            language_obj, created = Language.objects.get_or_create(
                resume=resume,
                name=name,
                defaults={'level': level}
            )

            if not created:
                
                language_obj.level = level
                language_obj.save()

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({"message": "Languages saved/updated successfully."}, status=status.HTTP_200_OK)
