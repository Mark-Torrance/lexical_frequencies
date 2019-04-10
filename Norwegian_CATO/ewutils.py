import string
import os
import sys
import math
import codecs
from traceback import print_exc as tback
from itertools import chain
from collections import OrderedDict
import ewgl

def initialise():
    ewgl.data = []
    ewgl.varis = []
    ewgl.pword = ''
    ewgl.pword_id = 0
    ewgl.inword = 0
    print "ewgl initialised"

def initialise_word():
    ewgl.c_up_count = 0
    ewgl.c_down_count = 0
    ewgl.c_right_count = 0
    ewgl.c_left_count = 0
    ewgl.delete_count = 0
    ewgl.insert_count = 0
    ewgl.ispwd = 1

def error_report(msg, error, trace = False):
    print "error %s: %s"%(msg,error)
    if trace: tback(file=sys.stdout)

#subvars is list of subject and trial variable names
#subdata is the corresponding subject data
#for norwegian coding needs to be 'iso-8859-1'
def getdata(datafile,event_type = 'all',subvars=[],subdata=[],coding = 'utf_8'):
    dat = []
    i = -1 #create whole-file index
    header = []
    for line in codecs.open(datafile, 'r', coding,'replace'):
        line = line.rstrip('\n\r').split('\t')
        line = ['LF' if x == r'\n' else x for x in line]
        line = ['?' if x == '\r' else x for x in line]
        if i == -1:
            header = ['lineID']+subvars+line
            dat.append(header)
        else:
            keep = 0
            if len(line[0]): #check first item in line is filled
                if event_type == 'fix': keep = line[3] == 'FIXATION'
                if event_type == 'keys': keep = line[3] != 'FIXATION'
                if event_type == 'all': keep = 1
            if keep:
                    dat.append(pad([i]+subdata+line,header))
        i += 1
    print event_type.upper(),i,'lines processed in',datafile
    print"input file coding assumed to be",coding
    return dat

def pad(shortlist,longlist):
    diff = len(longlist)-len(shortlist)
    for i in range(0,diff):
        shortlist = shortlist+['']
    return shortlist

#create frequencies dictionary
#fr_col = column that freq value is in
def getfreqdic(freqfile,coding = 'utf_8', fr_col = 1):
    print "getting frequencies from",freqfile,"assuming",coding,"coding"
    fr = {}
    for line in codecs.open(freqfile, 'r', coding,'replace'):
            line = line.rstrip().split('\t')
            try:
                fr[line[0]]=float(line[fr_col]) #or whatever column frequencies are in
            except: pass
    return fr

# change dic to ordered dic
#sort: on key = 0, on value = 1, don't sort = 3
def od(dic, sort = 0, rev = False):
    if sort != 3:
        return OrderedDict(sorted(dic.items(), key=lambda t: t[sort],reverse = rev))
    else:
        return OrderedDict(dic)


def savedata(filename,data, padding = True, coding = 'utf_8'):
        fo = open(filename, 'w')
        i = 0
        for d in data:
            d = flatten(d)
            if padding and i > 0: #pad to length of header
                pad(d,data[0])
            fo.write(('\t'.join(map(unicode, d))+'\n').encode(coding))
            i += 1
        fo.close()
        print "saving data to",filename
        print "with",coding,"encoding"
        print ""

#sort: on key = 0, on value = 1, don't sort = 3
def save_dictionary(filename,dic,header=[], coding = 'utf_8',sort = 0):
        fo = open(filename, 'w')
        if len(header) > 0: fo.write('\t'.join(map(unicode, header))+'\n')
        data = []
        for key in dic.keys():
            data.append([key]+flatten(dic[key]))
        if sort != 3: data.sort(key = lambda v:v[sort])
        for d in data:
            fo.write(('\t'.join(map(unicode, d))+'\n').encode(coding,errors = 'replace'))
        fo.close()
        print "saving dictionary to",filename
        print "with",coding,"encoding"
        print ""


#gives update on units processed, by increment, unitname might be 'cases'
def report_progress(count,increment,unitname,msg):
        if count % increment == 0:
            print msg,count,unitname,"processed"

#create dictionary of varname:item number. Header is first row of data object.
def getvardict(data):
    d = {}
    header = data[0]
    for i in range(0,len(header)):
        d[header[i]]=i
    return d

def alnum(string): #remove non alphanumeric chars from string
    s=''
    for c in str(string):
        if str(c).isalnum() or c == ' ' or c == '-': s += str(c)
    return s

def is_sentence_terminator(char):
    v = 0
    try:
        if char in '.!?:': v = 1
    except: pass
    return v

def sentendword(string): #identifies sentence end words
    c=0
    for i in '.!?:':
        if i in string:
            c=1
            break
    return c

#create frequencies dictionary
#word in first column, freq in column number = col
def getlogfreq(freqfile,col = 4):
    logfr = {}
    for line in open(freqfile, 'r'):
            line = line.rstrip('\n').split('\t')
            logfr[line[0]]=float(line[col]) #or whatever column frequencies are in
    return logfr

#create dictionary for two colunms in any tab delimited data file
def file2dic(datafile,keycol,valuecol):
    dic = {}
    for line in open(freqfile, 'r'):
            line = line.rstrip('\n').split('\t')
            dic[line[keycol]]=line[valuecol]
    return dic

#look up word in frequencies dictionary
def getfreq(word, freqdic):
    try: f = round(freqdic[(word.lower())],3)
    except: f = ''
    return f

#flattens complex-nested lists. If not list then redefine as list.
def flatten(x):
    if hasattr(x,"__iter__"):
        result = []
        for el in x:
            if hasattr(el, "__iter__") and not isinstance(el, basestring):
                result.extend(flatten(el))
            else:
                result.append(el)
    else: result = [x]
    return result


def printwordlist():
    try:
        yn = raw_input("Would you like the word list? y/n")
        if 'y' in yn:
            for word in ewgl.wordlist:
                print word
    except: pass

#tablevalues is list of varnames in table for vars to be transfered to datafile
#keys are the lookup keys (e.g., participant number, word etc)
def lookup(datafile,tablefile,datakey,tablekey,tablevalues, cod = 'uft_8'):
    data = getdata(datafile, coding = cod)
    dvars = getvardict(data)
    tdata = getdata(tablefile, coding = cod)
    tvars = getvardict(tdata)
    table = {}
    for i in range(1,len(tdata)): #create lookup dictionary
        table[tdata[i][tvars[tablekey]]] = []
        for v in tablevalues:
            table[tdata[i][tvars[tablekey]]] += [tdata[i][tvars[v]]]
    print "created lookup dictionary from",tablefile
    print data[0]
    data[0] += tablevalues #header
    count = 0
    for i in range(1,len(data)):
        dk = data[i][dvars[datakey]]
        data[i] += table.get(dk,'')
        count += 1
        report_progress(count,5000,'lines','Looking up:')
    print ""
    print tablevalues
    print "added from",tablefile,"to",datafile
    print "for",str(count),"lines of data"
    print ""
    return data

