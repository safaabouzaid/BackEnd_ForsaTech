
from .utils import get_sbert_model, get_opportunity_vector
from human_resources.models import Opportunity
import numpy as np

# @shared_task
def generate_opportunity_embedding(opp_id, model=None):
    if model is None:
        model = get_sbert_model()
    opp = Opportunity.objects.get(pk=opp_id)
    vec = get_opportunity_vector(opp, model)
    if np.linalg.norm(vec) > 0:
        opp.embedding = vec.tolist()
        opp.save()

def generate_all_opportunity_embeddings():
    model = get_sbert_model()
    opportunities = Opportunity.objects.all()
    for opp in opportunities:
        generate_opportunity_embedding(opp.id, model)
