
from django.db import models
from accounts.models import User
# Create your models here.

class ChatRoom(models.Model):
    title = models.CharField(max_length=1000, null=True, blank=True)
    control_id = models.CharField(max_length=1000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    unread_user = models.BooleanField(default=True, null = True, blank = True)
    unread_admin = models.BooleanField(default=True, null = True, blank = True)
    is_cargo = models.BooleanField(default=False, null = True, blank = True)
    is_customer = models.BooleanField(default=False, null = True, blank = True)
    is_guest = models.BooleanField(default=False, null = True, blank = True)
    is_seller = models.BooleanField(default=False, null = True, blank = True)
    participant =  models.JSONField(null = True, blank = True)
    online_users = models.JSONField(null = True, blank = True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return str(self.title)
    


class Message(models.Model):
    ## TODO: Add is_active field 
    # is_active = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='messages')
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, null=True, blank=True, related_name='messages')
    message = models.TextField(null=False)
    created_at = models.DateTimeField(auto_now_add = True)
    read_time = models.DateTimeField(auto_now_add = False,null=True, blank=True)
    is_read = models.BooleanField(default=0)
    read_time = models.DateTimeField(auto_now_add = False,null=True, blank=True)
    is_file = models.BooleanField(default=0)
    is_auth_user = models.BooleanField(default=1)
    anonymous_user_secret = models.CharField(max_length=254, null=True, blank=True)
    sender_name = models.CharField(max_length=254, null=True, blank=True)
    
    

    @property
    def get_date(self):
        return f'{self.created_at.hour}:{self.created_at.minute} {self.created_at.day}/{self.created_at.month}/{self.created_at.year}'


