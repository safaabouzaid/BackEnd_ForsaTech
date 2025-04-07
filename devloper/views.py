from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import status
from .serializer import LoginSerializer, SingUpSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

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
        email = serializer.validated_data.get('email',None)
        username = serializer.validated_data.get('username',None)
        password = serializer.validated_data.get('password')

      
        user = None
        if email:
            user = User.objects.filter(email=email).first()
        elif username:
            user = User.objects.filter(username=username).first()

        if user and user.check_password(password):  
            authenticated_user = authenticate(username=user.username, password=password)
            if authenticated_user:
                refresh = RefreshToken.for_user(authenticated_user)
                return Response({
                    'username': user.username,
                    'email': user.email,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid username/email or password'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    