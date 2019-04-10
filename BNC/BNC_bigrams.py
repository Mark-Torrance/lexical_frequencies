import os
from bs4 import BeautifulSoup
from collections import Counter
import string

bnc_dir = './test_data'
#bnc_dir = 'F:/BNC/Texts'

def get_corpus_filenames(rootdir):
    corpus_xmlfiles = []
    for root, dirs, filenames in os.walk(rootdir):
        for filename in filenames:
            basename, extension = os.path.splitext(filename)
            if extension == '.xml':
                corpus_xmlfiles.append(os.path.join(root, filename))
    return corpus_xmlfiles

def parse_xml(filename):
    return BeautifulSoup(open(filename), 'xml')

def get_words(xmlelement):
    """
    Get all words, lower-cased, from the word tags in the BNC xmlelement.
    """
    return [word_tag.text.strip().lower()
        for word_tag in xmlelement.find_all('w')]
            
def is_only_letters(strng):
    var = True
    for char in strng:
        if char not in string.ascii_lowercase:
            var = False
            break
    return var

def get_bigrams(words):
    '''Return a Counter object counting the bigrams in the `words` list.'''
    bigs = zip(words, words[1:]) 
    l = []
    for big in bigs:
        if is_only_letters(big[0]+big[1]):
            l.append(big)   
    return Counter(l)

files = get_corpus_filenames(bnc_dir)

bigrams = Counter()
for file in files: # Iterate through xml files
    xmlobject = parse_xml(file) # Parse xml in each file
    for sentence in xmlobject.find_all('s'): # Iterate through each sentence in each file
        _bigrams = get_bigrams(get_words(sentence)) # Count bigrams in sentence
        bigrams.update(_bigrams) # Aggregate these counts
