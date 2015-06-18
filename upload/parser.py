'''
Created on Apr 28, 2015

@author: yaya
'''
import time
import json
import os

from django.conf import settings
import FDR

def getThld(f):
    '''
    description: using BH95 procedure to  get adjust LOD threshold 
    
    @type f: tab delimited file
    @param f: QTL mapping output LOD file
    
    @rtype pval_BH95: decimal
    @return pval_BH95: adjusted p value using BH95 procedure
    
    @rtype lod_BH95: decimal
    @return lod_BH95 adjusted LOD score using BH95 procedure
    
    @rtype lod_dic: dictionary
    @return lod_dic: LOD profile
    
    '''
    
    lod_dic = {}
    lod_list = []
    with open(f) as fi:
        tic = time.time()
        first_line = fi.readline().rstrip()
        lines = fi.readlines()
        for line in lines:
            col = line.rstrip().split('\t')
            lod = [abs(float(i)) if i!='' else 0.0 for i in col[1:] ]           
            lod_list.extend(lod)
            lod_dic[col[0]] = lod 
        lod_list_abs = [abs(i) for i in lod_list]
        sorted_pval_list = FDR.significantPval(lod_list_abs) 
        '''
        adjusted_pval = FDR.correct_pval_for_multiple_testing(sorted_pval_list,"Benjamini-Hochberg")
        #print type(adjusted_pval)
        #print adjusted_pval[:20]
        #print adjusted_pval[-20:]
        
        #pval_list = [FDR.LODToPval(lod) for lod in lod_list]
        #import ngslib
        #bh_thld = ngslib.bh_rejected(pval_list, 0.01)
        #print bh_thld
        #print len(bh_thld)
        
        ind = [ n for n,i in enumerate(adjusted_pval) if i>0.01 ][0]
        print ind,adjusted_pval[ind-1],sorted_pval_list[ind-1]
        print FDR.pvalToLOD(sorted_pval_list[ind-1])
        '''
        
        pval_BH95 = FDR.pvalThld(sorted_pval_list,0.05) 
        lod_BH95 = FDR.pvalToLOD(pval_BH95)
        print pval_BH95,lod_BH95 #pval: 0.0003 LOD: 3.51 397426 44381 1455 64574355 0.006
        toc = time.time()
        print 'Processed in %s seconds' % (toc-tic)
        
    return pval_BH95,lod_BH95,lod_dic

def outputJSON(lod_dic,path):
    '''
    description: output LOD profile of each probe individually  
    
    @type lod_dic: dictionary
    @param lod_dic: QTL mapping output: LOD profile dictionary
    
    @type path: string
    @param path: output path
    
    '''
    for ele in lod_dic:
        outputDic = {}
        outputDic['probe'] = ele
        outputDic['lod'] = lod_dic[ele]
        output_txt_name = '%s.json' % ele
        out_path  = os.path.join(path,output_txt_name)
        with open(out_path,'w') as fo:
            json.dump(outputDic,fo,indent=4)

if __name__ == '__main__':
    file_name = 'data/Rockman_etal/rock_qtl_con.txt'
    pass