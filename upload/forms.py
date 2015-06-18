'''
Created on Apr 8, 2015

@author: jiao
'''
from django import forms
from .models import Species


def getSpec():
    
    species = Species.objects.all().values_list('species_name',flat=True)
    choices = [(spec,'.'.join([spec[0],spec[spec.index(' ')+1:]])) for spec in species]
    return choices
    
    
class uploadForm(forms.Form):
    

    species = forms.CharField(widget=forms.Select(choices = getSpec()))
    experiment = forms.CharField(label = 'Experiment name: e.g. Basten Snoek etal 2010', max_length = 50, widget=forms.TextInput(attrs={}))
    parent = forms.CharField(label = 'Parent: e.g. N2 x CB4856', max_length = 50, widget=forms.TextInput(attrs={}))
    ref = forms.CharField(label = 'Literature reference: e.g. Genetical Genomics Reveals Large Scale Genotype-By-Environment Interactions in Arabidopsis thaliana', max_length = 200, widget=forms.TextInput(attrs={}))
    pubmed = forms.CharField(label = 'PMC: e.g. 20488933', max_length = 20, widget=forms.TextInput(attrs={}))
    arrayfile = forms.FileField(widget=forms.FileInput(attrs={'class':'file'}))
    markerfile = forms.FileField(widget=forms.FileInput(attrs={'class':'file'}))
    genotypefile = forms.FileField(widget=forms.FileInput(attrs={'class':'file'}),required=False)
    lodfile = forms.FileField(widget=forms.FileInput(attrs={'class':'file'}))

