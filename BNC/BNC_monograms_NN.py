from __future__ import division
#import os
import string
from collections import Counter
import cPickle as pickle

mon_infile = 'monograms_pos.txt'
mon_outfile = 'monogram_pos_NN1.txt'
bigram_file = 'Count.pkl'
#quarter\tNN1\t5

def is_only_letters(strng):
    var = True
    for char in strng:
        if char not in string.ascii_lowercase:
            var = False
            break
    return var
    
def divide(x,y):
    if y == 0: 
        return 1
    elif x == 0:
        return 0
    else: 
        return round(x/y,3)
        
def isnoun(word,mdict,thresh=.95): #thresh or more occurences must be NN1
    return mdict[word] > thresh
    
def nounlist(mdict, thresh=.95):
    l = []
    for word,dat in mdict.items():
        if dat[2] > thresh:
            l.append(word)
    return l

def monograms():
    f = open(mon_infile,'r')
    mdict = {}           
    for line in f:
        skip = False
        
        try:
            word,pos,freq = line.strip().split('\t')
        except:
            skip = 1
            
        if is_only_letters(word) and not skip:    
            fNN1,fOTHER,fratio = mdict.setdefault(word,(0,0,0))
        
            if pos == 'NN1': 
                fNN1 += int(freq)
            else: 
                fOTHER += int(freq)
                
            fratio = divide(fNN1,fOTHER+fNN1)
            mdict[word] = (fNN1,fOTHER,fratio)
            
    return mdict
    
    
def save_monograms(mdict):
    with open(mon_outfile,'w') as f:
        f.write('\t'.join(('word','total_freq','NN1_freq','other_freq','ratio')) + '\n')
        for item in mdict.items():             
            f.write('\t'.join(map(str,(item[0],item[1][0]+item[1][1],item[1][0],item[1][1],item[1][2])))+'\n')
            
          
mon_dict = monograms()
nouns = nounlist(mon_dict)  