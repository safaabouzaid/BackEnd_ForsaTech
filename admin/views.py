from django.shortcuts import get_object_or_404
from django.forms import model_to_dict
from rest_framework.decorators import api_view, permission_classes, authentication_classes, parser_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from human_resources.models import Company,CompanyAd, Opportunity,JobApplication,Complaint,humanResources,SubscriptionPlan,SubscriptionChangeRequest
from .serializers import CompanySerializer ,CompanyAdSerializer ,CompanyDetailSerializer,DashboardStatsSerializer
from human_resources.filters import CompaniesFilter
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Count,Avg, Sum
from datetime import datetime
from django.db.models.functions import TruncMonth
from .serializers import ComplaintSerializer
from rest_framework import status
from devloper.models import User
from django.core.mail import send_mail
from django.conf import settings
import random
import string
from human_resources.serializer import SubscriptionPlanSerializer,SubscriptionChangeRequestSerializer
from django.db.models import Q


def generate_password(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))


@api_view(['POST'])
@permission_classes([IsAdminUser])
def createCompany(request):
    try:
        free_plan = SubscriptionPlan.objects.get(name='free')
    except SubscriptionPlan.DoesNotExist:
        return Response({"error": "Free plan not found. Please create it first."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    serializer = CompanySerializer(data=request.data)
    if serializer.is_valid():
        company = serializer.save(subscription_plan=free_plan)

        email = request.data.get('email')
        password = generate_password()

        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already in use"}, status=status.HTTP_400_BAD_REQUEST)

        hr_user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )


        humanResources.objects.create(
            user=hr_user,
            company=company,
            location=company.address
        )

        subject = "Your company account has been created on the Forsa-tech platform"

        message = f"""
        Hello {company.name} 🌟,

        Your company has been successfully created on the Forsa-Tech platform.

        You can log in using the following information:
        Email: {email}
        Password: {password}

        Please change your password after your first login.

        Regards,
         Forsa-Tech Team
        """
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

        return Response({
            "message": "Company and HR account created successfully",
            "data": serializer.data,
            "hr_credentials": {
                "email": email,
                "password": password
            }
        }, status=status.HTTP_201_CREATED)

    return Response({"error": "Invalid data", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

#====================================== ALL COmpany  ============================================#

@api_view(['GET'])
#@permission_classes([IsAdminUser])
def listCompanies(request):
    #companies = Company.objects.all()
    filterset =CompaniesFilter(request.GET,queryset=Company.objects.all().order_by('id'))
    #serializer = CompanySerializer(companies, many=True)
    serializer = CompanySerializer(filterset.qs, many=True)

    return Response({"message": "Companies retrieved successfully", "data": serializer.data}, status=status.HTTP_200_OK)


@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([IsAdminUser])
def updateCompany(request, pk):
    company = get_object_or_404(Company, pk=pk)
    serializer = CompanySerializer(company, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Company updated successfully", "data": serializer.data})
    return Response({"error": "Invalid data", "details": serializer.errors},
     status=status.HTTP_400_BAD_REQUEST)




@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def deleteCompany(request, pk):
    company = get_object_or_404(Company, pk=pk)
    company.delete()
    return Response({"message": "Company deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


#==========================================   Company Ads  ====================================#

@api_view(['GET', 'POST'])   
@permission_classes([])       
def list_create_ads(request):
    if request.method == 'GET':
        ads = CompanyAd.objects.all()
        serializer = CompanyAdSerializer(ads, many=True)
        return Response({"message": "Company ads retrieved successfully", "data": serializer.data}, status=status.HTTP_200_OK)

    elif request.method == 'POST':
             
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response({"error": "You do not have permission to perform this action."},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = CompanyAdSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Company ad created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"error": "Failed to create company ad", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def suspend_ad(request, ad_id):
    ad = get_object_or_404(CompanyAd, pk=ad_id)

    if not ad.is_active:
        return Response({"message": "Ad is already suspended."}, status=status.HTTP_400_BAD_REQUEST)

    ad.is_active = False
    ad.save()

    company_email = ad.company.email
    if not company_email:
        return Response({"error": "Company does not have an email address."}, status=status.HTTP_400_BAD_REQUEST)

    subject = f"Your advertisement '{ad.title}' has been suspended"
    message = f"""
Hello {ad.company.name} 🌟,

Your advertisement titled '{ad.title}' has been suspended by the administration.

Please contact the security team to understand the reason for this suspension.

Regards,
Forsa-Tech Team
    """

    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [company_email], fail_silently=False)
    except Exception as e:
        return Response(
            {"error": f"Ad suspended but failed to send email notification. Error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return Response(
        {"message": f"Ad '{ad.title}' suspended and notification email sent to {company_email}."},
        status=status.HTTP_200_OK
    )

#===================================   Company Details  ==================================#

@api_view(['GET'])
def get_company_profile(request, pk):
    company = get_object_or_404(Company, pk=pk)
    serializer = CompanyDetailSerializer(company)
    return Response({'company': serializer.data}, status=status.HTTP_200_OK)

#====================================== dashboard stats. ========================================#

@api_view(['GET'])
@permission_classes([IsAdminUser]) 
def dashboard_stats(request):

#Number of Companies

    num_companies = Company.objects.count()

#Most Hiring Companies

    most_hiring_company = (
    Company.objects.annotate(num_jobs=Count('opportunity'))
    .filter(num_jobs__gt=0)
    .order_by('-num_jobs')
    .first()  
)

    most_hiring_name = most_hiring_company.name if most_hiring_company else "N/A"
    most_hiring_count = most_hiring_company.num_jobs if most_hiring_company else 0


    # Most Demanded Jobs
    most_demanded_jobs = (
        JobApplication.objects.values('opportunity__opportunity_name')  
        .annotate(count=Count('id'))
        .order_by('-count')[:3]
    )
    most_demanded_titles = [job['opportunity__opportunity_name'] for job in most_demanded_jobs]

    # Highest Paying Jobs
    def extract_max_salary(opportunity):
        try:
            return int(opportunity.salary_range.split('-')[-1])
        except:
            return 0
    
    opportunities = Opportunity.objects.exclude(salary_range__isnull=True)
    highest_salary_opportunity = Opportunity.objects.exclude(salary_range__isnull=True).order_by('-salary_range').first()
    highest_paying_job = {
        "title": highest_salary_opportunity.opportunity_name if highest_salary_opportunity else "N/A",  
        "salary": highest_salary_opportunity.salary_range if highest_salary_opportunity else "N/A"
    }



####Job Demand Change Over Months
    jobs_by_month = (
        Opportunity.objects.filter(created_at__year=datetime.now().year)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    line_chart_data = [
        {"month": item["month"].strftime("%B"), "count": item["count"]}
        for item in jobs_by_month
    ]


    # Job Distribution by Specialization
    jobs_by_title = (
        Opportunity.objects.values('opportunity_name')  
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    pie_chart_data = [
        {"name": item["opportunity_name"], "value": item["count"]}   
        for item in jobs_by_title
    ]

    # Active Jobs
    active_jobs = Opportunity.objects.filter(
        application_deadline__gte=datetime.now()
    ).count()
    

    avg_company_size = Company.objects.aggregate(
        avg_size=Avg('employees')
    )
    
    new_companies = Company.objects.filter(
        created_at__month=datetime.now().month
    ).count()

    #Premium Members Count
    premium_members_count = Company.objects.filter(
        Q(subscription_plan__price__gt=0)
    ).count()


    data = {
        "num_companies": num_companies,
        "most_hiring_company": most_hiring_name,
        "most_hiring_company_count": most_hiring_count,
        "most_demanded_jobs": most_demanded_titles,
        "highest_paying_job": highest_paying_job,
        "line_chart_data": line_chart_data,
        "pie_chart_data": pie_chart_data,
        "active_jobs": active_jobs,
        "avg_company_size": avg_company_size['avg_size'] or 0,
        "new_companies": new_companies,
        "premium_members": premium_members_count
    }

    serializer = DashboardStatsSerializer(data)
    return Response(serializer.data, status=status.HTTP_200_OK)



#============================================== complaints ==================================================##




@api_view(['GET'])
@permission_classes([IsAdminUser])   
def get_all_complaints(request):
    complaints = Complaint.objects.all()    
    serializer = ComplaintSerializer(complaints, many=True)
    return Response({'complaints': serializer.data}, status=status.HTTP_200_OK)

#=========================================  Update status  =============================#

@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def update_complaint_status(request, complaint_id):
    complaint = get_object_or_404(Complaint, pk=complaint_id)
    status_value = request.data.get('status')  

    if not status_value:
        return Response({"message": "Status is required."}, status=status.HTTP_400_BAD_REQUEST)

    if status_value not in ['new',  'resolved']:
        return Response({"message": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)

    complaint.status = status_value
    complaint.save()

    serializer = ComplaintSerializer(complaint)
    return Response({"message": "Complaint status updated", 'complaint': serializer.data}, status=status.HTTP_200_OK)



#============================================ Plans ===========================================#

@api_view(['GET'])
def list_subscription_plans(request):
    plans = SubscriptionPlan.objects.all()
    serializer = SubscriptionPlanSerializer(plans, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_subscription_plan(request):
    serializer = SubscriptionPlanSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def update_subscription_plan(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, pk=plan_id)
    
    serializer = SubscriptionPlanSerializer(plan, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_subscription_plan(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, pk=plan_id)
    plan.delete()
    return Response({"message": "Subscription plan deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAdminUser]) 
def list_subscription_requests(request):
    requests = SubscriptionChangeRequest.objects.all().order_by('-created_at')
    serializer = SubscriptionChangeRequestSerializer(requests, many=True)
    return Response(serializer.data)



@api_view(['POST'])
@permission_classes([IsAdminUser])  
def handle_subscription_request(request):
    request_id = request.data.get('request_id')
    action = request.data.get('action')   

    if not request_id or action not in ['approve', 'reject']:
        return Response({"error": "request_id and valid action required."}, status=400)

    try:
        sub_request = SubscriptionChangeRequest.objects.get(id=request_id)
    except SubscriptionChangeRequest.DoesNotExist:
        return Response({"error": "Request not found."}, status=404)

    if sub_request.status != 'pending':
        return Response({"error": "Request already processed."}, status=400)

    if action == 'approve':
        sub_request.company.subscription_plan = sub_request.requested_plan
        sub_request.company.save()
        sub_request.status = 'approved'
    else:
        sub_request.status = 'rejected'

    sub_request.save()
    return Response({"message": f"Request {action}d successfully."})


#=========================================company registration================================================#

@api_view(['POST'])
def request_company_registration(request):
    company_name = request.data.get('company_name')
    contact_email = request.data.get('contact_email')

    if not company_name or not contact_email:
        return Response({'error': 'Missing data'}, status=400)

    # Send email to admin
    send_mail(
        subject='New Company Registration Request',
        message=f'Company Name: {company_name}\nContact Email: {contact_email}',
        from_email='noreply@yourplatform.com',
        recipient_list=['abouzaidsafa@gmail.com'],
    )

    return Response({'message': 'Request sent successfully'})



#=============================================================================================#


@api_view(['POST'])
@permission_classes([IsAdminUser])
def companies_by_opportunity(request):
    opportunity_name = request.data.get('opportunity_name')
    if not opportunity_name:
        return Response({"error": "Missing opportunity_name"}, status=400)

    opportunities = Opportunity.objects.filter(opportunity_name=opportunity_name)

    if not opportunities.exists():
        return Response({"error": "No opportunities found for this name"}, status=404)

    companies = Company.objects.filter(opportunity__in=opportunities).distinct()

    serializer = CompanySerializer(companies, many=True)
    return Response(serializer.data)
