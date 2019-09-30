"""f2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.urls import path
from django.contrib import admin
import Sample.views
from django.conf import settings


urlpatterns = [
    path(r'admin/', admin.site.urls),
    path(r'about/',Sample.views.about),
    path(r'',Sample.views.Login,name="Login"),
   path(r'asd/',Sample.views.asd,name="asd"),
    path(r'main/',Sample.views.main),
    path(r'addstudent/',Sample.views.addstudents, name="addstudent"),
    path(r'capture/',Sample.views.capture, name="capture"),
    path(r'train/',Sample.views.training,name='training'),
    path(r'rec/',Sample.views.recg,name='recg'),
    url(r'^search/$',Sample.views.search,name='search'),
    url(r'logout/$',Sample.views.logout,name='logout'),
    url(r'attendance/$',Sample.views.attendance,name="attendance"),
    url(r'view_att/',Sample.views.home,name="view_att"),
       path(r'takenatt/',Sample.views.takenatt,name="takenatt"),
       path(r'add_course/',Sample.views.add_course,name="add_course"),
       path(r'Lec_cap',Sample.views.Lec_capture,name="Lec_cap"),
    path(r'S/',Sample.views.back,name="back"),
    path(r'Lec/',Sample.views.training_lec,name="training_lec"),
     path(r'traineigen/',Sample.views.trainingeigen,name='trainingeigen'),
    path(r'receigen/',Sample.views.recgeigen,name='recgeigen')


]