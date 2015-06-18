from django.contrib.auth.models import User
from django.db import models
import os

class Species(models.Model):
    species_name = models.CharField(max_length=50,primary_key=True)
    
    def __unicode__(self):
        return self.species_name

def uploadArrayPath(instance,filename):
    fname = 'array.txt'
    try:
        os.makedirs(os.path.join('data','%s' % instance.experiment_name)) 
        return os.path.join('data','%s' % instance.experiment_name,fname)
    except OSError as e:
        if e.errno ==17:
            #Dir already exists.
            return os.path.join('data','%s' % instance.experiment_name,fname)
        
def uploadMarkerPath(instance,filename):
    fname = 'marker.txt'
    try:
        os.makedirs(os.path.join('data','%s' % instance.experiment_name)) 
        return os.path.join('data','%s' % instance.experiment_name,fname)
    except OSError as e:
        if e.errno ==17:
            #Dir already exists.
            return os.path.join('data','%s' % instance.experiment_name,fname)

def uploadGenotypePath(instance,filename):
    fname = 'genotype.txt'
    try:
        os.makedirs(os.path.join('data','%s' % instance.experiment_name)) 
        return os.path.join('data','%s' % instance.experiment_name,fname)
    except OSError as e:
        if e.errno ==17:
            #Dir already exists.
            return os.path.join('data','%s' % instance.experiment_name,fname)

def uploadLODPath(instance,filename):
    fname = 'lod.txt'
    try:
        os.makedirs(os.path.join('data','%s' % instance.experiment_name)) 
        return os.path.join('data','%s' % instance.experiment_name,fname)
    except OSError as e:
        if e.errno ==17:
            #Dir already exists.
            return os.path.join('data','%s' % instance.experiment_name,fname)      
        
class Experiment(models.Model):

    species = models.ForeignKey(Species)
    experiment_name = models.CharField(max_length=50,primary_key=True)
    phenotypes = models.CharField(max_length=50,blank=True)
    type_of_array = models.CharField(max_length=50,blank=True)
    sample_size = models.CharField(max_length=50,blank=True)
    parental_strain = models.CharField(max_length=50,blank=True)
    reference = models.CharField(max_length=200,blank=True)
    pubmed = models.CharField(max_length=20,blank=True)
    pub_date = models.DateTimeField(auto_now_add=True, auto_now=False)
    upload_user = models.ForeignKey(User)
    array_file = models.FileField(upload_to=uploadArrayPath)
    marker_file = models.FileField(upload_to=uploadMarkerPath)
    genotype_file = models.FileField(upload_to=uploadGenotypePath)
    lod_file = models.FileField(upload_to=uploadLODPath)
    pvalthld = models.DecimalField(max_digits = 13,decimal_places = 12,blank=True)
    lodthld = models.DecimalField(max_digits = 6,decimal_places = 3,blank=True)
    
    def __unicode__(self):
        return self.experiment_name

class Line(models.Model):
    experiment_name = models.ForeignKey(Experiment)
    line_name = models.CharField(max_length=50)
    
    def __unicode__(self):
        return self.line_name
    
class ArraySpot(models.Model):
    spot_id = models.CharField(max_length=50)
    experiment_name = models.ForeignKey(Experiment)
    def __unicode__(self):
        return self.spot_id
    
class Marker(models.Model):
    
    marker_name = models.CharField(max_length=15) #
    marker_chr = models.CharField(max_length=10,null=True,blank=True)#1,2,3,4,5,X
    marker_start = models.IntegerField(null=True,blank=True)
    marker_end = models.IntegerField(null=True,blank=True)
    experiment_name = models.ForeignKey(Experiment)
    
    def __unicode__(self):
        return self.marker_name

class Transcript(models.Model):
    transcript_name = models.CharField(max_length = 30,null=True,blank=True)
    spot_id = models.ForeignKey(ArraySpot)
    ref_id = models.CharField(max_length = 20,null=True,blank=True)
    chr = models.CharField(max_length=3,blank=True)
    start = models.IntegerField(null=True,blank=True)
    end = models.IntegerField(null=True,blank=True)
    
    def __unicode__(self):
        return self.transcript_name
    
#class GO (models.Model):
#    gene_name = models.ForeignKey(Gene)  
#    molecular_function = models.CharField(max_length = 200,blank=True)
#    biological_process = models.CharField(max_length = 200,blank=True)
#    cellular_location = models.CharField(max_length = 200,blank=True)
    

 
