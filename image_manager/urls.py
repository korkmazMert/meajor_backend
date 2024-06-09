from django.urls import path
from . import views

urlpatterns = [
    
    path('get_images/', views.get_images, name='api_get_images'),
    

]