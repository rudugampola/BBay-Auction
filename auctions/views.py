import numpy as np
from mail.models import Email
from .models import (Bid, Category, Comment, Expenses, Listing, ListingFilter, Profits, Sales,
                     User, UserProfile)
import base64
import csv
import io
import time
from datetime import datetime, timedelta
from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.html import format_html
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.utils.translation import gettext as _
from django.utils.translation import get_language, activate


# Stripe Information
import stripe
stripe.api_key = "sk_test_51M0Z0iAVXcXhXFdu5e2NEfPISaTOn4qw7GAiVyfjWlZvwXxJUtEz3DmIwakyoqHH1HEITTZS2n9T1EBRXz2gSX1a000uF27rfu"

# Pagination page numbers
PAGES = 5

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
today = datetime.today()
long_ago = today + timedelta(days=-30)  # 30 days ago


def translate(language):
    """Translate the page to the selected language"""
    cur_language = get_language()
    try:
        activate(language)
    finally:
        activate(cur_language)


class NewBidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['offer']


class NewListingForm(forms.ModelForm):
    class Meta:
        model = Listing

        # Add placeholders to all fields
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Title of Listing', 'class': 'form-control', }),
            'description': forms.Textarea(attrs={'placeholder': 'Description of Listing', 'class': 'form-control', }),
            'bid_start': forms.NumberInput(attrs={'placeholder': 'Starting Bid Price'}),
            'image': forms.FileInput(attrs={'placeholder': 'Image', 'class': 'form-control', 'type': 'file', }),
            'category': forms.Select(attrs={'placeholder': 'Category', 'class': 'form-control', 'type': 'select', 'required': 'true', }),
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


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def index(request):
    """Show all active listings"""
    listings = Listing.objects.filter(active=True)
    # Update watchlist
    count = 0
    categories = Category.objects.all()
    if request.user.is_authenticated:
        for listing in Listing.objects.all():
            if listing in request.user.watchlist.all():
                count += 1
        request.session['watchlist_count'] = count

    trendingListings(request)

    return render(request, "auctions/index.html", {
        "title": "Home",
        "listings": listings,
        "categories": categories,
    })


def support(request):
    """Show the support page"""
    return render(request, "auctions/support.html", {
        "title": "Support"
    })


def agreement(request):
    """Show the agreement page"""
    messages.warning(
        request, "The User Agreement was recently updated. Please read it carefully.")
    return render(request, "auctions/agreement.html", {
        "title": "User Agreement"
    })


def privacy(request):
    """Show the privacy page"""
    messages.warning(
        request, "The privacy policy was recently updated. Please read it carefully.")
    return render(request, "auctions/privacy.html", {
        "title": "Privacy Policy"
    })


@ login_required
def rate_listing(request):
    """Rate a listing"""
    if request.method == 'POST':
        listing_id = request.POST.get('listing_id')

        val = request.POST.get('rating')
        obj = Listing.objects.get(id=listing_id)
        obj.score = val
        obj.save()
        return JsonResponse({'success': 'true', "score": val}, safe=False)
    return JsonResponse({'success': 'false'}, safe=False)


@ login_required
def charge(request):
    """ Charge the user for the listing"""
    pendingPayments = []
    total = 0
    for sale in Sales.objects.filter(buyer=request.user):
        if sale.listing.paid == False:
            pendingPayments.append(sale)
            total += sale.price

    if request.method == 'POST':
        for sale in Sales.objects.filter(buyer=request.user):
            if sale.listing.paid == False:
                sale.listing.paid = True
                sale.listing.save()

        customer = stripe.Customer.create(
            email=request.POST.get('email'),
            name=request.POST.get('name'),
            source=request.POST.get('stripeToken'),
        )

        intent = stripe.PaymentIntent.create(
            customer=customer['id'],
            setup_future_usage='off_session',
            amount=int(total * 100),
            currency='usd',
            payment_method_types=['card'],
            receipt_email=request.POST.get('email'),
            description='Payment for purchases on Auctions',
        )

        return render(request, 'auctions/thanks.html')
    else:
        return render(request, "auctions/payments.html", {
            "pendingPayments": pendingPayments,
            "total": total,
            "user": request.user,
        })


def tips(request):
    """Show the tips page"""
    return render(request, "auctions/tips.html", {
        "title": "Tips"
    })


@login_required
def create(request):
    """Create a new listing"""
    if request.method == 'POST':
        form = NewListingForm(request.POST, request.FILES)
        if form.is_valid():
            newListing = form.save(commit=False)
            newListing.creator = request.user
            newListing.bid_current = newListing.bid_start
            newListing.save()
            messages.success(
                request, 'Listing was created successfully!')
            return HttpResponseRedirect(reverse("auctions:listing", args=[newListing.id]))
        else:  # If form is invalid
            messages.error(
                request, 'There was an error creating your listing.')
            return render(request, "auctions/create.html", {
                "form": form,
                "title": "Create a New Listing"
            })
    else:
        messages.info(
            request, format_html("{} <a href='tips/'>{}</a>",
                                 'See our tips for creating a great listing and ways to set yourself up for success', 'here!'))
        return render(request, "auctions/create.html", {

            "form": NewListingForm(),
            "title": "Create a New Listing"
        })


@ login_required
def edit_listing(request, listing_id):
    """Edit a listing"""
    listing = Listing.objects.get(id=listing_id)
    # Prefill the form with the current listing data to be edited
    form = NewListingForm(instance=listing)

    if request.method == 'POST':
        listing.title = request.POST['title']
        listing.description = request.POST['description']
        # Update the image if a new one is uploaded
        if request.FILES.get('image'):
            listing.image = request.FILES['image']

        listing.bid_start = request.POST['bid_start']
        if Category.objects.filter(id=request.POST['category']).exists():
            listing.category = Category.objects.get(
                id=request.POST['category'])
        listing.save()

        messages.success(
            request, 'Listing edited successfully!')
        return HttpResponseRedirect(reverse("auctions:listing", args=[listing_id]))
    else:
        return render(request, "auctions/edit_listing.html", {
            "listing": listing,
            "form": form
        })


@ login_required
def listing(request, listing_id):
    """Show a listing"""
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('auctions:login'))

    listing = Listing.objects.get(id=listing_id)
    # Increment the views count
    listing.listing_views += 1
    listing.save()

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


@ login_required
def like(request, pk):
    """Like a listing and add it to the user's liked listings"""
    listing = get_object_or_404(Listing, id=request.POST.get('listing_id'))
    liked = False
    if listing.likes.filter(id=request.user.id).exists():
        listing.likes.remove(request.user)
        liked = False
    else:
        listing.likes.add(request.user)
        liked = True
    return HttpResponseRedirect(reverse('auctions:listing', args=[str(pk)]))


@ login_required
def delete_listing(request, listing_id):
    """Delete a listing"""
    listing = Listing.objects.get(id=listing_id)

    if request.user == listing.creator:
        listing.delete()
        messages.success(
            request, 'Listing deleted successfully!')
        return HttpResponseRedirect(reverse("auctions:listings"))
    else:
        messages.error(
            request, 'Listing was not closed!')
        return HttpResponseRedirect(reverse("auctions:listing", args=[listing_id]))


@ login_required
def import_csv(request):
    """Import a CSV file of listings"""
    # Import CSV data that user uploads into Listings table
    if request.method == 'POST':

        if len(request.FILES) == 0:
            messages.error(request, 'No file was uploaded!')
            return HttpResponseRedirect(reverse("auctions:import_csv"))

        csv_file = request.FILES['csv_file']

        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'File is not CSV type!')
            return HttpResponseRedirect(reverse("auctions:import_csv"))

        data_set = csv_file.read().decode('UTF-8')
        io_string = io.StringIO(data_set)
        next(io_string)

        print(bcolors.WARNING + "Importing CSV: " +
              csv_file.name + bcolors.ENDC)

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
    """Search for listings"""
    query = request.GET.get('q')
    listings = Listing.objects.filter(title__icontains=query, active=True)
    paginator = Paginator(listings, PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    if not listings:
        return render(request, "auctions/nosearch.html",)
    else:
        return render(request, "auctions/listings.html", {
            "page_obj": page_obj,
            "listings": listings,
            "title": "Search Results for \"{query}\"".format(query=query)
        })


@ login_required
def user_profile(request, user_id):
    """Show a user's profile"""
    user = User.objects.get(id=user_id)
    listings = Listing.objects.filter(creator=user, active=True)
    paginator = Paginator(listings, PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    watchlist = request.user.watchlist.all()

    pendingPayments = []
    total = 0
    for sale in Sales.objects.filter(buyer=request.user):
        if sale.listing.paid == False:
            pendingPayments.append(sale)
            total += sale.price

    if request.method == 'POST':
        user = User.objects.get(id=user_id)
        user_profile = UserProfile.objects.get(user=user)
        user_profile.avatar = request.FILES['avatar']
        user_profile.save()

        messages.success(
            request, 'Profile picture updated successfully!')
        return HttpResponseRedirect(reverse("auctions:user_profile", args=[user_id]))

    return render(request, "auctions/user_profile.html", {
        "page_obj": page_obj,
        "search_user": user,
        "search_profile": UserProfile.objects.get(user=user),
        "listings": listings,
        "title": user.username.title(),
        "watchlist": watchlist,

        "pendingPayments": pendingPayments,
        "total": total,
        "user": request.user,
        "userInfo": UserProfile.objects.get(user=request.user)
    })


@ login_required
def update_userInfo(request, user_id):
    """Update a user's profile"""
    user = User.objects.get(id=user_id)
    user_profile = UserProfile.objects.get(user=user)

    firstName = request.POST.get('firstName')
    lastName = request.POST.get('lastName')
    phone = request.POST.get('UpdatePhone')
    address = request.POST.get('UpdateAddress')
    city = request.POST.get('UpdateCity')
    state = request.POST.get('UpdateState')
    zipcode = request.POST.get('UpdateZipcode')

    facebook = request.POST.get('facebook')
    youtube = request.POST.get('youtube')
    twitter = request.POST.get('twitter')
    instagram = request.POST.get('instagram')
    github = request.POST.get('github')

    if firstName:
        user.first_name = firstName
    if lastName:
        user.last_name = lastName
    user.save()

    if phone:
        user_profile.phone = phone
    if address:
        user_profile.address = address
    if city:
        user_profile.city = city
    if state:
        user_profile.state = state
    if zipcode:
        user_profile.zipcode = zipcode

    if facebook:
        user_profile.facebook = facebook
    if youtube:
        user_profile.youtube = youtube
    if twitter:
        user_profile.twitter = twitter
    if instagram:
        user_profile.instagram = instagram
    if github:
        user_profile.github = github

    user_profile.save()

    messages.success(request, 'User info updated successfully!')

    return HttpResponseRedirect(reverse('auctions:user_profile', args=[str(user_id)]))


def categories(request):
    "Show all categories"
    all_categories = Category.objects.all()
    category_id = request.GET.get("category", None)
    listings = Listing.objects.filter(category=category_id, active=True)
    category_count = listings.count()
    if request.user.is_authenticated:
        watchlist = request.user.watchlist.all()
    else:
        watchlist = None

    paginator = Paginator(listings, PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if category_id is None and page_number is None:
        return render(request, "auctions/categories.html", {
            "all_categories": all_categories,
            "title": "Categories"
        })
    else:
        return render(request, "auctions/listings.html", {
            "page_obj": page_obj,
            "listings": listings,
            "category_count": category_count,
            "category": Category.objects.get(id=category_id),
            "watchlist": watchlist,
        })


@ login_required
def create_category(request):
    """Create a new category"""
    if request.method == 'POST':
        category = request.POST['category']
        new_category = Category(category=category)
        new_category.save()
        messages.success(request, 'Category created successfully!')
        return HttpResponseRedirect(reverse("auctions:categories"))
    else:
        return render(request, "auctions/create_category.html", {
            "title": "Create Category"
        })


def listings(request):
    """Show all listings"""
    listings = Listing.objects.filter(active=True)
    count = 0
    paginator = Paginator(listings, PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    watchlist = []
    if request.user.is_authenticated:
        watchlist = request.user.watchlist.all()

    for listing in listings:
        if request.user in listing.watchers.all():
            listing.watched = True
            count += 1
        else:
            listing.watched = False
        request.session['watchlist_count'] = count
    # Send a html message
    messages.info(
        request, format_html("{} <a href='/filter'>{}</a>",
                             'For an advanced search, try using advanced filters ', 'here!'))
    return render(request, "auctions/listings.html", {
        'page_obj': page_obj,
        "listings": listings,
        "title": "Active Listings",
        "watchlist": watchlist
    })


def trendingListings(request):
    """Show all trending listings, calculate a score for each listing"""
    rdata = Listing.objects.filter(created_date__gte=long_ago)
    likerate = []
    viewrate = []
    for i in rdata:
        lr = i.total_likes() + 1
        vr = i.total_views() + 1
        lr = lr / vr
        likerate.append(lr)
        u = User.objects.count()
        vrt = vr / u
        viewrate.append(vrt)
    lr1 = np.array(likerate)
    vr1 = np.array(viewrate)
    lr = lr1.round(2)
    vr = vr1.round(2)
    for i in lr, vr:
        a = lr + vr
        a = a * 50
    rdata = Listing.objects.filter(created_date__gte=long_ago)
    trendingdata = a
    j = 0
    trendingdict = {}
    for i in rdata:
        trendingdict[i.id] = trendingdata[j]
        j += 1
    trend = {k: v for k, v in sorted(
        trendingdict.items(), key=lambda item: item[1], reverse=True)}
    trendlist = []
    for k in trend.keys():
        trendlist.append(k)
    print('trendlist --', trendlist)
    return trendlist


def filter(request):
    """Filter listings"""
    f = ListingFilter(request.GET, queryset=Listing.objects.all())
    # Show message when filter is submitted
    if request.GET:
        messages.success(request, str(f.qs.count()) + ' listings found!')

    return render(request, 'auctions/filter.html', {'filter': f, 'title': 'Filter Results'})


@ login_required
def comment(request, listing_id):
    """Add a comment to a listing"""
    listing = Listing.objects.get(id=listing_id)
    form = NewCommentForm(request.POST)
    newComment = form.save(commit=False)
    newComment.user = request.user
    newComment.listing = listing
    newComment.save()
    messages.success(
        request, "You\'ve commented successfully.")

    return HttpResponseRedirect(reverse("auctions:listing", args=[listing_id]))


@ login_required
def bid(request, listing_id):
    """Add a bid to a listing"""
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

        return HttpResponseRedirect(reverse("auctions:listing", args=[listing_id]))

    else:
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "form": NewBidForm(),
            "min_error": True
        })


def bid_valid(offer, listing):
    """Check if bid is valid"""
    if offer >= listing.bid_start and (listing.bid_current is None or offer > listing.bid_current):
        return True
    else:
        return False


@ login_required
def close_listing(request, listing_id):
    """Close a listing"""
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

        # Create one email for each recipient, plus sender
        body = "Congratulations! You have won the auction for " + listing.title + " for $" + \
            str(listing.bid_current) + "." + " Please contact the seller at " + \
            listing.creator.email + " to arrange for the delivery of the item."
        subject = "You have won 🎉 the auction for " + listing.title + "!"

        sender = Email.objects.create(
            body=body, subject=subject, sender=request.user, user=request.user)
        receiver = Email.objects.create(
            body=body, subject=subject, sender=request.user, user=buyer)

        sender.recipients.set([buyer])
        receiver.recipients.set([buyer])
        sender.save()
        receiver.save()

        messages.success(
            request, 'Listing closed successfully!')

        return HttpResponseRedirect(reverse("auctions:listing", args=[listing_id]))


@ login_required
# Show all the items that have been paid for and ready to ship to buyers
@user_passes_test(lambda u: u.is_superuser)
def shipping(request):
    """Show all the items that have been paid for and ready to ship to buyers"""
    ready_to_ship = Listing.objects.filter(paid=True, shipped=False)
    buyers_address = {}
    for listing in ready_to_ship:
        address = UserProfile.objects.get(user=listing.buyer)
        buyers_address[listing.buyer] = address

    sale_ID = {}
    for listing in ready_to_ship:
        sale = Sales.objects.get(listing=listing)
        # Get PK of the sale
        sale_ID[sale.id] = listing

    if request.method == "POST":
        listing_ids = request.POST.getlist('listing-id')
        for listing_id in listing_ids:
            listing = Listing.objects.get(id=listing_id)
            listing.shipped = True
            listing.save()
        messages.success(
            request, 'Item(s) marked as shipped!')

        return HttpResponseRedirect(reverse("auctions:shipping"))

    return render(request, "auctions/shipping.html", {
        "title": "Shipping",
        "ready_to_ship": ready_to_ship,
        "buyers_address": buyers_address,
        "sale_ID": sale_ID
    })


@ login_required
def profits(request):
    """Show all the profits"""
    profits = Profits.objects.filter(user=request.user)
    #  Sum all profits
    total = 0
    for profit in profits:
        total += profit.profit

    # Create a JSON object to store the profits
    data = profits.values('user', 'profit', 'date')
    profitsJSON = (JsonResponse({'data': list(data), 'type': 'profit'}))

    # Write the JSON object to a file
    print(bcolors.HEADER +
          "\nRequesting data from Microservice... 🌎\n" + bcolors.ENDC)
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
    """Show all the expenses"""
    expenses = Expenses.objects.filter(user=request.user)
    #  Sum all expenses
    total = 0
    for expense in expenses:
        total += expense.expense

    # Create a JSON object to store the expenses
    data = expenses.values('user', 'expense', 'date')
    expensesJSON = (JsonResponse({'data': list(data), 'type': 'expense'}))

    # Write the JSON object to a file
    print(bcolors.HEADER + "\nRequesting data from Microservice... 🌎\n" + bcolors.ENDC)
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
    """Show all the items in the user's watchlist"""
    listings = request.user.watchlist.all()
    paginator = Paginator(listings, PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    watchlist = request.user.watchlist.all()

    for listing in listings:
        if request.user in listing.watchers.all():
            listing.watched = True
        else:
            listing.watched = False
    watchlistCount = listings.count()
    print(bcolors.OKGREEN + "Watchlist count: " + bcolors.ENDC, watchlistCount)

    return render(request, "auctions/listings.html", {
        "page_obj": page_obj,
        "listings": listings,
        "title": "My Watchlist",
        "watchlistCount": watchlistCount,
        "watchlist": watchlist
    })


@ login_required
def update_watchlist(request, listing_id, reverse_method):
    """Add or remove an item from the user's watchlist"""
    listing = Listing.objects.get(id=listing_id)
    if request.user in listing.watchers.all():
        listing.watchers.remove(request.user)
    else:
        listing.watchers.add(request.user)

    if reverse_method == "auctions:listings":
        # Updated watchlist_count for the navbar
        if request.user in listing.watchers.all():
            listing.watched = True
            request.session['watchlist_count'] += 1  # Update watchlist_count
        else:
            listing.watched = False
            request.session['watchlist_count'] = request.user.watchlist.count()

    # Stay on the same page, but update the watchlist_count for the navbar
        return HttpResponseRedirect(reverse(reverse_method))

    if reverse_method == "auctions:listing":
        request.session['watchlist_count'] = request.user.watchlist.count()
        return HttpResponseRedirect(reverse(reverse_method, args=[listing_id]))

    else:  # reverse_method = "listing"
        request.session['watchlist_count'] = request.user.watchlist.count()
        return HttpResponseRedirect(reverse(reverse_method, args=[request.user.id]))


def login_view(request):
    if request.method == "POST":
        """Log user in"""
        # Get the query string parameter 'next' from the URL
        nex = request.POST.get('next')

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Remember user if checkbox is checked
        if 'remember_me' in request.POST:
            request.session.set_expiry(1209600)  # 2 weeks

        # Check if authentication successful
        if user is not None:
            login(request, user)
            print(bcolors.WARNING + "\nUser logged in: " +
                  bcolors.ENDC + str(user) + "\n")
            if nex:
                return HttpResponseRedirect(nex)
            else:
                return HttpResponseRedirect(reverse("auctions:index"))

        else:
            messages.error(
                request, "Invalid username and/or password.")
            return HttpResponseRedirect(reverse("auctions:login"))
    else:
        return render(request, "auctions/login.html", {
            "title": "Login"
        })


def logout_view(request):
    """Log user out"""
    logout(request)
    messages.success(
        request, "Logged out successfully!")
    return HttpResponseRedirect(reverse("auctions:index"))


def register(request):
    """Register user"""
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            messages.error(request, "Passwords must match.")
            return HttpResponseRedirect(reverse("auctions:register"))

        try:
            user = User.objects.create_user(username, email, password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            subject = 'Welcome to Bbay Auctions!'
            message = f'Hello {first_name},\n\nThank you for registering with Bbay Auctions. We hope you enjoy your stay!\n\nBest regards,\nBbay Auctions Team'
            from_email = settings.EMAIL_HOST_USER
            recepient_list = [email]
            send_mail(subject, message, from_email,
                      recepient_list, fail_silently=False)

            # Create a profile for every user created, avatar will be default
            profile = UserProfile(user=user)
            profile.save()
        except IntegrityError:
            messages.error(request, "Username already taken.")
            return HttpResponseRedirect(reverse("auctions:register"))
        login(request, user)
        messages.success(request, "User Registered successfully!")
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/register.html", {
            "title": "Register"
        })
