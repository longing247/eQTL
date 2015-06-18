'''
Created on Dec 18, 2014

@author: jiao
'''
from numpy import array, empty   
import sys
import os
import time
import math
import operator
from ngslib import bh_rejected,bh_qvalues,get_pi0,storey_qvalues

#sys.path.append('/mnt/geninf15/prog/www/django/QTL')
sys.path.append('/User/yaya/www/QTLProject')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QTLProject.settings')

from django.db.models import Q


def significantLOD(exp,_gxe):
    '''
    LOD:

    The log of the odds (LOD) ratio provides a measure of the association between variation in a phenotype and genetic differences (alleles) at a particular chromosomal locus. 
    It also provides a measure of the strength of linkage between two markers and can be used to evaluate whether two or more markers to each other on the same chromosome.

    A LOD score is defined as the logarithm of the ratio of two likelihoods:
    (1) the likelihood for the alternative hypothesis (that there is a QTL) and (2) the likelihood of the null hypothesis (that there is no QTL). 
    Likelihoods are probabilities, but they are not Pr(hypothesis | data) but rather Pr(data | hypothesis). 
    That's why they are called likelihoods rather than probabilities. (The "|" symbol translates to "given the").

    In the two likelihoods, one has maximized over the various nuisance parameters (the mean phenotypes for each genotype group, or overall for the null hypothesis, and the residual variance). 
    Or one can say, one has plugged in the maximum likelihood estimates for these nuisance parameters.

    With complete data at a marker, the log likelihood for the normal model reduces to the (-n/2) times the log of the residual sum of squares.

    LOD values can be converted to LRS scores (likelihood ratio statistics) by multiplying by 4.61.
    
    [Williams RW, June 15, 2005, updated with text from Karl Broman, Oct 28, 2010]
    '''
    tic = time.time()
    #lod1 = -math.log10(lod_th)
    #lod2 = -lod1
    #print lod1,lod2
    #lod_list = LOD.objects.filter(Q(LOD_score__gte=lod_th) |Q(LOD_score__lte=-lod_th),experiment_name=exp).values('id','LOD_score').order_by('-LOD_score')
    lod_list = LOD.objects.filter(experiment_name=exp,gxe=_gxe).values_list('LOD_score',flat=True).order_by('-LOD_score')
    lod_list = list(lod_list)
    
    print 'Size of the QueryValueSet %d' % sys.getsizeof(lod_list)
    toc = time.time()
    print 'QuerySet was successfully finished in %f seconds'%(toc-tic)
    return lod_list   

def LODToPval(lod_score):
    '''
    The LOD is also roughly equivalent to the -log(P), where P is the probability of linkage (P = 0.001 => 3). 
    The LOD itself is not a precise measurement of the probability of linkage, but in general for F2 crosses and RI strains, values above 3.3 will usually be worth attention for simple interval maps.
    [Williams RW, June 15, 2005, updated with text from Karl Broman, Oct 28, 2010]
    '''
    pval = math.pow(10,-math.fabs(lod_score))
    return pval


def significantPval(lod_list):
    '''
    Add an extra attribute 'pval' into each entry resulted from significantLOD()
    '''
    tic = time.time()
    sorted_lod_list = sorted(map(abs,lod_list),reverse=True) #sort the list which take the absolute value; The bigger LOD socre, the smaller p valuue
    print 'Size of the sorted input lod list %d' % sys.getsizeof(sorted_lod_list)
    pval_list = []
    for lod in sorted_lod_list:
        pval_list.append(LODToPval(lod))
    del sorted_lod_list
    print 'Size of the sorted input lod list %d after deleting' % sys.getsizeof(pval_list)
    print 'Size of the sorted p value list %d' % sys.getsizeof(pval_list)
    toc = time.time()
    print 'Pval list length: %f' % len(pval_list)
    print 'pval list was converted successfully in %f seconds'%(toc-tic)
    return pval_list

def correct_pval_for_multiple_testing(pval, correction_type):                
    """                                                                                                   
    consistent with R, but not used yet.
    """
    tic = time.time()                                                                     
    pval = array(pval) 
    n = int(pval.shape[0])                                                                           
    adjust_pval = empty(n)
    if correction_type == "Bonferroni":                                                                   
        adjust_pval = n * pval
    elif correction_type == "Bonferroni-Holm":                                                            
        values = [ (pvalue, i) for i, pvalue in enumerate(pval) ]                                      
        values.sort()
        for rank, vals in enumerate(values):                                                              
            pvalue, i = vals
            adjust_pval[i] = (n-rank) * pvalue                                                            
    elif correction_type == "Benjamini-Hochberg":                                                         
        values = [ (pvalue, i) for i, pvalue in enumerate(pval) ]                                      
        values.sort()
        values.reverse()                                                                                  
        new_values = []
        for i, vals in enumerate(values):                                                                 
            rank = n - i
            pvalue, index = vals                                                                          
            new_values.append((n/rank) * pvalue)                                                          
        for i in xrange(0, int(n)-1):  
            if new_values[i] < new_values[i+1]:                                                           
                new_values[i+1] = new_values[i]                                                           
        for i, vals in enumerate(values):
            pvalue, index = vals
            adjust_pval[index] = new_values[i]     
    toc = time.time()
    print 'adjust pval list was converted successfully in %f seconds'%(toc-tic)
    print 'Size of the adjust p value list %d' % sys.getsizeof(adjust_pval)                                                                                                             
    return adjust_pval

def adjustedPval(pval_list):
    '''
    return the adjusted P value list. Not used yet.
    '''
    tic = time.time()
    adjustPval = correct_pval_for_multiple_testing(pval_list,"Benjamini-Hochberg") 
    toc = time.time()
    print 'Adjusted p values in %f seconds'%(toc-tic)
    return adjustPval

def pvalThld(pval_list,fdr):
    '''
    max{i:Pi<=i*a/m} where i is the maximal index, a is the FDR contrl rate, and m is the size of the list
    which allows the corresponding p value is smaller than the product of i*a/m
    Benjamini and Hochberg FDR-controlling procedure
    '''
    thld = None
    for i in range(len(pval_list)-1,-1,-1):# Division of zero error
        if i!=0:
            if pval_list[i] <= ((i+1)*fdr/len(pval_list)):
                thld = pval_list[i]
                break
        else:
            if pval_list[i] > ((i+1)*fdr/len(pval_list)):
                raise ValueError('None of the p value will be rejected.')
            else:
                thld = pval_list[i]
    return thld   

def pvalToLOD(pval):
    '''
    Convert p value to LOD score.
    The LOD is also roughly equivalent to the -log(P), where P is the probability of linkage (P = 0.001 => 3). 
    '''
    lod = -math.log(pval,10)
    return lod 


def getDicVal(dic):
    '''
    extract dictionary value into a list in ascending order.
    '''
    li = dic.values()
    li.sort()

    return li

def sortDicByVal(dic):
    '''
    Sort a dictionary by value and convert it into a list of tuples
    '''
    sorted_dic = sorted(dic.items(),key=operator.itemgetter(1))
    return sorted_dic
    

if __name__=="__main__":
    #BH pval: 0.000139798657224 LOD: 3.854497    Storey:(i)5928 qval:0.0499958818396 pval:0.000160715957486
    #lod_list = significantLOD('Ligterink_2014',False) 
    #BH pval: 1.68594343678e-07 LOD: 6.773157    Storey: 6 0.0486991023789 1.68594343678e-07
    #lod_list = significantLOD('Ligterink_2014',True) 
    #BH pval: 0.000495268834226 LOD: 3.305159    Storey: 7554 0.0499964825558 0.000639533060296
    #lod_list = significantLOD('Keurentjes_2007',False) 
    #BH pval: 0.000816476426122 LOD: 3.00805635    Storey: 52956 0.0499968149156 0.00104801112293
    #lod_list = significantLOD('Snoek_2012',True) 
    #pval_list = significantPval(lod_list)
    #print pval_list[:10]

    #bh_rejected_list = bh_rejected(pval_list,0.05)
    #print bh_rejected_list[-1]

    #storey_qvalues_list =storey_qvalues(pval_list)
    #rejected_index = -1
    #for i in xrange(len(storey_qvalues_list)-1,-1,-1):
    #    if storey_qvalues_list[i] <= 0.05:
    #        rejected_index = i
    #        break
    
    #print rejected_index,storey_qvalues_list[rejected_index],pval_list[rejected_index]
    print LODToPval(5.19)*25
    print LODToPval(3.8)
    print pvalToLOD(0.0000529)
    pass
