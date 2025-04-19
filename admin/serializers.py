from rest_framework import serializers
from human_resources.models import Company ,CompanyAd


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'




class CompanyAdSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(write_only=True) 
    company_logo = serializers.ImageField(source='company.logo', read_only=True)
    company = serializers.CharField(source='company.name', read_only=True)  

    class Meta:
        model = CompanyAd
        fields = ['id', 'title', 'description', 'created_at', 'company','company_logo', 'company_name']

    def create(self, validated_data):
        company_name = validated_data.pop('company_name')
        try:
            company = Company.objects.get(name=company_name)
        except Company.DoesNotExist:
            raise serializers.ValidationError(f"Company with name '{company_name}' does not exist.")
        validated_data['company'] = company
        return super().create(validated_data)
