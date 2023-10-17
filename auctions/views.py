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
            "categories": Category.objects.all(),
            "active_page": "index"
        })
    listings = Listing.objects.filter(is_active=True)
    categories = Category.objects.all()
    return render(request, "auctions/index.html", {
        "listings": listings,
        "categories": categories,
        "active_page": "index"
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
                "message": "Invalid username and/or password.",
                "active_page": "index"
            })
    else:
        if "next" in request.GET:
            messages.info(request, "You need to login first")
        return render(request, "auctions/login.html", {
            "active_page": "login"
        })


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
                "message": "Passwords must match.",
                "active_page": "register"
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken.",
                "active_page": "register"
            })
        login(request, user)
        messages.success(request, "Congratulations, you are registered")
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
            print(f"This is image url: {listing.image}")
            messages.success(request, "Your listing has been added successfully")
            return HttpResponseRedirect(reverse("index"))
        else:
            messages.error(request, "Sorry, your Form is not valid, check it and submit again")
            return render(request, "auctions/listingForm.html", {
                "form": f,
                "active_page": "listingform"
            })

    # if method is get
    return render(request, 'auctions/listingForm.html', {
        "form": ListingForm,
        "active_page": "listingform"
    })
@login_required
def listing_page(request,listing_id):
    user = request.user
    listing = Listing.objects.get(pk=listing_id)
    bids = Bid.objects.filter(listing=listing_id)
    max_bid = 0
    for bid in bids:
        if bid.bid > max_bid:
            max_bid = bid.bid
    watchlists = user.watchlistings.all()
    return render(request, "auctions/listing.html", {
        "listing": listing, 
        "watchlists": watchlists,
        "bid": BidForm,
        "comments": Comment.objects.filter(listing=listing),
        "commentform": CommentForm,
        "currentbid": max_bid
    })

@login_required
def closed_listing(request):
    closed_listings = Listing.objects.filter(is_active=False)
    return render(request, "auctions/closed.html", {
        "listings": closed_listings,
        "active_page": "closed_listing",
        "active_page": "closed"
    })
# function to add listing to watch list
@login_required
def to_watch(request, id):
    user = request.user
    if request.method == "POST":
        listing = Listing.objects.get(pk=id)
        user.watchlistings.add(listing)
    return render(request, "auctions/watchlist.html", {
        "listings": Listing.objects.filter(watchlist=user),
        "active_page": "watchlist"
      
    })
# from listing from a watch list
@login_required
def from_watch(request, id):
    user = request.user
    if request.method == "POST":
        listing = Listing.objects.get(pk=id)
        user.watchlistings.remove(listing)
    return render(request, "auctions/watchlist.html", {
        "listings": Listing.objects.filter(watchlist=user),
        "active_page": "watchlist"
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
            return HttpResponseRedirect(reverse("listing_page"))
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
                messages.error(request, "Sorry, bid must be larger than starting price")
                return HttpResponseRedirect(reverse("listing_page", args=(listing_id, )))
            # otherwise if bid_price is > start_price
            else:
                # create a bid object
                bid = Bid(bider=user, listing=listing, bid=bid_price)
                # save bid to the database
                bid.save()
                messages.success(request, "Your bid has been placed successfully")
                return HttpResponseRedirect(reverse("listing_page", args=(listing_id, )))
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
                    messages.error(request, "Sorry, your bid must be greater than current bid" )
                    return HttpResponseRedirect(reverse("listing_page", args=(listing_id, )))
            # set default values for current bid object
            bid = Bid(bider=user, listing=listing, bid=bid_price)
            bid.save()
            messages.success(request, "Your bid has been placed successfully")
            return HttpResponseRedirect(reverse("listing_page", args=(listing_id, )))
        

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
        messages.success(request, "Your auction has been closed succefully")
        return HttpResponseRedirect(reverse("closed"))   
    return HttpResponseRedirect(reverse("index"))

# comment function
@login_required
def comment(request, listing_id):
    if request.method == 'POST':
        f = CommentForm(request.POST)
        if not f.is_valid():
            messages.error(request, "Sorry, your form is not valid, correct it and submit again")
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

