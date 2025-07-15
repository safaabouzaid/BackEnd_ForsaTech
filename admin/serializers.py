from rest_framework import serializers
from human_resources.models import Company ,CompanyAd,Complaint,SubscriptionPlan
from devloper.models import User


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'




class CompanyAdSerializer(serializers.ModelSerializer):
    #company_name = serializers.CharField(write_only=True)
    company_logo = serializers.URLField(source='company.logo', read_only=True)
    company = serializers.CharField(source='company.name', read_only=True)
    ad_image = serializers.URLField(required=False)
    is_active = serializers.BooleanField(read_only=True)


    class Meta:
        model = CompanyAd
        fields = ['id', 'title', 'description', 'created_at', 'company', 'company_logo','ad_image','is_active',]


    def create(self, validated_data):
        company_name = validated_data.pop('company_name', None)
        company = None
        if company_name:
            try:
                company = Company.objects.get(name=company_name)
            except Company.DoesNotExist:
                raise serializers.ValidationError({"company_name": "Company not found"})
        return CompanyAd.objects.create(company=company, **validated_data)


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['name'] 



class CompanyDetailSerializer(serializers.ModelSerializer):
    opportunity_count = serializers.SerializerMethodField()
    subscription_plan = SubscriptionPlanSerializer()
     
    class Meta:
        model = Company
        fields = ['id', 'name','email', 'logo', 'description', 'website', 'address', 'employees', 'opportunity_count','subscription_plan']

    def get_opportunity_count(self, obj):
        return obj.opportunity_set.count()




class DashboardStatsSerializer(serializers.Serializer):
    num_companies = serializers.IntegerField()
    most_hiring_company = serializers.CharField(allow_null=True)
    most_hiring_company_count = serializers.IntegerField(allow_null=True)
    most_demanded_jobs = serializers.ListField(child=serializers.CharField())
    highest_paying_job = serializers.DictField()
    line_chart_data = serializers.ListField(child=serializers.DictField())
    pie_chart_data = serializers.ListField(child=serializers.DictField())
    active_jobs = serializers.IntegerField()
    avg_company_size = serializers.IntegerField()
    new_companies = serializers.IntegerField()
    premium_members = serializers.IntegerField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email']    

class ComplaintSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True) 


    class Meta:
        model = Complaint
        fields = ['id', 'user', 'title', 'description', 'status', 'created_at']
        read_only_fields = ['user', 'created_at']


