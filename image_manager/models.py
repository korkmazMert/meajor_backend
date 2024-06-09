from django.db import models

# Create your models here.
from django.db import models

class ImageModel(models.Model):
    image = models.ImageField(upload_to='images/')