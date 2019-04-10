from __future__ import division
import os
import string
from collections import Counter
# import cPickle as pickle
from bs4 import BeautifulSoup as bs
from timeit import time as time

mon_infile = 'monograms_pos.txt'
mon_outfile = 'monogram_pos_NN1.txt'
big_outfile = 'bigram_NN1.txt'
# bnc_dir = './test_data2'
bnc_dir = 'F:/BNC/Texts'
#quarter\tNN1\t5

def report_progress(count,increment,unitname,msg):
        if count % increment == 0:
            print count,unitname,msg

letters = set(string.ascii_lowercase)

def is_only_letters(strng):
    var = True
    for char in strng:
        if char not in letters:
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
    print "making noun list"
    l = []
    for word,dat in mdict.items():
        if dat[2] > thresh:
            l.append(word)
    print "finished making noun list"
    return set(l) #set makes doing a in list massively quicker

def monograms():
    print "processing monographs from",mon_infile
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
    print "total of %d words (types)"%(len(mdict))        
    return mdict
      
def save_monograms(mdict):
    with open(mon_outfile,'w') as f:
        f.write('\t'.join(('word','total_freq','NN1_freq','other_freq','ratio')) + '\n')
        for item in mdict.items():             
            f.write('\t'.join(map(str,(item[0],item[1][0]+item[1][1],item[1][0],item[1][1],item[1][2])))+'\n')
            
def get_corpus_filenames(rootdir):
    corpus_xmlfiles = []
    for root, dirs, filenames in os.walk(rootdir):
        for filename in filenames:
            basename, extension = os.path.splitext(filename)
            if extension == '.xml':
                corpus_xmlfiles.append(os.path.join(root, filename))
    return corpus_xmlfiles

def parse_xml(filename):
    return bs(open(filename), 'xml')

# note that this skips over punctuation which means that a bigram could cross a 
# punctuation boundary. .find_all(['w','c']) get punctuation as well
# you can then filter out birgrams that contain non-letter
def get_words(xmlelement):
    """
    Get all words, lower-cased, from the word tags in the BNC xmlelement.
    """
    return [word_tag.text.strip().lower()
        for word_tag in xmlelement.find_all('w')]
            
def get_bigrams(words,nounlist):
    '''Return a Counter object counting the bigrams in the `words` list.'''
    bigs = zip(words, words[1:])
    #print bigs
    l = []
    for big in bigs:
        if big[0] in nounlist and big[1] in nounlist:
            l.append(big)
            #print big
    return Counter(l)
    
def save_bigrams(bigs):
    print "saving bigrams"
    with open(big_outfile,'w') as f:
        for item in bigs.items():             
            f.write(','.join(map(str,(item[0][0],item[0][1],item[1])))+'\n')



if __name__ == "__main__":
    st = time.clock()
    mon_dict = monograms()
    nouns = nounlist(mon_dict)
    print 'time: ',round(time.clock() - st,3)
    
    
              
    print "getting bigrams"
    files = get_corpus_filenames(bnc_dir)
    bigrams = Counter()
    i = 0
    for file in files: # Iterate through xml files
        xmlobject = parse_xml(file) # Parse xml in each file
        for sentence in xmlobject.find_all('s'): # Iterate through each sentence in each file
            _bigrams = get_bigrams(get_words(sentence),nouns) # Count bigrams in sentence
            bigrams.update(_bigrams) # Aggregate these counts
            i += 1
            report_progress(i,50000,'sentences processed at',round(time.clock() - st,3))
    
    save_bigrams(bigrams)
    print 'done'
       



        
