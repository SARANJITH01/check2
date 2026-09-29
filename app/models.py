from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class User_Profile(models.Model):
    USER = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    place = models.CharField(max_length=255)
    gender = models.CharField(max_length=255)



class Complaint(models.Model):
    USER_PROFILE = models.ForeignKey(User_Profile, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    reply = models.CharField(max_length=255, blank=True, null=True)
    date = models.CharField(max_length=255)



class Feedback(models.Model):
    USER_PROFILE = models.ForeignKey(User_Profile, on_delete=models.CASCADE)
    feedback = models.CharField(max_length=255)
    date = models.CharField(max_length=255)



