# -*- coding:utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sys import argv
import sys
import MySQLdb

def initNJUJw(user,pwd):
	userInput=webdriver.find_element_by_name('userName')
	pwdInput=webdriver.find_element_by_name('password')
	userInput.send_keys(user)
	pwdInput.send_keys(pwd)
	sub=webdriver.find_element_by_class_name('Btn')
	sub.click()
	check='UserInfo'
	try:
		webdriver.find_element_by_id(check)
	except Exception, e:
		raise e
		return False
	else:
		return True

def navigateToCourse(dbname,dbpwd):
	db,cur=dbInit(dbname,dbpwd)
	webdriver.get('http://219.219.120.48/jiaowu/student/elective/freshman_discuss.do')
	publicAndGeneralCourses(db,cur,"tb_campus3","仙林校区")
	publicAndGeneralCourses(db,cur,"tb_campus1","鼓楼校区")
	webdriver.get('http://219.219.120.48/jiaowu/student/elective/publicCourseList.do')
	publicAndGeneralCourses(db,cur,"tb_campus3","仙林校区")
	publicAndGeneralCourses(db,cur,"tb_campus1","鼓楼校区")
	dbClose(db,cur)

def publicAndGeneralCourses(db,cur,tb_campus,area):
	try:
		tbody=WebDriverWait(webdriver,10).until(EC.presence_of_element_located((By.ID,tb_campus)))
	except Exception, e:
		raise e
		webdriver.quit()
		return
	courses=tbody.find_elements_by_tag_name('tr')
	if len(courses)>0:
		for course in courses:
			Id,name,point,climit,ctype,teacher,note=coursesDetails(course)
			if Id != None:
				if checkTheSameCourse(cur, Id, teacher): continue
				try:
					try:
						point=float(point)
					except ValueError, e:
						point=2
						print "point error => ",Id,name
					try:
						climit=int(climit)
					except ValueError, e:
						climit=100
						print "climit error => ",Id,name
						
					if note:
						sql="INSERT INTO CoursesOther(id,name,point,area,teacher,climit,ctype,note) VALUES('%s','%s',%.2f,'%s','%s','%d','%s','%s');" % (Id,name,point,area,teacher,climit,ctype,note)
					else:
						sql="INSERT INTO CoursesOther(id,name,point,area,teacher,climit,ctype) VALUES('%s','%s',%.2f,'%s','%s','%d','%s');" % (Id,name,point,area,teacher,climit,ctype)
					res=cur.execute(sql)
					if res == 1:
						db.commit()
						print Id,name,note," => Course"
				except Exception, e:
					db.rollback()
					raise e
	
def coursesDetails(course):
	messages=course.find_elements_by_tag_name('td')
	Id=messages[0].find_elements_by_tag_name('a')
	if len(Id) == 0:
		Id=None
		print 'ID none'
	else :
		Id=Id[0].text
	name=messages[2].text
	name,note=disperseNote(name)
	point=messages[3].text
	climit=messages[7].text
	ctype=messages[6].text
	teacher=messages[5].text
	return Id,name,point,climit,ctype,teacher,note

def disperseNote(name):
	name.replace('\n','')
	patt='(备注'
	if name.find(patt) == -1:
		note=None
	else:
		note=name[name.find(patt)+1:name.find(')')]
		name=name[0:name.find(patt)]
	return name,note

def checkTheSameCourse(cur,Id,teacher):
	sql="select * from CoursesOther where id='%s';" % Id
	cur.execute(sql)
	rows=cur.fetchall()
	if len(rows) == 0:
		print 'check:',False,'rows 0'
		return False
	for row in rows:
		if row[4].encode('utf8') == teacher.encode('utf8'):
			print 'check:',True
			return True
	print 'check:',False,'teacher different'
	return False

def dbInit(dbname,dbpwd):
	db=MySQLdb.connect('localhost',dbname,dbpwd,charset='utf8')
	cur=db.cursor()
	cur.execute('USE NJUCourses')
	return (db,cur)

def dbClose(db,cur):
	cur.close()
	db.close()

reload(sys)
sys.setdefaultencoding("utf8")
webdriver=webdriver.PhantomJS()
webdriver.get('http://219.219.120.48/jiaowu/')
user=argv[1]
pwd=argv[2]
dbname=argv[3]
dbpwd=argv[4]
if initNJUJw(user,pwd):
	print "Login!"
	navigateToCourse(dbname,dbpwd)
	print "Complete!"
else:
	print "Stop!"
	

