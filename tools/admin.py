from django.contrib import admin
from tools.models import UserData
from tools.models import ShareZone
from tools.models import CommunityShed
from tools.models import Tool
from tools.models import Reservation
from tools.models import ToolType
from tools.models import Notification

class UserInLine( admin.TabularInline ):
    model = UserData
    extra = 1

class CommunityShedInLine( admin.TabularInline ):
    model = CommunityShed
    extra = 1
    
class ToolInLine( admin.TabularInline ):
    model = Tool
    extra = 1
    
class UserAdmin( admin.ModelAdmin ):
    inlines = [ToolInLine]
    
class ShareZoneAdmin( admin.ModelAdmin ):
    fields = ['name', 'restrictedAge', 'isActive']
    list_display = ['name', 'isActive']
    inlines = [CommunityShedInLine, UserInLine]
    actions = ['set_inactive']

    def set_inactive( modeladmin, request, queryset ):
        #queryset.update( 
        pass
    set_inactive.short_description = "Mark selected ShareZones as inactive"
    
admin.site.register( UserData )
admin.site.register( ShareZone, ShareZoneAdmin )
admin.site.register( CommunityShed )
admin.site.register( Tool )
admin.site.register( Reservation )
admin.site.register( ToolType )
admin.site.register( Notification )