'''
Created on Apr 8, 2015

@author: jiao
'''
from django import forms
from django.utils.translation import ugettext_lazy as _

from upload.models import Species,Experiment


thld_choices = ('default FDR control 0.05')

def getExp():
    
    species = Species.objects.all().values_list('species_name',flat = True)
    exp = []
    for spec in species:
        exp_ins_list = []
        spec_ins = Species.objects.get(species_name = spec)
        experiments = Experiment.objects.filter(species = spec_ins).values_list('experiment_name',flat=True)
        for exp_ins in experiments:
            exp_ins_bak = exp_ins.encode('ascii','ignore')
            exp_ins_image = exp_ins.encode('ascii','ignore')+' '
            exp_ins_list.append((exp_ins_bak,exp_ins_image))
        exp.append((spec,tuple(exp_ins_list)))
    exp_tuple = tuple(exp)     
    return exp_tuple
    
    
class investigationForm(forms.Form):
    
    exp = forms.CharField(widget = forms.Select(choices = getExp()))
    thld = forms.RegexField(regex=r'^[1-9]\d*(\.\d+)?$', widget=forms.TextInput(attrs=dict(required=True, max_length=5)), label=_("-logP"), error_messages={ 'invalid': _("Invalid threshold") })
    marker = forms.CharField(label = 'marker', max_length = 20, widget=forms.TextInput(attrs={}))
    gene_list = forms.CharField(widget=forms.TextInput(attrs={}),required=False)
    gene_list_file = forms.FileField(widget=forms.FileInput(attrs={'class':'file'}),required=False)

class investigationQTLForm(forms.Form):
    exp = forms.CharField(widget = forms.Select(choices = getExp()))
    region = forms.RegexField(regex=r'^(chr|)*\s*([0-9]{1,2}|X|CP|MT)\s*(:)?\s*(\d+)\s*(-)?\s*(\d+)\s*', widget=forms.TextInput(attrs=dict(required=True, max_length=12)), label=_("Chromosome region"), error_messages={ 'invalid': _("Invalid chromsome region")})
    qtl_gene_list = forms.CharField(widget=forms.TextInput(attrs={}),required=False)
    qtl_gene_list_file = forms.FileField(widget=forms.FileInput(attrs={'class':'file'}),required=False)
