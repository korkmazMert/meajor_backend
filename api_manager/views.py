from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.http.response import HttpResponse,JsonResponse
from accounts.models import * 
from django.contrib.auth import logout, authenticate, login
from accounts.serializers import *

 


# def delete_superuser(request):
#     superuser_email = request.GET.get('email')
#     superuser = User.objects.filter(is_superuser=True,email=superuser_email).delete()
#     if superuser:
   
        
#         print(f"Superuser with email {superuser_email} has been deleted.")
#         return HttpResponse('Superuser deleted successfully')

#     else:
#         print(f"No superuser found with email {superuser_email}.")
#         return HttpResponse('No superuser found with email')
    
class SignoutView(APIView):
    def get(self, request):
        logout(request)
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


class SigninView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        if email and password:
            user = User.objects.filter(email=email).first()
            if not user:
                return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            if not user.check_password(password):
                return Response({'message': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)
            user = authenticate(email=email, password=password)
            if user:
                login(request, user)
                return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class SignupView(APIView):
    def post(self, request):
        email = request.data.get('email')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        password = request.data.get('password')
        password2 = request.data.get('password2')
        response_data_s = {}


        if first_name and last_name and email :

            if password and password2:
                if password == password2:

                    if(User.objects.filter(email = email)):

                        response_data_s['result'] = 'failed'
                        response_data_s['message'] = 'email already exist'
                    else:
                        new_user = User.objects.create_user(email= email, first_name = first_name, last_name= last_name, password = password ,is_superuser =False)
                        new_user.set_password(password)
                        new_user.email = email
                        new_user.save()

                        user = authenticate(username=email, password=password)

                        login(request, user)

                        response_data_s['result'] = 'success'
                        response_data_s['message'] = 'sign up success'

                else:
                    response_data_s['result'] = 'failed'
                    response_data_s['message'] = 'Passwords do not match'

            else:
                response_data_s['result'] = 'failed'
                response_data_s['message'] = 'Password1 and password2 required'

        else:
            response_data_s['result'] = 'failed'
            response_data_s['message'] = 'First name, last_name, phone number and email required'


        return JsonResponse(response_data_s)
    