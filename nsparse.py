#coding:UTF-8

import re
from pprint import pprint
import sys

def parse(pattern,File):
    content=File.readlines()
    lines=[re.sub(pattern," ",l.strip('\n').lower()) for l in content if l!='\n']
    return lines

def statistic(lines,dic):
    wordlist=[]
    for line in lines:
        words=line.split(' ')
        for word in words:
           # if len(word) == 1 and word !='a': print line
            if word == '':
                continue
            if "'" in word:
                word=word[0:word.index("'")]
            if word in dic:
                dic[word]+=1
            else:
                dic[word]=1
                wordlist.append(word)
    return wordlist
            
def duplicateRemoval(dic,wordlist):
    dup=[]
    wordlist.sort()
    for word in wordlist:
        if len(word)>2:
            same=[word+'es',word+'ing',word+'ed',word+'s']
            for one in same:
                if one in dic:
                    dic[word]+=dic[one]
                    del dic[one]
                    del wordlist[wordlist.index(one)]
                    dup.append(one)
    return dup

def outDic(wordlist,dic,limit):
    print "\nWords total(limit:%d):" % limit
    i=1
    for word in wordlist:
        if dic[word]>limit:
            if i != 3:
                print "%-13s: %d\t" % (word,dic[word]),
            else:
                print "%-13s: %d\t" % (word,dic[word])
                i=0
            i+=1
    print "\n"

def outRemoval(dup):
    i=1
    print "Words removed:"
    for word in dup:
        if i != 4:
            print "%-13s  " % word,
        else: 
            print "%-13s  " % word
            i=0
        i+=1
pattern="[,\.\-\?\"—\(\)…! ;:&]+"
File=open(sys.argv[1],'r')
lines=parse(pattern,File)
dic={}
wordlist=statistic(lines,dic)
dup=duplicateRemoval(dic,wordlist)
outDic(wordlist,dic,0)
#outRemoval(dup)
#pprint(dic)
#pprint(dup)
#print dic
File.close()
