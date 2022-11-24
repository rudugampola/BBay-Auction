from django.contrib import admin

# Register your models here.
from .models import Email


class EmailAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'sender',
                    'subject', 'read', 'timestamp')
    list_display_links = ('id', 'subject')
    search_fields = ('subject', 'recipient')
    list_per_page = 25


admin.site.register(Email, EmailAdmin)
