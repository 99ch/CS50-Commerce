from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass





#Table category dans la base de données
class Category(models.Model):
    categoryName = models.CharField(max_length=50)

    def __str__(self):
        return self.categoryName




#Table of Bid
class Bid(models.Model):
    bid = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE,blank=True, null=True, related_name="userBid")




#Table Listing dans la base dedonnées
class Listing(models.Model):
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=300)
    imageUrl = models.CharField(max_length=1000)
    price = models.ForeignKey(Bid,on_delete=models.CASCADE,blank=True,null=True, related_name="bidPrice")
    isActive = models.BooleanField(default=True)
    owner = models.ForeignKey(User,on_delete=models.CASCADE,blank=True,null=True,related_name="user")
    category = models.ForeignKey(Category,on_delete=models.CASCADE,blank=True,related_name="category") 
    watchlist = models.ManyToManyField(User, blank=True, null=True, related_name="listingWatchlist")

    def __str__(self):
        return self.title



#Table de commentaire
class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,blank=True, null=True, related_name="userComment")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True, related_name="listing")
    message = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.author} comment on {self.listing}"

