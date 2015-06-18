'''
Created on Apr 7, 2015

@author: jiao
'''
from django.conf.urls import patterns, include, url
from upload.views import uploadView
from django.conf import settings
from django.conf.urls.static import static
 
 
urlpatterns = patterns('',
    url(r'^upload/$', uploadView),
)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)