from rest_framework import serializers
from devloper.models import User
from .models import Opportunity,JobApplication,CompanyAd,OpportunityName

class HumanResourcesSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password') 
        extra_kwargs = {
            'username': {'required': True, 'allow_blank': False},
            'password': {'required': True, 'allow_blank': False, 'min_length': 8, 'write_only': True}
        }


class OpportunitySerializer(serializers.ModelSerializer):
    opportunity_name_choice = serializers.ChoiceField(choices=[], required=False)
    opportunity_name = serializers.CharField(required=False, allow_blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        names = OpportunityName.objects.values_list('name', 'name')
        self.fields['opportunity_name_choice'].choices = names

    def validate(self, attrs):
        name = attrs.get('opportunity_name')
        choice = attrs.get('opportunity_name_choice')

        if not name and not choice:
            raise serializers.ValidationError("You must either enter a custom name or select from the list.")
        
        # لو اختار من الخيارات، نعيّن القيمة لمجال الاسم
        if choice:
            attrs['opportunity_name'] = choice

        return attrs

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
