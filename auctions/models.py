from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from PIL import Image

from django.core.files.storage import default_storage as storage
import django_filters
from crispy_forms.helper import FormHelper


class User(AbstractUser):
    pass


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(
        upload_to="profile/", default='profile/avatar.png')


class Category(models.Model):
    category = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.category}"


class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=1024, null=True)
    bid_start = models.FloatField()
    bid_current = models.FloatField(blank=True, null=True)
    created_date = models.DateTimeField(default=timezone.localtime())
    creator = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="all_listings")
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 blank=True, null=True, related_name="listings_same_category")
    # Image is saved to aws s3 bucket
    image = models.ImageField(
        upload_to="upload/", default='upload/placeholder.png')
    buyer = models.ForeignKey(User, null=True, on_delete=models.PROTECT)
    active = models.BooleanField(default=True)
    watchers = models.ManyToManyField(
        User, blank=True, related_name="watchlist")

    def save(self, force_insert=False, force_update=False, using=None):
        super().save()  # saving image first
        # Use aws for storage
        img = storage.open(self.image.name)  # Open image using self
        # if img.height > 300 or img.width > 300:
        #     new_img = (300, 300)
        #     img.thumbnail(new_img)
        #     img.save(self.image.path)  # saving image at the same path

    def __str__(self):
        # Show in admin panel
        return f"{self.title} - {self.creator} - {self.created_date} - {self.category} - {self.active}"


class ListingFilter(django_filters.FilterSet):
    class Meta:
        model = Listing
        fields = {
            # Add placeholders to filter
            'bid_start': ['lte', 'gte'],
            'created_date': ['year__lte', 'year__gte'],
            'bid_current': ['lte', 'gte'],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Your code
        self.form.helper = FormHelper()
        self.form.helper.form_show_labels = False
        # Add placeholders
        self.form.fields['bid_start__lte'].widget.attrs['placeholder'] = 'Start Bid Less Than or Equal To'
        self.form.fields['bid_start__gte'].widget.attrs['placeholder'] = 'Start Bid Greater Than or Equal To'
        self.form.fields['bid_current__lte'].widget.attrs['placeholder'] = 'Current Bid Less Than or Equal To'
        self.form.fields['bid_current__gte'].widget.attrs['placeholder'] = 'Current Bid Greater Than or Equal To'
        self.form.fields['created_date__year__lte'].widget.attrs['placeholder'] = 'Created Year Less Than or Equal To'
        self.form.fields['created_date__year__gte'].widget.attrs['placeholder'] = 'Created Year Greater Than or Equal To'


class Bid(models.Model):
    auction_list = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    offer = models.FloatField()
    date = models.DateTimeField(auto_now=True)


class Comment(models.Model):
    comment = models.CharField(max_length=100)
    created_date = models.DateTimeField(default=timezone.localtime())
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="user_comment")

    def get_date(self):
        return self.created_date.strftime('%B %d %Y')


class Sales(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    buyer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sale_buyer")
    seller = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sale_seller")
    date = models.DateTimeField(default=timezone.localtime())
    price = models.FloatField()


class Profits(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profit = models.FloatField(default=0)
    date = models.DateTimeField(default=timezone.localtime())

    def __str__(self):
        return f"User: {self.user} , Profit: {self.profit}"

    def get_date(self):
        return self.date.strftime('%B %d %Y')


class Expenses(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expense = models.FloatField(default=0)
    date = models.DateTimeField(default=timezone.localtime())

    def __str__(self):
        return f"User: {self.user} , Expense: {self.expense}"

    def get_date(self):
        return self.date.strftime('%B %d %Y')
