from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager, PermissionsMixin
from django.utils import timezone
import uuid

class ActivationUser(models.Model):
    user_secret = models.CharField(max_length=254, null=True, blank=True)
    last_activity = models.DateTimeField(auto_now=True)

    
class UserManager(BaseUserManager):

  def _create_user(self, email, first_name, last_name, password, is_staff, is_superuser, **extra_fields):
    if not email:
        raise ValueError('Users must have an email address')
    now = timezone.now()
    email = self.normalize_email(email)

    user = self.model(
        email=email,
        first_name = first_name,
        last_name = last_name,
        is_staff=is_staff,
        is_active=True,
        is_superuser=is_superuser,
        last_login=now,
        date_joined=now,
        **extra_fields
    )



    user.set_password(password)
    user.save(using=self._db)
  
    return user



  def create_user(self, email, first_name, last_name, password, **extra_fields):
    return self._create_user(email, first_name, last_name, password, False, **extra_fields)


  def create_user_company(self, email, company, phone, password, **extra_fields):
    return self._create_user_company(email, company, phone, password, False, **extra_fields)

  def create_superuser(self, email, first_name, last_name , password, **extra_fields):
    user=self._create_user(email, first_name, last_name, password, True, True, **extra_fields)
    user.save(using=self._db)
    return user


class User(AbstractBaseUser, PermissionsMixin):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=254, unique=True)
    username = models.CharField(max_length=254, null=True, blank=True)
    first_name = models.CharField(max_length=254, null=True, blank=True)
    last_name = models.CharField(max_length=254, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    phone = models.CharField(max_length=254, null=True, blank=True)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    def get_absolute_url(self):
        return "/users/%i/" % (self.pk)
    
    def __str__(self):
        return self.email