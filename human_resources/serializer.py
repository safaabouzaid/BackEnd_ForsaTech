from rest_framework import serializers
from devloper.models import User
from .models import Opportunity,JobApplication,CompanyAd,OpportunityName,SubscriptionPlan


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
        model = Opportunity
        exclude = ['company']


class ApplicantSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username', 'email','location','github_link','linkedin_link','phone']  

class OpportunityDetailsSerializer(serializers.ModelSerializer):
    applicants = serializers.SerializerMethodField()

    class Meta:
        model = Opportunity
        fields = ['id', 'description', 'applicants']

    def get_applicants(self, obj):
        applications = JobApplication.objects.filter(opportunity=obj)
        users = [app.user for app in applications]
        return ApplicantSerializer(users, many=True).data



class CompanyAdSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyAd
        fields = ['id', 'title', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']



class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'
