from django.forms import model_to_dict
from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from human_resources.models import Company, Opportunity
from human_resources.serializer import *
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from .models import User  ,humanResources,OpportunityName,Opportunity, JobApplication
from django.utils import timezone
from devloper.models import User, Resume, Education, Experience, Language
from devloper.serializer import ResumeSerializer


@api_view(['POST'])
def loginHumanResource(request):
    if request.method == 'GET':
        return Response({'error': 'This endpoint only accepts POST requests'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    data = request.data
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)
    
    if user is None:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    if not user.is_active:
        return Response({'error': 'Account is disabled'}, status=status.HTTP_403_FORBIDDEN)

    
    if not hasattr(user, 'humanresources'):
        return Response({'error': 'This account is not authorized to access this endpoint'}, status=status.HTTP_403_FORBIDDEN)

    refresh = RefreshToken.for_user(user)
    # جبت معلومات الشركة
    hr_profile = user.humanresources
    company = hr_profile.company
    company_name = company.name if company else None
    company_logo = request.build_absolute_uri(company.logo.url) if company and company.logo else None


    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'company_name': company_name,
        'company_logo': company_logo
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createOpportunity(request):
    user = request.user

    try:
        hr = humanResources.objects.get(user=user)
        company = hr.company
    except humanResources.DoesNotExist:
        return Response({"error": "User is not registered as HR"}, status=status.HTTP_403_FORBIDDEN)
    except Company.DoesNotExist:
        return Response({"error": "HR is not associated with any company"}, status=status.HTTP_400_BAD_REQUEST)

    subscription_plan = company.subscription_plan  
    job_post_limit = subscription_plan.job_post_limit if subscription_plan else None

    current_month = timezone.now().month
    current_year = timezone.now().year

    current_jobs_count = Opportunity.objects.filter(
        company=company,
        created_at__year=current_year,
        created_at__month=current_month
    ).count()

    if job_post_limit is not None and current_jobs_count >= job_post_limit:
        return Response(
            {"error": "Job posting limit reached for this month."},
            status=status.HTTP_403_FORBIDDEN
        )

    data = request.data.copy()
    data.pop('company', None)

    serializer = OpportunitySerializer1(data=data)

    if serializer.is_valid():
        opportunity = Opportunity.objects.create(company=company, **serializer.validated_data)
        result = OpportunityDetailSerializer(opportunity)
        return Response({"opportunity": result.data}, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def deleteOpportunity(request,pk):
    opportunity=get_object_or_404(Opportunity,id=pk)
    opportunity.delete()
    return Response({'Details':"Delete action is done"},status=status.HTTP_200_OK)







@csrf_exempt
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateOpportunity(request,pk):
    opportunity=get_object_or_404(Opportunity,id=pk)


    # if opportunity.request!=request.user:
    #     return Response({"errors": "sorry, you cannot update this opportunity"}, status=status.HTTP_403_FORBIDDEN)4

    if "Opportunity" in request.data:
        data = request.data["Opportunity"]
    else:
        data = request.data 

    serializer=OpportunitySerializer1(opportunity,data=data)
    if serializer.is_valid():
        serializer.save()
        return Response ({"Update opportunity":serializer.data})
    

    return Response({"error ":serializer.errors},status=status.HTTP_400_BAD_REQUEST)




@api_view(['Get'])
@permission_classes([IsAuthenticated])
def getByIdOpportunity(requst,pk):
    opportunity=get_object_or_404(Opportunity,id=pk)
    serializer=OpportunitySerializer(opportunity,many=False)
    print(opportunity)
    return Response({'Opportunity':serializer.data})

#####
### JobCard  
@api_view(['Get'])
def getJobCard(request):
    opportunities = Opportunity.objects.all()
    serializer = OpportunitySerializer1(opportunities, many=True)
    return Response(serializer.data)


###Forsazforfile  

@api_view(['GET'])
def opportunity_list(request):
    opportunities = Opportunity.objects.all()
    serializer = OpportunitySerializer1(opportunities, many=True)
    return Response(serializer.data)



###forsa by id 
##
@api_view(['GET'])
def opportunityById(request,pk ):
    opportunities = Opportunity.objects.get(pk=pk)
    serializer = OpportunitySerializer(opportunities)
    return Response(serializer.data)
    
    
    
###    
## apply forsa 

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_for_opportunity(request, opportunity_id):
    user = request.user

    missing_sections = []

    if not Education.objects.filter(resume__user=user).exists():
        missing_sections.append("education")
    if not Experience.objects.filter(resume__user=user).exists():
        missing_sections.append("experience")
    if not Language.objects.filter(resume__user=user).exists():
        missing_sections.append("language")

    if missing_sections:
        return Response({
            "error": "You must complete all required sections before applying.",
            "missing_sections": missing_sections
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        opportunity = Opportunity.objects.get(id=opportunity_id)
    except Opportunity.DoesNotExist:
        return Response({"error": "Opportunity not found."}, status=status.HTTP_404_NOT_FOUND)

    if JobApplication.objects.filter(user=user, opportunity=opportunity).exists():
        return Response({"error": "You have already applied for this opportunity."},
                        status=status.HTTP_400_BAD_REQUEST)

    application = JobApplication.objects.create(
        user=user,
        opportunity=opportunity,
        status='pending'
    )

    return Response({
        "message": "Application submitted successfully.",
        "application_id": application.id,
        "status": application.status
    }, status=status.HTTP_200_OK)



###### resume details for developer

@api_view(['GET'])
def user_resume(request):
    username = request.data.get('username')
    if not username:
        return Response({"detail": "Username is required."}, status=status.HTTP_400_BAD_REQUEST)

    user = get_object_or_404(User, username=username)
    resume = Resume.objects.filter(user=user).last()

    if not resume:
        return Response({"detail": "No resume found for this user."}, status=status.HTTP_404_NOT_FOUND)

    personal_details = {
        "username": user.username,
        "email": user.email,
        "phone": user.phone,
        "location": user.location,
        "github_link": user.github_link,
        "linkedin_link": user.linkedin_link
    }

    resume_data = ResumeSerializer(resume).data
    resume_data.pop("pdf_file", None)
    resume_data.pop("created_at", None)

    response_data = {
        "personal_details": personal_details,
        "summary": resume_data["summary"],
        "skills": resume_data["skills"],
        "education": resume_data["education"],
        "projects": resume_data["projects"],
        "experiences": resume_data["experiences"],
        "trainings_courses": resume_data["trainings_courses"]
    }

    return Response(response_data, status=status.HTTP_200_OK)

##create ad

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_company_ad(request):
    try:
        hr = humanResources.objects.get(user=request.user)
        company = hr.company
        if not company:
            return Response({"detail": "This user does not belong to any company."}, status=status.HTTP_400_BAD_REQUEST)
    except humanResources.DoesNotExist:
        return Response({"detail": "  user is not  HR."}, status=status.HTTP_403_FORBIDDEN)

    serializer = CompanyAdSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(company=company)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#===============================    get_opportunity_names   =================================#

@api_view(['GET'])
def get_opportunity_names(request):
    names = OpportunityName.objects.values_list('name', flat=True)
    return Response(names)


#================get mycomany opp.===========#
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_opportunities_for_hr_company(request):
    user = request.user

    if not hasattr(user, 'humanresources') or not user.humanresources.company:
        return Response({'error': 'HR user or company not found'}, status=status.HTTP_403_FORBIDDEN)

    company = user.humanresources.company
    opportunities = Opportunity.objects.filter(company=company)
    
    serializer = OpportunitySerializer1(opportunities, many=True)
    return Response({'opportunities': serializer.data}, status=status.HTTP_200_OK)





###############33
@api_view(['GET'])
def opportunity_details_view(request):
    opportunity_id = request.headers.get('opportunity-id')

    if not opportunity_id:
        return Response({"error": "Missing opportunity-id in headers"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        opportunity = Opportunity.objects.get(id=opportunity_id)
    except Opportunity.DoesNotExist:
        return Response({"error": "Opportunity not found"}, status=status.HTTP_404_NOT_FOUND)

    #   يلي قدموا
    applications = JobApplication.objects.filter(opportunity=opportunity)
    users = [app.user for app in applications]
    applicants_data = ApplicantSerializer(users, many=True).data

    opportunity_data = OpportunityDetailSerializer(opportunity).data

    return Response({
        "opportunity_name": opportunity.opportunity_name, 
        "opportunity": opportunity_data,
        "applicants": applicants_data,
    }, status=status.HTTP_200_OK)





################## change plan
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_subscription_change(request):
    user = request.user
    try:
        hr = humanResources.objects.get(user=user)
        company = hr.company
    except:
        return Response({"error": "User is not HR or has no company."}, status=403)

    requested_plan_id = request.data.get('requested_plan')
    if not requested_plan_id:
        return Response({"error": "requested_plan is required."}, status=400)

    if SubscriptionChangeRequest.objects.filter(company=company, status='pending').exists():
        return Response({"error": "You already have a pending request."}, status=400)

    try:
        plan = SubscriptionPlan.objects.get(id=requested_plan_id)
    except SubscriptionPlan.DoesNotExist:
        return Response({"error": "Requested plan not found."}, status=404)

    request_obj = SubscriptionChangeRequest.objects.create(company=company, requested_plan=plan)
    serializer = SubscriptionChangeRequestSerializer(request_obj)
    return Response(serializer.data, status=201)
