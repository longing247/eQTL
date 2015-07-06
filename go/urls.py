'''
Created on Jul 6, 2015

@author: Jiao
'''

from django.conf.urls import patterns, include, url
from .views import GOView
from django.conf import settings
from django.conf.urls.static import static
 
urlpatterns = patterns('',               
    url(r'^GO/', GOView),
)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
        