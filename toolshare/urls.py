from django.conf.urls import patterns, include, url
from django.contrib import admin
from share_app import views

admin.autodiscover()

# MAIN

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'toolshare.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
	url(r'^share_app/', include('share_app.urls', namespace="share_app")),
	url(r'^admin/', include(admin.site.urls)),
)