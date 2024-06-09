from django.db import models
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
from django.conf import settings

class ImageModel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to='images/', null=True)
    processed_image = models.ImageField(upload_to='processed_images/', null=True)
    widths = models.JSONField(null=True)
    heights = models.JSONField(null=True)
    