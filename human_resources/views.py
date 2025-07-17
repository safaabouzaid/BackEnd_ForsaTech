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
from .models import User  ,humanResources,OpportunityName,Opportunity, JobApplication,InterviewSchedule,PasswordResetCode,PasswordResetCode
from django.utils import timezone
from devloper.models import User, Resume, Education, Experience, Language
from devloper.serializer import ResumeSerializer
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
from django.db.models import Count
from .models import SubscriptionChangeRequest
from admin.serializers import CompanyDetailSerializer
from .utils import send_push_notification
from firebase_admin import messaging
import random
import string


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
    company_logo = request.build_absolute_uri(company.logo) if company and company.logo else None



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


   #

@api_view(['Get'])
@permission_classes([IsAuthenticated])
def getByIdOpportunity(requst,pk):
    opportunity=get_object_or_404(Opportunity,id=pk)
    serializer=OpportunitySerializer(opportunity,many=False)
    print(opportunity)
    return Response({'Opportunity':serializer.data})


#============================================== JobCard =================================================#
@api_view(['Get'])
def getJobCard(request):
    opportunities = Opportunity.objects.all()
    serializer = OpportunitySerializer1(opportunities, many=True)
    return Response(serializer.data)


#============================================Forsazforfile  ==============================================#

@api_view(['GET'])
def opportunity_list(request):
    opportunities = Opportunity.objects.all()
    serializer = OpportunitySerializer1(opportunities, many=True)
    return Response(serializer.data)



#=========================================forsa by id ===========================================#

@api_view(['GET'])
def opportunityById(request,pk ):
    opportunities = Opportunity.objects.get(pk=pk)
    serializer = OpportunitySerializer1(opportunities)
    return Response(serializer.data)
    
    
    
#===================================== apply forsa =======================================#

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

    company_hr = getattr(opportunity.company, 'hr_user', None) or getattr(opportunity.company, 'humanresources', None)
    if company_hr:

        hr_user = getattr(company_hr, 'user', company_hr)  
        hr_token = getattr(hr_user, 'device_token', None)  

        if hr_token:
            send_push_notification(
                token=hr_token,
                title="📢  New job Application ",
                body=f"{user.username} Apply for : {opportunity.title}"
            )

    return Response({
        "message": "Application submitted successfully.",
        "application_id": application.id,
        "status": application.status
    }, status=status.HTTP_200_OK)



#========================== resume details for developer========================================#

@api_view(['POST'])
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

#=========================================== create AD==================================#

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


#============================== get mycomany OPP.=====================================#
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






#======================================== OPP. details ==============================================#
@api_view(['GET'])
def opportunity_details_view(request):
    opportunity_id = request.headers.get('opportunity-id')

    if not opportunity_id:
        return Response({"error": "Missing opportunity-id in headers"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        opportunity = Opportunity.objects.get(id=opportunity_id)
    except Opportunity.DoesNotExist:
        return Response({"error": "Opportunity not found"}, status=status.HTTP_404_NOT_FOUND)

    applications = JobApplication.objects.filter(opportunity=opportunity)

    applicants_data = JobApplicationSerializer(applications, many=True).data

    opportunity_data = OpportunityDetailSerializer(opportunity).data

    return Response({
        "opportunity_name": opportunity.opportunity_name, 
        "opportunity": opportunity_data,
        "applicants": applicants_data,  #    user + status
    }, status=status.HTTP_200_OK)


#======================================= change plan====================================#
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


#================================ Update Job Application Status  =================================================#
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_job_application_status(request):
    application_id = request.data.get('application_id')  
    action = request.data.get('action')

    if not application_id or not action:
        return Response({'error': 'Both application_id and action are required'}, status=status.HTTP_400_BAD_REQUEST)

    if action not in ['accept', 'reject']:
        return Response({'error': 'Invalid action. Must be either accept or reject.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        application = JobApplication.objects.get(id=application_id)
    except JobApplication.DoesNotExist:
        return Response({'error': 'Job application not found.'}, status=status.HTTP_404_NOT_FOUND)

    if application.status != 'pending':
        return Response({'error': 'This application has already been processed.'}, status=status.HTTP_400_BAD_REQUEST)

    # Update status
    if action == 'accept':
        application.status = 'accepted'
    elif action == 'reject':
        application.status = 'rejected'

    application.save()

    # Prepare email
    user = application.user
    job_title = application.opportunity.opportunity_name
    company_name = application.opportunity.company.name
    user_email = user.email

    if action == 'accept':
        subject = '🎉 Your application has been accepted!'
        message = (
            f"Hello {user.username},\n\n"
            f"🎉 Congratulations! Your application for the position \"{job_title}\" at {company_name} has been accepted.✅ \n"
            f"Our team will contact you soon 📞.\n\n"
            f"Best regards,\n"
            f"Forsa-Tech Team "
        )
    else:
        subject = '❌ Your application has been rejected'
        message = (
            f"Hello {user.username},\n\n"
            f" Unfortunately, your application for the position \"{job_title}\" at {company_name} has been rejected.\n"
            f"💡 Don't give up! You're welcome to apply for other opportunities in the future.\n\n"
            f"Best wishes,\n"
            f"Forsa-Tech Team "
        )

    if user_email:
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user_email],
                fail_silently=False
            )
        except Exception as e:
            print(f"Failed to send email: {e}")

    return Response({'message': f'Application {action}ed and user notified via email.'}, status=status.HTTP_200_OK)
#=============================================    All_job_applications   =============================================#

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_job_applications(request):
    applications = JobApplication.objects.all().order_by('-applied_at')
    serializer = JobApplicationSerializer(applications, many=True)
    return Response(serializer.data, status=200)






#========================================CHeck status ==============================================#
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_application_status(request):
    username = request.data.get('username')
    opportunity_id = request.data.get('opportunity_id')

    if not username or not opportunity_id:
        return Response({'error': 'username and opportunity_id are required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    try:
        opportunity = Opportunity.objects.get(id=opportunity_id)
    except Opportunity.DoesNotExist:
        return Response({'error': 'Opportunity not found.'}, status=status.HTTP_404_NOT_FOUND)

    # جيب الخطة الحالية للشركة
    subscription_plan = None
    if opportunity.company and opportunity.company.subscription_plan:
        subscription_plan = opportunity.company.subscription_plan.name

    application = JobApplication.objects.filter(user=user, opportunity=opportunity).first()
    if application:
        return Response({
            'status': application.status,
            'subscription_plan': subscription_plan
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'status': 'not_applied',
            'subscription_plan': subscription_plan
        }, status=status.HTTP_200_OK)


# ========================== HR Dashboard Stats ================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def hr_dashboard_stats(request):
    hr_user = request.user

    if not hasattr(hr_user, 'humanresources'):
        return Response({'detail': 'User is not HR'}, status=status.HTTP_403_FORBIDDEN)

    company = hr_user.humanresources.company

    today = datetime.now()
    days_since_sunday = (today.weekday() + 1) % 7
    start_of_week = today - timedelta(days=days_since_sunday)

    # Number of applications 
    applications_this_week = JobApplication.objects.filter(
        opportunity__company=company,
        applied_at__date__gte=start_of_week.date()
    ).count()

    # Status
    pending_applications = JobApplication.objects.filter(
        opportunity__company=company,
        status='pending'
    ).count()

    accepted_applications = JobApplication.objects.filter(
        opportunity__company=company,
        status='accepted'
    ).count()

    rejected_applications = JobApplication.objects.filter(
        opportunity__company=company,
        status='rejected'
    ).count()

    # Active job
    active_jobs = Opportunity.objects.filter(
        company=company,
        application_deadline__gte=datetime.now()
    ).count()

    data = {
        "applications_this_week": applications_this_week,
        "pending_applications": pending_applications,
        "accepted_applications": accepted_applications,
        "rejected_applications": rejected_applications,
        "active_jobs": active_jobs,
    }

    return Response(data, status=status.HTTP_200_OK)

#================================================= check subscription status ======================================================#

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_subscription_status(request):
    user = request.user

    if not hasattr(user, 'humanresources'):
        return Response({
            'detail': 'You are not authorized as HR'
        }, status=status.HTTP_403_FORBIDDEN)

    company = user.humanresources.company

    if not company:
        return Response({
            "status": "No Company",
            "message": "Your account is not linked to any company. Please contact the admin.",
            "current_plan": None
        }, status=status.HTTP_200_OK)

    current_plan = company.subscription_plan

    sub_request = SubscriptionChangeRequest.objects.filter(company=company).order_by('-created_at').first()

    if not current_plan:
        return Response({
            "status": "No Plan",
            "message": "You do not have any active subscription plan. We recommend subscribing to unlock more features!",
            "current_plan": None
        }, status=status.HTTP_200_OK)

    if sub_request:
        if sub_request.status == 'pending':
            return Response({
                "status": f"Pending",
                "message": "Your subscription change request is pending. Please wait, we will notify you once it's processed.",
                "current_plan": current_plan.name
            }, status=status.HTTP_200_OK)
        
        elif sub_request.status == 'approved':
            return Response({
                "status": f"approved",
                "message": f"Your company is now subscribed to {current_plan.name}. Enjoy the features, and consider upgrading for more benefits!",
                "current_plan": current_plan.name
            }, status=status.HTTP_200_OK)
        
        elif sub_request.status == 'rejected':
            return Response({
                "status": f"Rejected",
                "message": "Your subscription change request was rejected. Please contact support or submit a new request.",
                "current_plan": current_plan.name
            }, status=status.HTTP_200_OK)

    return Response({
        "status": f"{current_plan.name}",
        "message": f"Your company is subscribed to {current_plan.name}. Consider upgrading to a higher plan for more features.",
        "current_plan": current_plan.name
    }, status=status.HTTP_200_OK)


#========================================== applay ads ============================================

@api_view(['GET'])

def company_ads_list(request):
    ads = CompanyAd.objects.all()
    serializer = CompanyAdSerializer1(ads, many=True)
    return Response(serializer.data)





#==========================================Interview Schedules=====================================#

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_interview_schedule(request):
    user = request.user
    if not hasattr(user, 'humanresources'):
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

    hr = user.humanresources

    username = request.data.get('username')
    opportunity_id = request.data.get('opportunity_id')
    date = request.data.get('date')
    time = request.data.get('time')

    if not all([username, opportunity_id, date, time]):
        return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        dev_user = User.objects.get(username=username)
        opportunity = Opportunity.objects.get(id=opportunity_id)

        InterviewSchedule.objects.create(
            hr=hr,
            user=dev_user,
            opportunity=opportunity,
            date=date,
            time=time
        )
        return Response({'message': 'Interview scheduled successfully'}, status=status.HTTP_201_CREATED)

    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Opportunity.DoesNotExist:
        return Response({'error': 'Opportunity not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_interview_schedules(request):
    user = request.user
    if not hasattr(user, 'humanresources'):
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

    hr = user.humanresources
    schedules = InterviewSchedule.objects.filter(hr=hr)
    serializer = InterviewScheduleSerializer(schedules, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



#===================================================company profile===============================================================#

@api_view(['GET'])
@permission_classes([IsAuthenticated])  
def get_hr_company_profile(request):
    user = request.user

    if not hasattr(user, 'humanresources'):
        return Response({'error': 'This account is not authorized to access this endpoint'}, status=status.HTTP_403_FORBIDDEN)

    hr_profile = user.humanresources
    company = hr_profile.company

    if not company:
        return Response({'error': 'No company assigned to this HR'}, status=status.HTTP_404_NOT_FOUND)

    serializer = CompanyDetailSerializer(company)
    return Response({'company': serializer.data}, status=status.HTTP_200_OK)


##job app
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_job_applications(request):
    user = request.user
    applications = JobApplication.objects.filter(user=user).select_related('opportunity', 'opportunity__company')

    # اختيارياً: فلترة حسب status
    status = request.GET.get('status')
    if status:
        applications = applications.filter(status=status.lower())

    serializer = JobApplicationSerializer1000(applications, many=True)
    return Response(serializer.data)

#======================================================#
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_device_token(request):
    token = request.data.get('device_token')
    if not token:
        return Response({'error': 'Device token is required'}, status=400)

    user = request.user
    user.fcm_token = token
    user.save()
    return Response({'message': 'Device token updated successfully'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def do_something(request):
    user = request.user  
    if user.fcm_token:
        try:
            send_push_notification(
                token=user.fcm_token,
                title=' title',
                body=' body'
            )
            return Response({'message': 'Notification sent successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)
    return Response({'error': 'User has no device token'}, status=400)



#===========================================================================================#

def generate_reset_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@api_view(['POST'])
def request_password_reset(request):
    email = request.data.get('email')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "Email not found."}, status=status.HTTP_404_NOT_FOUND)

    active_code = PasswordResetCode.objects.filter(user=user, expires_at__gt=timezone.now()).first()
    if active_code:
        return Response({"message": "A code is already active. Please check your email."}, status=status.HTTP_200_OK)

    code = generate_reset_code()
    expires_at = timezone.now() + timedelta(minutes=10)  

    PasswordResetCode.objects.create(user=user, code=code, expires_at=expires_at)

    subject = "Password Reset Request"
    message = f"""
    Hello,

    You requested to reset your password.
    Here is your verification code: {code}

    This code will expire in 10 minutes.

    Regards,
    Forsa-Tech Team
    """

    send_mail(subject, message, 'noreply@forsa-tech.com', [email])

    return Response({"message": "Password reset code sent to your email."}, status=status.HTTP_200_OK)

#===============================================================================================#


@api_view(['POST'])
def confirm_password_reset(request):
    email = request.data.get('email')
    code = request.data.get('code')
    new_password = request.data.get('new_password')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "Invalid email."}, status=status.HTTP_404_NOT_FOUND)

    try:
        reset_code = PasswordResetCode.objects.get(user=user, code=code)
    except PasswordResetCode.DoesNotExist:
        return Response({"error": "Invalid code."}, status=status.HTTP_400_BAD_REQUEST)

    if reset_code.is_expired():
        return Response({"error": "Code has expired."}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()

    reset_code.delete()

    return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)




#==============================================================================================#
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_subscription_plans(request):
    plans = SubscriptionPlan.objects.all()
    serializer = SubscriptionPlanSerializer(plans, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


#================================================================================================#


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_company_info(request):
    try:
        hr = humanResources.objects.get(user=request.user)
    except humanResources.DoesNotExist:
        return Response({"error": "HR not found."}, status=status.HTTP_404_NOT_FOUND)

    company = hr.company
    if not company:
        return Response({"error": "No company assigned to this HR."}, status=status.HTTP_400_BAD_REQUEST)

    serializer = CompanyUpdateSerializer(company, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Company info updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



#=======================================================================================#

@api_view(['GET'])
def get_opportunities_by_company_id(request, company_id):

    try:
        company = Company.objects.get(id=company_id)
    except Company.DoesNotExist:
        return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)

    opportunities = Opportunity.objects.filter(company=company)
    serializer = OpportunitySerializer1(opportunities, many=True)

    return Response({'opportunities': serializer.data}, status=status.HTTP_200_OK)