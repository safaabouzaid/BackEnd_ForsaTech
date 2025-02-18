from django.shortcuts import render

# Create your views here.
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from human_resources.models import Company
from .serializers import CompanySerializer

class CompanyCreateView(APIView):
    # permission_classes = [IsAdminUser]  

    def post(self, request):
        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompanyListView(APIView):
    permission_classes = [IsAdminUser]  

    def get(self, request):
        companies = Company.objects.all()  
        serializer = CompanySerializer(companies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CompanyUpdateView(APIView):
    permission_classes = [IsAdminUser]  

    def put(self, request, pk):
        company = get_object_or_404(Company, pk=pk) 
        serializer = CompanySerializer(company, data=request.data)  
        if serializer.is_valid():
            serializer.save()  
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompanyDeleteView(APIView):
    permission_classes = [IsAdminUser] 
    def delete(self, request, pk):
        company = get_object_or_404(Company, pk=pk)  
        company.delete()  
        return Response(status=status.HTTP_204_NO_CONTENT)
