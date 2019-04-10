import string
import os
import sys
import math
import ewutils
from collections import OrderedDict

#open wordlist file with format [word] [frequency]
filename = 'tidy_1gram_nob_abc.txt'
filename = 'DU_freqs.txt'
dfile = os.path.join('.','data2',filename)

#creates list of all letter types
def getletters(data):
    letters = []
    for row in data[1:len(data)]:
        word = row[1].lower()
        for let in word:
            if let not in letters:
                  letters += let
    return sorted(letters)

def getgraphs(letters):
    mons,digs,trigs = {},{},{}
    for x in letters:
        mons.setdefault(x,0)
        for y in letters:
            digs.setdefault(x+y,0)
            for z in letters:
                trigs.setdefault(x+y+z,0)
    return mons,digs,trigs

#make dictionary lets = 1 for monograph, 2 for digraph etc
#needs list of mons, digs or trigs
#data has header row
def getfreqs(data,n,graphdic):
    for row in data[1:len(data)]:
        word = row[1].lower()
        freq = row[2]
        x = 0
        y = n
        while y <= len(word):
                a = word[x:y]
                graphdic[a] += int(freq)
                x = x+1
                y = y+1
    return graphdic

def od(dic):
    return OrderedDict(sorted(dic.items(), key=lambda t: t[1],reverse = True))

def outf(tag):
    return os.path.join('.','data2',tag+filename)

#do it.
data = ewutils.getdata(dfile,coding = 'utf-8')
graphs = getgraphs(getletters(data))
mons,digs,trigs = graphs[0],graphs[1],graphs[2]

print'frequencies calculated, now saving files'
print ''
ewutils.save_dictionary(outf('mons'),od(getfreqs(data,1,mons)),sort = 3)
ewutils.save_dictionary(outf('digs'),od(getfreqs(data,2,digs)),sort = 3)
ewutils.save_dictionary(outf('trigs'),od(getfreqs(data,3,trigs)),sort = 3)

print 'done'
