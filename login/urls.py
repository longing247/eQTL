'''
Created on Apr 7, 2015

@author: jiao
'''
from django.conf.urls import patterns, include, url
from login.views import *
 
urlpatterns = patterns('',
    url(r'^logout/$', logout_page),
    url(r'^login/$', 'django.contrib.auth.views.login'), # If user is not login it will redirect to login page
    url(r'^register/$', register),
    url(r'^register/success/$', register_success),
)