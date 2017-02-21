# -*- coding:utf-8 -*-
from selenium import webdriver
from sys import argv
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
	li=webdriver.find_element_by_id('teachinginfo')
	courses=li.find_element_by_tag_name('a')
	courses.click()
	Function=webdriver.find_element_by_id('Function')
	funcLinks=Function.find_elements_by_tag_name('a')
	funcLinks[1].click()
	btSearch=webdriver.find_element_by_id('btSearch')
	db,cur=dbInit(dbname,dbpwd)
	
	termList=webdriver.find_element_by_id('termList')
	termList=termList.find_elements_by_tag_name("option")
	gradeList=webdriver.find_element_by_id('gradeList')
	gradeList=gradeList.find_elements_by_tag_name("option")
	academySelect=webdriver.find_element_by_id('academySelect')
	academySelect=academySelect.find_elements_by_tag_name("option")
	i=0
	j=0
	while i<2:
		i=i+1
		termList[i].click()
		j=0
		while j<4:
			j=j+1
			gradeList[j].click()
			k=1
			while k<len(academySelect):
				academySelect[k].click()
				academy=academySelect[k].text
				specialitySelect=webdriver.find_element_by_id('specialitySelect')
				specialitySelect=specialitySelect.find_elements_by_tag_name("option")
				ki=1;
				while ki<len(specialitySelect):
					specialitySelect[ki].click()
					special=specialitySelect[ki].text
					btSearch.click()
					if i == 1:
						term='b'
					else :
						term='a'
					print term,gradeList[j].text,academy,special
					getCoursesList(db,cur,academy,special,term)
					ki=ki+1
				k=k+1
	dbClose(db,cur)

def getCoursesList(db,cur,academy,special,term):
	webdriver.switch_to.frame('frameCourseView')
	tbody=webdriver.find_element_by_tag_name('tbody')
	tbody=webdriver.find_element_by_tag_name('tbody')
	trOut=tbody.find_element_by_tag_name('tr')
	courses=trOut.find_elements_by_tag_name('tr')
	if len(courses)>1:
		i=1
		while i<len(courses):
			Id,name,point,time,area,teacher=coursesDetails(courses[i])
			i=i+1
			if Id == None:
				continue
			if len(teacher)>=148:
				teacher=teacherPartial(teacher)
			print Id,name,point,time,area,teacher
			if checkTheSameCourse(cur,Id,teacher):
				continue
			try:
				sql="INSERT INTO CoursesMain(id,name,point,time,area,teacher,academy,special,term) VALUES('%s','%s',%.1f,%d,'%s','%s','%s','%s','%s')" % (Id,name,float(point),int(time),area,teacher,academy,special,term)
				result=cur.execute(sql)
				if result == 1:
					db.commit()
			except Exception, e:
				db.rollback()
				raise e
	webdriver.switch_to.default_content()

def coursesDetails(course):
	messages=course.find_elements_by_tag_name('td')
	Id=messages[0].find_elements_by_tag_name('a')
	if len(Id) == 0:
		Id=None
		print 'ID none'
	else :
		Id=Id[0].text
	name=messages[1].text
	point=messages[4].text
	time=messages[5].text
	area=messages[6].text
	teacher=messages[7].text
	return Id,name,point,time,area,teacher

def teacherPartial(teacher):
	teachers=teacher.split(', ')
	resetTeachers=""
	i=0
	while (len(resetTeachers)+len(teachers[i])+2)<148:
		resetTeachers=resetTeachers+', '+teachers[i]
		i=i+1
	return resetTeachers[2:len(resetTeachers)]

def checkTheSameCourse(cur,Id,teacher):
	sql="select * from CoursesMain where id='%s';" % Id
	cur.execute(sql)
	rows=cur.fetchall()
	if len(rows) == 0:
		print 'check:',False,'rows 0'
		return False
	for row in rows:
		if row[5].encode('utf8') == teacher.encode('utf8'):
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

webdriver=webdriver.PhantomJS()
webdriver.get('http://219.219.121.224:8080/jiaowu/')
user=argv[1]
pwd=argv[2]
dbname=argv[3]
dbpwd=argv[4]
if initNJUJw(user,pwd):
	navigateToCourse(dbname,dbpwd)
	
	

