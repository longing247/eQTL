from django.conf.urls import patterns, url
from browser.views import browserView
from django.conf import settings
from django.conf.urls.static import static
 
urlpatterns = patterns('',
    url(r'^browser/', browserView),
)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
        