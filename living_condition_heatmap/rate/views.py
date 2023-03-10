from django.shortcuts import render
from django.http import HttpResponse
from rate.models import Rating
from .utils.location import format_location
from .utils.user import get_user
import json
import requests
from django.conf import settings
    
 
def get_rating(request):
    user_key = get_user(request)
    ratings = Rating.objects.filter(user_key=user_key)
    ratings = list(ratings)
    ratings_response = []
    for rating in ratings:
        lat_lng_key = str(rating.lat_lng_key)
        lat = int(lat_lng_key[2:8]) / 10000
        if lat_lng_key[1] == "1":
            lat = -lat
        lng = int(lat_lng_key[9:]) / 10000
        if lat_lng_key[8] == "1":
            lng = -lng
        ratings_response.append({
            "rating": rating.rate,
            "latitude": lat,
            "longitude": lng
        })
    return HttpResponse(ratings_response)


def update_rating(request):
    # CORS preflight request
    # This is necessary only for local env.
    if request.method == 'OPTIONS':
        response = HttpResponse()
        response['Access-Control-Allow-Origin'] = 'http://localhost:8000'
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Allow-Headers'] = "Authorization, Content-Type, Accept, X-CSRFToken"
        response['Access-Control-Allow-Methods'] = "PUT, OPTIONS, HEAD"
        return response

    data = json.loads(request.body)
    latitude = data['latitude']
    longitude = data['longitude']
    rating = int(data['score'])
    location_int = format_location(latitude, longitude)
    try:
        user_key = get_user(request)
        r = Rating(user_key=user_key, lat_lng_key=location_int, rate=rating)
        r.save()
        return HttpResponse(json.dumps({"code": 0}))
    except Exception as err:
        print(err)
        return HttpResponse(json.dumps({"code": 1}))