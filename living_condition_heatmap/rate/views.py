from django.shortcuts import render

from django.http import HttpResponse
from rate.models import Rating
from .utils.location import format_location
import json
    
 
def get_rating(request):
    # todo: jwt token authorization for user key
    ratings = Rating.objects.filter(user_key=100)
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
    data = json.loads(request.body)
    latitude = data['latitude']
    longitude = data['longitude']
    rating = int(data['score'])
    location_int = format_location(latitude, longitude)
    try:
        # todo: jwt token authorization for user key
        r = Rating(user_key=100, lat_lng_key=location_int, rate=rating)
        r.save()
        return HttpResponse(json.dumps({"code": 0}))
    except Exception as err:
        print(err)
        return HttpResponse(json.dumps({"code": 1}))
