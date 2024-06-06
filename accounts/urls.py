from django.urls import path
from . import views

urlpatterns = [

    path('api/account_info/', views.AccountInfoView.as_view(), name='api_account_info'),
    

]