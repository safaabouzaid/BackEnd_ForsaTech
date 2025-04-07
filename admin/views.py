from django.shortcuts import get_object_or_404
from django.forms import model_to_dict
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from human_resources.models import Company
from .serializers import CompanySerializer
from human_resources.filters import CompaniesFilter

@api_view(['POST'])
@permission_classes([IsAdminUser])
def createCompany(request):
    serializer = CompanySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Company created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
    return Response({"error": "Invalid data", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def listCompanies(request):
    #companies = Company.objects.all()
    filterset =CompaniesFilter(request.GET,queryset=Company.objects.all().order_by('id'))
    #serializer = CompanySerializer(companies, many=True)
    serializer = CompanySerializer(filterset.qs, many=True)

    return Response({"message": "Companies retrieved successfully", "data": serializer.data}, status=status.HTTP_200_OK)


@api_view(['PUT'])
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
