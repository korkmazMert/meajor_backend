from django.urls import path
from . import views

urlpatterns = [
    
    path('get_images/', views.get_images, name='api_get_images'),
    path('get_image/<int:image_id>/', views.get_image, name='api_get_image'),
    path('get_users_images/', views.get_users_images, name='api_get_users_images'),
    path('save_image_to_db/', views.save_image_to_db, name='api_save_image_to_db'), 
    

]