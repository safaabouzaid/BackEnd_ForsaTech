from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .utils import recommend_opportunities,recommend_users_for_opportunity
import time
from human_resources.models import humanResources,Opportunity,JobApplication

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
            "top_candidates": filtered_users
        })

    return Response(all_opportunity_data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommend_users_view(request):
    try:
        hr = humanResources.objects.get(user=request.user)
    except humanResources.DoesNotExist:
        return Response({"error": "You are not an HR user."}, status=403)

    opportunities = Opportunity.objects.filter(company=hr.company)
    result = []

    for opportunity in opportunities:
        recommendations = recommend_users_for_opportunity(opportunity)

        # المتقدمين بس
        applied_user_ids = set(
            JobApplication.objects.filter(opportunity=opportunity)
            .values_list('user__id', flat=True)
        )

        # أفضل 5  قدموا
        top_candidates = []
        for item in recommendations:
            user = item["user"]
            if user.id not in applied_user_ids:
                continue

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

            if len(top_candidates) == 5:
                break

        result.append({
            "opportunity_id": opportunity.id,
            "opportunity_name": opportunity.opportunity_name,
            "description": opportunity.description,
            "salary_range": opportunity.salary_range,
            "location": opportunity.location,
            "experience_level": opportunity.experience_level,
            "recommendations": top_candidates
        })

    return Response(result)
