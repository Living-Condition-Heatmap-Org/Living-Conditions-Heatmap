import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_DIR)
sys.path.append(os.path.dirname(os.path.dirname(SCRIPT_DIR)))

from rate.utils.rating import get_user_ratings
from file_utils import *
from math_utils import *
import numpy as np
import itertools
from collections import defaultdict
from sklearn.model_selection import train_test_split
import xgboost as xgb
import random

def calculate_recommendations(user_id_input):
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(curr_dir, "data/")
    root_dir = os.path.dirname(os.path.dirname(curr_dir))
    location_file = "custom_export.json"
    model_file = os.path.join(data_dir, "xgboost_model.json")
    
    xgb_model = xgb.Booster()
    xgb_model.load_model(model_file)
        
    location_data = read_file_in_dir(root_dir, location_file)
    user_data = get_user_ratings()
    
    id_per_loc = {}
    loc_per_id = {}
    for id, loc_dict in enumerate(location_data):
        loc_key = loc_dict["pk"]
        id_per_loc[loc_key] = id
        loc_per_id[id] = loc_key
        
    data_per_location = {}
    feature_list = ["walk_score", "bike_score", "transit_score", "sound_score", "grocery_dist", "school_dist", "transit_dist"]
    for loc_dict in location_data:
        feature = []
        for feat in feature_list:
            #val = loc_dict["fields"][feat]
            feature.append(loc_dict["fields"][feat])
        loc_key = loc_dict["pk"]
        data_per_location[loc_key] = feature
    
    num_users = len(user_data)
    num_locations = len(data_per_location)
    
    int_id_per_user_id = {}
    user_id_per_int_id = {}
    for id, (user_id, _) in enumerate(user_data.items()):
        int_id_per_user_id[user_id] = id
        user_id_per_int_id[id] = user_id
    print(int_id_per_user_id)
    
    user_onehots = one_hot_encoding(list(int_id_per_user_id.values()))
    loc_onehots = one_hot_encoding(list(range(num_locations)))
    
    features = []
    for loc_id in range(num_locations):
        loc_key = loc_per_id[loc_id]
        features.append(data_per_location[loc_key] + loc_onehots[id_per_loc[loc_key]] + user_onehots[int_id_per_user_id[user_id_input]])
    
    rec_list = xgb_model.predict(xgb.DMatrix(features))
    rec_dict = {}
    for id, rec in enumerate(rec_list):
        rec_dict[loc_per_id[id]] = rec
        
    return rec_dict
