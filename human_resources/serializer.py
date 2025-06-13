from rest_framework import serializers
from devloper.models import User,Resume
from .models import Opportunity,JobApplication,CompanyAd,OpportunityName,Company

class HumanResourcesSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password') 
        extra_kwargs = {
            'username': {'required': True, 'allow_blank': False},
            'password': {'required': True, 'allow_blank': False, 'min_length': 8, 'write_only': True}
        }
    

class OpportunitySerializer(serializers.ModelSerializer):
    opportunity_name = serializers.ChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # جبت أسماء الفرص من  OpportunityName
        names = OpportunityName.objects.values_list('name', 'name')
        self.fields['opportunity_name'].choices = names

    class Meta:
        model=Opportunity
        exclude = ['company']
        
        
class OpportunitySerializer1(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_logo = serializers.ImageField(source='company.logo', read_only=True)  
    class Meta:
        model = Opportunity
        fields = [
            'id' ,
            # 'title',
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

class ApplicantSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username', 'email','location','github_link','linkedin_link','phone']  

class OpportunitySerializer(serializers.ModelSerializer):
    company = CompanySerializer()
    applicants = serializers.SerializerMethodField()

    class Meta:
        model = Opportunity
        fields = ['id', 'description', 'applicants', 'company']

    def get_applicants(self, obj):
        applications = JobApplication.objects.filter(opportunity=obj)
        users = [app.user for app in applications]
        return ApplicantSerializer(users, many=True).data


class OpportunitySerializer1(serializers.ModelSerializer):

    class Meta:
        model = Opportunity
        fields = ['id','opportunity_name','description']

class CompanyAdSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyAd
        fields = ['id', 'title', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']








from rest_framework import serializers
from .models import SubscriptionPlan

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'
