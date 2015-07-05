from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',

    url(r'^', include('login.urls')), 
    url(r'^', include('upload.urls')),
    url(r'^', include('cistrans.urls')), 
    url(r'^', include('investigation.urls')),
    url(r'^', include('documentation.urls')),
    url(r'^', include('about.urls')),  
    url(r'^admin/', include(admin.site.urls)),
    #url(r'^$', indexView,name='index'),

    
)
