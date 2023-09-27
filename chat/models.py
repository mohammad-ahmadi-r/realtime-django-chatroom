import uuid
from django.db import models
from django.contrib.auth.models import User

class profile(models.Model):
    id = models.UUIDField(default = uuid.uuid4 , primary_key = True)
    owner_prof= models.OneToOneField(User, on_delete=models.CASCADE)
    userid= models.CharField(max_length=150, blank=True)
    picture= models.ImageField(upload_to ='images/', blank=True)
    phone_number= models.CharField(max_length=150, blank=True)
    about= models.CharField(max_length=250, blank=True)
    is_online = models.BooleanField(default=False)

class Roomcode(models.Model):
    id = models.UUIDField(default = uuid.uuid4 , primary_key = True)
    code= models.UUIDField(default = uuid.uuid4 , unique=False)
    sender = models.ForeignKey(User, related_name='senderr', on_delete=models.CASCADE, null=True, unique=False)
    receiver = models.ForeignKey(User, related_name='receiverr', on_delete=models.CASCADE, null=True, unique=False)
    receiveronchat= models.BooleanField(default=False)

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sender', on_delete=models.CASCADE, null=True)
    receiver = models.ForeignKey(User, related_name='receiver', on_delete=models.CASCADE, null=True)
    content = models.TextField(null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('date_added',)
