import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_DIR)

from file_utils import *
from math_utils import *
import numpy as np
import itertools
from collections import defaultdict
from sklearn.model_selection import train_test_split
import xgboost as xgb
import random

def calculate_recommendations(user_id):
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.join(curr_dir, "data/")
    location_file = "export_dataframe.json"
    user_file = "user_ratings.json"
    model_file = os.path.join(root_dir, "xgboost_model.json")
    
    xgb_model = xgb.Booster()
    xgb_model.load_model(model_file)
        
    location_data = read_file_in_dir(root_dir, location_file)
    user_data = read_file_in_dir(root_dir, user_file)
    
    data_per_location = [[coordinate[0], coordinate[1], grocery[1], school[1], transit[1]] for (coordinate, grocery, school, transit) in location_data['data']]
    
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
    for loc_id in range(num_locations):
        features.append(data_per_location[loc_id] + loc_onehots[loc_id] + user_onehots[int_id_per_user_id[user_id]])
    
    recommendations = xgb_model.predict(xgb.DMatrix(features))
    return recommendations
    
if __name__ == "__main__":
    recommendations = calculate_recommendations("0")
    print(recommendations)
