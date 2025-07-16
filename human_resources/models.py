from django.db import models
from devloper.models import User
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone
from datetime import timedelta

class SubscriptionPlan(models.Model):
    
    name = models.CharField(max_length=100,unique=True)
    job_post_limit = models.IntegerField(null=True, blank=True)  
    can_generate_tests = models.BooleanField(default=False)
    can_schedule_interviews = models.BooleanField(default=False)
    
    candidate_suggestions = models.CharField(
        max_length=50,
        choices=[('none', 'No suggestions'), ('once', 'One time'), ('always', 'Always')],
        default='none'
    )
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True) 
    max_candidate_suggestions = models.IntegerField(null=True, blank=True)


    def __str__(self):
        return self.name


class Company(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    logo = models.URLField(blank=True, null=True)
    website = models.URLField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    employees = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=True)
    job_posts_this_month = models.IntegerField(default=0, null=True)  
    used_candidate_suggestions_count = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name if self.name else "Unnamed Company"




class humanResources(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    location = models.CharField(max_length=40, blank=True, null=True)

    def __str__(self):
        return str(self.user)
    


class CompanyAd(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True,blank=True, related_name='ads')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ad_image = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
      
    

    def __str__(self):
        return f"{self.title}"


class OpportunityName(models.Model):
    name = models.CharField(max_length=255,blank=True)
    
    def __str__(self):
        return self.name


class Opportunity(models.Model):
    EMPLOYMENT_TYPE_CHOICES = [
        ('remote', 'Remote'),
        ('on-site', 'On-site'),
        ('hybrid', 'Hybrid'),
        ('freelance', 'Freelance'),
        ('internship', 'Internship'),
        ('part-time', 'Part-time'),
        ('full-time', 'Full-time'),
    ]
    opportunity_name = models.CharField(max_length=255, blank=True)
    description = models.TextField(null=True, blank=True)
    employment_type = models.CharField(max_length=50, choices=EMPLOYMENT_TYPE_CHOICES, null=True, blank=True)
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
    created_at = models.DateTimeField(auto_now_add=True)
    embedding = ArrayField(models.FloatField(), size=384, null=True, blank=True)

    
    def __str__(self):
         return f"{self.opportunity_name} at {self.company.name}"
    


class JobApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')])

    def __str__(self):
        return f"{self.user} applied for {self.opportunity.opportunity_name}"

        

class GenerateQuestion(models.Model):
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name="questions")
    questions = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def str(self):
        return f"Questions for {self.opportunity}"
    

class Complaint(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('resolved', 'Resolved'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Complaint from {self.user.email} - {self.title}"





class SubscriptionChangeRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    requested_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company.name} - {self.requested_plan.name} ({self.status})"




class InterviewSchedule(models.Model):
    hr = models.ForeignKey(humanResources, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.opportunity.opportunity_name} on {self.date} at {self.time}"




class PasswordResetCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at
