from rest_framework import serializers
from devloper.models import User
from .models import Opportunity
class HumanResourcesSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')  # تأكد من أن User يحتوي على هذه الحقول
        extra_kwargs = {
            'username': {'required': True, 'allow_blank': False},
            'password': {'required': True, 'allow_blank': False, 'min_length': 8, 'write_only': True}
        }





class OpportunitySerializer(serializers.ModelSerializer):
    class Meta:
        model=Opportunity
        exclude = ['company']