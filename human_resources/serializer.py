from rest_framework import serializers
from devloper.models import User
from .models import Opportunity
class HumanResourcesSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password') 
        extra_kwargs = {
            'username': {'required': True, 'allow_blank': False},
            'password': {'required': True, 'allow_blank': False, 'min_length': 8, 'write_only': True}
        }





class OpportunitySerializer(serializers.ModelSerializer):
    class Meta:
        model=Opportunity
        exclude = ['company']
        
        
class OpportunitySerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_logo = serializers.ImageField(source='company.logo', read_only=True)  
    class Meta:
        model = Opportunity
        fields = [
            'title',
            'company_logo',
            'experience_level',   # job level
            'years_of_experience',# experience
            'location',
            'posting_date' ,
            'company_name',
        ]      
        
        
        