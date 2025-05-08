from rest_framework import serializers
from devloper.models import User
from .models import Opportunity , Company
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
<<<<<<< HEAD
        exclude = ['company']
        
        
class OpportunitySerializer1(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_logo = serializers.ImageField(source='company.logo', read_only=True)  
    class Meta:
        model = Opportunity
        fields = [
            'id' ,
            'title',
            'company_logo',
            'experience_level',   # job level
            'years_of_experience',# experience
            'location',
            'employment_type' ,
            'posting_date' ,
            'company_name',
        ]      
        
        
        
class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [ 'name', 'logo', 'website', 'description', 'email', 'address', 'employees']

class OpportunitySerializer(serializers.ModelSerializer):
    company = CompanySerializer()

    class Meta:
        model = Opportunity
        fields = ['id', 'title', 'description', 'employment_type', 'location', 'salary_range', 
                  'currency', 'experience_level', 'required_skills', 'preferred_skills', 'education_level', 
                  'certifications', 'languages_required', 'years_of_experience', 'posting_date', 
                  'application_deadline', 'status', 'benefits', 'company']        
        
        
        
=======
        exclude = ['company']
>>>>>>> 791cbf3cd573cd588591bcc0c1dbb4b8748675b9
