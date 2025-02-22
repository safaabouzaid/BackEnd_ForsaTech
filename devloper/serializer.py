from rest_framework import serializers
from .models import User

  
class SingUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}} 





class LoginSerializer(serializers.ModelSerializer) : 
    class Meta:
        model = User
        fields = ('username', 'password', 'email')
        extra_kwargs = {
            'username': {'required': False },
             'email': {'required': False },
            'password': {'required': True}
        }



