# -*- coding:utf-8 -*-
import BeautifulSoup as b
import sys
import os
from sys import argv
from urllib import urlopen
from os import chdir,getcwd
from re import sub

def clearError(x):
	x=x.getText()
	x=x.replace("&nbsp;","")
	return x

def getMain(con):
	text=con.findAll("div",{"class":"text"})
	txt=con.findAll("div",{"class":"txtcont"})
	pt=con.findAll("div",{"class":"post-ctc box"})
	pd=con.findAll("div",{"class":"postdesc"})
	print len(text),len(txt),len(pt),len(pd)
	if len(text) != 0:
		result=text[len(text)-1]
	elif len(txt) != 0:
		result=txt[len(txt)-1]
	elif len(pt) != 0:
		result=pt[len(pt)-1]
	else:
		result=pd[len(pd)-1]

	result=result.findAll('p')
	result=[clearError(x) for x in result]
	return result

def crawArticle(url,txt=None):
	site=urlopen(url)
	content=site.read()
	content=b.BeautifulSoup(content)
	site.close()
	ar=getMain(content)
	prefix=getcwd()+'/'
	if txt == None:
		title=content.title.getText()
		title=sub("&.+;","",title)
		title=title[0:title.find('-')]
		title=title.replace("/","-")
		print title
		fname=open(prefix+title,"w")
	else:
		fname=open(prefix+txt,'a')
		fname.write('\n')
	fname.write('\n'.join(ar))
	fname.close()

def systemSet():
	reload(sys)
	sys.setdefaultencoding('utf-8')
	os.chdir('sdcard')
	os.chdir('Download')
	os.chdir('txt')

systemSet()
url=argv[1]
listMessage="ExistedFile: \n"
ExList=os.walk("./").next()[2]
ExList.sort(lambda x,y:cmp(os.path.getmtime(x),os.path.getmtime(y)), reverse=True)
i=0
for f in ExList:
	listMessage=listMessage+str(i)+" "+f+"\n"
	i=i+1
	if i > 15: break
num=input(listMessage)
if num == -1 or num >= len(ExList):
	txt=None
else:
	txt=ExList[num]
crawArticle(url,txt)