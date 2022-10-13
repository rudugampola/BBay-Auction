import base64
import csv
import io
import time

from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.db import IntegrityError
from django.http import FileResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from PIL import Image
from reportlab.pdfgen import canvas

from .models import (Bid, Category, Comment, Expenses, Listing, Profits, Sales,
                     User)

# TODO - Run a report on all listings and their bids and comments and watchers

# TODO - Editing a Listing


def edit_listing(request, listing_id):
    pass


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


def index(request):
    return render(request, "auctions/index.html")


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


def delete_listing(request, listing_id):
    listing = Listing.objects.get(id=listing_id)

    if request.user == listing.creator:
        listing.delete()
        return HttpResponseRedirect(reverse("listings"))
    else:
        return HttpResponseRedirect(reverse("listing", args=[listing_id]))


def import_csv(request):
    # Import CSV data that user uploads into Listings table
    if request.method == 'POST':
        csv_file = request.FILES['csv_file']

        if not csv_file.name.endswith('.csv'):
            return render(request, "auctions/import_csv.html", {
                "message": "Error: File is not CSV type!"
            })

        data_set = csv_file.read().decode('UTF-8')
        io_string = io.StringIO(data_set)
        next(io_string)

        print("Importing CSV: " + csv_file.name)

        for column in csv.reader(io_string, delimiter=',', quotechar="|"):
            _, created = Listing.objects.update_or_create(
                title=column[0],
                description=column[1],
                bid_start=column[2],
                # Convert the image to a File object to save images from CSV
                # image=File(open(column[3], 'rb')),
                image=column[3],
                category=Category.objects.get(id=column[4]),
                creator=request.user,
                active=True,
            )
        context = {}
        context['success'] = True  # Set to True if successful

        return render(request, 'auctions/listings.html', context)
    return render(request, 'auctions/import_csv.html')


def search(request):
    query = request.GET.get('q')
    listings = Listing.objects.filter(title__icontains=query, active=True)
    return render(request, "auctions/listings.html", {
        "listings": listings,
        "title": "Search Results"
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
            "title": Category.objects.get(id=category_id)
        })


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


# TODO - Create a PDF report of the expenses and profits
def pdf(request):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(100, 100, "Hello world.")

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='hello.pdf')


@login_required
def comment(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    form = NewCommentForm(request.POST)
    newComment = form.save(commit=False)
    newComment.user = request.user
    newComment.listing = listing
    messages.success(
        request, message='Success: You\'ve commented successfully.')

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
    buyer = Bid.objects.filter(auction_list=listing).last().user
    if request.user == listing.creator:
        listing.active = False
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

        return HttpResponseRedirect(reverse("listing", args=[listing_id]))
    else:
        listing.watchers.add(request.user)
    return HttpResponseRedirect(reverse("watchlist"))


@login_required
def profits(request):
    profits = Profits.objects.filter(user=request.user)
    #  Sum all profits
    total = 0
    for profit in profits:
        total += profit.profit

    # Create a JSON object to store the profits
    data = profits.values('user', 'profit', 'date')
    profitsJSON = (JsonResponse({'data': list(data), 'type': 'profit'}))

    # Write the JSON object to a file
    with open('C:/Users/ravin/CS361/BBay Auction/auctions/static/graphs/data.txt', 'w') as f:
        f.write(profitsJSON.content.decode('utf-8'))

    # Read the image
    time.sleep(1)
    with open('C:/Users/ravin/CS361/BBay Auction/auctions/static/graphs/graph.png', 'rb') as image_file:
        image = base64.b64encode(image_file.read()).decode('utf-8')

    return render(request, "auctions/profits.html", {
        "profits": profits,
        "total": total,
        "image": image
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
    with open('C:/Users/ravin/CS361/BBay Auction/auctions/static/graphs/data.txt', 'w') as f:
        f.write(expensesJSON.content.decode('utf-8'))

    # Read the image
    time.sleep(1)
    with open('C:/Users/ravin/CS361/BBay Auction/auctions/static/graphs/graph.png', 'rb') as image_file:
        image = base64.b64encode(image_file.read()).decode('utf-8')

    return render(request, "auctions/expenses.html", {
        "expenses": expenses,
        "total": total,
        "image": image
    })


@ login_required
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


@ login_required
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
                "message": "Error: Invalid username and/or password."
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
                "message": "Error: Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Error: Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
