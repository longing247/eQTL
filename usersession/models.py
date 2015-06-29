from django.db import models
from django.contrib.auth.models import User
from upload.models import Experiment,ArraySpot,Transcript,Marker
# Create your models here.
class Task(models.Model):
    user_name = models.ForeignKey(User)
    experiment = models.ForeignKey(Experiment)
    probe = models.ForeignKey(ArraySpot)
    transcript =models.ForeignKey(Transcript)
    marker = models.ForeignKey(Marker)
    lod_si = models.CharField(max_length = 50)