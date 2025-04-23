from django.shortcuts import get_object_or_404
from django.forms import model_to_dict
from rest_framework.decorators import api_view, permission_classes, authentication_classes, parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from human_resources.models import Company,CompanyAd, Opportunity,JobApplication
from .serializers import CompanySerializer ,CompanyAdSerializer ,CompanyDetailSerializer,DashboardStatsSerializer
from human_resources.filters import CompaniesFilter
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Count
from datetime import datetime
from django.db.models.functions import TruncMonth


@api_view(['POST'])
@permission_classes([IsAdminUser])
def createCompany(request):
    serializer = CompanySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Company created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
    return Response({"error": "Invalid data", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


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


#================================   Company Ads    ==================================#

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


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_ad(request, ad_id):
    ad = get_object_or_404(CompanyAd, pk=ad_id)
    ad.delete()
    return Response({"message": "Company ad deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


####    Company Details    #####

@api_view(['GET'])
def get_company_profile(request, pk):
    company = get_object_or_404(Company, pk=pk)
    serializer = CompanyDetailSerializer(company)
    return Response({'company': serializer.data}, status=status.HTTP_200_OK)





#==================================== dashboard_stats =============================#

@api_view(['GET'])
def dashboard_stats(request):

#Number of Companies

    num_companies = Company.objects.count()

#Most Hiring Companies

    most_hiring_company = (
        Company.objects.annotate(num_jobs=Count('opportunity'))
        .order_by('-num_jobs')
        .first()
    )
    most_hiring_name = most_hiring_company.name if most_hiring_company else "N/A"

#Most Demanded Jobs

    most_demanded_jobs = (
    JobApplication.objects.values('opportunity__title')
    .annotate(count=Count('id'))
    .order_by('-count')[:3]
)
    most_demanded_titles = [job['opportunity__title'] for job in most_demanded_jobs]

##Highest Paying Jobs

    def extract_max_salary(opportunity):
        try:
            return int(opportunity.salary_range.split('-')[-1])
        except:
            return 0

    opportunities = Opportunity.objects.exclude(salary_range__isnull=True)
    highest_salary_opportunity = max(opportunities, key=extract_max_salary, default=None)
    highest_paying_job = {
        "title": highest_salary_opportunity.title,
        "salary": highest_salary_opportunity.salary_range
    } if highest_salary_opportunity else {"title": "N/A", "salary": "N/A"}


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

#Job Distribution by Specialization
    jobs_by_title = (
        Opportunity.objects.values('title')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    pie_chart_data = [
        {"name": item["title"], "value": item["count"]}
        for item in jobs_by_title
    ]

    data = {
        "num_companies": num_companies,
        "most_hiring_company": most_hiring_name,
        "most_demanded_jobs": most_demanded_titles,
        "highest_paying_job": highest_paying_job,
        "line_chart_data": line_chart_data,
        "pie_chart_data": pie_chart_data,
    }

    serializer = DashboardStatsSerializer(data)
    return Response(serializer.data, status=status.HTTP_200_OK)
