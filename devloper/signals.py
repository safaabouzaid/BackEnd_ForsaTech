import sys
from django.dispatch import receiver
from .gemini import get_inferred_skills
from django.db.models.signals import post_save, post_delete
from .models import Resume, Skill, Experience, Project, TrainingCourse
from Recommendation.utils import get_sbert_model, get_user_resume_vector,get_opportunity_vector
import numpy as np
from human_resources.models import Opportunity

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





@receiver([post_save, post_delete], sender=Skill)
@receiver([post_save, post_delete], sender=Experience)
@receiver([post_save, post_delete], sender=Project)
@receiver([post_save, post_delete], sender=TrainingCourse)
def update_embedding(sender, instance, **kwargs):
    resume = instance.resume
    model = get_sbert_model()
    vec = get_user_resume_vector(resume.user, model)
    if np.linalg.norm(vec) > 0:
        resume.embedding = vec.tolist()
    else:
        resume.embedding = None
    resume.save()


@receiver(post_save, sender=Opportunity)
def update_opportunity_embedding(sender, instance, created, **kwargs):
    if created:  
        model = get_sbert_model()
        vec = get_opportunity_vector(instance, model)
        if np.linalg.norm(vec) > 0:
            Opportunity.objects.filter(pk=instance.pk).update(embedding=vec.tolist())
        else:
            Opportunity.objects.filter(pk=instance.pk).update(embedding=None)
