from django.contrib import admin
from .models import Opportunity, humanResources
# Register your models here.

admin.site.register(humanResources)

admin.site.register(Opportunity)