from django.db import models
from django.contrib.auth.models import User
from EC_Admin.models import Voters



# Create your models here.
class Voted(models.Model):
    election_id = models.CharField(max_length=50)
    voter_id = models.CharField(max_length=10)
    state = models.CharField(max_length=50)
    constituency = models.CharField(max_length=50)
    has_voted = models.CharField(max_length=3)
    where_voted = models.CharField(max_length=7, null=True)
    ipaddress = models.GenericIPAddressField(null=True)
    datetime = models.DateTimeField(null=True)


class Complain(models.Model):
    voterid_no=models.CharField(max_length=10)
    complain=models.CharField(max_length=5000)
    complain_reply=models.CharField(max_length=5000, null=True)
    viewed=models.BooleanField(default=False)
    replied=models.BooleanField(default=False)
    
class OTP(models.Model):
    voters = models.OneToOneField(Voters, on_delete=models.CASCADE)
    # user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)