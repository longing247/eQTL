'''
Created on Apr 29, 2015

@author: jiao
'''

from django.conf.urls import patterns, include, url
from cistrans.views import eQTLPlotView
from django.conf import settings
from django.conf.urls.static import static
 
urlpatterns = patterns('',
    url(r'^cistrans$', eQTLPlotView),
)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
        