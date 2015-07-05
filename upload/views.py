import time
import json
import os

from parser import getThld,outputJSON
from experiment.Arabidopsis import Arabidopsis
from experiment.Celegans import Celegans
 
from django.shortcuts import render_to_response,HttpResponseRedirect,render
from django.contrib.auth.decorators import login_required

from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth.models import User
from django.conf import settings

#from .forms import ModelFormWithFileField
from upload.models import Species,Experiment,Line,ArraySpot,Marker,Transcript
from upload.forms import uploadForm

@login_required(login_url="/login/")
def uploadView(request):
    '''handle parsing file, and saving each entry to MySQL DB
    '''
    
    #initialize database
    #insert into upload_species (species_name) values ('Arabidopsis Thaliana');
    #insert into upload_species (species_name) values ('Caenorhabditis Elegans');
    
    #c = {}
    #c.update(csrf(request))
    
    if request.method=='POST':
        
        form = uploadForm(request.POST,request.FILES)
        if form.is_valid():  
            #Validation of POST.get('')
            
            spec = request.POST.get('species')
            exp_name = request.POST.get('experiment')
            ps = request.POST.get('parent')
            reference = request.POST.get('ref') 
            pm = request.POST.get('pubmed')
            
            _array_file = request.FILES.get('arrayfile')
            _marker_file = request.FILES.get('markerfile')
            _genotype_file = request.FILES.get('genotypefile')#missing RILs genotype allowed, return None
            _lod_file = request.FILES.get('lodfile')
            
            _array = request.FILES.get('arrayfile').temporary_file_path()
            _marker = request.FILES.get('markerfile').temporary_file_path() 
            _genotype = request.FILES.get('genotypefile').temporary_file_path() if _genotype_file != None else None # missing RILs genotype
            _lod = request.FILES.get('lodfile').temporary_file_path()
            _user = request.user
            if spec and exp_name and _array \
                and _marker and _lod: # instead of request.FILES['genefile'], using get('genefile') to avoid multi dictionary key value exception
    
                #procedure of data validation
                
                array_info_header,array_info_matrix = readTabFileCol(_array)
                spots_index = array_info_header.index('spot') # raise Exception!!!
                transcripts_index = array_info_header.index('transcript') 
                refs_index = array_info_header.index('ref') 
                chrs_index = array_info_header.index('chr') 
                starts_index = array_info_header.index('start') 
                ends_index = array_info_header.index('end') 
                
                spots = matrixCol(array_info_matrix,spots_index)
                transcripts = matrixCol(array_info_matrix,transcripts_index)
                refs = matrixCol(array_info_matrix,refs_index)
                chrs = matrixCol(array_info_matrix,chrs_index)
                starts = matrixCol(array_info_matrix,starts_index)
                ends = matrixCol(array_info_matrix,ends_index)
                
                
                marker_header,marker_matrix = readTabFileCol(_marker)
                marker_index = marker_header.index('marker')
                marker_chr_index = marker_header.index('chr')
                marker_start_index = marker_header.index('start')
                marker_end_index = marker_header.index('end')
                
                markers = matrixCol(marker_matrix,marker_index)
                markers_chr = matrixCol(marker_matrix,marker_chr_index)
                markers_start = matrixCol(marker_matrix,marker_start_index)
                markers_end = matrixCol(marker_matrix,marker_end_index)
                
                if _genotype_file != None:
                    geno_lines,geno_markers = readTabFile2D(_genotype)

                lod_markers,lod_spots = readTabFile2D(_lod)                
    
                # compare spots with lod_spots, markers with lod_markers and geno_markers 
                # did not work: the number of spots in Arrayinfo is 45221, whereas the number of spots in LOD is 44382.
                # a number of spots were not used for QTL mapping
                
                for i in range(len(markers)):
                    if markers[i]!=lod_markers[i]:
                        print i,markers[i],lod_markers[i]
                
                if set(markers) != set(lod_markers):
                    print 'Marker information is differently given among MarkerInfo, genotype, and LOD'
                
                else:
                    #create and save Experiment instance 
                    sp = Species.objects.get(species_name=spec)
                    login_user = User.objects.get(username = _user)
                    exp_ins = Experiment()
                    exp_ins.species = sp
                    exp_ins.experiment_name =exp_name
                    exp_ins.parental_strain = ps
                    exp_ins.reference = reference
                    exp_ins.pubmed = pm
                    exp_ins.upload_user = login_user
                    exp_ins.array_file = _array_file
                    exp_ins.marker_file = _marker_file
                    if _genotype_file != None:
                        exp_ins.genotype_file = _genotype_file 
                    exp_ins.lod_file = _lod_file
                    pval_thld,lod_thld,lod_dic = getThld(_lod)
                    exp_ins.pvalthld = pval_thld
                    exp_ins.lodthld = lod_thld  
                    exp_ins.save()
                    try:
                        os.makedirs(os.path.join(settings.MEDIA_ROOT,'data','%s' % exp_name,'probe')) 
                    except OSError as e:
                        print e.errno
                    probe_out_path = os.path.join(settings.MEDIA_ROOT,'data','%s' % exp_name,'probe')
                    outputJSON(lod_dic,probe_out_path)# write probe profile file in probe folder
                    
                    #create and save Line instances
                    if _genotype_file != None:
                        for line in geno_lines:
                            line_ins = Line()
                            line_ins.experiment_name = Experiment.objects.get(experiment_name=exp_name)
                            line_ins.line_name = line
                            line_ins.save()
                    
                    #create and save ArraySpot instances
                    for spot in spots:
                        spot_ins=ArraySpot()
                        spot_ins.experiment_name = Experiment.objects.get(experiment_name = exp_name)
                        spot_ins.spot_id = spot
                        spot_ins.save()
                    
                    #create and save Marker instances
                    for i in range(0,len(markers)):
                        marker_ins = Marker()
                        marker_ins.marker_name = markers[i]
                        marker_ins.marker_chr = markers_chr[i]
                        marker_ins.marker_start = int(markers_start[i]) if markers_start[i]!='' else None
                        marker_ins.marker_end = int(markers_end[i]) if markers_end[i]!='' else None
                        marker_ins.experiment_name = Experiment.objects.get(experiment_name = exp_name)
                        marker_ins.save()
                    
                    #create and save Transcript instances                    
                    for i in range(0,len(spots)):
                        transcript_ins = Transcript()
                        transcript_ins.transcript_name = transcripts[i] 
                        transcript_ins.spot_id = ArraySpot.objects.get(spot_id = spots[i],experiment_name= exp_name)
                        transcript_ins.ref_id = refs[i]
                        transcript_ins.chr = chrs[i]
                        transcript_ins.start = int(starts[i]) if starts[i]!='' else None
                        transcript_ins.end = int(ends[i]) if ends[i]!='' else None
                        transcript_ins.save()
                    
                    lod_out_path = 'lod.json'
                    lod_file_rn = 'lod.txt'
                    outputJson(exp_name,lod_file_rn,lod_thld,lod_out_path)
                    
                    return render_to_response('upload/sucess.html',context_instance=RequestContext(request))
        
            else:
                print 'incomplete update files'
                messages.error(request,'Error')
                return render_to_response('upload/upload.html')
            
    else:# request.method =='GET'
        form = uploadForm()

    return render_to_response('upload/upload.html',{'user':request.user,'form':form},context_instance=RequestContext(request))


        
def readTabFileCol(f):
    '''
    description: collect tab delimited txt file by parsing each columns in a file into a matrix 
    
    @type f: tab delimited file
    @param f: array info file
    
    @rtype: header: list
    @return header: header of a files
    
    @rtype data_matrix: list (matrix: list of lists)
    @return data_matrix: a data matrix that describes a file 
    
    '''
    print 'File %s is being parsed' % f
    data_matrix = []
    with open(f) as fi:
        tic = time.time()
        first_line = fi.readline().rstrip()
        header = first_line.split('\t')
        print header
        
        lines =fi.readlines()
        for line in lines:
            row = line.rstrip().split('\t')
            data_matrix.append(row)
        toc = time.time()
        print 'Processed in %s seconds' % (toc-tic)
        return header,data_matrix  
        

def readTabFile2D(f):
    '''
    description: collect tab delimited txt file header (all column names of a file) and the first column of a file
    
    @type f: tab delimited file
    @param f: array info file
    
    @rtype header: list
    @return header: header - names of each columns (1st name will be ignored)
    
    @rtype first_column: list
    @return first_column: first column of the file (1st element of the column will be ignored)
    '''
    print 'File %s is being parsed' % f
    header = []
    first_column = []
    with open(f) as fi:
        tic = time.time()
        first_line = fi.readline().rstrip()
        header = first_line.split('\t')[1:]
        lines = fi.readlines()
        for line in lines:
            col = line.rstrip().split('\t')
            first_column.append(col[0])
        toc = time.time()
        print 'Processed in %s seconds' % (toc-tic)
    return header,first_column   

    
def matrixCol(mat,col_index):
    '''
    description: collect a column list from a matrix
    
    @type mat: list
    @param mat: lists of list (matrix)
    
    @type col_index: int
    @param mat: index of a column in a matrix
    
    @rtype col: list:
    @return col: a list contains elements in a column of a matrix
    '''
    
    col = [row[col_index] for row in mat]
    return col


def outputJson(experiment_name,qtl_file,thld,output):
    '''
    description: parse upload information into JSON file format later which later will be used for cistrans plot. 
    
    @type experiment_name: name of experiment
    @param experiment_name: string
    
    @type qtl_file: qtl mapping output
    @param qtl_file: file
    
    @type thld: LOD theshold
    @param thld: decimal
    
    @rtype output: path of output file
    @return output: string
    
    '''
    
    tic = time.time()
    in_path = os.path.join(settings.MEDIA_ROOT,'data/%s/%s' % (experiment_name,qtl_file))
    out_path = os.path.join(settings.MEDIA_ROOT,'data/%s/%s' % (experiment_name,output))
    
    output_dic = {}
    
    #define KEY chrnames and chr
    species_name = getSpecies(experiment_name)
    chr_nr = None

    if species_name == 'Arabidopsis Thaliana':
        arabidopsis = Arabidopsis()
        output_dic['chrnames'] = arabidopsis.getChr()
        output_dic['chr'] = arabidopsis.getChrLen()
        chr_nr = output_dic['chrnames']
    
    elif species_name == 'Caenorhabditis Elegans':
        celegans = Celegans()
        output_dic['chrnames'] = celegans.getChr()
        output_dic['chr'] = celegans.getChrLen()
        chr_nr = output_dic['chrnames']
    
    #define KEY spec
    output_dic['spec'] = species_name;
    
    #define KEY pmarknames
    chr_marker_list_dic = {}
    for i in chr_nr:
        chr_marker_list_dic[i] = list(getChrMarkers(experiment_name,i))  #django.db.models.query.ValuesListQuerySet
    output_dic['pmarknames'] = chr_marker_list_dic

    # define KEY markers
    markers = list(getMarkers(experiment_name))
    output_dic['markers'] = markers
    
    # define KEY pmark
    marker_list_dic = {} 
    marker_queryset_list = getMarkerObjects(experiment_name)
    for m in marker_queryset_list:
        m_info ={'chr':m.marker_chr,'start':int(m.marker_start)}
        marker_list_dic[m.marker_name.encode('ascii','ignore')] = m_info
    output_dic['pmark'] = marker_list_dic
    
    # define KEY spot/gene
    spots_list = ArraySpot.objects.filter(experiment_name = experiment_name)
    spots_dic = {}
    for spot in spots_list:
        trans_ins = Transcript.objects.get(spot_id= spot)
        if trans_ins.start !='' and trans_ins.chr !='' :
            spots_dic[spot.spot_id] = {'chr':trans_ins.chr,'start':int(trans_ins.start),'end':int(trans_ins.end),'ref':trans_ins.ref_id,'transcript':trans_ins.transcript_name}
        else:
            spots_dic[spot.spot_id] = {'chr':'1','start':0,'end':0,'ref':trans_ins.ref_id,'transcript':trans_ins.transcript_name}
    output_dic['spot'] =  spots_dic
    
    with open(in_path) as fi:
        i = 0
        j = 0
        markers_lod = []
        peaks_list = []

        chr_names = output_dic['chrnames'] 
        with open(out_path,'w') as fo:
            first_line = fi.readline().rstrip()
            markers_lod = first_line.split('\t')[1:]
            lines = fi.readlines()
            
            #count number of markers per chromosome
            chr_nr_of_markers = {}
            nr_of_markers = 0
            
            for chr_ref1 in chr_names:  
                chr_nr_of_markers[chr_ref1] = len(output_dic['pmarknames'][chr_ref1])
            for line in lines:
                j+=1
                col = line.rstrip().split('\t')
                # assign LOD value to 0 if null
                lod_list = [ float(lod) if lod!='' else 0.0 for lod in col[1:]] 
                k = 0 # splice index
                lod_list_chr = {} #initialise lod_list_chr         
                #splice lod_list to sub_lod_list per chromosome
                for chr_ref2 in chr_names:
                    lod_list_chr[chr_ref2] = lod_list[k:k+chr_nr_of_markers[chr_ref2]]
                    k += chr_nr_of_markers[chr_ref2]
                
                for chr_ref3 in chr_names: # lod list per chromosome
                    
                    #check if any significant LOD value in the list per chromosome
                    if any(x for x in lod_list_chr[chr_ref3] if abs(x)>=thld):
                        interval_list = []
                        ref_index_list = []
                        for m in range(len(lod_list_chr[chr_ref3])):
                            if abs(lod_list_chr[chr_ref3][m])>=thld:
                                ref_index_list.append(m)
                        #group continuous significant LOD 
                        interval_list = list(ranges(ref_index_list))
                        
                        # if any intervals
                        for interval in interval_list:
                            i+=1
                            start,end = interval[0],interval[1]
                            
                            #LOD peak and LOD index
                            #find the max LOD value per significant LOD interval per chromosome
                            qtl_lod = max(lod_list_chr[chr_ref3][start:end+1])
                            qtl_index  = lod_list_chr[chr_ref3].index(qtl_lod) # LOD peak
                            
                            #initialize eQTL interval
                            inv_start = inv_start_lod_support = output_dic['chr'][chr_ref3]['start']
                            inv_end = inv_end_lod_support  = output_dic['chr'][chr_ref3]['end']
                            
                            #1 LOD support interval
                            lod_support = qtl_lod-1
                            
                            ##initialize eQTL interval
                            inv_start_ind_lod_support = inv_end_ind_lod_support = qtl_index  
                                                       
                            for ind in range(qtl_index,start-1 if start!=0 else start):
                                if lod_list_chr[chr_ref3][ind]>lod_support:
                                    inv_start_ind_lod_support = ind                         
                            for ind in range(qtl_index,end+1): #end+1 will not raise list index exception
                                if lod_list_chr[chr_ref3][ind]>lod_support:
                                    inv_end_ind_lod_support = ind
                            
                            #define LOD interval
                            if start>0 and end<len(lod_list_chr[chr_ref3])-1:
                                inv_start = getMarkerPos(experiment_name,output_dic['pmarknames'][chr_ref3][start-1])
                                inv_end = getMarkerPos(experiment_name,output_dic['pmarknames'][chr_ref3][end+1]) 
                                
                            if start==0 and end<len(lod_list_chr[chr_ref3])-1:
                                inv_end = getMarkerPos(experiment_name,output_dic['pmarknames'][chr_ref3][end+1]) 
                            
                            if start>0 and end==len(lod_list_chr[chr_ref3])-1:
                                inv_start = getMarkerPos(experiment_name,output_dic['pmarknames'][chr_ref3][start-1])
                            
                            #define one LOD support interval
                            if inv_start_ind_lod_support ==0 and inv_end_ind_lod_support != len(lod_list_chr[chr_ref3])-1:
                                inv_end_lod_support = getMarkerPos(experiment_name,output_dic['pmarknames'][chr_ref3][inv_end_ind_lod_support+1])
                            if inv_start_ind_lod_support !=0 and inv_end_ind_lod_support== len(lod_list_chr[chr_ref3])-1:
                                inv_start_lod_support = getMarkerPos(experiment_name,output_dic['pmarknames'][chr_ref3][inv_start_ind_lod_support-1])
                            if inv_start_ind_lod_support !=0 and inv_end_ind_lod_support!= len(lod_list_chr[chr_ref3])-1:
                                inv_start_lod_support = getMarkerPos(experiment_name,output_dic['pmarknames'][chr_ref3][inv_start_ind_lod_support-1])
                                inv_end_lod_support = getMarkerPos(experiment_name,output_dic['pmarknames'][chr_ref3][inv_end_ind_lod_support+1]) 
                                
                            #plot only peak LOD
                            lod_dic={} #empty dictionary for each iteration

                            #save to lod_dic
                            lod_dic['interval'] = '%s:%s-%s' % (chr_ref3,inv_start,inv_end) 
                            lod_dic['lod_support_interval'] = '%s:%s-%s' % (chr_ref3,inv_start_lod_support,inv_end_lod_support)  
                            lod_dic['spot'] = col[0].upper()
                            lod_dic['marker'] = output_dic['pmarknames'][chr_ref3][qtl_index]
                            lod_dic['lod'] = lod_list_chr[chr_ref3][qtl_index]     
                            lod_dic['transcript'] = output_dic['spot'][col[0].upper()]['transcript'] 
                            lod_dic['ref'] = output_dic['spot'][col[0].upper()]['ref'] 
                            peaks_list.append(lod_dic)
                        
                            '''
                            #plot every significant LOD scores
                            for step in range(start,end+1):
                                lod_dic={} #empty dictionary for each iteration
                                #save to lod_dic
                                lod_dic['interval'] = '%s:%s-%s' % (chr_ref3,inv_start,inv_end) 
                                lod_dic['spot'] = col[0]
                                lod_dic['marker'] = output_dic['pmarknames'][chr_ref3][step]
                                lod_dic['lod'] = lod_list_chr[chr_ref3][step]     
                                peaks_list.append(lod_dic)
                            '''
                                                                 
                
    output_dic['peaks'] = peaks_list
    
    with open(out_path,'w') as fo:
        json.dump(output_dic,fo,indent=4)
    print i,j
    toc=time.time()
    print 'Processed in %s seconds' % (toc-tic)

#simple query from database

def getMarkers(experiment):
    marker_list = Marker.objects.filter(experiment_name = experiment).order_by('marker_chr','marker_start').values_list('marker_name',flat=True)
    return marker_list 

def getChrMarkers(experiment,i):
    marker_list = Marker.objects.filter(experiment_name = experiment,marker_chr=i).order_by('marker_start').values_list('marker_name',flat=True)
    encode_marker_list = [marker.encode('ascii','ignore') for marker in marker_list]
    return encode_marker_list     

def getMarkerObjects(experiment):
    marker_list = Marker.objects.filter(experiment_name = experiment).order_by('marker_chr','marker_start')
    return marker_list 

def getSpecies(exp):
    species_name = Experiment.objects.get(experiment_name = exp).species.species_name
    return species_name

def getMarkerPos(exp,marker):
    return Marker.objects.get(experiment_name = exp,marker_name = marker).marker_start

def ranges(series_list):
    '''
    identify groups of continuous numbers in a list and group the continuous numbers as a sub-list
    for example,
    [1 ,2 ,6, 7, 8, 9, 10, 11]
    [(1,2),(6, 11)]
    '''
    start,end = series_list[0],series_list[0]
    for n in series_list[1:]:
        if n-1 ==end: # Part of the group, bump the end
            end = n
        else: # Not part of the group, yield current group and start a new
            yield start,end
            start = end = n
    yield start,end #Yield the last group

if __name__ == '__main__':
    
    #Rockman_etal_2010 3.512 0.000307339959 3.512380971
    #Vinuela_etal_2010_age1 4.304
    #Vinuela_etal_2010_age2 4.437
    #Vinuela_etal_2010_age3 4.920
    #Joosen_etal_2012 0.000139798657224 3.854497
    #Keurentjes_etal_2007 0.000495268834226 3.305159
    #Snoek_Terpstra_etal_2012 0.000815202066657 3.088734728
    
    
    
    exp_name = 'Joosen_etal_2012_env'
    output = 'lod_re.json'
    qtl_file = 'lod.txt'
    pval_thld,lod_thld,lod_dic = getThld(os.path.join(settings.MEDIA_ROOT,'data','%s' % exp_name,qtl_file))

    
    '''
    try:
        os.makedirs(os.path.join(settings.MEDIA_ROOT,'data','%s' % exp_name,'probe')) 
    except OSError as e:
        print e.errno
    probe_out_path = os.path.join(settings.MEDIA_ROOT,'data','%s' % exp_name,'probe')
    outputJSON(lod_dic,probe_out_path)# write probe profile file in probe folder
    outputJson(exp_name,qtl_file,lod_thld,output)
    '''             
    outputJson(exp_name,qtl_file,lod_thld,output)
    #pass

    #Rockman 22783 44381
    #Vinuela 663 23232
    #Vinuela 564 23232
    #Vinuela 210 23232
    #Joosen 2791 29304
    #Joosen_env 6 29304
    #Keurentjes 10116 24065
    #Basten 13255 20833

    