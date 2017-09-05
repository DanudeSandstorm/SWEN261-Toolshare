
from django.conf.urls import patterns, url

from tools import views

urlpatterns = patterns( '',
    url( r'^$', views.index, name = 'index' ),

    url( r'^register.html', views.register, name = 'register' ),
    url( r'^login.html', views.get_login_page, name = 'login' ),
    url( r'^me.html', views.me, name='userpage' ),
    url( r'^createsharezone.html', views.createShareZone, name = 'createsz' ),
    url( r'^zoneAll.html', views.zoneAll, name='zoneAll' ),
	url( r'^zone.html', views.zone, name='zone' ),
    url( r'^me.html', views.me, name='confirmReservation' ),
    url( r'^changeprefs.html', views.changeprefs, name='changeprefs' ),
    url( r'^adminChangePrefs.html', views.adminChangePrefs, name='adminChangePrefs'),
    url( r'^csview.html', views.viewCommunityShed, name='viewCommunityShed' ),
    url( r'^toolview.html', views.toolView, name='toolView' ),
    url( r'^createTool.html', views.createTool, name='createTool' ),
    url( r'^szadmin.html', views.szAdmin, name='szadmin' ),
    url( r'^uadmin.html', views.administrateUser, name='administrateUser' ),
    url( r'^logout.html', views.logout_view, name='logout' ),
    url( r'^admin.html', views.admin, name='adminpage' ),
    url( r'^approveUser.html', views.approveUser, name='approveUser' ),
    url( r'^borrowTool.html', views.showBorrowTool, name='showBorrowTool' ),
    url( r'^createcs.html', views.createcs, name='createcs' ),
    url( r'^myTools.html', views.toolAll, name='alltools'),
    url( r'^confirm.html', views.confirm, name='confirmation'), 
    url( r'^message.html', views.messagepg, name='message'),
    url( r'^statistics.html', views.getStats, name='getStats'),
    #url( r'^alltools.html', views.me, name='alltools' ),

    url( r'^notifications.html', views.getNotifications, name='notifications' ),
    url( r'^mysheds.html', views.csadmin, name='mycs' ),
    url( r'^findTool.html', views.findTool, name='findTool' ),
)
