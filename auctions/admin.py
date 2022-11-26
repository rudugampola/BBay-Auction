from django.contrib import admin
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.utils.html import escape
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (Bid, Category, Comment, Expenses, Listing, Profits, Sales,
                     User, UserProfile)


# Display Listings in a table
class ListingAdmin(admin.ModelAdmin):
    model = Listing
    list_display = ('title', 'creator', 'created_date', 'bid_start', 'bid_current',
                    'category', 'active', 'listing_views', 'score', 'paid', 'shipped', 'reported', 'id')
    list_filter = ('title', 'creator', 'created_date',
                   'category', 'active', 'score', 'reported', 'id')
    search_fields = ('title', 'creator', 'created_date',
                     'category', 'active', 'score', 'id')
    list_editable = ('bid_start', 'bid_current', 'active')

    actions = ['make_active', 'make_inactive',
               'paid', 'unpaid', 'shipped', 'unshipped']

    @admin.action(description='Mark selected Listings as Active')
    def make_active(self, request, queryset):
        queryset.update(active=True)

    @admin.action(description='Mark selected Listings as Inactive')
    def make_inactive(self, request, queryset):
        queryset.update(active=False)

    @admin.action(description='Mark selected Listings as Paid')
    def paid(self, request, queryset):
        queryset.update(paid=True)

    @admin.action(description='Mark selected Listings as Unpaid')
    def unpaid(self, request, queryset):
        queryset.update(paid=False)

    @admin.action(description='Mark selected Listings as Shipped')
    def shipped(self, request, queryset):
        queryset.update(shipped=True)

    @admin.action(description='Mark selected Listings as Unshipped')
    def unshipped(self, request, queryset):
        queryset.update(shipped=False)


class UserAdmin(admin.ModelAdmin):
    model = User
    list_display = ('username', 'email', 'first_name',
                    'last_name', 'id', 'is_superuser', 'date_joined', 'last_login', 'is_active', 'is_staff')
    list_filter = ('username', 'email', 'first_name', 'last_name', 'id')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'id')


class UserProfileAdmin(admin.ModelAdmin):
    model = UserProfile
    list_display = ('user', 'city', 'id')
    list_filter = ('user', 'city', 'id')
    search_fields = ('user', 'city', 'id')


class SalesAdmin(admin.ModelAdmin):
    model = Sales
    list_display = ('id', 'listing', 'buyer', 'seller', 'date', 'price')
    list_filter = ('listing', 'buyer', 'seller', 'date', 'price', 'id')
    search_fields = ('listing', 'buyer', 'seller', 'date', 'price', 'id')


class ProfitsAdmin(admin.ModelAdmin):
    model = Profits
    list_display = ('id', 'user', 'profit', 'date')
    list_filter = ('user', 'id')
    search_fields = ('user', 'id')


class ExpensesAdmin(admin.ModelAdmin):
    model = Expenses
    list_display = ('id', 'user', 'expense', 'date')
    list_filter = ('user', 'id')
    search_fields = ('user', 'id')


class CategoryAdmin(admin.ModelAdmin):
    model = Category
    list_display = ('id', 'category')


# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Sales, SalesAdmin)
admin.site.register(Expenses, ExpensesAdmin)
admin.site.register(Profits, ProfitsAdmin)
admin.site.register(UserProfile, UserProfileAdmin)

admin.site.site_header = "Auction Administation"
admin.site.site_title = "Auction Administation Portal"


# See all logs and monitor all the activities in the admin panel
@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    date_hierarchy = 'action_time'

    list_filter = [
        'user',
        'content_type',
        'action_flag'
    ]

    search_fields = [
        'object_repr',
        'change_message'
    ]

    list_display = [
        'action_time',
        'user',
        'content_type',
        'object_link',
        'action_flag',
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def object_link(self, obj):
        if obj.action_flag == DELETION:
            link = escape(obj.object_repr)
        else:
            ct = obj.content_type
            link = '<a href="%s">%s</a>' % (
                reverse('admin:%s_%s_change' %
                        (ct.app_label, ct.model), args=[obj.object_id]),
                escape(obj.object_repr),
            )
        return mark_safe(link)
    object_link.admin_order_field = "object_repr"
    object_link.short_description = "object"
