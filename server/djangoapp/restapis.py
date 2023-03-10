import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
import os
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    print("json data {} ".format(json_data))
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url,json_payload, **kwargs):
    print(kwargs)
    print("POST from {} ".format(url))
    try:
        response = requests.post(url,params=kwargs,json=json_payload)
        print(response.text, "hello")
        return json.loads(response.text)
    except Exception as e:
        print(e)
        return

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
'''
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)
    return results
'''
def get_dealers_from_cf(url, **kwargs):
    results = []
    json_result = get_request(url)
    if json_result:
        dealers = json_result["rows"]

        for dealer in dealers:
            dealer_doc = dealer["doc"]
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)
    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_by_id(url, dealerId):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url,id=dealerId)
    print(json_result)
    if json_result:
        # Get the row list in JSON as reviews
        reviews = json_result["data"]["docs"]
        # For each review object
        for review in reviews:
            # Get its content in `doc` object
            # dealer_doc = dealer["doc"]
            # Create a DealerReview object with values in `doc` object
            review_obj = DealerReview(dealership=review["dealership"], review=review["review"], car_make=review["car_make"],
                                   car_model=review["car_model"], car_year=review["car_year"], name=review["name"],
                                   purchase=review["purchase"],
                                   purchase_date=review["purchase_date"], id=review["id"],
                                   sentiment = analyze_review_sentiments(review["review"])
                                   )                                   
            results.append(review_obj)

    return results
    
    # Call get_request with a URL parameter
    json_result = get_request(url,st=state)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["_id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def get_dealer_reviews_from_cf(url):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    print(json_result)
    if json_result:
        # Get the row list in JSON as reviews
        reviews = json_result["data"]["docs"]
        # For each review object
        for review in reviews:
            # Get its content in `doc` object
            # dealer_doc = dealer["doc"]
            # Create a DealerReview object with values in `doc` object
            review_obj = DealerReview(dealership=review["dealership"], review=review["review"], car_make=review["car_make"],
                                   car_model=review["car_model"], car_year=review["car_year"], name=review["name"],
                                   purchase=review["purchase"],
                                   purchase_date=review["purchase_date"], id=review["id"],
                                   sentiment = analyze_review_sentiments(review["review"]))                                                                                  
                                       
            results.append(review_obj)

    return results

def analyze_review_sentiments(review):
    url='https://api.us-east.natural-language-understanding.watson.cloud.ibm.com/instances/95aae7c8-2182-4fd6-aa49-5fb6085d70ba'
    text=review    
    api_key='n5zMDUwUSQJOLPoS5JkBb8X2lRSsQKnfGAm9gKwjxKoE'
    features={"sentiment":{}}    
    version='2020-08-01'
    return_analyzed_text=True

    authenticator = IAMAuthenticator(api_key)
    natural_language_understanding = NaturalLanguageUnderstandingV1(
    version=version,
    authenticator=authenticator
    )
    natural_language_understanding.set_service_url(url)
    return natural_language_understanding.analyze(text=text,return_analyzed_text=return_analyzed_text, features=features,language='en').get_result()