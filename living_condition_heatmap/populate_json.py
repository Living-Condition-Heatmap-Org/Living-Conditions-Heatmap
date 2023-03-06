import json
import requests
import sys
import time

wsapikey = ''
hlapikey = ''

ws_base_url = 'https://api.walkscore.com/score'
hl_url = 'https://api.howloud.com/score'

def get_ws_scores(lat, lon):
    ws_params = { 
        'format': 'json',
        'lat': lat, 
        'lon': lon, 
        'transit': 1, 
        'bike': 1,
        'wsapikey': wsapikey
    }
    r = requests.get(ws_base_url, params=ws_params).json()
    return r['walkscore'], r['bike']['score'], r['transit']['score']

def get_hl_score(lat, lon):
    hl_params = { 'lat': lat, 'lng': lon } 
    hl_headers = { 'x-api-key': hlapikey }
    r = requests.get(hl_url, params=hl_params, headers=hl_headers).json()
    while 'message' in r and r['message'] == 'Too Many Requests':
        print(r['message'] + '! Waiting for 10s.')
        time.sleep(10)
        r = requests.get(hl_url, params=hl_params, headers=hl_headers).json()
    # print(r)
    return r['result'][0]['score']

def decode_lat_lng_key(key):
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
    lat, lng = lat_lng
    enc_lat, enc_lng = abs(int(round(lat, 4) * 10000)), abs(int(round(lng, 4) * 10000))
    sign_lat, sign_lng = lat < 0, lng < 0
    return 1000000000000000 + \
        (100000000000000 if sign_lat else 0) + enc_lat * 100000000 + \
        (10000000 if sign_lng else 0) + enc_lng

def load_chris_data(path):
    with open(path) as f:
        data = json.load(f)['data']
    return data

def dump_table(chris_path):
    dist_data = load_chris_data(chris_path)
    coords = [d[0] for d in dist_data]

    ws_scores = [get_ws_scores(lat, lng) for lat, lng in coords]
    hl_scores = [get_hl_score(lat, lng) for lat, lng in coords]

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
                "grocery_dist": dist_data[i][1][1],
                "school_dist": dist_data[i][2][1],
                "transit_dist": dist_data[i][3][1]
            }
        })
    with open('custom_export.json', 'w') as f:
        json.dump(db_json, f)

if __name__ == '__main__':
    dump_table(sys.argv[1])
