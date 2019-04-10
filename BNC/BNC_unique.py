# -*- coding: utf-8 -*-
"""
Created on Wed Dec 13 18:19:39 2017

@author: Mark Torrance

Just playing: This aims to extract every word word that appears as the first
or last word in just one bigram type (of any frequency)

"""

bnc_dir = './test_data2\A0'
bnc_dir = './test_data'
bnc_dir = 'C:\Users\Mark Torrance\Dropbox\_dbBig\BNC\Texts'

import BNC_noun_bigrams as bgr
from collections import Counter, defaultdict
from timeit import time as time
import cPickle as pickle

postags = set(['AJ0','AJC','AJS','AV0',
                'CJC','CJS','CJT','DPS',
                'DTQ','NN0','NN1','NN2',
                'PNI','PNP','PNQ','PNX',
                'PRF','PRP','PUL','PUN',
                'PUQ','PUR','TO0','VBB',
                'VBD','VBG','VBI','VBN',
                'VBZ','VDB','VDD','VDG',
                'VDI','VDN','VDZ','VHB',
                'VHD','VHG','VHI','VHN',
                'VHZ','VM0','VVB','VVD',
                'VVG','VVI','VVN','VVZ','XX0'
                ])

#%%

def get_words(xmlelement):
    """
    Get all words, lower-cased, from the word tags in the BNC xmlelement.
    """
    return [word_tag.text.strip().lower()
        for word_tag in xmlelement.find_all(['w','c'])
        if word_tag['c5'] in postags] 

def get_bigrams(words):
    '''Return a Counter object counting the bigrams in the `words` list.'''
    bigs = zip(words, words[1:])
    #print bigs
    l = []
    for big in bigs:
       if bgr.is_only_letters(big[0]+big[1]):
            l.append(big)
            #print big
    return l


files = bgr.get_corpus_filenames(bnc_dir)

followed = defaultdict(Counter)
preceded = defaultdict(Counter)

fcount = 0
st = time.clock()

for file in files: # Iterate through xml files
    fcount +=1
    bgr.report_progress(fcount,10,'files processed of %d at'%(len(files)),round(time.clock() - st,3))
    xmlobject = bgr.parse_xml(file) # Parse xml in each file
    for sentence in xmlobject.find_all('s'): # Iterate through each sentence in each file
        _bigrams = get_bigrams(get_words(sentence)) # Count bigrams in sentence
        for i,j in [big for big in _bigrams]:
            
            if not followed[i] == 0:
                followed[i].update([j])
                if len(followed[i]) > 1:
                    followed[i] = 0
                    
            if not preceded[j] == 0:
                preceded[j].update([i])
                if len(preceded[j]) > 1:
                    preceded[j] = 0

followed = {i:j for i,j in followed.iteritems() if not followed[i] == 0}
preceded = {i:j for i,j in preceded.iteritems() if not preceded[i] == 0}

            
print '_'*70
bgr.report_progress(fcount,1,'files processed of %d at'%(len(files)),round(time.clock() - st,3))
            
pickle.dump(followed, open('followed.p','wb'))
pickle.dump(preceded, open('preceded.p','wb'))          


#%%              
def reload_f():       
    return pickle.load(open('followed.p','rb')) 

def reload_p():       
    return pickle.load(open('preceded.p','rb'))

def at_least(n):
    f = {i:j for i,j in followed.iteritems() if j.values()[0] > n}
    p = {i:j for i,j in preceded.iteritems() if j.values()[0] > n}
    return f,p

def print_(d):
    for i,j in d.iteritems():
        print i, j.keys()[0],j.values()[0]