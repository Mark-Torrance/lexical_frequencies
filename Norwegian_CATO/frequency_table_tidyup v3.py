#-------------------------------------------------------------------------------
# Name:        frequency_table_tidyup
# Purpose:  takes the Norwegian 1gram_nob_abc raw frequencies table and
#           does sensible things to it (like treat capitalised and non-capitalised
#           tokens as the same type)
#
# Author:      Mark Torrance
#
# Created:     19/09/2013
#-------------------------------------------------------------------------------

import string
import os
import sys
import math
import codecs
#import ewutils

#os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

min_freq = 10 #exclude words with frequency lower than this

datafile = '1gram_nob_abc.txt'
#datafile = 'gram_test_2.txt'
tempfile = 'freqtemp.txt'
outfile = 'tidy_'+datafile

global c_word
c_word = '' #current word for debugging

def isjustletters(word):
    v = 1
    for l in word:
        if l not in string.letters+'-'+u'\xe6\xf8\xe5\xc5\xc6\xd8':
            v = 0
            break
    return v

def islower(s):
    v = 1
    try:
        for a in s:
            if a not in u'abcdefghijklmnopqrstuvwxyz\xe6\xf8\xe5-':
                v = 0
    except: pass
    return v

def makelower(s):
    return s.replace(u'\xc5',u'\xe6').replace(u'\xc6',u'\xf8').replace(u'\xd8',u'\xe5').lower()


#make dictionary of all lower-case words
def freq_dict(datafile):
    fin = codecs.open(datafile, 'r+', 'iso-8859-1', 'replace')
    fo = codecs.open(tempfile, 'w', 'utf_8', 'replace')
    dic = {}
    i = j = 0
    for line in fin:
        if j < 20000000 and len(line) > 2: # limit number of lines processed
            rawline = line
            line = line.strip().split()
            c_word = line
            if len(line) >=2:
                freq = int(line[0])
                word = line[1]
                if isjustletters(word) and freq >= min_freq:
                    if islower(word):
                        dic[word] = [freq,freq,0,0] #freqs for total, lower, initial cap, and mixed]
                        i+=1
                    else:
                        fo.write(rawline)
                j += 1
                if j % 50000 == 0:
                    print j,"lines processed from file,",i,"words added to dictionary"
    print i,"lowercase words now in dictionary"
    fin.close()
    fo.close()
    return dic


def addmorefreqs(freqdict):
    dic = freqdict
    fin = codecs.open(tempfile, 'r+','utf_8','replace')
    i = j = 0
    for line in fin:
        line = line.strip().split()
        freq = int(line[0])
        word = line[1]
        lowword = makelower(word)
        try:
            freqdict[lowword]
            dic[lowword][0] += freq
            if not islower(word[0]) and islower(word[1:]):
                dic[lowword][2] += freq
            else:
                dic[lowword][3] += freq
            i += 1
        except: pass
        j += 1
        if j % 50000 == 0:
                print j,"mixed-case words processed,",i,"frequencies added"
    fin.close()
    print i,"frequencies from mixed case tokens added to dictionary"
    return dic

def saveoutfile(freqdict):
    print "Saving data to",outfile
    flist = []
    d = freqdict
    kys = d.keys()
    flist = []
    for k in kys:
        fr = d[k]
        flist.append([k,fr[0],math.log10(fr[0]),fr[1],fr[2],fr[3]])
    fo = codecs.open(outfile, 'w', 'utf_8','replace')
    fo.write('\t'.join(('fword','freq','logfreq','freq_lower','freq_initialcap','freq_mixedcase'))+'\n')
    for w in flist:
        wd = w[0]
        fo.write('\t'.join([wd]+map(unicode,w[1:]))+'\n')
    print''
    print "frequencies data saved to",outfile
    fo.close()


freqdict = freq_dict(datafile)
freqdict = addmorefreqs(freqdict)
saveoutfile(freqdict)
print ""
print "all done"


