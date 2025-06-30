from celery import shared_task
from .utils import get_sbert_model, get_opportunity_vector
from human_resources.models import Opportunity
import numpy as np

@shared_task
def generate_opportunity_embedding(opp_id):
    opp = Opportunity.objects.get(pk=opp_id)
    vec = get_opportunity_vector(opp, get_sbert_model())
    if np.linalg.norm(vec) > 0:
        opp.embedding = vec.tolist()
        opp.save()
