from django.contrib import admin
from .models import * 
# Register your models here.
admin.site.register(User)
admin.site.register(Resume)
admin.site.register(Skill)
admin.site.register(Education)
admin.site.register(Project)
admin.site.register(Experience)
admin.site.register(TrainingCourse)
admin.site.register(Language)


