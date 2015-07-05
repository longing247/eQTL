'''
Created on Jun 16, 2015

@author: Jiao
'''

from django.conf.urls import patterns, include, url
from .views import docView
from django.conf import settings
from django.conf.urls.static import static
 
urlpatterns = patterns('',
    url(r'^documentation/$', docView),
)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
        