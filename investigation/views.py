import time
import json
import os
import re

from django.shortcuts import render
from django.conf import settings

from upload.models import Experiment,ArraySpot,Transcript
from .forms import investigationForm,investigationQTLForm

# Create your views here.
def investigationView(request):
    if request.POST.get('exp') and request.POST.get('thld') and request.POST.get('marker'):
        if request.POST.get('gene_list') and request.POST.get('gene_list_file'):
            raise Exception('You must choose only one, not both')
        if not request.POST.get('gene_list') and not request.FILES.get('gene_list_file'):
            raise Exception('You must choose only one')
        if request.POST.get('gene_list') or request.FILES.get('gene_list_file'): 
            print request.POST.get('gene_list')
            print request.FILES.get('gene_list_file')
            form = investigationForm(request.POST)
            if form.is_valid():
                exp = request.POST.get('exp')
                thld = float(request.POST.get('thld'))
                marker = request.POST.get('marker').encode('ascii','ignore').strip()
                
                #Create JSON file 
                in_path = os.path.join(settings.MEDIA_ROOT,'data/%s/%s' % (exp,'lod.txt'))
                
                lod_probe_list = []
                with open(in_path) as fi:
                    #find marker index
                    header = fi.readline()
                    header_line = [marker_ins.encode('ascii','ignore').lower() for marker_ins in header.strip().split('\t')[1:]]
                    marker_ind = -1
                    try:
                        marker_ind = header_line.index(marker.lower())                  
                    except IndexError:
                        print 'Query marker is not in the list'
                    
                    for raw_line in fi.readlines():
                        line = raw_line.strip().split('\t')
                        if float(line[marker_ind+1]) >= thld:
                            lod_probe_list.append(line[0])
                    
                probe_list = ArraySpot.objects.filter(spot_id__in=lod_probe_list)
                gene_unicode_list = Transcript.objects.filter(spot_id__in=probe_list).values_list('transcript_name',flat=True)
                gene_list = [ gene.encode('ascii','ignore') for gene in gene_unicode_list ]
                    
                
                if request.POST.get('gene_list'):
                    raw_gene_list_string = request.POST.get('gene_list').encode('ascii','ignore')
                    delimiter_type = delimiter(raw_gene_list_string)
                    target_gene_list = raw_gene_list_string.strip().split(delimiter_type)
                    inter = intersect(gene_list,target_gene_list)
                    return render(request,'investigation/investigation.html',{'intersection':inter})
                    
                        
                if request.FILES.get('gene_list_file'):
                    fi = request.FILES.get('gene_list_file').read()
   
                    target_gene_list = []
                    content = fi.encode('ascii','ignore')
                    delimiter_type = delimiter(content)
                    target_gene_list = content.strip().split(delimiter_type)

                    inter = intersect(gene_list,target_gene_list)
                    print inter
                    return render(request,'investigation/investigation.html',{'intersection':inter})
                
    elif request.POST.get('region') and request.POST.get('exp'):
        form = investigationQTLForm(request.POST)
        if form.is_valid():
            region = request.POST.get('region').strip().encode('ascii','ignore')
            regex_for_chr = re.compile('([0-9]{1,2}|X|CP|MT)\s*(:)?\s*')
            regex_for_start_end = re.compile('(\d+)\s*(-)?\s*(\d+)\s*')
            chr_ = re.search(regex_for_chr,region).group().replace(' ','').replace(':','')
            start_,end_ = re.search(regex_for_start_end,region).group().replace(' ','').split('-')
            
            exp_ = request.POST.get('exp').strip().encode('ascii','ignore')
            
            experiment = Experiment.objects.get(experiment_name = exp_)
            probes = ArraySpot.objects.filter(experiment_name = experiment)
            candidates = Transcript.objects.filter(spot_id__in = probes,chr=chr_,start__gte=start_,end__lte=end_).order_by('start').values_list('transcript_name',flat=True)
            query_candidates = [ candidate.encode('ascii','ignore' ) for candidate in candidates]
            
            
            if request.POST.get('qtl_gene_list') and request.POST.get('qtl_gene_list_file'):
                raise Exception('You must choose only one, not both')
            if request.POST.get('qtl_gene_list'):
                raw_gene_list_string = request.POST.get('qtl_gene_list').encode('ascii','ignore')
                delimiter_type = delimiter(raw_gene_list_string)
                target_gene_list = raw_gene_list_string.strip().split(delimiter_type)
                candidates = intersect(query_candidates,target_gene_list)
                return render(request,'investigation/investigation.html',{'candidates':candidates})
           
            if request.FILES.get('qtl_gene_list_file'):
                        fi = request.FILES.get('qtl_gene_list_file').read()
                        target_gene_list = []
                        content = fi.encode('ascii','ignore')
                        delimiter_type = delimiter(content)
                        target_gene_list = content.strip().split(delimiter_type)
    
                        candidates = intersect(query_candidates,target_gene_list)
                        return render(request,'investigation/investigation.html',{'candidates':candidates})    

        
    else:
        form = investigationForm()
        form1 = investigationQTLForm()
        return render(request,'investigation/investigation.html',{'form':form,'form1':form1})
    
    
    
def delimiter(st):
    delimiter_type_list = ['\t',';',' ',',','\r\n','\n']
    for delimiter_ins in delimiter_type_list:
        if delimiter_ins in st:
            return delimiter_ins

def intersect(list1,list2):
    intersect_index = []
    inter = []
    list1_low = [gene.lower() for gene in list1]
    list2_low = [gene.lower() for gene in list2]
    for i in range(len(list2_low)):
        if list2_low[i] in list1_low:
            intersect_index.append(i)
    for ind in intersect_index:
        inter.append(list2[ind])
    inter = set(inter)
    return inter
    