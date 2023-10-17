from django import forms
from .models import *

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = (
                  'title',
                   'category', 
                   'image',
                  'description',
                  'starting_bid'
                  )
        
        widgets = {
            'title': forms.TextInput(attrs={'class': "form-control"}),
            'category': forms.Select(attrs={'class': "form-control"}),
            'image': forms.TextInput(attrs={'class': "form-control", "placeholder": "Insert image urls"}),
            'starting_bid': forms.NumberInput(attrs={"class": "form-control", "min":1, "placeholder": "In USD"}),
            'description': forms.Textarea(attrs={'class': "form-control"})
        }

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = (
            'bid',
        )

        widgets = {
            'bid': forms.NumberInput(attrs={"class": "form-control", "min":1})
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("comment", )

        widgets = {
            "comment": forms.Textarea(attrs={"class": "form-control"})
        }
