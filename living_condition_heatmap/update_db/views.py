from django.shortcuts import render

from django.http import HttpResponse
# from rate.models import Rating
from update_db.models import Location
import json
    
 
def get_location_scores(request):
    # todo: jwt token authorization for user key
    locations = Location.objects.all()
    locations = list(locations)
    location_info = []

    for location in locations:
        lat_lng_key = str(location.lat_lng_key)
        lat = int(lat_lng_key[2:8]) / 10000
        if lat_lng_key[1] == "1":
            lat = -lat
        lng = int(lat_lng_key[9:]) / 10000
        if lat_lng_key[8] == "1":
            lng = -lng
        location_info.append({
            "latitude": lat,
            "longitude": lng,
            "walkScore": location.walk_score,
            "bikeScore": location.bike_score,
            "transitScore": location.transit_score,
            "soundScore": location.sound_score,
            "nearestGrocery": location.grocery_dist,
            "nearestSchool": location.school_dist,
            "nearestTransit": location.transit_dist
        })

    return HttpResponse(json.dumps(location_info))

