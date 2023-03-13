import json
import requests
import sys
import time
from tqdm import tqdm

wsapikey = ''  # WalkScore API key; get one from https://www.walkscore.com/professional/api.php
hlapikey = ''  # HowLoud API key; get one from https://howloud.com/developers

ws_url = 'https://api.walkscore.com/score'
hl_url = 'https://api.howloud.com/score'


def get_ws_scores(lat, lon) -> tuple[int,int,int]:
    """Queries the WalkScore API for the given latitude and longitude.

    Args:
        lat (float): the latitude of the location
        lon (float): the longitude of the location

    Returns:
        tuple[int,int,int]: a tuple of 0-100 ints (walk_score, bike_score, transit_score)
    """    
    ws_params = { 
        'format': 'json',
        'lat': lat, 
        'lon': lon, 
        'transit': 1, 
        'bike': 1,
        'wsapikey': wsapikey
    }
    r = requests.get(ws_url, params=ws_params).json()
    
    # sometimes, walkscore API returns a response without 'bike' or 'transit' keys (their fault, not ours)
    retry_count = 0
    while 'bike' not in r.keys() or 'transit' not in r.keys() and retry_count < 5:
        retry_count += 1
        print('Walkscore API error! Waiting for 5s.')
        print(f"{'bike' in r.keys()=}; {'transit' in r.keys()=}; {r=}")
        time.sleep(5)
        r = requests.get(ws_url, params=ws_params).json()
    if retry_count == 5:
        print('Walkscore API error! Skipping this location.')

    walk_score = r['walkscore'] if 'walkscore' in r else None
    bike_score = r['bike']['score'] if 'bike' in r and 'score' in r['bike'] else None
    transit_score = r['transit']['score'] if 'transit' in r and 'score' in r['transit'] else None

    return (walk_score, bike_score, transit_score)


def get_hl_score(lat, lon):
    """Queries the HowLoud API for the given latitude and longitude.

    Args:
        lat (float): the latitude of the location
        lon (float): the longitude of the location

    Returns:
        int: the sound score (50-100), or None if no score is available
    """    
    hl_params = { 'lat': lat, 'lng': lon } 
    hl_headers = { 'x-api-key': hlapikey }
    r = requests.get(hl_url, params=hl_params, headers=hl_headers).json()

    # if we hit the HowLoud API rate limit, wait 10s and try again up to 5 times
    retry_count = 0
    while 'message' in r and r['message'] == 'Too Many Requests' and retry_count < 5:
        print(r['message'] + '! Waiting for 10s.')
        time.sleep(10 * (retry_count + 1))
        retry_count += 1
        r = requests.get(hl_url, params=hl_params, headers=hl_headers).json()
    if retry_count == 5:
        print('HowLoud API error! Skipping this location.')
        return None

    # try to avoid hitting the rate limit by waiting 1s between requests
    time.sleep(1)
    return r['result'][0]['score'] if r['status'] != 'ZERO_RESULTS' else None


def decode_lat_lng_key(key):
    """Decodes a location key into a latitude and longitude. The location key is a 16-digit integer
    such that digit 0 is 1 (dummy digit), digit 1 is 0 or 1 (sign of latitude), digits 2-3 are the
    latitude whole number, digits 4-7 are the latitude fractional number, digit 8 is 0 or 1 (sign of
    longitude), and digits 9-12 are the longitude whole number and digits 13-15 are the longitude 
    fractional number. For example, the location key 1047608511223295 corresponds to the latitude
    47.6085 and longitude -122.3295.

    Args:
        key (int): the location key

    Returns:
        tuple[float,float]: the latitude and longitude
    """

    # 0th digit is 1, allows leading zero for sign digit
    # 1 0 47 6085 1 122 3295
    lng_sign = -1 if int(str(key)[-8]) == 1 else 1
    lng_whole = int(str(key)[-7:-4])
    lng_frac = int(str(key)[-4:]) / 10000
    lng = lng_sign * (lng_whole + lng_frac)

    lat_sign = -1 if int(str(key)[1]) == 1 else 1
    lat_whole = int(str(key)[2:4])
    lat_frac = int(str(key)[4:8]) / 10000
    lat = lat_sign * (lat_whole + lat_frac)

    return lat, lng


def encode_lat_lng(lat_lng):
    """Encodes a latitude and longitude tuple into a location key. The location key is a 16-digit
    integer such that digit 0 is 1 (dummy digit), digit 1 is 0 or 1 (sign of latitude), digits 2-3
    are the latitude whole number, digits 4-7 are the latitude fractional number, digit 8 is 0 or 1
    (sign of longitude), and digits 9-12 are the longitude whole number and digits 13-15 are the
    longitude fractional number. For example, the location key 1047608511223295 corresponds to the
    latitude 47.6085 and longitude -122.3295.

    Args:
        lat_lng (tuple[int]): a tuple containing the latitude and longitude to encode

    Returns:
        int: the encoded location key
    """
    lat, lng = lat_lng
    enc_lat, enc_lng = abs(int(round(lat, 4) * 10000)), abs(int(round(lng, 4) * 10000))
    sign_lat, sign_lng = lat < 0, lng < 0
    return 1000000000000000 + \
        (100000000000000 if sign_lat else 0) + enc_lat * 100000000 + \
        (10000000 if sign_lng else 0) + enc_lng


def load_chris_data(path):
    """Loads Chris's JSON file.

    Args:
        path (str): the path to Chris's JSON file

    Returns:
        list: a list of tuples containing a latitude-longitude pair and the names and normalized distances
            of the closest grocery stores, schools, and transit stops
    """
    with open(path) as f:
        data = json.load(f)['data']
    return data


def dump_table(chris_path):
    """Creates and dumps the location table to a JSON file by querying the Walkscore and HowLoud APIs
    for each location in Chris's JSON file. The JSON file is formatted for use with the Django
    fixture system.

    Args:
        chris_path (str): the path to Chris's JSON file
    """
    dist_data = load_chris_data(chris_path)
    coords = [d[0] for d in dist_data]

    print("Getting walk scores...")
    ws_scores = [get_ws_scores(lat, lng) for lat, lng in tqdm(coords)]
    print("Getting sound scores...")
    hl_scores = [get_hl_score(lat, lng) for lat, lng in tqdm(coords)]

    db_json = []
    for i, (lat, lng) in enumerate(coords):
        db_json.append({
            "model": "update_db.location",
            "pk": encode_lat_lng((lat, lng)),
            "fields": {
                "walk_score": ws_scores[i][0],
                "bike_score": ws_scores[i][1],
                "transit_score": ws_scores[i][2],
                "sound_score": hl_scores[i],
                "grocery_dist": dist_data[i][1],
                "school_dist": dist_data[i][3],
                "transit_dist": dist_data[i][5]
            }
        })
    with open('custom_export.json', 'w') as f:
        json.dump(db_json, f)


def get_api_keys(env_path):
    """Gets the Walk Score and HowLoud API keys from the environment file.

    Args:
        env_path (str): the path to the environment file
    """
    with open(env_path) as f:
        global wsapikey
        global hlapikey
        wsapikey = f.readline().strip().split('=')[1]
        hlapikey = f.readline().strip().split('=')[1]


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python populate_json.py <chris_data_path> <env_path>')
        exit(1)
    get_api_keys(sys.argv[2])
    dump_table(sys.argv[1])
