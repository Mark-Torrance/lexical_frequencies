import os
from bs4 import BeautifulSoup as bs
from collections import Counter
import codecs
#import cPickle as pickle

bnc_dir = './test_data'
bnc_dir = 'F:/BNC/Texts'

def report_progress(count,increment,unitname,msg):
        if count % increment == 0:
            print count,unitname,msg

def get_corpus_filenames(rootdir):
    corpus_xmlfiles = []
    for root, dirs, filenames in os.walk(rootdir):
        for filename in filenames:
            basename, extension = os.path.splitext(filename)
            if extension == '.xml':
                corpus_xmlfiles.append(os.path.join(root, filename))
    return corpus_xmlfiles

def parse_xml(filename):
    return bs(codecs.open(filename,'r','utf_8','replace'), 'xml')

def get_words(xmlelement):
    return [word_tag.text.strip().lower()
        for word_tag in xmlelement.find_all('w')]

def get_bigrams(words):
    return Counter(zip(words, words[1:]))

files = get_corpus_filenames(bnc_dir)

monograms = Counter()
i = 0

for file in files:
    xmlobject = parse_xml(file)
    for word in xmlobject.find_all('w'):
        pos = word['c5']
        wd = word.text.strip().lower()
        monograms.update([(wd,pos),])
        i += 1
        report_progress(i,100000,'word tokens','processed so far')

print ''
print 'processed total of',i,'word tokens in corpus' 
print ''

i = 0   
outf = 'monograms_pos.txt'
print ''
print 'saving',len(monograms),'word types to',outf
    
with codecs.open(outf,'w','utf_8','replace') as f:
    for item in monograms.items():
        f.write('\t'.join(map(unicode,[item[0][0],item[0][1],item[1]]))+'\n')
        i += 1
        report_progress(i,100000,'words','saved')

print 'all done'

