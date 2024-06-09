from django.shortcuts import render
from django.http import JsonResponse
from .models import *
from .serializers import *

def get_images(self):
    images = ImageModel.objects.all()
    images_serialized = ImageSerializer(images, many=True).data
    return JsonResponse({'images': images_serialized})