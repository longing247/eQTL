import time
import json
import os
import re

from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required

from upload.models import Species,Experiment,ArraySpot,Transcript,Marker
from usersession.models import Task
from investigation.forms import investigationForm,investigationQTLForm,investigationTaskForm,investigationQTLTaskForm

@login_required(login_url="/login/")
def investigationView(request):
    if request.method=='POST':
        if request.POST.get('exp') and request.POST.get('thld') and request.POST.get('marker'):
            if request.POST.get('gene_list') and request.POST.get('gene_list_file'):
                raise Exception('You must choose only one, not both')
            if request.POST.get('gene_list') or request.FILES.get('gene_list_file'): 
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
                            if abs(float(line[marker_ind+1])) >= thld:
                                lod_probe_list.append(line[0])
                        
                    probe_list = ArraySpot.objects.filter(spot_id__in=lod_probe_list,experiment_name=exp)
                    gene_unicode_list = Transcript.objects.filter(spot_id__in=probe_list).values_list('transcript_name',flat=True)
                    target_gene_list = [ gene.encode('ascii','ignore') for gene in gene_unicode_list ]
                        
                    
                    if request.POST.get('gene_list'):
                        raw_gene_list_string = request.POST.get('gene_list').encode('ascii','ignore')
                        
                        delimiter_type = delimiter(raw_gene_list_string)
                        if delimiter!=' ':    
                            query_gene_list = raw_gene_list_string.strip().replace(' ','').split(delimiter_type)
                        else:
                            query_gene_list = raw_gene_list_string.strip().split(delimiter_type)
                        
                        inter = intersect(target_gene_list,query_gene_list)
                        has_inter = True
                        return render(request,'investigation/investigation.html',{'has_inter':has_inter,'intersection':inter,'exp':exp,'target_gene_list':target_gene_list,'query_gene_list':query_gene_list})
                        
                            
                    if request.FILES.get('gene_list_file'):
                        fi = request.FILES.get('gene_list_file').read()
       
                        target_gene_list = []
                        content = fi.encode('ascii','ignore')
                        delimiter_type = delimiter(content)
                        query_gene_list = content.strip().split(delimiter_type)
                        
                        inter = intersect(target_gene_list,target_gene_list)
                        has_inter = True
                        return render(request,'investigation/investigation.html',{'has_inter':has_inter,'intersection':inter,'exp':exp,'target_gene_list':target_gene_list,'query_gene_list':query_gene_list})
                    
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
                         
        elif request.POST.get('target_sel_qtl') and request.POST.get('thld'):
            if request.POST.get('gene_list') and request.POST.get('gene_list_file'):
                raise Exception('You must choose only one, not both')
            target_qtl = request.POST.get('target_sel_qtl')
            thld = float(request.POST.get('thld'))
            form = investigationTaskForm(request.POST)
            if form.is_valid():
                qtl_gene_lists = []
                
                #get Target qtl co-regulated gene list
                target_dic_ins = {}
                target_gene_list = getQTLGeneList(target_qtl,thld)
                target_qtl_ins = Task.objects.get(id = target_qtl)
                target_dic_ins['id'] = target_qtl
                target_dic_ins['exp'] = target_qtl_ins.experiment_id
                target_dic_ins['target_probe'] = ArraySpot.objects.get(id = target_qtl_ins.probe_id).spot_id
                target_trans_ins = Transcript.objects.get(id = target_qtl_ins.transcript_id)
                target_dic_ins['target_trans'] = target_trans_ins.transcript_name
                target_dic_ins['target_ref'] = target_trans_ins.ref_id
                target_dic_ins['target_marker'] = Marker.objects.get(id = target_qtl_ins.marker_id)
                target_dic_ins['target_lod_si'] = target_qtl_ins.lod_si
                
                exp = Experiment.objects.get(experiment_name = target_qtl_ins.experiment_id)
                target_dic_ins['target_spec'] = exp.species
                target_spot_list = ArraySpot.objects.filter(spot_id__in=target_gene_list,experiment_name = exp)
                target_trans_list = Transcript.objects.filter(id__in=target_spot_list).values_list('transcript_name',flat=True)
                target_dic_ins['target_trans_list'] = target_trans_list
                qtl_gene_lists.append(target_trans_list)
                #get query co-regualted gene list(s)           
                 
                if request.POST.getlist('query_sel_qtl'):
                    query_qtl_ins_list = []
                    query_qtls =  request.POST.getlist('query_sel_qtl')
                    if len(query_qtls)!=0:
                        for query_qtl in query_qtls:
                            query_dic_ins = {}
                            query_qtl_ins = Task.objects.get(id=query_qtl)
                            query_dic_ins['id'] = query_qtl
                            query_dic_ins['exp'] = query_qtl_ins.experiment_id
                            query_dic_ins['query_probe'] = ArraySpot.objects.get(id = query_qtl_ins.probe_id).spot_id
                            query_trans_ins = Transcript.objects.get(id = query_qtl_ins.transcript_id)
                            query_dic_ins['query_trans'] = query_trans_ins.transcript_name
                            query_dic_ins['query_ref'] = query_trans_ins.ref_id
                            query_dic_ins['query_marker'] = Marker.objects.get(id = query_qtl_ins.marker_id)
                            query_dic_ins['query_lod_si'] = query_qtl_ins.lod_si
                            
                            query_qtl_gene_list = getQTLGeneList(query_qtl,thld)
                            qtl_query_ins = Task.objects.get(id = query_qtl)
                            exp_ins = Experiment.objects.get(experiment_name = qtl_query_ins.experiment_id)
                            query_dic_ins['query_spec'] = exp_ins.species
                            query_spot_list = ArraySpot.objects.filter(spot_id__in=query_qtl_gene_list,experiment_name = exp_ins)
                            query_trans_list = Transcript.objects.filter(spot_id__in=query_spot_list).values_list('transcript_name',flat=True)
                            
                            query_dic_ins['query_trans_list'] = query_trans_list
                            
                            query_qtl_ins_list.append(query_dic_ins)
                            qtl_gene_lists.append(query_trans_list)
                            
                        inter = intersect_mul(*qtl_gene_lists)
                        for query in query_qtl_ins_list:
                            if query['query_spec']!=target_dic_ins['target_spec']:
                                raise Exception('Invalid comparison among different species')
                        has_inter = True
                        return render(request,'investigation/investigation.html',{'has_inter':has_inter,'intersection':inter,'target_QTL_ins':target_dic_ins,'query_QTL_ins_list':query_qtl_ins_list})
                else:
                    if request.POST.get('gene_list'):
                        raw_gene_list_string = request.POST.get('gene_list').encode('ascii','ignore')
                        delimiter_type = delimiter(raw_gene_list_string)
                        query_gene_list = raw_gene_list_string.strip().split(delimiter_type)
                        inter = intersect(target_gene_list,query_gene_list)
                        has_inter = True
                        return render(request,'investigation/investigation.html',{'has_inter':has_inter,'intersection':inter,'exp':exp,'target_gene_list':target_gene_list,'query_gene_list':query_gene_list})
                    if request.FILES.get('gene_list_file'):
                        fi = request.FILES.get('gene_list_file').read()
                        target_gene_list = []
                        content = fi.encode('ascii','ignore')
                        delimiter_type = delimiter(content)
                        query_gene_list = content.strip().split(delimiter_type)
                        inter = intersect(target_gene_list,query_gene_list)
                        has_inter = True
                        if len(inter)==0:
                            has_inter = False
                        return render(request,'investigation/investigation.html',{'has_inter':has_inter,'intersection':inter,'exp':exp,'target_gene_list':target_gene_list,'query_gene_list':query_gene_list})
                    if not request.POST.get('gene_list') and not request.POST.get('gene_list_file'):
                        return render(request,'investigation/investigation.html',{'target_QTL_ins':target_dic_ins})
                        
                        
                        
        elif request.POST.get('sel_qtl'):
            form = investigationQTLTaskForm(request.POST)
            if form.is_valid():
                qtl_list_candidates = []
                qtl_id = request.POST.get('sel_qtl')
                
                region = Task.objects.get(id=qtl_id).lod_si.encode('ascii','ignore')
                regex_for_chr = re.compile('([0-9]{1,2}|X|CP|MT)\s*(:)?\s*')
                regex_for_start_end = re.compile('(\d+)\s*(-)?\s*(\d+)\s*')
                chr_ = re.search(regex_for_chr,region).group().replace(' ','').replace(':','')
                start_,end_ = re.search(regex_for_start_end,region).group().replace(' ','').split('-')
                
                exp_ = Task.objects.get(id=qtl_id).experiment_id.encode('ascii','ignore')
                
                experiment = Experiment.objects.get(experiment_name = exp_)
                probes = ArraySpot.objects.filter(experiment_name = experiment)
                target_candidates = Transcript.objects.filter(spot_id__in = probes,chr=chr_,start__gte=start_,end__lte=end_).order_by('start').values_list('transcript_name',flat=True)
                target_candidates = [ candidate.encode('ascii','ignore' ) for candidate in target_candidates]
                qtl_list_candidates.append(target_candidates)
                if request.POST.get('qtl_gene_list') and request.POST.get('qtl_gene_list_file'):
                    raise Exception('You must choose only one, not both')
                
                if request.POST.getlist('query_qtls'):
                    query_qtls = request.POST.getlist('query_qtls')
                   
                    if len(query_qtls)!=0:
                        for qtl in query_qtls:
                            query_region = Task.objects.get(id=qtl).lod_si.encode('ascii','ignore')
                            query_chr_ = re.search(regex_for_chr,query_region).group().replace(' ','').replace(':','')
                            query_start_,query_end_ = re.search(regex_for_start_end,query_region).group().replace(' ','').split('-')
                            
                            query_exp_ = Task.objects.get(id=qtl).experiment_id.encode('ascii','ignore')
                            query_experiment = Experiment.objects.get(experiment_name = query_exp_)
                            query_probes = ArraySpot.objects.filter(experiment_name = query_experiment)
                            query_candidates = Transcript.objects.filter(spot_id__in = query_probes,chr=chr_,start__gte=start_,end__lte=end_).order_by('start').values_list('transcript_name',flat=True)
                            query_candidates = [ candidate.encode('ascii','ignore' ) for candidate in target_candidates]
                            qtl_list_candidates.append(query_candidates)
                            candidates = intersect_mul(*qtl_list_candidates)
                            return render(request,'investigation/investigation.html',{'candidates':candidates}) 
                    else:  
                        if request.POST.get('qtl_gene_list'):
                            raw_gene_list_string = request.POST.get('qtl_gene_list').encode('ascii','ignore')
                            delimiter_type = delimiter(raw_gene_list_string)
                            query_candidates = raw_gene_list_string.strip().split(delimiter_type)
                            candidates = intersect(target_candidates,query_candidates)
                            return render(request,'investigation/investigation.html',{'candidates':candidates})
                       
                        if request.FILES.get('qtl_gene_list_file'):
                            fi = request.FILES.get('qtl_gene_list_file').read()
                            target_gene_list = []
                            content = fi.encode('ascii','ignore')
                            delimiter_type = delimiter(content)
                            query_candidates = content.strip().split(delimiter_type)
                            candidates = intersect(target_candidates,query_candidates)
                            return render(request,'investigation/investigation.html',{'candidates':candidates})   
            
    else:
        if request.GET.getlist('QTL_list'):
            qtl_list = request.GET.getlist('QTL_list')
            task_list = Task.objects.filter(id__in=qtl_list)
            task_session = []
            for task in task_list:
                task_ins = {}
                task_ins['id'] = task.id
                task_ins['experiment_id'] = task.experiment_id
                task_ins['probe_id'] = ArraySpot.objects.get(id=task.probe_id).spot_id
                task_ins['transcript_id'] = Transcript.objects.get(id=task.transcript_id).transcript_name
                task_ins['ref_id'] = Transcript.objects.get(id=task.transcript_id).ref_id
                task_ins['marker_id'] = Marker.objects.get(id = task.marker_id).marker_name
                task_ins['lod_si'] = task.lod_si
                task_session.append(task_ins)
            
            form = investigationTaskForm()
            form1 = investigationQTLTaskForm()
            return render(request,'investigation/investigation.html',{'form':form,'form1':form1,'tasks':task_session})
                
            
        else:   
            form = investigationForm()
            form1 = investigationQTLForm()
            return render(request,'investigation/investigation.html',{'form':form,'form1':form1})       
        
    
def delimiter(st):
    delimiter_type_list = ['\t',';',',','\r\n','\n',' ']
    for delimiter_ins in delimiter_type_list:
        if delimiter_ins in st:
            return delimiter_ins

def checkSpace(st):
    if ' ' in st:
        return True
    else:
        return False
 

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

def intersect_mul(*d):
    result = set(d[0]).intersection(*d[1:])
    return result

def getQTLGeneList(qtl_id,thld):
    qtl_info = Task.objects.get(id=qtl_id)
    exp = Experiment.objects.get(experiment_name = qtl_info.experiment_id).experiment_name.encode('ascii','ignore')
    marker = Marker.objects.get(id = qtl_info.marker_id).marker_name.encode('ascii','ignore')
    lod_file_path = os.path.join(settings.MEDIA_ROOT,'data','%s' % exp,'lod.txt')
    
    gene_list = []
    with open(lod_file_path) as fi:
        marker_header = [i.strip() for i in fi.readline().split('\t')]
        try:
            target_marker_ind = marker_header.index(marker)
        except IndexError:
            print 'Query marker is not in the list'
        lines = fi.readlines()
        for line in lines:
            lod_profile = line.split('\t')
            if abs(float(lod_profile[target_marker_ind])) >=thld:
                gene_list.append(lod_profile[0])
    return gene_list

if __name__ == '__main__':
    d = [['a','b','c','d'],['b','c'],['c','d']]
    print intersect_mul(*d)
    
    