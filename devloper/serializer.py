from rest_framework import serializers
from .models import User

  
class SingUpSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}} 





class LoginSerializer(serializers.Serializer): 
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ('username', 'password', 'email')
        extra_kwargs = {
            'username': {'required': False },
             'email': {'required': False },
            'password': {'required': True}
        }


