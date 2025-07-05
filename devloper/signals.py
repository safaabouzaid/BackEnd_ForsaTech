import sys
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from .models import Resume, Skill, Experience, Project, TrainingCourse
from .gemini import get_inferred_skills

from Recommendation.utils import get_sbert_model, get_user_resume_vector
from human_resources.models import Opportunity

import numpy as np


if 'loaddata' not in sys.argv:

    @receiver(post_save, sender=Skill)
    def create_inferred_skills(sender, instance, created, **kwargs):
        

        if created and not instance.is_inferred:
            print(f"Skill added: {instance.skill}")

            inferred_skills = get_inferred_skills(instance.skill)
            print(f"Inferred skills: {inferred_skills}")

            for skill_name in inferred_skills:

                if skill_name == instance.skill:
                    continue


                Skill.objects.get_or_create(
                    resume=instance.resume,
                    skill=skill_name,
                    defaults={
                        "is_inferred": True,
                        "source_skill": instance.skill
                    }
                )

    
    @receiver(post_save, sender=Opportunity)
    def update_opportunity_embedding(sender, instance, created, **kwargs):

        if created:
            pass  
