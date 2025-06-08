from django.db import models

# Create your models here.
from django.db import models


class User(models.Model):
    user_id = models.CharField(max_length=32, primary_key=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    nickname = models.CharField(max_length=30)
    birth = models.CharField(max_length=8)
    gender = models.CharField(max_length=8)
    job = models.CharField(max_length=50, null=True, blank=True)
    profile_image = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=10, default='guest')
    social_provider = models.CharField(max_length=10, null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
