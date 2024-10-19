from django.urls import path
from . import views
from chat.views import *

urlpatterns = [
    # path('api/delete_superuser/', views.delete_superuser, name='delete_superuser'),
    path('api/get_control_id/', views.get_control_id, name='api_get_control_id'),
    
    path('api/signin/', views.SigninView.as_view(), name='api_signin'),
    path('api/signup/', views.SignupView.as_view(), name='api_signup'),
    path('api/signout/', views.SignoutView.as_view(), name='api_signout'),
    path('api/superuser_signin/', views.SuperUserSignin.as_view(), name='api_superuser_signin'),
    path("api/open_live_support/", open_live_support, name="open_live_support"),  

    path('api/get_chatrooms/', get_chatrooms, name='api_get_chatrooms'),
     path('api/get_chatroom/', get_chatroom, name='api_get_chatroom'),
    path('api/check_receiver_online/', check_receiver_online, name='api_check_receiver_online'),

    
 
]