from rest_framework import serializers
from devloper.models import User,Resume
from .models import Opportunity,JobApplication,CompanyAd,OpportunityName,Company,SubscriptionPlan,SubscriptionChangeRequest
from devloper.serializer import ResumeSerializer
class HumanResourcesSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password') 
        extra_kwargs = {
            'username': {'required': True, 'allow_blank': False},
            'password': {'required': True, 'allow_blank': False, 'min_length': 8, 'write_only': True}
        }
    

        
        
        
class OpportunitySerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_logo = serializers.URLField(source='company.logo', read_only=True)  
    opportunity_name = serializers.CharField() 
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
    
    resume = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'location', 'github_link', 'linkedin_link', 'phone', 'resume']

    def get_resume(self, obj):
        try:
            resume = Resume.objects.get(user=obj)
            return ResumeSerializer(resume).data
        except Resume.DoesNotExist:
            return None

# serializers.py
class OpportunitySerializer1(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_logo = serializers.URLField(source='company.logo', read_only=True)
    opportunity_name = serializers.CharField()
    company = serializers.PrimaryKeyRelatedField(read_only=True) 

    class Meta:
        model = Opportunity
        fields = '__all__'


class OpportunitySerializer2(serializers.ModelSerializer):
    class Meta:
        model = Opportunity
        fields = '__all__'



class JobApplicationSerializer(serializers.ModelSerializer):
    user = ApplicantSerializer(read_only=True)
    #opportunity = OpportunitySerializer2(read_only=True)

    class Meta:
        model = JobApplication
        fields = ['id', 'user', 'opportunity', 'applied_at', 'status']

#class OpportunitySerializer(serializers.ModelSerializer):
#    company = CompanySerializer()
#    applicants = serializers.SerializerMethodField()

#    class Meta:
#        model = Opportunity
#        fields = ['id', 'description', 'applicants', 'company']

 #   def get_applicants(self, obj):
  #      applications = JobApplication.objects.filter(opportunity=obj)
   #     users = [app.user for app in applications]
    #    return ApplicantSerializer(users, many=True).data

class OpportunityDetailSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_logo = serializers.URLField(source='company.logo', read_only=True)

    class Meta:
        model = Opportunity
        fields = '__all__'




class CompanyAdSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyAd
        fields = ['id', 'title', 'description', 'created_at' ,'ad_image']
        read_only_fields = ['id', 'created_at']









class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'



class SubscriptionChangeRequestSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    requested_plan_name = serializers.CharField(source='requested_plan.name', read_only=True)

    class Meta:
        model = SubscriptionChangeRequest
        fields = ['id', 'company', 'company_name', 'requested_plan', 'requested_plan_name', 'status', 'created_at']
        read_only_fields = ['status', 'created_at']



## ads 
class CompanyAdSerializer1(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = CompanyAd
        fields = ['id', 'company_name', 'title', 'description', 'ad_image']
