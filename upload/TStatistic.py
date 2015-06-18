'''
Created on Jan 13, 2015

@author: jiao
'''
from __future__ import division
import math
from scipy import stats
import numpy as np
import collections
import random
import bisect

def tTest(n1,n2,avg_x1,avg_x2,se1,se2):
    '''
    Welch's t-test: used only when the two ppulation variances are not assumed to be equal.
    
    Statistical significance in the two sample problem (groups) for equal or unequal sample size, equal
    
    Algorithm: isites.harvard.edu/fs/docs/icb.topic1041076.files/lecture7_DiffExpr.ppt
    where n1 and n2 are the number of replicates, avg_x1 and avg_x2 are the mean of each sample group, sd1 and sd2 are the standard deviation,respectively.
    
    @type n1,n2:int
    @param n1,n2: sample size of experiment 1 and 2, respectively
    
    @type avg_x1,avg_x2: float
    @param avg_x1,avg_x2: average expression level of trait
    
    @type s1,s2: float
    @param s1,s2: variance 
    
    @rtype t: float
    @return t: t score
    '''
    s1 = seToS(se1,n1)
    s2 = seToS(se2,n2)
    sp = psd(s1,s2,n1,n2)
    print sp
    se = standardError(sp,n1,n2)
    print se
    print avg_x1, avg_x2
    t = math.fabs(avg_x1-avg_x2)/se
    return t

def seToVar(se,nr):
    '''
    Convert stand error to variance.

    @type se:float
    @param se: stand error
    @type nr: int
    @param nr: sample size

    @rtype s2: float
    @return s2: variance
    '''
    s2 = se*math.sqrt(nr)*se*math.sqrt(nr)
    return s2

def seToS(se,nr):
    '''
    Convert stand error to standard deviation.
    @type se:float
    @param se: stand error
    @type nr: int
    @param nr: sample size

    @rtype s: float
    @return s: variance
    '''
    s = se*math.sqrt(nr)
    return s

def tToP(tscore,df):
    '''
    Convert Welch's t-test t score to two tailed p value
    
    @type tscore:float
    @param tscore: Welch's t-test t score
    @type df: int
    @param df: degree of freedom n1+n2-2 
    
    @rtype pval: float
    @return pval: p value
    '''

    pval = stats.t.sf(np.abs(tscore),df)*2
    
    return pval

def psd(s1,s2,n1,n2):
    '''
    Pooled standard deviation sp
    '''
    sp2 = ((s1**2)*(n1-1)+(s2**2)*(n2-1))/((n1-1)+(n2-1))
    sp = math.sqrt(sp2)
    return sp

def standardError(sp,n1,n2):
    '''
    Standard error
    '''
    se = sp*math.sqrt((1/n1)+(1/n2))
    
    return se

def log2(log2val):
    '''
    Convert log2 value to the origin
    '''
    exp = 2**log2val
    return exp

def sample(xs, sample_size = None, replace=False, sample_probabilities = None):
    """
    Adopt from stackoverflow.com/users/412529/jnnnnn
    Mimics the functionality of http://statistics.ats.ucla.edu/stat/r/library/bootstrap.htm sample()
    
    """

    if not isinstance(xs, collections.Iterable):
        xs = range(xs)
    if not sample_size:
        sample_size = len(xs)            

    if not sample_probabilities:
        if replace:
            return [random.choice(xs) for _ in range(sample_size)]
        else:
            return random.sample(xs, sample_size)
    else:
        if replace:
            total, cdf = 0, []
            for x, p in zip(xs, sample_probabilities):
                total += p
                cdf.append(total)

            return [ xs[ bisect.bisect(cdf, random.uniform(0, total)) ] 
                    for _ in range(sample_size) ]
        else:            
            assert len(sample_probabilities) == len(xs)
            xps = list(zip(xs, sample_probabilities))           
            total = sum(sample_probabilities)
            result = []
            for _ in range(sample_size):
                # choose an item based on weights, and remove it from future iterations.
                # this is slow (N^2), a tree structure for xps would be better (NlogN)
                target = random.uniform(0, total)
                current_total = 0                
                for index, (x,p) in enumerate(xps):
                    current_total += p
                    if current_total > target:
                        xps.pop(index)
                        result.append(x)
                        total -= p
                        break
            return result
     
if __name__ == "__main__":
    
    #pass
    #print log2(3.9)
    #t = tTest(3,3,4.8675,4.65812,0.073,0.053)
    n1 = 21
    n2 = 23
    s1 = 7.1
    s2 = 7.4
    se1 = s1/math.sqrt(n1)
    se2 = s2/math.sqrt(n2)
    t = tTest(21,23,64.3,68.8,se1,se2)
    df = n1+n2-2
    print t,tToP(t,df)
    