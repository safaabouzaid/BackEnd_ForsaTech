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



    filtered_recommendations = []

    for item in recommendations:
        opportunity = item["opportunity"]
        score = item["ranking_score"]

        employment_type = (opportunity.employment_type or "").strip().lower()
        opportunity_location = (opportunity.location or "").strip().lower()

        if employment_type != "remote":
            if not user_location or user_location != opportunity_location:
                continue

        filtered_recommendations.append({
            "id": opportunity.id,
            "title": opportunity.opportunity_name,
            "description": opportunity.description,
            "similarity_score": round(score, 3)
        })

    return Response(filtered_recommendations)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommend_users_view(request, opportunity_id):
    try:
        hr = humanResources.objects.get(user=request.user)
    except humanResources.DoesNotExist:
        return Response({"error": "You are not an HR user."}, status=403)

    try:
        opportunity = Opportunity.objects.get(id=opportunity_id, company=hr.company)
    except Opportunity.DoesNotExist:
        return Response({"error": "Opportunity not found or does not belong to your company."}, status=404)

    opportunity_location = (opportunity.location or "").strip().lower()
    employment_type = (opportunity.employment_type or "").strip().lower()

    recommendations = recommend_users_for_opportunity(opportunity)

    #  بس  اللي قدموا عالفرصة
    applied_user_ids = set(
        JobApplication.objects.filter(opportunity=opportunity)
        .values_list('user__id', flat=True)
    )

    filtered_recommendations = [
        {
            "user_id": item["user"].id,
            "username": item["user"].username,
            "email": item["user"].email,
            "similarity_score": round(item["ranking_score"], 3)
        }
        for item in recommendations
        if item["user"].id in applied_user_ids
    ]

    return Response(filtered_recommendations)










