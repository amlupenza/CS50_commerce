from django.contrib.auth.models import AbstractUser
from django.db import models



class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=60)
    def __str__(self):
        return f"{self.name}"


class Listing(models.Model):
    title = models.CharField(max_length=60)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="items")
    description = models.TextField(max_length=1000)
    image = models.CharField(max_length=1000, blank=True, null=True)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    date = models.DateTimeField()
    watchlist = models.ManyToManyField(User, related_name="watchlistings", null=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    buy_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    def __str__(self):
        return f"Title: {self.title}, Category: {self.category}"
    


# bid table
class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, null=True)
    bid = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    bider = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

# comments table
class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, null=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField()
    date = models.DateField()
    
    def __str__(self):
        return f"{self.comment}"


