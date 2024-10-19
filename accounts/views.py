from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from django.http.response import JsonResponse
from rest_framework.response import Response
from accounts.models import * 
from django.contrib.auth import logout, authenticate, login
from accounts.serializers import *


class AccountInfoView(APIView):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            user_serialized = UserSerializer(user).data
            return Response({'result': 'success','message': 'account info fetched successfuly','user': user_serialized}, status=status.HTTP_200_OK)
        else:
            return Response({'result': 'failed','message': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        
