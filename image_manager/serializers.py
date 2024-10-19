from rest_framework import serializers
from django.conf import settings
from .models import ImageModel 

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageModel
        fields = '__all__'
        
