from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.http.response import HttpResponse,JsonResponse
from accounts.models import * 
from django.contrib.auth import logout, authenticate, login
from accounts.serializers import *


class AccountInfoView(APIView):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            user_serialized = UserSerializer(user).data
            return Response({'user': user_serialized}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)