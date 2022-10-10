from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from PIL import Image


class User(AbstractUser):
    pass


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
    image = models.ImageField(
        upload_to="upload/", default='upload/placeholder.png')
    buyer = models.ForeignKey(User, null=True, on_delete=models.PROTECT)
    active = models.BooleanField(default=True)
    watchers = models.ManyToManyField(
        User, blank=True, related_name="watchlist")

    def save(self):
        super().save()  # saving image first
        img = Image.open(self.image.path)  # Open image using self
        if img.height > 300 or img.width > 300:
            new_img = (300, 300)
            img.thumbnail(new_img)
            img.save(self.image.path)  # saving image at the same path

    def __str__(self):
        return f"{self.title} : {self.description}"


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

# Model to record sales history


class Sales(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)
    price = models.FloatField()
