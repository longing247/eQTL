import os

from django.shortcuts import render,render_to_response
from django.conf import settings
from upload.models import ArraySpot,Experiment
# Create your views here.
def eQTLPlotView(request):
    '''
    plot eQTL maping
    
    '''
    if request.GET.get('experiment_name'):
        exp_name = request.GET.get('experiment_name')
        
        selected_spot = ArraySpot.objects.all()[0].spot_id
        #spot ='AGIUSA1'
        return render_to_response('cistrans/eQTL.html',{'selected_spot':selected_spot,
                                                        'experiment_name': exp_name,

                                                   })
    else:
        experiments = Experiment.objects.all().values_list('experiment_name',flat=True)
        return render_to_response('cistrans/eQTL.html',{'experiments':experiments})
