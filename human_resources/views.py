from django.forms import model_to_dict
from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from human_resources.models import Company, Opportunity
from human_resources.serializer import HumanResourcesSerializer, OpportunitySerializer
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt


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

    refresh = RefreshToken.for_user(user)

    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }, status=status.HTTP_200_OK)






@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createOpportunity(request):
    data=request.data
    company_id=data.pop('company',None)
    
    try:
        company=Company.objects.get(id=company_id)
    except Company.DoesNotExist:
       return Response({"error": "Invalid company ID"}, status=status.HTTP_400_BAD_REQUEST)


    serializer=OpportunitySerializer(data=data)

    if serializer.is_valid():
        opportunity=Opportunity.objects.create(company=company, **serializer.validated_data)
        result=OpportunitySerializer(opportunity,many=False)
        return Response({"opportunity":result.data},status=status.HTTP_201_CREATED)
    else:  
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    




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

    serializer=OpportunitySerializer(opportunity,data=data)
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





@api_view(['Get'])
@permission_classes([IsAuthenticated])
def getAllOpportunity(requst):
    opportunity=get_object_or_404(Opportunity)
    serializer=OpportunitySerializer(opportunity,many=False)
    print(opportunity)
    return Response({'Opportunity':serializer.data})