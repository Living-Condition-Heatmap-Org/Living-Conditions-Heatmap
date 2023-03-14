import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_DIR)
sys.path.append(os.path.dirname(os.path.dirname(SCRIPT_DIR)))

from rate.utils.rating import get_user_ratings
from file_utils import *
from math_utils import *
import numpy as np
import xgboost as xgb
from processing import *
import scipy

'''
get_prediction_data
---------------------------
Takes in location data and one user key and constructs the feature matrix for use in prediction
input -
    location_data: list of dictionaries with the key "pk" for the location key
    user_data: dictionary where keys are the keys of users
    data_dir: string for the directory path to load mappings from
output -
    features: scipy sparse matrix of feature data, each row corresponds to a (user, location) interaction. for given user key and all locations
'''
def get_prediction_data(location_data, user_key, data_dir):
    id_per_loc = read_file_in_dir_yaml(data_dir, "id_per_loc.yaml")
    loc_per_id = read_file_in_dir_yaml(data_dir, "loc_per_id.yaml")
    id_per_user = read_file_in_dir_yaml(data_dir, "id_per_user.yaml")

    data_per_location = extract_data_per_location(location_data)

    num_locations = len(data_per_location)

    user_onehot = one_hot_encoding([id_per_user[user_key]], num_classes = len(id_per_user))[0]
    loc_onehots = one_hot_encoding(list(range(num_locations)))
    
    features = []
    for loc_id in range(num_locations):
        loc_key = loc_per_id[loc_id]
        features.append(data_per_location[loc_key] + loc_onehots[id_per_loc[loc_key]] + user_onehot)
    
    features = scipy.sparse.csr_matrix(features, dtype=float)
    return features

'''
calculate_recommendations
---------------------------
Runs the features for a specific user through a trained XGBoost model which is loaded from file.
input -
    user_key: string key for a given user to obtain recommendations for
output -
    rec_dict: recommendation dictionary mapping location keys to predicted float rating (1-5)
'''
def calculate_recommendations(user_key):
    
    # ---------- INITIALIZE PATH NAMES ----------
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(curr_dir, "data/")
    root_dir = os.path.dirname(os.path.dirname(curr_dir))
    location_file = "custom_export.json"
    model_file = os.path.join(data_dir, "xgboost_model.json")
    
    # ---------- LOAD TRAINED MODEL ----------
    xgb_model = xgb.Booster()
    xgb_model.load_model(model_file)
            
    # ---------- LOAD DATA ----------
    location_data = read_file_in_dir(root_dir, location_file)
    
    # ---------- BUILD FEATURES MATRIX ----------
    features = get_prediction_data(location_data, user_key, data_dir)
        
    # ---------- USE MODEL TO OBTAIN RECOMMENDATIONS ----------
    rec_list = xgb_model.predict(xgb.DMatrix(features))
    
    # ---------- CONVERT TO DICT FOR OUTPUT ----------
    loc_per_id = read_file_in_dir_yaml(data_dir, "loc_per_id.yaml")
    rec_dict = {}
    for id, rec in enumerate(rec_list):
        # clip output to range [1,5] for rating prediction
        rec_dict[loc_per_id[id]] = np.clip(rec, 1, 5)
        
    return rec_dict
