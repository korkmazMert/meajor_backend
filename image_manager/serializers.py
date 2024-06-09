from rest_framework import serializers
from django.conf import settings
from .models import ImageModel 

class ImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField('get_image_url')

    class Meta:
        model = ImageModel
        fields = ('image', 'image_url')

    def get_image_url(self, obj):
        return obj.image.url if obj.image else ''