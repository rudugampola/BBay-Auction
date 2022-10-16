from django.contrib import admin

from .models import (Bid, Category, Comment, Expenses, Listing, Profits, Sales,
                     User, UserProfile)

# Register your models here.
admin.site.register(User)
admin.site.register(Listing)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(Category)
admin.site.register(Sales)
admin.site.register(Expenses)
admin.site.register(Profits)
admin.site.register(UserProfile)
