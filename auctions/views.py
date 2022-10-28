import base64
import csv
import io
import time

from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.html import format_html
from matplotlib.pyplot import get
from commerce.storage_backends import FileStorage
from django.core.paginator import Paginator


from .models import (Bid, Category, Comment, Expenses, Listing, ListingFilter, Profits, Sales,
                     User, UserProfile)

# TODO - Run a report on all listings and their bids and comments and watchers


class NewBidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['offer']


class NewListingForm(forms.ModelForm):
    class Meta:
        model = Listing

        # Add placeholders to all fields
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Title of Listing'}),
            'description': forms.Textarea(attrs={'placeholder': 'Description of Listing'}),
            'bid_start': forms.NumberInput(attrs={'placeholder': 'Starting Bid Price'}),
            'image': forms.FileInput(attrs={'placeholder': 'Image'}),
            'category': forms.Select(attrs={'placeholder': 'Category'}),
        }

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


def index(request):
    return render(request, "auctions/index.html", {
        "title": "Home"
    })


@login_required
def create(request):
    if request.method == 'POST':
        form = NewListingForm(request.POST, request.FILES)
        if form.is_valid():
            newListing = form.save(commit=False)
            newListing.creator = request.user
            newListing.bid_current = newListing.bid_start
            newListing.save()
            messages.success(
                request, 'Success ✅: Listing was created successfully!')
            return HttpResponseRedirect(reverse("listings"))
    else:
        return render(request, "auctions/create.html", {
            "form": NewListingForm(),
            "title": "Create Listing"
        })


def edit_listing(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    # Prefill the form with the current listing data to be edited
    form = NewListingForm(instance=listing)

    if request.method == 'POST':
        listing.title = request.POST['title']
        listing.description = request.POST['description']
        # Allow imagefield to be blank so that it doesn't have to be updated
        request.FILES.getlist('image')
        listing.bid_start = request.POST['bid_start']
        listing.category = Category.objects.get(id=request.POST['category'])
        listing.save()

        messages.success(
            request, 'Success ✅: Listing edited successfully!')
        return HttpResponseRedirect(reverse("listing", args=[listing_id]))
    else:
        return render(request, "auctions/edit_listing.html", {
            "listing": listing,
            "form": form
        })


def listing(request, listing_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    listing = Listing.objects.get(id=listing_id)

    liked = False
    if listing.likes.filter(id=request.user.id).exists():
        liked = True

    if request.user in listing.watchers.all():
        listing.watched = True
    else:
        listing.watched = False

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "form": NewBidForm(),
        "comments": listing.user_comment.all(),
        "form_comment": NewCommentForm(),
        "title": listing.title.title(),
        "liked": liked,
        "total_likes": listing.total_likes()
    })


def like(request, pk):
    listing = get_object_or_404(Listing, id=request.POST.get('listing_id'))
    liked = False
    if listing.likes.filter(id=request.user.id).exists():
        listing.likes.remove(request.user)
        liked = False
    else:
        listing.likes.add(request.user)
        liked = True
    return HttpResponseRedirect(reverse('listing', args=[str(pk)]))


def delete_listing(request, listing_id):
    listing = Listing.objects.get(id=listing_id)

    if request.user == listing.creator:
        listing.delete()
        messages.success(
            request, 'Success ✅: Listing deleted successfully!')
        return HttpResponseRedirect(reverse("listings"))
    else:
        messages.error(
            request, 'Error 💥: Listing was not closed!')
        return HttpResponseRedirect(reverse("listing", args=[listing_id]))


def import_csv(request):
    # Import CSV data that user uploads into Listings table
    if request.method == 'POST':
        csv_file = request.FILES['csv_file']

        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Error 💥: File is not CSV type!')
            return HttpResponseRedirect(reverse("import_csv"))

        data_set = csv_file.read().decode('UTF-8')
        io_string = io.StringIO(data_set)
        next(io_string)

        print("Importing CSV: " + csv_file.name)

        for column in csv.reader(io_string, delimiter=',', quotechar="|"):
            _, created = Listing.objects.update_or_create(
                title=column[0],
                description=column[1],
                bid_start=column[2],
                image=column[3],
                category=Category.objects.get(id=column[4]),
                creator=request.user,
                active=True,
            )
        context = {}
        context['success'] = True  # Set to True if successful

        return render(request, 'auctions/listings.html', context)
    return render(request, 'auctions/import_csv.html', {
        "title": "Import CSV"
    })


def search(request):
    query = request.GET.get('q')
    listings = Listing.objects.filter(title__icontains=query, active=True)
    if not listings:
        return render(request, "auctions/nosearch.html",)
    else:
        return render(request, "auctions/listings.html", {
            "listings": listings,
            "title": "Search Results for \"{query}\"".format(query=query)
        })


def user_profile(request, user_id):
    user = User.objects.get(id=user_id)
    listings = Listing.objects.filter(creator=user, active=True)

    if request.method == 'POST':
        user = User.objects.get(id=user_id)
        user_profile = UserProfile.objects.get(user=user)
        user_profile.avatar = request.FILES['avatar']
        user_profile.save()

        messages.success(
            request, 'Success ✅: Profile picture updated successfully!')
        return HttpResponseRedirect(reverse("user_profile", args=[user_id]))

    return render(request, "auctions/user_profile.html", {
        "search_user": user,
        "listings": listings,
        "title": user.username.title()
    })


def categories(request):
    all_categories = Category.objects.all()
    category_id = request.GET.get("category", None)
    listings = Listing.objects.filter(category=category_id, active=True)

    if category_id is None:
        return render(request, "auctions/categories.html", {
            "all_categories": all_categories,
            "title": "Categories"
        })
    else:
        return render(request, "auctions/listings.html", {
            "listings": listings,
            "title": Category.objects.get(id=category_id)
        })


def create_category(request):
    if request.method == 'POST':
        category = request.POST['category']
        new_category = Category(category=category)
        new_category.save()
        messages.success(request, 'Success ✅: Category created successfully!')
        return HttpResponseRedirect(reverse("categories"))
    else:
        return render(request, "auctions/create_category.html", {
            "title": "Create Category"
        })


def listings(request):
    listings = Listing.objects.filter(active=True)
    count = 0
    paginator = Paginator(listings, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    for listing in listings:
        if request.user in listing.watchers.all():
            listing.watched = True
            count += 1
        else:
            listing.watched = False
        request.session['watchlist_count'] = count
    # send a html message
    messages.info(
        request, format_html("{} <a href='/filter'>{}</a>",
                             'Protip! For an advanced search, try using ', 'advanced filters.'))
    return render(request, "auctions/listings.html", {
        'page_obj': page_obj,
        "listings": listings,
        "title": "Active Listings"
    })


def filter(request):
    f = ListingFilter(request.GET, queryset=Listing.objects.all())
    # Show message when filter is submitted
    if request.GET:
        messages.info(request, 'Success ✅: ' +
                      str(f.qs.count()) + ' listings found!')

    return render(request, 'auctions/filter.html', {'filter': f, 'title': 'Filter Results'})


@ login_required
def comment(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    form = NewCommentForm(request.POST)
    newComment = form.save(commit=False)
    newComment.user = request.user
    newComment.listing = listing
    newComment.save()
    messages.success(
        request, "Success ✅: You\'ve commented successfully.")

    return HttpResponseRedirect(reverse("listing", args=[listing_id]))


@ login_required
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
    listing.active = False
    if Bid.objects.filter(auction_list=listing).last() is not None:
        buyer = Bid.objects.filter(auction_list=listing).last().user
    else:
        buyer = None

    if request.user == listing.creator:
        # listing.active = False
        if buyer is not None:
            listing.buyer = buyer
            listing.save()

            # Create a new Sales transaction
            sale = Sales.objects.create(
                listing=listing, buyer=buyer, seller=request.user, price=listing.bid_current)
            sale.save()

            # Create a new profit for the seller
            profit = Profits.objects.create(
                user=request.user, profit=listing.bid_current)
            profit.save()

            # Create a new expense for the buyer
            expense = Expenses.objects.create(
                user=buyer, expense=listing.bid_current)
            expense.save()

        messages.success(
            request, 'Success ✅: Listing closed successfully!')

        return HttpResponseRedirect(reverse("listing", args=[listing_id]))


@ login_required
def profits(request):
    profits = Profits.objects.filter(user=request.user)
    #  Sum all profits
    total = 0
    for profit in profits:
        total += profit.profit

    # Create a JSON object to store the profits
    data = profits.values('user', 'profit', 'date')
    profitsJSON = (JsonResponse({'data': list(data), 'type': 'profit'}))

    # TODO - Make the Report Microservice work for Profit and Expenses using AWS S3
    # Storing data.txt in AWS S3
    # file_storage = FileStorage()
    # file = file_storage.open('data.txt', 'w')
    # file.write(profitsJSON.content)
    # file.close()

    # Write the JSON object to a file
    with open('auctions/graphs/data.txt', 'w+') as f:
        f.write(profitsJSON.content.decode('utf-8'))

    # Read the image
    time.sleep(1)
    with open('auctions/graphs/graph.png', 'rb') as image_file:
        image = base64.b64encode(image_file.read()).decode('utf-8')

    return render(request, "auctions/profits.html", {
        "profits": profits,
        "total": total,
        "image": image,
        "title": "Profit Report"
    })


@ login_required
def expenses(request):
    expenses = Expenses.objects.filter(user=request.user)
    #  Sum all expenses
    total = 0
    for expense in expenses:
        total += expense.expense

    # Create a JSON object to store the expenses
    data = expenses.values('user', 'expense', 'date')
    expensesJSON = (JsonResponse({'data': list(data), 'type': 'expense'}))

    # Write the JSON object to a file
    with open('auctions/graphs/data.txt', 'w+') as f:
        f.write(expensesJSON.content.decode('utf-8'))

    # Read the image
    time.sleep(1)
    with open('auctions/graphs/graph.png', 'rb') as image_file:
        image = base64.b64encode(image_file.read()).decode('utf-8')

    return render(request, "auctions/expenses.html", {
        "expenses": expenses,
        "total": total,
        "image": image,
        "title": "Expense Report"
    })


@ login_required
def watchlist(request):
    listings = request.user.watchlist.all()

    for listing in listings:
        if request.user in listing.watchers.all():
            listing.watched = True
        else:
            listing.watched = False
    watchlistCount = listings.count()
    print("Watchlist count: ", watchlistCount)

    return render(request, "auctions/listings.html", {
        "listings": listings,
        "title": "My Watchlist",
        "watchlistCount": watchlistCount
    })


@ login_required
def update_watchlist(request, listing_id, reverse_method):
    listing = Listing.objects.get(id=listing_id)
    if request.user in listing.watchers.all():
        listing.watchers.remove(request.user)
    else:
        listing.watchers.add(request.user)

    if reverse_method == "listings":
        # Updated watchlist_count for the navbar
        if request.user in listing.watchers.all():
            listing.watched = True
            request.session['watchlist_count'] += 1  # Update watchlist_count
        else:
            listing.watched = False
            request.session['watchlist_count'] = request.user.watchlist.count()

    # Stay on the same page, but update the watchlist_count for the navbar
        return HttpResponseRedirect(reverse(reverse_method))
    else:  # reverse_method = "listing"
        request.session['watchlist_count'] = request.user.watchlist.count()
        return HttpResponseRedirect(reverse(reverse_method, args=[listing_id]))


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
            messages.error(
                request, "Error 💥: Invalid username and/or password.")
            return HttpResponseRedirect(reverse("login"))
    else:
        return render(request, "auctions/login.html", {
            "title": "Login"
        })


def logout_view(request):
    logout(request)
    messages.success(
        request, "Success ✅: Logged out successfully!")
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            messages.error(request, "Error 💥: Passwords must match.")
            return HttpResponseRedirect(reverse("register"))

        try:
            user = User.objects.create_user(username, email, password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
        except IntegrityError:
            messages.error(request, "Error 💥: Username already taken.")
            return HttpResponseRedirect(reverse("register"))
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html", {
            "title": "Register"
        })
