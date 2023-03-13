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
from xgboost import XGBRegressor
import random

def train_model():
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(curr_dir, "data/")
    root_dir = os.path.dirname(os.path.dirname(curr_dir))
    location_file = "custom_export.json"
    output_path = os.path.join(data_dir, "xgboost_model.json")
    
    location_data = read_file_in_dir(root_dir, location_file)
    user_data = get_user_ratings()
    
    id_per_loc = {}
    loc_per_id = {}
    id = 0
    for loc_dict in location_data:
        loc_key = loc_dict["pk"]
        id_per_loc[loc_key] = id
        loc_per_id[id] = loc_key
        id += 1
    
    
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
    id = 0
    for (user_id, _) in user_data.items():
        int_id_per_user_id[user_id] = id
        user_id_per_int_id[id] = user_id
        id += 1
    
    user_onehots = one_hot_encoding(list(int_id_per_user_id.values()))
    loc_onehots = one_hot_encoding(list(range(num_locations)))
    
    features = []
    labels = []
    for (user_id, ratings_list) in user_data.items():
        for (loc_key, rating) in ratings_list:
            features.append(data_per_location[loc_key] + loc_onehots[id_per_loc[loc_key]] + user_onehots[int_id_per_user_id[user_id]])
            labels.append(rating)
            
    features = np.array(features, dtype=float)
    labels = np.array(labels, dtype=float)
    
    train_features, test_features, train_labels, test_labels = train_test_split(features, labels, test_size = 0.1)
    
    xgb_model = XGBRegressor(reg_lambda = 0.01, objective='reg:squarederror').fit(train_features, train_labels)
    
    xgb_model.save_model(output_path)

if __name__ == "__main__":
    train_model()
