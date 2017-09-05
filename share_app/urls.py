from django.conf.urls import patterns, url
from share_app import views

# SHARE_APP

urlpatterns = patterns('',
	url(r'^signup/?$', views.signup, name='signup'),
	url(r'^tryLogin/?$', views.tryLogin, name='tryLogin'),
	url(r'^tryLogout/?$', views.tryLogout, name='tryLogout'),
	url(r'^addTool/?$', views.addTool, name='addTool'),
	url(r'^borrowTool/?$', views.borrowTool, name='borrowTool'),
	url(r'^returnTools/?$', views.returnTools, name='returnTools'),
	url(r'^addShed/?$', views.addShed, name='addShed'),
	url(r'^tool/?$', views.addTool, name='addTool'),
	url(r'^edit_info/?$', views.editAccountInfo, name='editAccountInfo'),
	url(r'^saveAccountInfo/?$', views.saveAccountInfo, name='saveAccountInfo'),
	url(r'^editTools/?$', views.editTools, name='editTools'),
	url(r'^sendMessage/?$', views.sendMessage, name='sendMessage'),
	url(r'^approveUser/?$', views.approveUser, name='approveUser'),
	url(r'^$', views.index, name='index'),
)