import os
import json
# transfer the latitude and longitude to the str
# Digit 0 is a dummy digit to allow for leading zero(s).
# Digit 1 is a sign digit for latitude; 0 = +; 1 = -.
# Digits 2 and 3 are the integer part of the latitude
# Digits 4-7 are the fractional part of the latitude
# Digit 8 is a sign digit for longitude; 0 = +; 1 = -.
# Digits 9-11 are the integer part of the longitude
# Digits 12-15 are the fractional part of the longitude
# e.g. (lat, lon) = (+45.1234, -123.4567) -> 1045123411234567 (1_0_45_1234_1_123_4567)
def format_location(latitude, longitude):
    result = "1"
    if latitude >= 0:
        result += "0"
    else:
        result += "1"
    latitude = abs(latitude)
    result += str(int(latitude))
    result += str(round(latitude - int(latitude), 4))[2:]
    if longitude >= 0:
        result += "0"
    else:
        result += "1"
    longitude = abs(longitude)
    result += str(int(longitude))
    result += str(round(longitude - int(longitude), 4))[2:]
    return int(result)

def unformat_location(location_int):
    lat_lng_key = str(location_int)
    lat = int(lat_lng_key[2:8]) / 10000
    if lat_lng_key[1] == "1":
        lat = -lat
    lng = int(lat_lng_key[9:]) / 10000
    if lat_lng_key[8] == "1":
        lng = -lng
    return (lat, lng)

def find_nearest_location(location_int):
    lat, lng = unformat_location(location_int)
    min_dist = float("INF")
    nearest_lat = None
    nearest_lng = None
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(os.path.dirname(curr_dir))
    location_file = "custom_export.json"
    location_file = os.path.join(root_dir, location_file)
    with open(location_file) as json_file:
        locations = json.load(json_file)
        print(locations)
        for location in locations:
            curr_location_int = location["pk"]
            curr_lat, curr_lng = unformat_location(curr_location_int)
            dist = (curr_lat - lat) * (curr_lat - lat) + (curr_lng - lng) * (curr_lng - lng)
            if dist < min_dist:
                min_dist = dist
                nearest_lat = curr_lat
                nearest_lng = curr_lng
    return format_location(nearest_lat, nearest_lng)
    

if __name__ == "__main__":
    print(format_location(+45.1234, -123.4567))