
from .utils import *
from human_resources.models import Opportunity
import numpy as np

# @shared_task
def generate_opportunity_embedding(opp_id, model=None):
    if model is None:
        model = get_sbert_model()
    opp = Opportunity.objects.get(pk=opp_id)
    if opp.embedding and np.linalg.norm(opp.embedding) > 0:
        return  

    
    title_vec = text_to_vector([opp.opportunity_name or ""], model, f"Opp Title ({opp.id})")
    desc_vec = text_to_vector([opp.description or ""], model)
    skills = [normalize_skill(s.strip()) for s in (opp.required_skills or "").split(",") if s.strip()]
    skills_vec = text_to_vector(skills, model, f"Opp Skills ({opp.id})")

    combined = (
        OPP_TITLE_WEIGHT * title_vec +
        OPP_DESC_WEIGHT * desc_vec +
        OPP_SKILL_WEIGHT * skills_vec
    )
    norm = np.linalg.norm(combined)
    vec = combined / norm if norm != 0 else np.zeros(VECTOR_SIZE)

    if np.linalg.norm(vec) > 0:
        opp.embedding = vec.tolist()
        opp.save()

def generate_all_opportunity_embeddings():
    model = get_sbert_model()
    opportunities = Opportunity.objects.all()
    for opp in opportunities:
        generate_opportunity_embedding(opp.id, model)
