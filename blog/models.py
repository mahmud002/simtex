from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

from django.contrib.auth.models import User,auth

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    first_name=models.TextField(max_length=1000, null=True, blank=True)
    last_name=models.TextField(max_length=1000, null=True, blank=True)
    gender=models.TextField(max_length=1000, null=True, blank=True)
    email=models.TextField(max_length=1000, null=True, blank=True)

    address = models.TextField(max_length=1000, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    image=models.ImageField(upload_to="blog/images", default="",null=True, blank=True)
    