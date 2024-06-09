from django.db import models
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image


class ImageModel(models.Model):
    image = models.ImageField(upload_to='images/', null=True)
