from django.db import models # type: ignore
from django.contrib.auth.models import AbstractUser # type: ignore
from django.conf import settings # type: ignore
from django.core.validators import EmailValidator # type: ignore
from django.contrib.postgres.fields import ArrayField
#
#class User(AbstractUser):
#    email = models.EmailField(unique=True,null=True, blank=True )  
#    username = models.CharField(max_length=150, unique=True,null=True, blank=True ) 
#    password = models.CharField(max_length=128,null=True, blank=True)
    
#    REQUIRED_FIELDS = [] 

#    def __str__(self):
#        return self.email
    

    
class User(AbstractUser):
    username = models.CharField(max_length=255,unique=False, default='')
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    github_link = models.URLField(blank=True, null=True)     
    linkedin_link = models.URLField(blank=True, null=True)     
    password = models.CharField(max_length=128,null=True, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    fcm_token = models.CharField(max_length=600, blank=True, null=True)

    def __str__(self):
        return self.username

class Developer(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='developer_profile')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    birth_date = models.DateField(blank=True, null=True) 
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='developers/', blank=True, null=True)

    def __str__(self):
        return f"Developer Profile of {self.user.username}"
    
    

class Resume(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="resumes",null=True, blank=True)
    summary = models.TextField(blank=True, null=True)
    pdf_file = models.FileField(upload_to='resumes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    embedding = ArrayField(models.FloatField(), size=384, null=True, blank=True)


    def __str__(self):
        return f"Resume for {self.user.username} - {self.created_at}"

class Skill(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="skills")
    skill = models.CharField(max_length=255)
    level = models.CharField(max_length=50, blank=True, null=True)
    is_inferred = models.BooleanField(default=False,null=True)
    source_skill = models.CharField(max_length=255, blank=True, null=True)   #في حال ماكانت الاصلية يلي عندي 

    def __str__(self):
        return f"{self.skill} - {self.resume.user.username}"

class Education(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="education")
    degree = models.CharField(max_length=255)
    institution = models.CharField(max_length=255)
    start_date = models.CharField(max_length=20, blank=True, null=True)
    end_date = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.degree} at {self.institution} - {self.resume.user.username}"

class Project(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="projects")
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    github_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.resume.user.username}"

class Experience(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="experiences")
    job_title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    start_date = models.CharField(max_length=20, blank=True, null=True)
    end_date = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.job_title} at {self.company} - {self.resume.user.username}"

class TrainingCourse(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="trainings_courses")
    title = models.CharField(max_length=255)
    institution = models.CharField(max_length=255)
    start_date = models.CharField(max_length=20, blank=True, null=True)
    end_date = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} at {self.institution} - {self.resume.user.username}"




class Language(models.Model):
    LANGUAGE_CHOICES = [
        ('Arabic', 'Arabic'),
        ('English', 'English'),
        ('Spanish', 'Spanish'),
        ('German', 'German'),
        ('Turkish', 'Turkish'),
        ('Russian', 'Russian'),
        ('French', 'French'),
        ('Chinese', 'Chinese'),
        ('Japanese', 'Japanese'),
        ('Hindi', 'Hindi'),
        ('Italian', 'Italian'),
        ('Portuguese', 'Portuguese'),
        ('Korean', 'Korean'),
        ('Persian', 'Persian'),
        ('Urdu', 'Urdu'),
    ]

    LEVEL_CHOICES = [
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
    ]

    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="languages")
    name = models.CharField(max_length=50, choices=LANGUAGE_CHOICES)
    level = models.CharField(max_length=6, choices=LEVEL_CHOICES)

    def __str__(self):
        return f"{self.get_name_display()} - {self.get_level_display()} ({self.resume.user.username})"


