from wsgiref.validate import validator

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

from django.core.files.storage import default_storage as storage
import django_filters
from crispy_forms.helper import FormHelper
from ckeditor.fields import RichTextField

import requests
from django.core.files.base import ContentFile
from django_resized import ResizedImageField
from taggit.managers import TaggableManager


class User(AbstractUser):
    pass


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(
        upload_to="profile/", default='profile/avatar.png')
    facebook = models.CharField(max_length=100, blank=True)
    twitter = models.CharField(max_length=100, blank=True)
    youtube = models.CharField(max_length=100, blank=True)
    instagram = models.CharField(max_length=100, blank=True)
    github = models.CharField(max_length=100, blank=True)

    def __str__(self) -> str:
        return self.user.username


class Category(models.Model):
    category = models.CharField(max_length=30)
    image = models.ImageField(
        upload_to='upload/category/', blank=True, null=True, default='upload/placeholder.png')

    def __str__(self):
        return f"{self.category}"


class Listing(models.Model):
    title = models.CharField(max_length=64)
    # description = models.TextField(max_length=1024, null=True)
    description = RichTextField(max_length=1024, null=True, blank=True)
    bid_start = models.FloatField()
    bid_current = models.FloatField(blank=True, null=True)
    # created_date = models.DateTimeField(default=timezone.localtime())
    created_date = models.DateTimeField(default=timezone.now)
    creator = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="all_listings")
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 blank=True, null=True, related_name="listings_same_category")
    # Image is saved to aws s3 bucket
    image = ResizedImageField(
        size=[300, 300], quality=100, upload_to='upload/', default='upload/placeholder.png')
    buyer = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.PROTECT, )
    active = models.BooleanField(default=True)
    watchers = models.ManyToManyField(
        User, blank=True, related_name="watchlist")
    likes = models.ManyToManyField(
        User, related_name='listing_likes', blank=True)
    score = models.IntegerField(default=0, validators=[
                                MinValueValidator(0), MaxValueValidator(5)])
    paid = models.BooleanField(default=False)
    shipped = models.BooleanField(default=False)
    listing_views = models.IntegerField(default=0, blank=True, null=True)
    tags = TaggableManager()

    def save(self, *args, **kwargs):
        response = requests.post(
            'https://api.remove.bg/v1.0/removebg',
            data={'size': 'auto',
                  'image_url': self.image.url},
            headers={'X-Api-Key': 'UKdAAGc7341VQSGKf8zYqZXi'},
        )
        if response.status_code == requests.codes.ok:
            self.image.save(f"rmbg/{self.image.name}",
                            ContentFile(response.content),
                            save=False,
                            )
        else:
            print("Error:", response.status_code, response.text)
        super().save(*args, **kwargs)

    def total_likes(self):
        return self.likes.count()

    def total_views(self):
        return self.listing_views

    def __str__(self):
        # Show in admin panel
        return f"{self.title}"

    class Meta:
        ordering = ['-id']


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
    # created_date = models.DateTimeField(default=timezone.localtime())
    created_date = models.DateTimeField(default=timezone.now)
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
    # date = models.DateTimeField(default=timezone.localtime())
    date = models.DateTimeField(default=timezone.now)
    price = models.FloatField()


class Profits(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profit = models.FloatField(default=0)
    # date = models.DateTimeField(default=timezone.localtime())
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"User: {self.user} , Profit: {self.profit}"

    def get_date(self):
        return self.date.strftime('%B %d %Y')


class Expenses(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expense = models.FloatField(default=0)
    # date = models.DateTimeField(default=timezone.localtime())
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"User: {self.user} , Expense: {self.expense}"

    def get_date(self):
        return self.date.strftime('%B %d %Y')
