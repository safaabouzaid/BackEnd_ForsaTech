import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from django.core.cache import cache
import logging
from devloper.models import Resume, Skill, User
from human_resources.models import Opportunity

logger = logging.getLogger(__name__)

# --- Lazy Loading SpaCy ---
nlp = None
def get_nlp():
    global nlp
    if nlp is None:
        import spacy
        try:
            nlp = spacy.load("en_core_web_sm")
        except OSError:
            import spacy.cli
            spacy.cli.download("en_core_web_sm")
            nlp = spacy.load("en_core_web_sm")
    return nlp

# --- Lazy Loading SBERT ---
sbert_model = None
def get_sbert_model():
    global sbert_model
    if sbert_model is not None:
        return sbert_model
    try:
        from sentence_transformers import SentenceTransformer
        model = cache.get('sbert_model')
        if not model:
            model = SentenceTransformer('paraphrase-albert-small-v2')
            cache.set('sbert_model', model, timeout=None)
        sbert_model = model
        return sbert_model
    except Exception as e:
        logger.error(f"Error loading SBERT model: {e}")
        return None

# --- Constants ---
VECTOR_SIZE = 384
SKILL_WEIGHT = 0.5
EXPERIENCE_WEIGHT = 0.25
PROJECT_WEIGHT = 0.15
TRAINING_WEIGHT = 0.1
OPP_TITLE_WEIGHT = 0.2
OPP_DESC_WEIGHT = 0.1
OPP_SKILL_WEIGHT = 0.7

# --- Helpers ---
def tokenize(text):
    if not isinstance(text, str):
        return []
    doc = get_nlp()(text.lower().strip())
    return [token.lemma_ for token in doc if not token.is_punct and not token.is_space and token.is_alpha]

def normalize_skill(skill):
    if not isinstance(skill, str):
        return ""
    skill = skill.lower().strip()
    replacements = {
        "react.js": "react", "react js": "react", "js": "javascript",
        "front-end": "frontend", "front end": "frontend",
        "py": "python", "ml": "machine learning", "ai": "artificial intelligence",
        "node.js": "node", "node js": "node",
        "back-end": "backend", "back end": "backend",
        "html5": "html", "css3": "css",
        "c++": "cpp", "c#": "csharp",
        "asp.net": "aspnet", "dot net": "dotnet",
        "sql server": "sql", "postgresql": "postgres", "mongodb": "mongo",
        "aws": "amazon web services", "azure": "microsoft azure", "gcp": "google cloud platform",
        "ui/ux": "ui ux design", "agile scrum": "agile"
    }
    for key, val in replacements.items():
        skill = skill.replace(key, val)
    return skill

def text_to_vector(text_list, model, debug_label=""):
    if not model:
        logger.warning("SBERT model is not loaded.")
        return np.zeros(VECTOR_SIZE)
    filtered = [t for t in text_list if isinstance(t, str) and t.strip()]
    if not filtered:
        return np.zeros(VECTOR_SIZE)
    try:
        embeddings = model.encode(filtered)
        return np.mean(embeddings, axis=0)
    except Exception as e:
        logger.error(f"Encoding failed for {debug_label}: {e}")
        return np.zeros(VECTOR_SIZE)

# --- Resume Vectors ---
def get_user_skills_vector(user, embeddings):
    resume = Resume.objects.filter(user=user).first()
    if not resume:
        return np.zeros(VECTOR_SIZE)
    skills = Skill.objects.filter(resume=resume).values_list('skill', flat=True)
    normalized_skills = [normalize_skill(s) for s in skills]
    return text_to_vector(normalized_skills, embeddings, debug_label=f"User Skills ({user.username})")

def get_experience_vector(user, embeddings):
    resume = Resume.objects.filter(user=user).first()
    if not resume:
        return np.zeros(VECTOR_SIZE)
    experiences = resume.experiences.all()
    texts = [f"{exp.job_title or ''} {exp.company or ''} {exp.description or ''}" for exp in experiences]
    return text_to_vector(texts, embeddings, debug_label=f"User Experience ({user.username})")

def get_project_vector(user, embeddings):
    resume = Resume.objects.filter(user=user).first()
    if not resume:
        return np.zeros(VECTOR_SIZE)
    projects = resume.projects.all()
    texts = [f"{proj.title or ''} {proj.description or ''}" for proj in projects]
    return text_to_vector(texts, embeddings, debug_label=f"User Projects ({user.username})")

def get_training_vector(user, embeddings):
    resume = Resume.objects.filter(user=user).first()
    if not resume:
        return np.zeros(VECTOR_SIZE)
    trainings = resume.trainings_courses.all()
    texts = [f"{tr.title or ''} {tr.institution or ''} {tr.description or ''}" for tr in trainings]
    return text_to_vector(texts, embeddings, debug_label=f"User Training ({user.username})")

def get_user_resume_vector(user, embeddings):
    skill_vec = get_user_skills_vector(user, embeddings)
    experience_vec = get_experience_vector(user, embeddings)
    project_vec = get_project_vector(user, embeddings)
    training_vec = get_training_vector(user, embeddings)
    combined = (
        SKILL_WEIGHT * skill_vec +
        EXPERIENCE_WEIGHT * experience_vec +
        PROJECT_WEIGHT * project_vec +
        TRAINING_WEIGHT * training_vec
    )
    norm = np.linalg.norm(combined)
    return combined / norm if norm != 0 else np.zeros(VECTOR_SIZE)

# --- Opportunity Vector ---
def get_opportunity_vector(opportunity, embeddings):
    title_vec = text_to_vector([opportunity.opportunity_name or ""], embeddings, debug_label=f"Opp Title ({opportunity.id})")
    desc_vec = text_to_vector([opportunity.description] if opportunity.description else [], embeddings)
    raw_skills = [normalize_skill(s.strip()) for s in (opportunity.required_skills or "").split(",") if s.strip()]
    skill_vec = text_to_vector(raw_skills, embeddings, debug_label=f"Opp Skills ({opportunity.id})")
    combined = (
        OPP_TITLE_WEIGHT * title_vec +
        OPP_DESC_WEIGHT * desc_vec +
        OPP_SKILL_WEIGHT * skill_vec
    )
    norm = np.linalg.norm(combined)
    return combined / norm if norm != 0 else np.zeros(VECTOR_SIZE)

# --- Recommendation Logic ---
def get_opportunities_with_vectors(embeddings):
    opportunities = Opportunity.objects.all()
    result = []
    for opp in opportunities:
        vec = get_opportunity_vector(opp, embeddings)
        if np.linalg.norm(vec) > 0:
            result.append({"id": opp.id, "opportunity": opp, "vector": vec})
    return result

def recommend_opportunities(user):
    model = get_sbert_model()
    if model is None:
        return []
    user_vector = get_user_resume_vector(user, model)
    if np.linalg.norm(user_vector) == 0:
        logger.warning(f"User {user.username} has no valid resume data.")
        return []

    user_location = user.location.strip().lower() if user.location else ""
    opportunities_data = get_opportunities_with_vectors(model)
    scores = []
    for item in opportunities_data:
        opp = item["opportunity"]
        opp_vector = item["vector"]
        job_location = opp.location.strip().lower() if opp.location else ""
        job_type = (opp.employment_type or "").strip().lower()
        if job_type in ['on-site', 'hybrid'] and user_location and job_location and user_location != job_location:
            continue
        similarity = cosine_similarity([user_vector], [opp_vector])[0][0]
        scores.append({"opportunity": opp, "similarity": similarity})

    if scores:
        sims = np.array([s["similarity"] for s in scores]).reshape(-1, 1)
        if np.all(sims == sims[0]):
            for s in scores:
                s["ranking_score"] = 0.5
        else:
            scaled = MinMaxScaler().fit_transform(sims)
            for i, s in enumerate(scores):
                s["ranking_score"] = scaled[i][0]
        scores.sort(key=lambda x: x["ranking_score"], reverse=True)
    return scores

def get_all_users_with_vectors(embeddings):
    users = User.objects.all()
    result = []
    for user in users:
        vec = get_user_resume_vector(user, embeddings)
        if np.linalg.norm(vec) > 0:
            result.append({"user": user, "vector": vec})
    return result

def recommend_users_for_opportunity(opportunity):
    model = get_sbert_model()
    if model is None:
        return []
    opp_vector = get_opportunity_vector(opportunity, model)
    if np.linalg.norm(opp_vector) == 0:
        logger.warning(f"Opportunity {opportunity.opportunity_name} has no valid data.")
        return []
    all_users = get_all_users_with_vectors(model)
    scores = []
    opp_location = opportunity.location.strip().lower() if opportunity.location else ""
    opp_type = (opportunity.employment_type or "").strip().lower()
    for data in all_users:
        user = data["user"]
        user_vec = data["vector"]
        user_location = user.location.strip().lower() if user.location else ""
        if opp_type in ['on-site', 'hybrid'] and opp_location and user_location and opp_location != user_location:
            continue
        sim = cosine_similarity([opp_vector], [user_vec])[0][0]
        scores.append({"user": user, "similarity": sim})
    if scores:
        sims = np.array([s["similarity"] for s in scores]).reshape(-1, 1)
        if np.all(sims == sims[0]):
            for s in scores:
                s["ranking_score"] = 0.5
        else:
            scaled = MinMaxScaler().fit_transform(sims)
            for i, s in enumerate(scores):
                s["ranking_score"] = scaled[i][0]
        scores.sort(key=lambda x: x["ranking_score"], reverse=True)
    return scores
