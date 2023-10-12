from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .forms import *
from datetime import datetime
from .models import *



def index(request):
    listings = Listing.objects.filter(is_active=True)
    return render(request, "auctions/index.html", {
        "listings": listings
    })


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
    
# listing view
def listing(request):
    # check method is post
    if request.method == "POST":
        # get user and user id
        user = request.user
        user_id = user.id
        # get the date
        today = datetime.today()
        # instantiate listing with default values
        listing = Listing(seller=user, date=today, is_active=True)
        # add fields to the listing
        f = ListingForm(request.POST, instance=listing)
        # save to the model
        f.save()
        return HttpResponseRedirect(reverse("index"))

    return render(request, 'auctions/listingForm.html', {
        "form": ListingForm
    })

def listing_page(request,listing_id):
    user = request.user
    listing = Listing.objects.get(pk=listing_id)
    watchlist = user.watchlistings.all()
    return render(request, "auctions/listing.html", {
        "listing": listing, 
        "watchlist": watchlist
    })

def closed_listing(request):
    closed_listings = Listing.objects.filter(is_active=False)
    return render(request, "auctions/closed.html", {
        "listings": closed_listings
    })
# function to add listing to watch list
def to_watch(request, id):
    user = request.user
    if request.method == "POST":
        listing = Listing.objects.get(pk=id)
        user.watchlistings.add(listing)
    return render(request, "auctions/watchlist.html", {
        "listings": Listing.objects.filter(watchlist=user)
    })
# from listing from a watch list
def from_watch(request, id):
    user = request.user
    if request.method == "POST":
        listing = Listing.objects.get(pk=id)
        user.watchlistings.remove(listing)
    return render(request, "auctions/watchlist.html", {
        "listings": Listing.objects.filter(watchlist=user)
    })

# biding functing

# add comment fucntion
