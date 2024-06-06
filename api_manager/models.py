from django.db import models
from accounts.models import *

class Device(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True, blank=True)
    fcm_token = models.CharField(max_length=500, null=True, blank=True)
