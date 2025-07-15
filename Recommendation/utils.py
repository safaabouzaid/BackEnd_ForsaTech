import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import logging
from devloper.models import Resume, Skill, User
from human_resources.models import Opportunity
from sentence_transformers import SentenceTransformer

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
    if sbert_model is None:
        sbert_model = SentenceTransformer('./my_local_sbert')
    return sbert_model

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
        batch_size = 32  
        embeddings = []
        
        for i in range(0, len(filtered), batch_size):
            batch = filtered[i:i+batch_size]
            batch_embeds = model.encode(batch)
            embeddings.append(batch_embeds)
        
        embeddings = np.vstack(embeddings)  
        return np.mean(embeddings, axis=0)  
    
    except Exception as e:
        logger.error(f"Encoding failed for {debug_label}: {e}")
        return np.zeros(VECTOR_SIZE)

# --- Resume Vectors ---
def get_user_resume_vector(user, model=None):
    resume = Resume.objects.filter(user=user).first()
    if resume and resume.embedding:
        return np.array(resume.embedding)  

    model = model or get_sbert_model()
    if not model or not resume:
        return np.zeros(VECTOR_SIZE)

    skills = Skill.objects.filter(resume=resume).values_list('skill', flat=True)
    skills_vec = text_to_vector([normalize_skill(s) for s in skills], model, f"User Skills ({user.username})")

    experiences = resume.experiences.all()
    exp_texts = [f"{e.job_title or ''} {e.company or ''} {e.description or ''}" for e in experiences]
    exp_vec = text_to_vector(exp_texts, model, f"User Experience ({user.username})")

    projects = resume.projects.all()
    proj_texts = [f"{p.title or ''} {p.description or ''}" for p in projects]
    proj_vec = text_to_vector(proj_texts, model, f"User Projects ({user.username})")

    trainings = resume.trainings_courses.all()
    train_texts = [f"{t.title or ''} {t.institution or ''} {t.description or ''}" for t in trainings]
    train_vec = text_to_vector(train_texts, model, f"User Training ({user.username})")

    combined = (
        SKILL_WEIGHT * skills_vec +
        EXPERIENCE_WEIGHT * exp_vec +
        PROJECT_WEIGHT * proj_vec +
        TRAINING_WEIGHT * train_vec
    )
    norm = np.linalg.norm(combined)
    final_vec = combined / norm if norm != 0 else np.zeros(VECTOR_SIZE)

    resume.embedding = final_vec.tolist()
    resume.save()

    return final_vec

# --- Opportunity Vector ---
def get_opportunity_vector(opportunity, model=None):
    if opportunity.embedding:
        vec = np.array(opportunity.embedding)
        if np.linalg.norm(vec) > 0:
            return vec
    return None

# --- Recommendation Logic ---
def get_opportunities_with_vectors():
    opportunities = Opportunity.objects.all()
    result = []
    for opp in opportunities:
        vec = get_opportunity_vector(opp)
        if vec is not None:
            result.append({"opportunity": opp, "vector": vec})
    return result

def recommend_opportunities(user):
    user_vector = get_user_resume_vector(user)
    if np.linalg.norm(user_vector) == 0:
        logger.warning(f"User {user.username} has no valid resume data.")
        return []

    user_location = (user.location or "").strip().lower()
    opportunities = get_opportunities_with_vectors()
    scores = []
    for item in opportunities:
        opp = item["opportunity"]
        opp_vector = item["vector"]
        job_location = (opp.location or "").strip().lower()
        job_type = (opp.employment_type or "").strip().lower()

        if job_type in ['on-site', 'hybrid'] and user_location and job_location and user_location != job_location:
            continue
        if opp_vector is None or np.linalg.norm(opp_vector) == 0:
            continue

        sim = cosine_similarity([user_vector], [opp_vector])[0][0]
        scores.append({"opportunity": opp, "similarity": sim})

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

    return scores[:10]

def recommend_users_for_opportunity(opportunity):
    opp_vector = get_opportunity_vector(opportunity)
    if opp_vector is None or np.linalg.norm(opp_vector) == 0:
        logger.warning(f"Opportunity {opportunity.opportunity_name} has no valid data.")
        return []

    opp_location = (opportunity.location or "").strip().lower()
    opp_type = (opportunity.employment_type or "").strip().lower()

    resumes = Resume.objects.select_related('user').filter(embedding__isnull=False)
    user_resume_map = {resume.user_id: resume for resume in resumes}

    all_users = User.objects.filter(id__in=user_resume_map.keys()).distinct()
    valid_users = []
    user_vectors = []
    
    for user in all_users:
        resume = user_resume_map.get(user.id)
        if not resume or not resume.embedding:
            continue
    
        user_vector = np.array(resume.embedding)
        if np.linalg.norm(user_vector) == 0:
            continue
    
        user_location = (user.location or "").strip().lower()
        if opp_type in ['on-site', 'hybrid'] and opp_location and user_location and opp_location != user_location:
            continue
    
        valid_users.append(user)
        user_vectors.append(user_vector)
    
    if not user_vectors:
        return []
    
    user_matrix = np.vstack(user_vectors)  # مصفوفة كل الـ vectors
    similarities = cosine_similarity([opp_vector], user_matrix)[0]  # دفعة وحدة!
    
    scores = [{"user": u, "similarity": s} for u, s in zip(valid_users, similarities)]
    

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



def suggest_additional_skills(user, opportunities):
    
    resume = Resume.objects.filter(user=user).first()
    if not resume:
        return []
    
    user_skills = set([normalize_skill(s) for s in Skill.objects.filter(resume=resume).values_list('skill', flat=True)])
    
    suggestions = []
    for item in opportunities:
        opp = item["opportunity"]
        score = item["ranking_score"]

        opp_skills = set([
            normalize_skill(s.strip()) for s in (opp.required_skills or "").split(",") if s.strip()
        ])
        
        missing_skills = list(opp_skills - user_skills)
        
        suggestions.append({
            "opportunity_id": opp.id,
            "opportunity_name": opp.opportunity_name,
            "description": opp.description,
            "similarity_score": round(score, 3),
            "missing_skills": missing_skills
        })

    return suggestions
