# -*- coding:utf-8 -*-

import requests, sys, re
import BeautifulSoup as b

def systemSet():
	reload(sys)
	sys.setdefaultencoding('utf-8')

def findCoursePosition(soup,num,tablePosition):
	idPattern="\(([0-9]+),'"+num+"'\)"
	table=soup.findAll("table")[tablePosition]
	trs1=table.findAll("tr",{"class":"TABLE_TR_01"})
	trs2=table.findAll("tr",{"class":"TABLE_TR_02"})
	for tr in trs1:
		tds=tr.findAll("td")
		tda=tds[0].a
		if tda.text == num:
			javascript=tda['href']
			classId=re.findall(idPattern,javascript)[0]
			return classId
	return None

def courseSelected(responseText):
	js=responseText.findAll("script")[0]
	jsContent=js.text
	jsContent=jsContent.strip()
	jsContent=jsContent.replace('\n','').replace('\r','').replace('\t','')
	jsContent=jsContent.replace(' ','')
	alertPattern="initSelectedList\(\)\{alert\(\"(.+?)\"\);\}"
	message=re.findall(pattern=alertPattern,string=jsContent)[0]
	success="操作成功"
	if message.find(success) != -1:
		status=True
	else:
		status=None
	return status,message

def selectCourse(session,classGetUrl,username,password):
	while True:
		response=session.get(classGetUrl)
		if response.url == classGetUrl:
			responseText=b.BeautifulSoup(response.text)
			status,message=courseSelected(responseText)
			print message #android
			if status:
				break
		else:
			print "Logout, automatically try to login again!" #android
			init(username, password)
def coursesScan(session,num):
	basicUrlCross="http://jw.nju.edu.cn:8080/jiaowu/student/elective/courseList.do?method=openRenewCourse&campus=%E4%BB%99%E6%9E%97%E6%A0%A1%E5%8C%BA&academy="
	for x in range(1,46):
		if x>=10:
			academy=str(x)
		else:
			academy="0"+str(x)
		completeUrl=basicUrlCross+academy
		r=session.get(completeUrl)
		htmlParse=b.BeautifulSoup(r.text)
		classId=findCoursePosition(htmlParse,num,1)
		if classId:
			print "跨专业选课 classId:",classId #android
			classGetUrl="http://jw.nju.edu.cn:8080/jiaowu/"+"student/elective/courseList.do?method=submitOpenRenew&classId="+classId+"&academy="+academy
			return classGetUrl
	basicUrlCross=[]
	basicUrlCross.append("http://jw.nju.edu.cn:8080/jiaowu/student/elective/courseList.do?method=publicRenewCourseList&campus=%E4%BB%99%E6%9E%97%E6%A0%A1%E5%8C%BA")
	basicUrlCross.append("http://jw.nju.edu.cn:8080/jiaowu/student/elective/courseList.do?method=publicRenewCourseList&campus=%E9%BC%93%E6%A5%BC%E6%A0%A1%E5%8C%BA")
	basicUrlCross.append("http://jw.nju.edu.cn:8080/jiaowu/student/elective/courseList.do?method=discussRenewCourseList&campus=%E4%BB%99%E6%9E%97%E6%A0%A1%E5%8C%BA")
	basicUrlCross.append("http://jw.nju.edu.cn:8080/jiaowu/student/elective/courseList.do?method=discussRenewCourseList&campus=%E9%BC%93%E6%A5%BC%E6%A0%A1%E5%8C%BA")
	classType=["公选课补选","通识课补选"]
	campusList=["仙林校区","鼓楼校区"]
	submitType=['Public','Discuss']
	for urlNo in range(0,len(basicUrlCross)):
		url=basicUrlCross[urlNo]
		r=session.get(url)
		htmlParse=b.BeautifulSoup(r.text)
		classId=findCoursePosition(htmlParse,num,0)
		if classId:
			g_campus=campusList[urlNo%2]
			print classType[urlNo/2],g_campus,"classId:",classId #android
			classGetUrl="http://jw.nju.edu.cn:8080/jiaowu/"+"student/elective/courseList.do?method=submit"+submitType[urlNo/2]+"Renew&classId=" + classId + "&campus=" + g_campus
			return classGetUrl
	if not classId:
		print "Class %s does not exist" % num #android
		return None
	return classGetUrl

def init(username,password):
	session=requests.Session()
	url="http://jw.nju.edu.cn:8080/jiaowu/"
	data={"userName":username,"password":password}
	response=session.post(url,data=data)
	header=response.headers
	try:
		test=header['Expires']
	except KeyError, e:
		print "Login failed!" #android
		return None
	print "Login:",test #android

username=sys.argv[1] #android
password=sys.argv[2] #android
while True:
	session=init(username, password)
	if session:
		break
num=raw_input("Desire course number: ")
classGetUrl=coursesScan(session,num)
if classGetUrl:
	selectCourse(session,classGetUrl,username,password)
session.close()

