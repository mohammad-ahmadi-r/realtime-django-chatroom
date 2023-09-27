from django.db import models
import uuid
from django.contrib.auth.models import User

class Token(models.Model):
    id= models.UUIDField(primary_key=True, default= uuid.uuid4)
    user_token= models.ForeignKey(User, on_delete=models.CASCADE)
    valid= models.IntegerField(default=0)