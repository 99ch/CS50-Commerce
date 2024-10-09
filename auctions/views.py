from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Category, Listing, Comment, Bid

# Affichage des détails d'un article
def listing(request, id):
    listingData = Listing.objects.get(pk=id)
    isListingInWatchlist = request.user in listingData.watchlist.all()
    allComments = Comment.objects.filter(listing=listingData)
    isOwner = request.user.username == listingData.owner.username
    return render(request, "auctions/listing.html", {
        "listing": listingData,
        "isListingInWatchlist": isListingInWatchlist,
        "allComments": allComments,
        "isOwner": isOwner
    })


def closeAuction(request, id):
    listingData = Listing.objects.get(pk=id)
    listingData.isActive = False
    listingData.save()
    isOwner = request.user.username == listingData.owner.username
    isListingInWatchlist = request.user in listingData.watchlist.all()
    allComments = Comment.objects.filter(listing=listingData)

    return render(request, "auctions/listing.html",{
        "listing":listingData,
        "isListingInWatchlist":isListingInWatchlist,
        "allComments":allComments,
        "isOwner":isOwner,
        "update": True,
        "message":"Your auction is closed"
        })

def watchlist(request):
    currentUser = request.user
    listings = currentUser.listingWatchlist.all()
    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })

def addWatchlist(request, id):
    listingData = Listing.objects.get(pk=id)
    currentUser = request.user
    listingData.watchlist.add(currentUser)
    return HttpResponseRedirect(reverse("listing", args=(id,)))

def removeWatchlist(request, id):
    listingData = Listing.objects.get(pk=id)
    currentUser = request.user
    listingData.watchlist.remove(currentUser)
    return HttpResponseRedirect(reverse("listing", args=(id,)))

# Ajout d'un commentaire
def addComment(request, id):
    currentUser = request.user
    listingData = Listing.objects.get(pk=id)
    message = request.POST['newComment']

    newComment = Comment(
        author=currentUser,
        listing=listingData,
        message=message
    )
    newComment.save()
    return HttpResponseRedirect(reverse("listing", args=(id,)))

# Page d'accueil avec affichage des enchères actives
def index(request):
    activeListing = Listing.objects.filter(isActive=True)
    allCategories = Category.objects.all()
    return render(request, "auctions/index.html", {
        "listings": activeListing,
        "categories": allCategories,
    })

# Affichage des articles en fonction de la catégorie
def displayCategory(request):
    if request.method == "POST":
        categoryFromForm = request.POST['category']
        category = Category.objects.get(categoryName=categoryFromForm)
        activeListings = Listing.objects.filter(isActive=True, category=category)
        allCategories = Category.objects.all()
        return render(request, "auctions/index.html", {
            "listings": activeListings,
            "categories": allCategories,
        })

# Ajout d'une enchère
def addBid(request, id):
    newBid = int(request.POST['newBid'])
    listingData = Listing.objects.get(pk=id)
    isListingInWatchlist = request.user in listingData.watchlist.all()
    allComments = Comment.objects.filter(listing=listingData)
    isOwner = request.user.username == listingData.owner.username

    # Vérification si l'enchère est supérieure à la dernière ou au prix de départ
    current_price = listingData.price.bid if listingData.price else listingData.starting_price

    if newBid > current_price:
        updateBid = Bid(user=request.user, bid=newBid)
        updateBid.save()

        # Mise à jour du prix du listing
        listingData.price = updateBid
        listingData.save()

        return render(request, "auctions/listing.html", {
            "listing": listingData,
            "message": "Bid placed successfully",
            "update": True,
            "isListingInWatchlist": isListingInWatchlist,
            "isOwner": isOwner,
            "allComments": allComments,
        })
    else:
        return render(request, "auctions/listing.html", {
            "listing": listingData,
            "message": "Bid must be higher than the current price",
            "update": False,
            "isListingInWatchlist": isListingInWatchlist,
            "isOwner": isOwner,
            "allComments": allComments,
        })

# Création d'une nouvelle enchère

def createListing(request):
    if request.method == "GET":
        allCategories = Category.objects.all()
        return render(request, "auctions/create.html", {
            "categories": allCategories
        })
    else:
        # Récupération des données du formulaire
        title = request.POST["title"]
        description = request.POST["description"]
        imageurl = request.POST["imageurl"]
        starting_price = request.POST["starting_price"]
        category = request.POST["category"]

        # Récupération de la catégorie sélectionnée
        categoryData = Category.objects.get(categoryName=category)

        # Récupération de l'utilisateur actuel
        currentUser = request.user

        # Création de la nouvelle annonce (Listing)
        newListing = Listing(
            title=title,
            description=description,
            imageUrl=imageurl,
            starting_price=int(starting_price),
            category=categoryData,
            owner=currentUser,
            isActive=True
        )
        newListing.save()  # Enregistrer le Listing avant de créer le Bid

        # Création d'un objet Bid associé au Listing
        bid = Bid(bid=int(starting_price), user=currentUser)
        bid.save()

        # Redirection vers la page d'accueil
        return HttpResponseRedirect(reverse(index))

#Authentification
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
