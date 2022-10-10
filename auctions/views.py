from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib import messages

from .models import User, Listing, Bid, Category, Comment

from django.contrib.auth.decorators import login_required


class NewBidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['offer']


class NewListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'bid_start', 'image', 'category']


class NewCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']
        widgets = {
            'comment': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Leave your comment here',
            })
        }


@login_required
def create(request):
    if request.method == 'POST':
        form = NewListingForm(request.POST, request.FILES)
        if form.is_valid():
            newListing = form.save(commit=False)
            newListing.creator = request.user
            newListing.save()
            return HttpResponseRedirect(reverse("listings"))
    else:
        return render(request, "auctions/create.html", {
            "form": NewListingForm()
        })


def listing(request, listing_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    listing = Listing.objects.get(id=listing_id)

    if request.user in listing.watchers.all():
        listing.watched = True
    else:
        listing.watched = False

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "form": NewBidForm(),
        "comments": listing.user_comment.all(),
        "form_comment": NewCommentForm()
    })


def categories(request):
    all_categories = Category.objects.all()
    category_id = request.GET.get("category", None)
    listings = Listing.objects.filter(category=category_id, active=True)

    if category_id is None:
        return render(request, "auctions/categories.html", {
            "all_categories": all_categories,
        })
    else:
        return render(request, "auctions/listings.html", {
            "listings": listings,
            "title": "Active Listings"
        })


def index(request):
    return render(request, "auctions/index.html")


def listings(request):
    listings = Listing.objects.filter(active=True)
    count = 0
    for listing in listings:
        if request.user in listing.watchers.all():
            listing.watched = True
            count += 1
        else:
            listing.watched = False
        request.session['watchlist_count'] = count
    return render(request, "auctions/listings.html", {
        "listings": listings,
        "title": "Active Listings"
    })


@login_required
def comment(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    form = NewCommentForm(request.POST)
    newComment = form.save(commit=False)
    newComment.user = request.user
    newComment.listing = listing
    messages.success(request, message='You\'ve commented successfully.')

    newComment.save()

    return HttpResponseRedirect(reverse("listing", args=[listing_id]))


@login_required
def bid(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    offer = float(request.POST['offer'])

    if bid_valid(offer, listing):
        listing.bid_current = offer
        form = NewBidForm(request.POST)
        new_bid = form.save(commit=False)
        new_bid.auction_list = listing
        new_bid.user = request.user
        new_bid.save()
        listing.save()

        return HttpResponseRedirect(reverse("listing", args=[listing_id]))

    else:
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "form": NewBidForm(),
            "min_error": True
        })


def bid_valid(offer, listing):
    if offer >= listing.bid_start and (listing.bid_current is None or offer > listing.bid_current):
        return True
    else:
        return False


def close_listing(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    if request.user == listing.creator:
        listing.active = False
        listing.buyer = Bid.objects.filter(auction_list=listing).last().user
        listing.save()

        return HttpResponseRedirect(reverse("listing", args=[listing_id]))
    else:
        listing.watchers.add(request.user)
    return HttpResponseRedirect(reverse("watchlist"))


@login_required
def watchlist(request):
    listings = request.user.watchlist.all()

    for listing in listings:
        if request.user in listing.watchers.all():
            listing.watched = True
        else:
            listing.watched = False

    return render(request, "auctions/listings.html", {
        "listings": listings,
        "title": "My watchlist"
    })


@login_required
def update_watchlist(request, listing_id, reverse_method):
    listing = Listing.objects.get(id=listing_id)
    if request.user in listing.watchers.all():
        listing.watchers.remove(request.user)
    else:
        listing.watchers.add(request.user)

    if reverse_method == "listing":
        return listing(request, listing_id)
    else:
        return HttpResponseRedirect(reverse(reverse_method))


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
