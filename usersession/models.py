from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Task(models.Model):
    user_name = models.ForeignKey(User)
    
    types = (
        ('Co-regulation', 'co-regulated genes'),
        ('candidates', 'candidate genes'),
    )
    analysis_type =  models.CharField(max_length=20, choices=types)
    info = models.TextField()