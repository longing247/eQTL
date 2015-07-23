import os

from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required

from upload.models import Species,Experiment,ArraySpot,Transcript,Marker

from .find_enrichment import read_associations
from .go_enrichment import GOEnrichmentStudy
from .obo_parser import GODag

#from upload.models import Experiment,ArraySpot,Transcript,Marker
#from usersession.models import Task
#from investigation.forms import investigationForm,investigationQTLForm,investigationTaskForm,investigationQTLTaskForm

# Create your views here.
@login_required(login_url="/login/")
def GOView(request):
    #if request.method=='GET':

    if request.method=="POST":
        if request.POST.get('gene_list') and request.POST.get('exp'):
            
            gene_str = request.POST.get('gene_list').encode('ascii','ignore').replace('\r','').replace('\n','').replace('\t','').strip()
            study = [ i.encode('ascii','ignore') for i in gene_str.strip().split(',') if i!='']
            
            exp = request.POST.get('exp')
            exp_ins = Experiment.objects.get(experiment_name = exp)
            spec = Species.objects.get(species_name=exp_ins.species).species_name.encode('ascii','ignore')
            spots = ArraySpot.objects.filter(experiment_name=exp_ins)
            trans = Transcript.objects.filter(spot_id__in=spots)
            pop = trans.values_list('transcript_name',flat=True)
            
            
            assoc_fn = os.path.join(settings.MEDIA_ROOT,'association/%s/%s' % (spec,'association.txt'))
            assoc = read_associations(assoc_fn)
            
            obo_fn = os.path.join(settings.MEDIA_ROOT,'obo/go-basic.obo')
            obo_dag = GODag(obo_file = obo_fn)
            
            methods = ["bonferroni", "sidak", "holm","fdr"]
            alpha = 0.05
            if request.POST.getlist('multiple_testing'):
                set_mul_test = set(request.POST.getlist('multiple_testing'))
                methods = [i.encode('ascii','ignore') for i in set_mul_test]
            if request.POST.get('alpha'):
                a = request.POST.get('alpha').encode('ascii','ignore')

                if a.replace('.','',1).isdigit():
                    if float(a)>0.0 or float(a)<1.0:
                        alpha = float(a)
            go = GOEnrichmentStudy(pop,assoc,obo_dag,alpha = alpha, study=study,methods=methods)
            results = go.results
            header = "id enrichment description ratio_in_study ratio_in_pop p_uncorrected p_bonferroni p_holm p_sidak p_fdr".split()
            ind_list = [i for i in range(len(methods)) if methods[i] in header] 
            go_list = []
            first= "id description ratio_in_study ratio_in_pop".split()
            if "bonferroni" in methods:
                first.append('p_bonferroni')
            if "holm" in methods:
                first.append('p_holm')
            if "sidak" in methods:
                first.append('p_sidak')
            if "fdr" in methods:
                first.append('p_fdr')
            for result in results:
                go_ins = [result.id,result.description,result.ratio_in_study,result.ratio_in_pop]
                if "bonferroni" in methods:
                    go_ins.append(float(result.p_bonferroni))
                if "holm" in methods:
                    go_ins.append(float(result.p_holm))
                if "sidak" in methods:
                    go_ins.append(float(result.p_sidak))
                if "fdr" in methods:
                    go_ins.append(float(result.p_fdr))
                go_list.append(go_ins)
            return render(request,'go/go.html',{'study':study,'exp':exp,'go_list':go_list,'first':first})
        
 