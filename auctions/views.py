from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .forms import *
from datetime import datetime
from .models import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required



def index(request):
    if request.method =="POST":
        category_id = int(request.POST.get("category"))
        category = Category.objects.get(pk=category_id)
        listings = Listing.objects.filter(category=category, is_active=True)
        return render(request, "auctions/index.html", {
            "listings": listings,
            "categories": Category.objects.all()
        })
    listings = Listing.objects.filter(is_active=True)
    categories = Category.objects.all()
    return render(request, "auctions/index.html", {
        "listings": listings,
        "categories": categories
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
@login_required
def listing(request):
    # check method is post
    if request.method == "POST":
        # get user and user id
        user = request.user
        # get the date
        today = datetime.now()
        f = ListingForm(request.POST)
        if f.is_valid():
            listing = f.save(commit=False)
            listing.seller = user
            listing.date = today
            listing.is_active = True
            listing.save()
        else:
            return render(request, "auctions/listingForm.html", {
                "form": f,
                "message": "Sorry, your Form is not valid, check it and submit again"
            })
        # instantiate listing with default values
        listing = Listing(seller=user, date=today, is_active=True)
        # add fields to the listing
       
        # save to the model
    return render(request, 'auctions/listingForm.html', {
        "form": ListingForm
    })
@login_required
def listing_page(request,listing_id):
    user = request.user
    listing = Listing.objects.get(pk=listing_id)
    bids = Bid.objects.filter(listing=listing_id)
    watchlists = user.watchlistings.all()
    return render(request, "auctions/listing.html", {
        "listing": listing, 
        "watchlists": watchlists,
        "bid": BidForm,
        "comments": Comment.objects.filter(listing=listing),
        "commentform": CommentForm
    })

def closed_listing(request):
    closed_listings = Listing.objects.filter(is_active=False)
    return render(request, "auctions/closed.html", {
        "listings": closed_listings
    })
# function to add listing to watch list
@login_required
def to_watch(request, id):
    user = request.user
    if request.method == "POST":
        listing = Listing.objects.get(pk=id)
        user.watchlistings.add(listing)
    return render(request, "auctions/watchlist.html", {
        "listings": Listing.objects.filter(watchlist=user)
    })
# from listing from a watch list
@login_required
def from_watch(request, id):
    user = request.user
    if request.method == "POST":
        listing = Listing.objects.get(pk=id)
        user.watchlistings.remove(listing)
    return render(request, "auctions/watchlist.html", {
        "listings": Listing.objects.filter(watchlist=user)
    })

# biding functing
@login_required
def make_bid(request, listing_id):
    if request.method == "POST":
        # get form values
        f = BidForm(request.POST)
        # check if form is valid
        if not f.is_valid():
            messages.error(request, "Sorry, your form is not valid")
            return render(request, "auctions/listing.html", {
                "bid": f,
                "message": "Sorry, your form is not valid"
            })
        # get user's input
        bid_price = float(f.cleaned_data["bid"])
        # get user object
        user = request.user
        # get listing object
        listing = Listing.objects.get(pk=listing_id)
        # identify current listing starting price
        start_price = listing.starting_bid

        # get all bids for this listing
        bids = Bid.objects.filter(listing=listing)
        if not bids:
            # check if bid_price is < than listing starting price
            if bid_price < start_price:
                
                return render(request, "auctions/listing.html", {
                    "bid": f, 
                    "message": "Bid must be larger than starting price",
                    "listing":listing
                })
            # otherwise if bid_price is > start_price
            else:
                # create a bid object
                bid = Bid(bider=user, listing=listing, bid=bid_price)
                # save bid to the database
                bid.save()
                return render(request, "auctions/listing.html", {
                    "bid":f,
                    "listing": listing,
                    "message": "Your bid has been placed successfully",
                    "currentbid": bid_price
                })
        # check if there is a bid for this listing
        else:
        
            # initiate maximum bid
            max_bid = 0
            # loop through the bid
            for bid in bids:
                # get maximum bid
                if bid.bid > max_bid:
                    # update maximum bid value
                    max_bid = bid.bid
            

            # check if maximum bid is greater than user's bid       
            if max_bid > bid_price: 
                    return render(request, "auctions/listing.html", {
                        "bid":f, 
                        "message": "Sorry, your bid must be greater than current bid",
                        "listing":listing,
                        "currentbid": max_bid
                    })
            # set default values for current bid object
            bid = Bid(bider=user, listing=listing, bid=bid_price)
            bid.save()
            return render(request, "auctions/listing.html", {
                "bid":f,
                "listing": listing,
                "message": "Your bid has been placed successfully",
                "currentbid": max_bid
                
            })
        

# close bid
@login_required
def close_bid(request, listing_id):
    if request.method == "POST":
        # get listing
        listing = Listing.objects.get(pk=listing_id)
        #update is_active field to False
        listing.is_active = False
        bids = Bid.objects.filter(listing=listing)
        # loop through bids to get max bid
        max_bid = 0
        for bid in bids:
            if bid.bid > max_bid:
                max_bid = bid.bid
        # get highest bid
        bid = Bid.objects.get(bid=max_bid, listing=listing)
        print(max_bid)
        print(bid)
        buyer = bid.bider
        listing.buyer = buyer
        listing.buy_price = max_bid
        listing.save()
        messages.success(request, "Your listing has been closed")
        return HttpResponseRedirect(reverse("closed"))   
    return HttpResponseRedirect(reverse("index"))

# comment function
@login_required
def comment(request, listing_id):
    if request.method == 'POST':
        f = CommentForm(request.POST)
        if not f.is_valid():
            return render(request, "auctions/listing.html", {
                "commentform": f
            })
        # get listing object
        listing = Listing.objects.get(pk=listing_id)
        now = datetime.now()
        comment = f.save(commit=False)
        comment.listing = listing
        comment.sender = request.user
        comment.date = now
        comment.save()
        messages.success(request, "Your comment was added successfully")
        return HttpResponseRedirect(reverse("listing_page", args=(listing_id, )))
    messages.MessageFailure(request, "You have to fill the form")
    return HttpResponseRedirect(reverse("listing_page", args=(listing_id, )))

