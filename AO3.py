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
	i=0
	for chapter in chapters:
		chapterTitle=chapter.h3.text
		articles=chapter.findAll("div",{"role":"article"})
		params=articles[0].findAll("p")
		if len(params) > 0:
			paramsText=[x.text for x in params]
			content='\r\n'.join(paramsText)
			txtFile.writeline(chapterTitle)
			txtFile.writeline(content+"\r\n")
			print "chapter",i,len(content)
		i+=1
	txtFile.close()

def systemSet():
	reload(sys)
	sys.setdefaultencoding('utf-8')
	# os.chdir('sdcard')
	# os.chdir('Download')
	# os.chdir('txt')

def crawArticle(url,txtName=None):
	i=0
	while True:
		try:
			session=requests.Session()
			data={"view_adult":True}
			session.get(url,data)
			data={"view_full_work":True}
			response=session.get(url,data)
			html=response.text
		except ChunkedEncodingError, e:
			i=i+1
			if i>10:
				print "Bad Connection"
				return
			continue
		break
	content=b.BeautifulSoup(html)
	prefix=os.getcwd()+'/'
	title=html.findAll("h2",{"class":"title heading"})
	title=title[0].text
	author=html.findAll("h3",{"class":"byline heading"})
	author=author[0].a.text
	head=title+" - "+author
	if txtName == None:
		getAndSaveContent(html, head, None)
	else:
		getAndSaveContent(html, txtName, 'w')

systemSet()
url=argv[1]