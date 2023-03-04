from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
from .restapis import *

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    return render(request, 'djangoapp/contact.html', context)



# Create a `login_request` view to handle sign in request
# def login_request(request):
# ...
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return render(request, 'djangoapp/index.html', context)
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/login.html', context)
        

# Create a `logout_request` view to handle sign out request
# def logout_request(request):
def logout_request(request):
    logout(request)
    return redirect('djangoapp:loggedout')

def loggedout(request):
    context = {}
    return render(request, 'djangoapp/loggedout.html', context)

# Create a `registration_request` view to handle sign up request
# def registration_request(request):
# ...
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        # Get user information from request.POST
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            # Login the user and redirect to course list page
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        url = "your-cloud-function-domain/dealerships/dealer-get"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        return HttpResponse(dealer_names)

def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = "you review url"
        reviews = get_dealer_reviews_from_cf(url, dealerId=dealer_id)
        #print(reviews)
        context['dealer_id'] = dealer_id
        temp = []
        for i in reviews:
            if i.dealership == dealer_id:
                print(i.name)
                temp.append(i)
        context['reviews'] = temp
        return render(request, 'djangoapp/dealer_details.html', context)
        #return HttpResponse(reviews[dealer_id].sentiment)       
# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...



# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...
def add_review(request, dealer_id):
    context = {}
    context["dealer_id"] = dealer_id
    review = dict()
    if request.method == "GET":
        return render(request, 'djangoapp/add_review.html', context)
    
    if request.method == "POST":
            if request.user.is_authenticated:
                review['review'] = {}
                review['review']["time"] = datetime.utcnow().isoformat()
                review['review']["dealership"] = dealer_id
                review['review']["review"] = request.POST["review"]
                review['review']["purchase"] = request.POST["purchase"]
                review['review']['purchase_date'] = request.POST['purchase_date'] or "Nil"
                review['review']["car_model"] = request.POST["car_model"] or "Nil"
                review['review']["car_make"] = request.POST["car_make"] or "Nil"
                review['review']["car_year"] = request.POST["car_year"] or "Nil"

                userr = User.objects.get(username=request.user)
                review['review']['id'] = userr.id
                review['review']["name"] = userr.first_name + " " + userr.last_name

                url = "https://8328ba60.us-south.apigw.appdomain.cloud/api/review/"

                #json_payload = {}
                #json_payload['review'] = review

                post_request(url, review, dealerId=dealer_id)
            
                return redirect('djangoapp:dealer_details', dealer_id=dealer_id)
