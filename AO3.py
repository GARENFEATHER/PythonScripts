# -*- coding:utf-8 -*-
import sys, os, re, requests
import BeautifulSoup as b
from sys import argv

def getAndSaveContent(content,fname,mode):
	if mode:
		txtFile=open(fname,'w')
	else:
		txtFile=open(fname,'a')
	chapters=content.findAll("div",{"id":"chapters"})
	chapters=chapters[0].findAll("div",{"class":"chapter"})
	if len(chapters) == 0: return None
	for i in range(0,len(chapters)):
		chapter=chapters[i]
		chapterTitle=chapter.h3.text
		articles=chapter.findAll("div",{"role":"article"})
		params=articles[0].findAll("p")
		if len(params) > 0:
			for x in xrange(0,len(params)):
				testBrTag=params[x].findAll(text=True)
				if len(testBrTag) != 0:
					contents=''.join(testBrTag)
					params[x].setString(contents)
			paramsText=[x.text.strip() for x in params]
			content='\r\n\r\n'.join(paramsText)
			txtFile.write("\r\n")
			txtFile.write(chapterTitle)
			txtFile.write("\r\n")
			txtFile.write(content+"\r\n")
			txtFile.write("\r\n")
			print "chapter-"+str(i+1),"words:",len(content)
	txtFile.close()

def systemSet():
	reload(sys)
	sys.setdefaultencoding('utf-8')
	# os.chdir('sdcard')
	# os.chdir('Download')
	# os.chdir('txt')
	# os.chdir('engNovels')

def crawArticle(url,txtName=None):
	i=0
	while True:
		try:
			session=requests.Session()
			data={"view_adult":True}
			session.get(url,data=data)
			data={"view_full_work":True}
			response=session.get(url,data=data)
			html=response.text
			break
		except requests.exceptions.ChunkedEncodingError, e:
			i=i+1
			print "ChunkedEncodingError Reconnect:",i
			if i>10:
				print "Bad Connection"
				return
			continue
		except requests.exceptions.ConnectionError, e:
			i=i+1
			print "ConnectionError Reconnect:",i
			if i>10:
				print "Bad Connection"
				return
			continue
	content=b.BeautifulSoup(html)
	session.close()
	prefix=os.getcwd()+'/'
	title=content.findAll("h2",{"class":"title heading"})
	title=title[0].text
	author=content.findAll("h3",{"class":"byline heading"})
	author=author[0].a.text
	head=title+" - "+author
	if txtName == None:
		getAndSaveContent(content, head, None)
	else:
		getAndSaveContent(content, txtName, 'w')

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