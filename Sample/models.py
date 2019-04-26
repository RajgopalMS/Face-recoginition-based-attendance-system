from django.db import models


class studentform(models.Model):
    Name=models.CharField(max_length=100)
    branch=models.CharField(max_length=2)
    sem=models.IntegerField()
    sec=models.CharField(max_length=100)
    usn=models.CharField(max_length=10)
    phone=models.IntegerField()
    email=models.CharField(max_length=100)


class cources(models.Model):
    id = models.AutoField(name='id',primary_key=True)
    cId=models.CharField(max_length=100)
    fmail=models.CharField(max_length=50)
    phno=models.CharField(max_length=50)
    cname=models.CharField(max_length=100)
    cfac=models.CharField(max_length=100)
    faceimage=models.ImageField(upload_to='upload/')
    branch=models.CharField(max_length=2)
    sem=models.IntegerField()
    sec=models.CharField(max_length=100)


class attend(models.Model):
    id = models.AutoField(name='id', primary_key=True)
    studentform = models.ForeignKey('studentform',on_delete=models.CASCADE,)
    date = models.DateTimeField()
    time=models.CharField(max_length=20)
    p_b = models.NullBooleanField()
    cid=models.IntegerField()

class time_table(models.Model):
    id=models.AutoField(name='id',primary_key=True)
    subject_id=models.ForeignKey('cources',on_delete=models.CASCADE,)
    weekday=models.CharField(max_length=100)
    timings=models.CharField(max_length=100)
