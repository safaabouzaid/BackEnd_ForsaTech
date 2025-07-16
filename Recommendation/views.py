from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import time
from human_resources.models import humanResources,Opportunity,JobApplication
from django.http import JsonResponse
from .tasks import generate_all_opportunity_embeddings,generate_all_resume_embeddings
from .utils import *
from devloper.models import Resume

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommend_opportunities_view(request):
    user = request.user
    user_location = user.location.strip().lower() if user.location else None

    start_time = time.time()
    recommendations = recommend_opportunities(user)
    end_time = time.time()

    all_opportunity_data = []

    for item in recommendations:
        opportunity = item["opportunity"]
        score = item["ranking_score"]

        employment_type = (opportunity.employment_type or "").strip().lower()
        opportunity_location = (opportunity.location or "").strip().lower()

        if employment_type != "remote":
            if not user_location or user_location != opportunity_location:
                continue

        recommended_users = recommend_users_for_opportunity(opportunity)
        applied_user_ids = set(
            JobApplication.objects.filter(opportunity=opportunity)
            .values_list('user__id', flat=True)
        )

        filtered_users = [
            {
                "user_id": u["user"].id,
                "username": u["user"].username,
                "email": u["user"].email,
                "similarity_score": round(u["ranking_score"], 3)
            }
            for u in recommended_users
            if u["user"].id in applied_user_ids
        ]

        all_opportunity_data.append({
            "id": opportunity.id,
            "title": opportunity.opportunity_name,
            "description": opportunity.description,
            "similarity_score": round(score, 3),
        })

    return Response(all_opportunity_data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommend_users_view(request):
    try:
        hr = humanResources.objects.get(user=request.user)
    except humanResources.DoesNotExist:
        return Response({"error": "You are not an HR user."}, status=403)

    company = hr.company
    plan = company.subscription_plan

    if not plan:
        return Response({"error": "No subscription plan assigned."}, status=403)

    if plan.max_candidate_suggestions == 0 or plan.candidate_suggestions == 'none':
        return Response({"error": "Your plan does not allow candidate suggestions."}, status=403)

    if plan.max_candidate_suggestions and company.used_candidate_suggestions_count >= plan.max_candidate_suggestions:
        return Response({"error": "You have used all your allowed candidate suggestions."}, status=403)

    company.used_candidate_suggestions_count += 1
    company.save()

    opportunities = Opportunity.objects.filter(company=hr.company)
    result = []

    for opportunity in opportunities:
        recommendations = recommend_users_for_opportunity(opportunity)

        # المتقدمين فقط
        applied_user_ids = set(
            JobApplication.objects.filter(opportunity=opportunity)
            .values_list('user__id', flat=True)
        )

        # أفضل 5 من الذين قدموا
        filtered_recommendations = [
            item for item in recommendations if item["user"].id in applied_user_ids
        ]
        filtered_recommendations.sort(key=lambda x: x["ranking_score"], reverse=True)
        
        top_candidates = []
        for item in filtered_recommendations[:5]:
            user = item["user"]
            resume = user.resumes.order_by('-created_at').first()
            skills = []
            if resume:
                skills = list(resume.skills.values_list('skill', flat=True))
        
            top_candidates.append({
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "similarity_score": round(item["ranking_score"], 3),
                "skills": skills
            })

        result.append({
            "opportunity_id": opportunity.id,
            "opportunity_name": opportunity.opportunity_name,
            "description": opportunity.description,
            "posting_date": opportunity.posting_date,
            "application_deadline": opportunity.application_deadline,
            "salary_range": opportunity.salary_range,
            "location": opportunity.location,
            "experience_level": opportunity.experience_level,
            "opportunity_status": opportunity.status,
            "recommendations": top_candidates,
        })

    return Response(result)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommend_applicants_for_opportunity(request, opportunity_id):
    try:
        hr = humanResources.objects.get(user=request.user)
    except humanResources.DoesNotExist:
        return Response({"error": "You are not an HR user."}, status=403)

    try:
        opportunity = Opportunity.objects.get(id=opportunity_id, company=hr.company)
    except Opportunity.DoesNotExist:
        return Response({"error": "Opportunity not found or does not belong to your company."}, status=404)

    recommendations = recommend_users_for_opportunity(opportunity)

    applied_user_ids = set(
        JobApplication.objects.filter(opportunity=opportunity)
        .values_list('user__id', flat=True)
    )

    filtered_recommendations = [
        item for item in recommendations if item["user"].id in applied_user_ids
    ]
    filtered_recommendations.sort(key=lambda x: x["ranking_score"], reverse=True)
    


    
    top_applicants = []
    for item in filtered_recommendations[:5]:
        user = item["user"]
        resume = user.resumes.order_by('-created_at').first()
        job_application = JobApplication.objects.filter(opportunity=opportunity, user=user).first()
        skills = []
        if resume:
            skills = list(resume.skills.values_list('skill', flat=True))
    
    
        top_applicants.append({
            
            "application_id": job_application.id if job_application else None,
            "username": user.username,
            "email": user.email,
            "similarity_score": round(item["ranking_score"], 3),
            "skills": skills
        })
                        
    return Response({
        "opportunity_id": opportunity.id,
        "opportunity_name": opportunity.opportunity_name,
        "opportunity_status": opportunity.status,
        "top_applicants": top_applicants[:5]  
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommend_skills_view(request):
    user = request.user
    recommendations = recommend_opportunities(user)
    skill_suggestions = suggest_additional_skills(user, recommendations)
    return Response(skill_suggestions)



def update_embeddings(request):
    generate_all_opportunity_embeddings()
    return JsonResponse({"status": "done"})



def update_resumes_embeddings(request):
    generate_all_resume_embeddings()
    return JsonResponse({"status": "done"})
