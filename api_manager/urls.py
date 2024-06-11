from django.urls import path
from . import views

urlpatterns = [
    # path('api/delete_superuser/', views.delete_superuser, name='delete_superuser'),
    
    path('api/signin/', views.SigninView.as_view(), name='api_signin'),
    path('api/signup/', views.SignupView.as_view(), name='api_signup'),
    path('api/signout/', views.SignoutView.as_view(), name='api_signout'),
    path('api/superuser_signin/', views.SuperUserSignin.as_view(), name='api_superuser_signin'),
    

]