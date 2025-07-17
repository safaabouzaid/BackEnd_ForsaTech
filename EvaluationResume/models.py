from django.db import models
from devloper.models import Resume
# Create your models here.


class ResumeEvaluation(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="evaluations")
    job_description = models.TextField()
    match_percentage = models.FloatField()
    missing_keywords = models.JSONField(default=list)
    improvement_tips = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Evaluation for {self.resume.user.username} - {self.match_percentage}%"