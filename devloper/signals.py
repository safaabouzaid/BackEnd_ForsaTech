import sys
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Skill
from .gemini import get_inferred_skills

if 'loaddata' not in sys.argv:
    @receiver(post_save, sender=Skill)
    def create_inferred_skills(sender, instance, created, **kwargs):
        if created and not instance.is_inferred:
            print(f"Skill added: {instance.skill}") 
            inferred_skills = get_inferred_skills(instance.skill)
            print(f"Inferred skills: {inferred_skills}")  
            for skill_name in inferred_skills:
                if not Skill.objects.filter(
                    resume=instance.resume,
                    skill=skill_name,
                    is_inferred=True,
                    source_skill=instance.skill
                ).exists():
                    Skill.objects.create(
                        resume=instance.resume,
                        skill=skill_name,
                        is_inferred=True,
                        source_skill=instance.skill
                    )
