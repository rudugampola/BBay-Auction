from django.contrib import admin

# Register your models here.
from .models import Email





class EmailAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'sender',
                    'subject', 'read', 'timestamp')
    list_filter = ('user', 'read', 'sender')
    list_display_links = ('id', 'subject')
    search_fields = ('subject', 'recipient')
    list_per_page = 25
    # Mark Emails as Read/Unread
    actions = ['mark_as_read', 'mark_as_unread']
    
    @admin.action(description='Mark selected Email as Read')
    def mark_as_read(self, request, queryset):
        queryset.update(read=True)


    @admin.action(description='Mark selected Email as Unread')
    def mark_as_unread(self, request, queryset):
        queryset.update(read=False)


admin.site.register(Email, EmailAdmin)
