from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.listing, name="listing"),
    path("listing/<int:listing_id>", views.listing_page, name="listing_page"),
    path("closed", views.closed_listing, name="closed"),
    path("to_watch/<int:id>", views.to_watch, name="to_watch"),
    path("from_watch/<int:id>", views.from_watch, name="from_watch"),
    path("make_bid/<int:listing_id>", views.make_bid, name="make_bid"),
    path("close/<int:listing_id>", views.close_bid, name="close"),
    path("comment/<int:listing_id>", views.comment, name="comment")
]
