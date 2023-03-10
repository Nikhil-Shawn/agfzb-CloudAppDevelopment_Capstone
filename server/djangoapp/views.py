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
        context = {}
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/80dba8ac-9699-4879-a3ff-49b1c42351e5/dealership-package/get-dealership.json"
        # Get dealers from the URL
        context["dealers"] = get_dealers_from_cf(url)
        return render(request,'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id,dealer_name):
    if request.method == "GET":
        context = {}        
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/69d2c467-206c-4606-b559-fa18d561d7e4/dealership-package/get-review?id=1"
        # Get dealers from the URL
        reviews = get_dealer_reviews_from_cf(url)
       # Get dealers from the URL
        context['reviews'] = get_dealer_by_id(url,dealer_id)
        context['dealerid'] = dealer_id
        context['dealer'] = dealer_name
        return render(request,'djangoapp/dealer_details.html', context)


# Create a `add_review` view to submit a review
def add_review(request, dealer_id, dealer_name):
    if request.method == "GET":
        context = {}  
        context['dealerid'] = dealer_id
        context['dealer'] = dealer_name
        cars = CarModel.objects.filter(dealer_id=int(dealer_id)).all()
        context['cars'] = cars
        return render(request, 'djangoapp/add_review.html',context)
    if request.method == "POST" and request.user.is_authenticated:
        car = CarModel.objects.get(pk=int(request.POST['car']))
        json_payload = {
"review": 
    {
        "id": 1117,
        "name": request.user.username,
        "dealership": dealer_id,
        "review": request.POST['content'],
        "purchase": False,
        "another": "field",
         'purchase': bool(request.POST.get('purchase',False)),
            'car_make': car.car_make.name,
            'car_model': car.name,
            'car_year': car.year.strftime("%Y"),
            'purchase_date': datetime.strptime(request.POST['purchasedate'], "%m/%d/%Y").isoformat()
    }
}
        url= "https://us-south.functions.appdomain.cloud/api/v1/web/08c5912a-d3c3-4838-9ab3-5be482070298/dealership-package/post-review"
        post_request(url=url, json_payload=json_payload)
        
        return redirect("djangoapp:dealer_details", dealer_id=dealer_id, dealer_name=dealer_name)
    else:
        return HttpResponse({"message":"Forbidden"})