'''
Created on May 7, 2015

@author: Jiao
'''


class Arabidopsis:
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        
        self.chr = ['1','2','3','4','5','cp','mt']
        self.chr_len = {'1': {'start': 3631,'end': 30425192},
                        '2': {'start': 1871,'end': 19696821},
                        '3': {'start': 4342,'end': 23459800},
                        '4': {'start': 1180,'end': 18584524},
                        '5': {'start': 1251,'end': 26970641},    
                        'cp':{'start': 0, 'end': 154478},
                        'mt':{'start': 0, 'end': 366924}
                        } 
     #http://www.nature.com/ng/journal/v15/n1/abs/ng0197-57.html   
     #The mitochondrial genome of Arabidopsis thaliana contains 57 genes in 366,924 nucleotides   
    def getChr(self):
        return self.chr
    def getChrLen(self):
        return self.chr_len
    