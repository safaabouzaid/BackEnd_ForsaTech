from rest_framework import serializers

from .models import ResumeEvaluation

class ResumeEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeEvaluation
        fields = ['match_percentage','missing_keywords','improvement_tips']

