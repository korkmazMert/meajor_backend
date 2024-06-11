from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.http.response import HttpResponse,JsonResponse
from accounts.models import * 
from api_manager.models import * 
from django.contrib.auth import logout, authenticate, login
from accounts.serializers import *
from api_manager.serializers import *
from django.db import IntegrityError

from rest_framework.authentication import SessionAuthentication
 


# def delete_superuser(request):
#     superuser_email = request.GET.get('email')
#     superuser = User.objects.filter(is_superuser=True,email=superuser_email).delete()
#     if superuser:
   
        
#         print(f"Superuser with email {superuser_email} has been deleted.")
#         return HttpResponse('Superuser deleted successfully')

#     else:
#         print(f"No superuser found with email {superuser_email}.")
#         return HttpResponse('No superuser found with email')

class SessionCsrfExemptAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        pass
    
class SignoutView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'result':'failed','message': 'User not authenticated'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            logout(request)
            return Response({'result':'success','message': 'Logout successful'}, status=status.HTTP_200_OK)
        except:
            return Response({'result':'failed','message': 'Logout failed'}, status=status.HTTP_400_BAD_REQUEST)




class SuperUserSignin(APIView):
    def get(self, request):
        try:
            if not request.user.is_authenticated:
                email = 'deneme2@deneme.com'
                password = '123'
                fcmToken = 'websocket_token'
                fcm_response = {}  # Define fcm_response here

                print('inside signinview',request.data)

                if email and password:
                    user = User.objects.filter(email=email).first()
                    if not user:
                        return JsonResponse({'result':'failed','message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
                    if not user.check_password(password):
                        return JsonResponse({'result':'failed','message': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)
                    user = authenticate(email=email, password=password)
                    if user:
                        login(request, user)
                        if fcmToken:
                            add_device_response = add_device(request,fcmToken)
                            fcm_response = {'fcm_response': add_device_response}  # Update fcm_response here
                        return JsonResponse({
                            'result': 'success',
                            'message': 'Login successful',
                            'data': fcm_response}, 
                            status=status.HTTP_200_OK)
                    else:
                        return JsonResponse({
                            'result':'failed',
                            'message': 'Invalid credentials'}, 
                            status=status.HTTP_401_UNAUTHORIZED)
            else: 
                return JsonResponse({
                    'result':'failed',
                    'message': 'User already authenticated',}, 
                    status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({
                'result':'failed',
                'message': e,
                }, 
                status=status.HTTP_400_BAD_REQUEST)
        


class SigninView(APIView):
    def post(self, request):
        try:
            if not request.user.is_authenticated:
                email = request.data.get('email')
                password = request.data.get('password')
                fcmToken = request.data.get('fcm_token')
                fcm_response = {}  # Define fcm_response here

                print('inside signinview',request.data)

                if email and password:
                    user = User.objects.filter(email=email).first()
                    if not user:
                        return JsonResponse({'result':'failed','message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
                    if not user.check_password(password):
                        return JsonResponse({'result':'failed','message': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)
                    user = authenticate(email=email, password=password)
                    if user:
                        login(request, user)
                        if fcmToken:
                            add_device_response = add_device(request,fcmToken)
                            fcm_response = {'fcm_response': add_device_response}  # Update fcm_response here
                        return JsonResponse({
                            'result': 'success',
                            'message': 'Login successful',
                            'data': fcm_response}, 
                            status=status.HTTP_200_OK)
                    else:
                        return JsonResponse({
                            'result':'failed',
                            'message': 'Invalid credentials'}, 
                            status=status.HTTP_401_UNAUTHORIZED)
            else: 
                return JsonResponse({
                    'result':'failed',
                    'message': 'User already authenticated',}, 
                    status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({
                'result':'failed',
                'message': e,
                }, 
                status=status.HTTP_400_BAD_REQUEST)



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





def add_device(request, fcmToken):
    if request.method == 'POST':
        user = request.user
        if fcmToken:
            if user.is_authenticated:
                try:
                    device = Device.objects.get(fcm_token = fcmToken)
                    device.user = user
                    device.save()
                    data = {'result':'success','message':'fcm token saved to current user','device': DeviceSerializer(device).data}
                except Device.DoesNotExist:
                    try:
                        device = Device.objects.create(user = user, fcm_token = fcmToken)
                        data = {'result':'success','message':'fcm token saved to user','device': DeviceSerializer(device).data}
                    except IntegrityError:
                        data = {'result':'success','message':'fcm token already exists'}
                except Exception as e:
                    data = {'result':'failed','message':str(e)}
                return data
            else:
                try:
                    device = Device.objects.get(fcm_token = fcmToken)
                    device.user = None
                    device.save()
                    data = {'result':'success','message':'fcm token saved to anonymous user','device': DeviceSerializer(device).data}
                except Device.DoesNotExist:
                    try:
                        device = Device.objects.create(fcm_token = fcmToken)
                        data = {'result':'success','message':'fcm token saved to anonymous user','device': DeviceSerializer(device).data}
                    except IntegrityError:
                        data = {'result':'success','message':'fcm token already exists'}
                except Exception as e:
                    data = {'result':'failed','message':str(e)}
                return data
        else:
            data = {'result':'failed','message':'fcm token not found'}
            return data



