from django.db import models
from devloper.models import User

class humanResources(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    company_name = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=40, blank=True, null=True)

    def __str__(self):
        return str(self.user)
    
    
    
    
    

class Company(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    logo = models.URLField(null=True, blank=True,max_length=1000)
    website = models.URLField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    
    def __str__(self):
        return self.name if self.name else "Unnamed Company"

class Opportunity(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    employment_type = models.CharField(max_length=50,null=True, blank=True)
    location = models.CharField(max_length=100,null=True, blank=True)
    salary_range = models.CharField(max_length=50,null=True, blank=True)
    currency = models.CharField(max_length=10,null=True, blank=True)
    experience_level = models.CharField(max_length=50,null=True, blank=True)
    required_skills = models.TextField(null=True, blank=True)
    preferred_skills = models.TextField(blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    education_level = models.CharField(max_length=100)
    certifications = models.TextField(blank=True, null=True)
    languages_required = models.TextField(blank=True, null=True)
    years_of_experience = models.CharField(max_length=10,blank=True, null=True)
    posting_date = models.DateTimeField(blank=True, null=True)
    application_deadline = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=50)
    benefits = models.CharField(max_length=50,blank=True, null=True)
    
    def __str__(self):
        return self.title
    