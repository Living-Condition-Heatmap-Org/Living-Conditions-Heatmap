import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_DIR)
sys.path.append(os.path.dirname(os.path.dirname(SCRIPT_DIR)))

from rate.utils.rating import get_user_ratings
from file_utils import *

'''
map_locations
---------------------------
Generates unique integer ids for each location and returns the mapping in both directions in dictionaries.
input -
    location_data: list of dictionaries with the key "pk" for the location key
output -
    id_per_loc: dict mapping from location key to integer id
    loc_per_id: dict mapping from integer id to location key
'''
def map_locations(location_data):
    id_per_loc = {}
    loc_per_id = {}
    for id, loc_dict in enumerate(location_data):
        loc_key = loc_dict["pk"]
        id_per_loc[loc_key] = id
        loc_per_id[id] = loc_key
    return id_per_loc, loc_per_id

'''
map_users
---------------------------
Generates unique integer ids for each user and returns the mapping in both directions in dictionaries.
input -
    user_data: dictionary where keys are the keys of users
output -
    id_per_user: dict mapping from user key to integer id
    user_per_id: dict mapping from integer id to user key
'''
def map_users(user_data):
    id_per_user = {}
    user_per_id = {}
    for id, user_key in enumerate(user_data.keys()):
        id_per_user[user_key] = id
        user_per_id[id] = user_key
    return id_per_user, user_per_id

'''
preprocess
---------------------------
Preprocesses the location data and user data by obtaining unique ids for both locations and users for use in the recommender.
The mappings are saved in files so both the training method and sampling method can use the same mappings.
input -
    location_data: list of dictionaries with the key "pk" for the location key
    user_data: dictionary where keys are the keys of users
    data_dir: string for the directory path to save mappings in
'''
def preprocess(location_data, user_data, data_dir):
    id_per_loc, loc_per_id = map_locations(location_data)
    id_per_user, user_per_id = map_users(user_data)

    write_to_file_in_dir_yaml(data_dir, "id_per_loc.yaml", id_per_loc)
    write_to_file_in_dir_yaml(data_dir, "loc_per_id.yaml", loc_per_id)
    write_to_file_in_dir_yaml(data_dir, "id_per_user.yaml", id_per_user)
    write_to_file_in_dir_yaml(data_dir, "user_per_id.yaml", user_per_id)

'''
extract_data_per_location
---------------------------
Parses the location data for relevant features and formats the data into a useable dictionary
input -
    location_data: list of dictionaries with the key "pk" for the location key and key "fields" containing a dictionary of features
output -
    data_per_location: dict mapping from location key to features list
'''
def extract_data_per_location(location_data):
    data_per_location = {}
    feature_list = ["walk_score", "bike_score", "transit_score", "sound_score", "grocery_dist", "school_dist", "transit_dist"]
    for loc_dict in location_data:
        feature = []
        for feat in feature_list:
            feature.append(loc_dict["fields"][feat])
        loc_key = loc_dict["pk"]
        data_per_location[loc_key] = feature
    return data_per_location
    
