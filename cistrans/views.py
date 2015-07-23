import json
import os

from django.shortcuts import render,render_to_response,HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.conf import settings

from upload.models import ArraySpot,Experiment,Transcript,Marker
from upload.views import outputJson
from usersession.models import Task
# Create your views here.
@login_required(login_url="/login/")
def eQTLPlotView(request):
    '''
    plot eQTL maping
    
    '''
    experiments = Experiment.objects.all().values_list('experiment_name',flat=True)
    if request.method=='GET':
        if request.GET.get('experiment_name'):
            exp_name = request.GET.get('experiment_name')
            user_ = User.objects.get(username = request.user)
            user_tasks = Task.objects.filter(user_name=user_).values('id','experiment','probe','marker')
            if request.GET.get('thld'):
                qtl_file = 'lod.txt'
                try:
                    thld = float(request.GET.get('thld'))
                    output = 'lod%s.json' % request.GET.get('thld').encode('ascii','ignore')
                    if not os.path.isfile(os.path.join(settings.MEDIA_ROOT,'data','%s' % exp_name,output)):
                        outputJson(exp_name,qtl_file,thld,output)
                    return render_to_response('cistrans/eQTL.html',{'experiment_name':exp_name,
                                                                    'experiments':experiments,
                                                                    'task_list':user_tasks,
                                                                    'user':request.user,
                                                                    'thld':request.GET.get('thld')}) 
                except ValueError:
                    return HttpResponse('<h1> invalid LOD threshold </h1>')
            else:
                
                user_ = User.objects.get(username = request.user)
                user_tasks = Task.objects.filter(user_name=user_).values('id','experiment','probe','marker')
                lodthld = Experiment.objects.get(experiment_name = exp_name).lodthld
                return render_to_response('cistrans/eQTL.html',{'experiment_name': exp_name,
                                                                'experiments':experiments,
                                                                'task_list':user_tasks,
                                                                'user':request.user,
                                                                'lodthld':lodthld})
        else:
            user_ = User.objects.get(username = request.user)
            user_tasks = Task.objects.filter(user_name=user_).values('id','experiment','probe','marker')         
            return render_to_response('cistrans/eQTL.html',{'experiments':experiments,
                                                            'task_list':user_tasks,
                                                            'user':request.user})                                 
    
    elif request.method=='POST':
        if request.POST.get('QTL'):
            post_text = request.POST.get('QTL')
            ins = post_text.split(' ')
            ins = [i.encode('ascii','ignore').strip() for i in ins]
            info_list = []
            for task in ins:
                ind = task.index(':')
                info_list.append(task[ind+1:].strip())
            task_ins = Task()
            task_ins.user_name = User.objects.get(username = request.user)
            task_ins.experiment = Experiment.objects.get(experiment_name = info_list[0])
            task_ins.probe = ArraySpot.objects.get(spot_id = info_list[1],experiment_name = task_ins.experiment)
            task_ins.transcript = Transcript.objects.get(transcript_name = info_list[2],spot_id = task_ins.probe)
            task_ins.marker = Marker.objects.get(marker_name = info_list[3],experiment_name = task_ins.experiment)
            task_ins.lod_si = info_list[4]
            task_ins.save()
            
            user_ = User.objects.get(username = request.user)
            user_tasks = Task.objects.filter(user_name=user_).values_list('id','experiment','probe','marker')
            
            task_list = []
            for id,exp,probe,mark in user_tasks:
                spot_id = ArraySpot.objects.get(id=probe).spot_id.encode('ascii','ignore')
                marker_name = Marker.objects.get(id = mark).marker_name.encode('ascii','ignore')
                task_list.append((str(id),exp.encode('ascii','ignore'),spot_id,marker_name))
            return HttpResponse(json.dumps(task_list),content_type="application/json")
        
        if request.POST.get('del_task'):
            post_text = request.POST.get('del_task')
            task = Task.objects.get(user_name = request.user,id=post_text).delete()
            user_ = User.objects.get(username = request.user)
            user_tasks = Task.objects.filter(user_name=user_).values_list('id','experiment','probe','marker')         
            task_list = []
            for id,exp,probe,mark in user_tasks:
                spot_id = ArraySpot.objects.get(id=probe).spot_id.encode('ascii','ignore')
                marker_name = Marker.objects.get(id = mark).marker_name.encode('ascii','ignore')
                task_list.append((str(id),exp.encode('ascii','ignore'),spot_id,marker_name))
            
            return HttpResponse(json.dumps(task_list),content_type="application/json")
