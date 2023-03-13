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
from xgboost import XGBRegressor
import random


def train_model():
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.join(curr_dir, "data/")
    location_file = "export_dataframe.json"
    user_file = "user_ratings.json"
    output_file = os.path.join(root_dir, "xgboost_model.json")
    
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
    labels = []
    for (user_id, ratings_list) in user_data.items():
        for (loc_id, rating) in ratings_list:
            features.append(data_per_location[loc_id] + loc_onehots[loc_id] + user_onehots[int_id_per_user_id[user_id]])
            labels.append(rating)
            
    features = np.array(features, dtype=float)
    labels = np.array(labels, dtype=float)
    
    train_features, test_features, train_labels, test_labels = train_test_split(features, labels, test_size = 0.1)
    
    xgb_model = XGBRegressor(reg_lambda = 0.01, objective='reg:squarederror').fit(train_features, train_labels)
    
    xgb_model.save_model(output_file)

if __name__ == "__main__":
    train_model()
