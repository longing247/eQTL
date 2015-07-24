from django.shortcuts import render

from upload.models import Species,Experiment,ArraySpot,Marker,Transcript
from experiment.Arabidopsis import Arabidopsis
from experiment.Celegans import Celegans

# Create your views here.
def browserView(request):
    if request.method=='GET':
        if request.GET.get('search_type') and request.GET.get('search'):
            type = request.GET.get('search_type')
            search = request.GET.get('search')
            if 'genes' in type:
                exp_ins =  Experiment.objects.get(experiment_name__iexact = search)
                spec = exp_ins.species.species_name.encode('ascii','ignore')
                link = getLinkPrefix(spec)
                array_ins = ArraySpot.objects.filter(experiment_name =exp_ins)
                trans_ins = Transcript.objects.filter(spot_id__in=array_ins).exclude(chr='').order_by('chr','start')
                return render(request,'browser/browser.html',{'genes':trans_ins,'link':link})
                    
            if 'markers' in type:
                exp_ins =  Experiment.objects.get(experiment_name__iexact = search)
                marker_ins = Marker.objects.filter(experiment_name=exp_ins).order_by('marker_chr','marker_start')
                return render(request,'browser/browser.html',{'markers':marker_ins})
                
            if 'gene' in type:
                gene_ins = Transcript.objects.filter(transcript_name__iexact = search)[0] #expect each gene symbol is unique defined across Species.
                spec = gene_ins.spot_id.experiment_name.species.species_name.encode('ascii','ignore')
                link = getLinkPrefix(spec)
                return render(request,'browser/browser.html',{'gene':gene_ins,'link':link})
    
            if 'marker' in type:
                marker_ins = Marker.objects.filter(marker_name__iexact= search)[0]
                return render(request,'browser/browser.html',{'marker':marker_ins})
                
        else:
            return render(request,'browser/browser.html',{})
            
def getLinkPrefix(spec):
    link = ''
    if 'Arabidopsis Thaliana' in spec:
        link = 'http://plants.ensembl.org/Arabidopsis_thaliana/Gene/Summary?g='
    elif 'Caenorhabditis Elegans' in spec:
        link = 'http://www.wormbase.org/species/c_elegans/gene/'
    return link
    
    
    
    