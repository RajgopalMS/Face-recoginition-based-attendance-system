from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpResponseRedirect,HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import (login as auth_login, logout as _logout,  authenticate)
from Sample.models import studentform,attend,cources,time_table
from django.db import IntegrityError
from background_task import background
import cv2 , csv,time
import os , schedule
import numpy as np
from PIL import Image 
import math,datetime


def Login(request):
    _msg='Please Sign in'
    if request.method == 'POST':
        _uname= request.POST['name']
        _password = request.POST['password']
        user = authenticate(username=_uname,password = _password)
        if user is not None:
            if user.is_active:
                auth_login(request,user)
                return HttpResponseRedirect('/main/')
            else:
                _msg='Not login'
        else:
            _msg='Invalid Username and password'
    context = {'message':_msg}
    return render(request,'Login.html',context)
        
def  about(request):
    return render(request,'about.html')

def  home(request):
    return render(request,'home.html')


def main(request):
    if not request.user.is_authenticated:
        return render(request, 'Login.html')
    else:
        date =datetime.datetime.now()
        print((date.isoweekday() % 7))
        return render(request,'main.html')



def addstudents(request):
    _mssg = 'Please Fill the details'
    if not request.user.is_authenticated:
        return render(request,'Login.html')
    else :
        if request.method =='POST':
            try:
                studentform1 = studentform()
                studentform1.Name = request.POST['Name']
                studentform1.branch = request.POST['branch']
                studentform1.sem = request.POST['Sem']
                studentform1.sec = request.POST['Sec']
                studentform1.usn = request.POST['USN']
                studentform1.phone = request.POST['Phno']
                studentform1.email = request.POST['email']
                studentform1.save()
                obj = studentform.objects.latest('id') 
                print(obj.id)
                subject ='Student Details Successfully added'
                message='Welcome '+ obj.Name +' Your ID is : '+ str(obj.id) +''
                from_email=settings.EMAIL_HOST_USER
                to_list=[studentform1.email,settings.EMAIL_HOST_USER]
                send_mail(subject,message,from_email,to_list,fail_silently=False)
                _mssg='Successfully Added the Student details'
            except IntegrityError:
                _mssg='USN had already added'
        else:
            _mssg=''
    details= studentform.objects    
    context = {'messages':_mssg,'details':details}
    return render(request,'addstudent.html',context)

def capture(request):
    _ids = request.POST['IDs']
    _path='./training-data/s'+_ids
    face_cascade = cv2.CascadeClassifier('./static/haarcascade_frontalface_default.xml')
    if not request.user.is_authenticated:
        return render(request,'Login.html')
    print(_ids)
    if request.method=="POST":
        try:
            os.mkdir(_path)
            print("Directory " , _path ,  " Created ") 
        except FileExistsError:
            print("Directory " , _path ,  " already exists")
        cam = cv2.VideoCapture(0)
        cv2.namedWindow("Capture the Faces")
        img_counter = 1
        while True:
            ret, frame = cam.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray,scaleFactor=1.1, minNeighbors=10)
            cv2.imshow("Capture the Faces Space to take a photo and esc to exit", frame)
            if not ret:
                break
            k = cv2.waitKey(1)
            if k%256 == 27:
                print("Escape hit, closing...")
                break
            elif k%256 == 32:
                img_name = "./"+_path+"/"+"{}.png".format(img_counter)
                cv2.imwrite(img_name, frame)
                print("{} written!".format(img_name))
                img_counter += 1
        cam.release()
        cv2.destroyAllWindows()   
    return render(request,'capture.html',{'successmsg':'success'})

#euledian


def detect_face(image):
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier('./static/haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=10);
    if (len(faces) == 0):
        return None, None
    (x, y, w, h) = faces[0]
    return gray[y:y+w, x:x+h], faces[0]

def training(request):
    if not request.user.is_authenticated:
        return render(request,'Login.html')
    faceinstance =[]
    dirs = os.listdir('./training-data/')
    faces = []
    labels = []
    for dir_name in dirs:
        if not dir_name.startswith("s"):
            continue;
        label = int(dir_name.replace("s", ""))
        subject_dir_path ='training-data' + "/" + dir_name        
        subject_images_names = os.listdir(subject_dir_path)
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        for image_name in subject_images_names:
            if image_name.startswith("."):
                continue;
            image_path = subject_dir_path + "/" + image_name
            image = cv2.imread(image_path)
            cv2.imshow("Training on image...", cv2.resize(image, (400, 500)))
            cv2.waitKey(100)
            face, rect = detect_face(image) 
            if face is not None:
                faces.append(face)
                labels.append(label)
            
    recognizer.train(faces,np.array(labels))
    recognizer.save("./traininglec.yml")
    cv2.destroyAllWindows()
    cv2.waitKey(1)
    cv2.destroyAllWindows()
    
    context = {'faces':'Successfully','label':'Trained'}
    return render(request,'main.html',context)

def saves(i,take,now,time,courceid): 
    takeatt = attend()
    takeatt.studentform_id=i
    takeatt.date=now
    takeatt.p_b=take
    takeatt.time=time
    takeatt.cid=courceid
    takeatt.save()

def excelsave(i,take,now,time,courceid):
    myData = [[id,date,p_b,studentform_id,time,cid], [i,take,now,time,courceid]]  
    myFile = open('csvexample3.csv', 'w')  
    with myFile:  
        writer = csv.writer(myFile)
        writer.writerows(myData)
    
def recg(request):
    if not request.user.is_authenticated:
        return render(request,'Login.html')
    if 'id' in request.GET and request.GET['id']:
        courceid= int(request.GET['id'])
        face_cascade = cv2.CascadeClassifier('./static/haarcascade_frontalface_default.xml')
        takeatt = attend()
        rec = cv2.face.LBPHFaceRecognizer_create()
        rec.read("trainingdata.yml")
        id=0
        cam = cv2.VideoCapture(0)
        font=cv2.FONT_HERSHEY_SIMPLEX
        now = datetime.datetime.now()
        time =now.strftime("%H:%M")
        date =now.strftime("%Y-%m-%d")
        
        att = []
        print(now)
        while 1:
            ret, img = cam.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2,
                        minNeighbors=10,
                        minSize=(25, 25))
            now = datetime.datetime.now()
            for (x,y,w,h) in faces:
                cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
                ids,conf=rec.predict(gray[y:y+h,x:x+w])
                stname = studentform.objects.get(id=ids)
                print(conf)
                if conf>75:
                    print(stname.id,now.strftime("%Y-%m-%d %H:%M"))
                    cv2.putText(img,str(stname.usn),(x,y+h), font, 2,20,2)
                   
                    att.append(stname.id)
            cv2.imshow('img',img)
            k = cv2.waitKey(1)
            if k%256 == 27:
                print("Escape hit, closing...")
                break;
        att=set(att)
        for i in att:
            saves(i,True,now,now.strftime("%H:%M"),courceid)
            #excelsave(i,True,now,now.strftime("%H:%M"),courceid)    
        cv2.destroyAllWindows()
        cv2.waitKey(1)
        cv2.destroyAllWindows()
        context = {'faces': 'success'}
        return render(request,'main.html',context)
    else:
        return render(request,'main.html',{'faces':'Please enter the Number'})

def search(request):
    if not request.user.is_authenticated:
        return render(request,'Login.html')
    details= studentform.objects    
    dirs = os.listdir('./training-data/')
    if 'q' in request.GET and request.GET['q']:
        q = request.GET['q']
        #print(q)
        books = studentform.objects.filter(usn=q)
        details= studentform.objects.get(usn=q)
        if books=="Null"and details=="Null":
            context = {'books': books, 'query': q,}
            return render(request, 'addstudent.html',context)
        else:
            context ={'books':'0','query':q}
    else:
        return HttpResponse('Enter the Correct USN.')

def logout(request):
    _logout(request)
    return redirect(Login)

def asd(request):
    if not request.user.is_authenticated:
        return render(request,'Login.html')
    details=studentform.objects
    if 'branch' in request.GET and request.GET['branch']:
        branch = request.GET['branch']
        sem =  request.GET['Sem']
        sec = request.GET['Sec']
        studetail = studentform.objects.filter(branch=branch,sem=sem,sec=sec)
        context = {'stuobj':studetail}
        return render(request,'asd.html',context)
    else:
        stuobj = 'No Data \n Please Select the Branch,Section and Semester'
        context = {'error':stuobj}
        return render(request,'asd.html',context)

def attendance(request):
    details=studentform.objects
    if 'id' in request.GET and request.GET['id']:
        id = request.GET['id']
        studetail = attend.objects.filter(studentform_id=id)
        
        context = {'stuobj':studetail}
        return render(request,'attendance.html',context)
    else:
        stuobj = 'No Data \n Please Select the Branch,Section and Semester'
        context = {'error':stuobj}
        return render(request,'Login.html',context)

def takenatt(request):
    if not request.user.is_authenticated:
        return render(request,'Login.html')
    details=cources.objects
    if 'branch' in request.GET and request.GET['branch']:
        branch = request.GET['branch']
        sem =  request.GET['Sem']
        sec = request.GET['Sec']
        studetail = cources.objects.filter(branch=branch,sem=sem,sec=sec)
        context = {'stuobj':studetail}
        return render(request,'takenatt.html',context)
    else:
        stuobj = 'No Data \n Please Select the Branch,Section and Semester'
        context = {'error':stuobj}
        return render(request,'takenatt.html',context)

def add_course(request):
    _mssg = 'Please Fill the details'
    if not request.user.is_authenticated:
        return render(request,'Login.html')
    else :
        if request.method =='POST':
            try:
                cources1 = cources()
                cources1.cId = request.POST['Subjectcode']
                cources1.cname = request.POST['SubName']
                cources1.cfac = request.POST['FacName']
                cources1.branch = request.POST['branch']
                cources1.sem = request.POST['Sem']
                cources1.sec = request.POST['Sec']
                cources1.faceimage = request.POST['files']
                cources1.fmail = request.POST['email']
                cources1.phno = request.POST['Phno']                
                cources1.save()
                obj1 = cources.objects.latest('id') 
                print(obj1.id)
                subject ='Student Details Successfully added'
                message='Welcome '+ obj1.cfac +' Your ID is : '+ str(obj1.id) +''
                from_email=settings.EMAIL_HOST_USER
                to_list=[cources1.fmail]
                send_mail(subject,message,from_email,to_list,fail_silently=False)
                _mssg='Successfully Added the Student details'
            except IntegrityError:
                _mssg='USN had already added'
        else:
            _mssg=''
    details= cources.objects    
    context = {'messages':_mssg,'details':details}
    return render(request,'add_course.html',context)

        #if student is preent or not
        #just check all the ids of student  with ids of attend and  time  = time-1 so if true send do nothing if not 

def rec_lec():
    lec_welcome="Recoginizing lecture"
    print(lec_welcome)
    face_cascade=cv2.CascadeClassifier('./static/haarcascade_frontalface_default.xml')
    rec=cv2.face.LBPHFaceRecognizer_create()
    rec.read("trainingdata.yml")
    cam=cv2.VideoCapture(0)
    cou
    while 1:
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2,
                minNeighbors=10,
                minSize=(25, 25))
        now = datetime.datetime.now()
        for (x,y,w,h) in faces:
            cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
            ids,conf=rec.predict(gray[y:y+h,x:x+w])
            lec_name = cources.objects.get(id=ids)
            print(conf)
            if conf>75:
                print(lec_name.id,now.strftime("%Y-%m-%d %H:%M"))
                cv2.putText(img,str(stname.usn),(x,y+h), font, 2,20,2)
                cv2.imshow('img',img)
        k = cv2.waitKey(1)
        if k%256 == 27:
            print("Escape hit, closing...")
            break;
        saves(11,True,now,now.strftime("%H:%M"),1)
        #excelsave(i,True,now,now.strftime("%H:%M"),courceid)    
    cv2.destroyAllWindows()
    cv2.waitKey(1)
    cv2.destroyAllWindows()

#Attendance using timetable
# @background(schedule=60)
# def hello():
#     now = datetime.datetime.now()
#     present_day = ((now.isoweekday() % 7)+1)
#     print(present_day)
#     present_day_time = '9:00'     # (now.strftime("%H:%M"))
#     time_list=['9:00','10:00']
#     for x in time_list:
#         if present_day_time==x:
#             present_day_time =x
#             print(present_day_time)
#             break;
#         else:
#             present_day_time='0:00'
#     if present_day > 0 and present_day_time !='0:00':
#         time_tb=time_table.objects.get(weekday=present_day,timings=present_day_time)  #0
#         if time_tb:
#             print(time_tb.id) 
#             Welcome ="Welcome To SKIT Attendance System Ready to Take Attendance"
#             print(Welcome)
#             courceid = int(time_tb.id)
#             face_cascade = cv2.CascadeClassifier('./static/haarcascade_frontalface_default.xml')
#             takeatt = attend()
#             rec = cv2.face.LBPHFaceRecognizer_create()
#             rec.read("trainingdata.yml")
#             id=0
#             cam = cv2.VideoCapture(0)
#             font=cv2.FONT_HERSHEY_SIMPLEX
            
#             time =now.strftime("%H:%M")
#             date =now.strftime("%Y-%m-%d")   
#             att = []
#             print(now)
#             mins=0
#             while mins!=120:
#                 ret, img = cam.read()
#                 gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#                 faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2,
#                             minNeighbors=10,
#                             minSize=(25, 25))
#                 now = datetime.datetime.now()
#                 for (x,y,w,h) in faces:
#                     cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
#                     ids,conf=rec.predict(gray[y:y+h,x:x+w])
#                     stname = studentform.objects.get(id=ids)
#                     print(conf)
#                     if conf>75:
#                         print(stname.id,now.strftime("%Y-%m-%d %H:%M"))
#                         cv2.putText(img,str(stname.usn),(x,y+h), font, 2,20,2)
#                         att.append(stname.id)
#                 cv2.imshow('img',img)
#                 mins+=1
#                 k = cv2.waitKey(1)
#                 if k%256 == 27:
#                     print("Escape hit, closing...")
#                     break;
#             att=set(att)
#             for i in att:
#                 saves(i,True,now,now.strftime("%H:%M"),courceid)
#                     #excelsave(i,True,now,now.strftime("%H:%M"),courceid)    
#             cv2.destroyAllWindows()
#             cv2.waitKey(1)
#             cv2.destroyAllWindows()
#         else:
#             print("welcome")
#     else:
#         print("Not Data")

@background(schedule=60)
def hello():
    now=datetime.datetime.now()
    present_day=((now.isoweekday() %7)+1)
    face_cascade=cv2.CascadeClassifier('./static/haarcascade_frontalface_default.xml')
    rec=cv2.face.LBPHFaceRecognizer_create()
    time =now.strftime("%H:%M")
    date =now.strftime("%Y-%m-%d")   
    
    print(now)
    if present_day>=0:
        present_day_time = '9:00'     # (now.strftime("%H:%M"))
        time_list=['9:00','10:00']
        for x in time_list:
            if present_day_time==x:
                present_day_time =x
                print(present_day_time)
                break
            else:
                present_day_time='0:00' 
        if present_day_time=='0:00':
            Do_no="Do Nothing"
            print(Do_no)
        else:
            rec.read('traininglec.yml')
            cam = cv2.VideoCapture(0)
            font=cv2.FONT_HERSHEY_SIMPLEX
            att_lec = []
            mins=0
            while mins!=120:
                ret, img = cam.read()
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2,
                            minNeighbors=10,
                            minSize=(25, 25))
                now = datetime.datetime.now()
                for (x,y,w,h) in faces:
                    cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
                    ids,conf=rec.predict(gray[y:y+h,x:x+w])
                    lec_name = cources.objects.get(id=ids)
                    print(conf)
                    if conf>75:
                        print(lec_name.id,now.strftime("%Y-%m-%d %H:%M"))
                        cv2.putText(img,str(lec_name.id),(x,y+h), font, 2,20,2)
                        att_lec.append(lec_name.id)
                cv2.imshow('img',img)
                mins+=1
                print(att_lec)
            if len(att_lec):
                lec_id=att_lec
                rec.read('trainingdata.yml')
                cam = cv2.VideoCapture(0)
                font=cv2.FONT_HERSHEY_SIMPLEX
                att = []
                mins=0
                while mins!=120:
                    ret, img = cam.read()
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2,
                                minNeighbors=10,
                                minSize=(25, 25))
                    now = datetime.datetime.now()
                    for (x,y,w,h) in faces:
                        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
                        ids,conf=rec.predict(gray[y:y+h,x:x+w])
                        stname = studentform.objects.get(id=ids)
                        print(conf)
                        if conf>75:
                            print(stname.id,now.strftime("%Y-%m-%d %H:%M"))
                            cv2.putText(img,str(stname.usn),(x,y+h), font, 2,20,2)
                            att.append(stname.id)
                    cv2.imshow('img',img)
                    mins+=1
                    k = cv2.waitKey(1)
                    if k%256 == 27:
                        print("Escape hit, closing...")
                        break;
                att=set(att)
                for i in att:
                    saves(i,True,now,now.strftime("%H:%M"),lec_id[0])
            else:
                No_lec="Lecture Not Found"
                print(No_lec)    
                
    else:
        No_lec="Lecture Not Found2323232323"
        print(No_lec)
    

            

# @background(schedule=60)
# def hello():
#     now = datetime.datetime.now()
#     present_day = ((now.isoweekday() % 7)+1)
#     present_day_time = '9:00'     # (now.strftime("%H:%M"))
#     time_list=['9:00','10:00']
#     for x in time_list:
#         if present_day_time==x:
#             present_day_time =x
#             print(present_day_time)
#             break;
#         else:
#             present_day_time='0:00'
            
#     if present_day > 0 and present_day_time !='0:00':
#         Welcome ="Welcome To SKIT Attendance System Ready to Take Attendance"
#         print(Welcome)
#         courceid = 1
#         face_cascade = cv2.CascadeClassifier('./static/haarcascade_frontalface_default.xml')
#         takeatt = attend()
#         rec = cv2.face.LBPHFaceRecognizer_create()
#         rec.read("trainingdata.yml")
#         id=0
#         cam = cv2.VideoCapture(0)
#         font=cv2.FONT_HERSHEY_SIMPLEX
        
#         time =now.strftime("%H:%M")
#         date =now.strftime("%Y-%m-%d")   
#         att = []
#         print(now)
#         mins=0
#         while mins !=120:
#             ret, img = cam.read()
#             gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#             faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2,
#                         minNeighbors=10,
#                         minSize=(25, 25))
#             now = datetime.datetime.now()
#             for (x,y,w,h) in faces:
#                 cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
#                 ids,conf=rec.predict(gray[y:y+h,x:x+w])
#                 try:
#                     lec_name = cources.objects.get(id=ids)
#                     print(conf)
#                     if conf>75:
#                         print(lec_name.id,now.strftime("%Y-%m-%d %H:%M"))
#                         cv2.putText(img,str(lec_name.id),(x,y+h), font, 2,20,2)
#                         att.append(lec_name.id)
#                 except:
#                     not_found="Lecture Not Found In Database"
#                     print(not_found)
#                     break;
#             cv2.imshow('img',img)
#             mins+=1
#             k = cv2.waitKey(1)
#             if k%256 == 27:
#                 print("Escape hit, closing...")
#                 break;
#         print(att) 
#         cv2.destroyAllWindows()
#         cv2.waitKey(1)
#         cv2.destroyAllWindows()
#     else:
#         print("Not Data")
        
def back(request):
    hello(schedule=90)
    return render(request,"main.html")