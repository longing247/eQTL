class Celegans:
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''        

        self.chr = ['1','2','3','4','5','X','mt']
        self.chr_len = {'1': {'start': 0,'end': 15972282},
                        '2': {'start': 0,'end': 16173999},
                        '3': {'start': 0.,'end': 14829314},
                        '4': {'start': 0,'end': 18450863},
                        '5': {'start': 0,'end': 21914693},
                        'X': {'start': 0,'end': 18748731},
                        'mt':{'start': 0,'end': 13794}}  
        self.link_pre = 'http://www.wormbase.org/species/c_elegans/gene/'
        # WormBook Mitochondrial genetics
        #'mt':{'start': 0,'end': 13794}
        # encodes 36 genes: 2 ribosomal RNAs (12SrRNA and 16S rRNA), 22 transfer RNAs, and 12 MRC subunits
    def getChr(self):
        return self.chr
    
    def getChrLen(self):
        return self.chr_len    
    
    def getLink(self):
        return self.link_pre