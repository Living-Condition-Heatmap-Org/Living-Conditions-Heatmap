import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_DIR)
sys.path.append(os.path.dirname(os.path.dirname(SCRIPT_DIR)))

from rate.utils.rating import get_user_ratings
from file_utils import *
from math_utils import *
import numpy as np
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from processing import *
import scipy
    
'''
get_train_data
---------------------------
Takes in location data and user data and constructs the feature and label matrices for use in training
input -
    location_data: list of dictionaries with the key "pk" for the location key
    user_data: dictionary where keys are the keys of users
    data_dir: string for the directory path to load mappings from
output -
    features: scipy sparse matrix of feature data, each row corresponds to a (user, location, rating) interaction
    labels: numpy float array of rating labels per interaction (1-5)
'''
def get_train_data(location_data, user_data, data_dir):
    
    # ---------- READ ID MAPPINGS ----------
    id_per_loc = read_file_in_dir_yaml(data_dir, "id_per_loc.yaml")
    id_per_user = read_file_in_dir_yaml(data_dir, "id_per_user.yaml")

    # ---------- PARSE INPUT FILE ----------
    data_per_location = extract_data_per_location(location_data)

    num_users = len(user_data)
    num_locations = len(data_per_location)

    # ---------- BUILD ONE-HOT MAPPINGS ----------
    user_onehots = one_hot_encoding(list(range(num_users)))
    loc_onehots = one_hot_encoding(list(range(num_locations)))

    # ---------- CONSTRUCT FEATURES ----------
    features = []
    labels = []
    for (user_key, ratings_list) in user_data.items():
        for (loc_key, rating) in ratings_list:
            if loc_key not in data_per_location:
                print("Warning: location key not found in location data while training, skipping this interaction")
                continue
            features.append(data_per_location[loc_key] + loc_onehots[id_per_loc[loc_key]] + user_onehots[id_per_user[user_key]])
            labels.append(rating)

    features = scipy.sparse.csr_matrix(features, dtype=float)
    labels = np.array(labels, dtype=float)
    return features, labels
    
'''
train_model
---------------------------
Trains the XGBoost model using location data read from the API-generated file, user data from the Django API call, and saves the model so it can be quickly loaded for predictions.
'''
def train_model():

    # ---------- INITIALIZE PATH NAMES ----------
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(curr_dir, "data/")
    root_dir = os.path.dirname(os.path.dirname(curr_dir))
    location_file = "custom_export.json"
    output_path = os.path.join(data_dir, "xgboost_model.json")
    
    # ---------- LOAD DATA ----------
    location_data = read_file_in_dir(root_dir, location_file)
    user_data = get_user_ratings()
    
    # ---------- SAVE ID MAPPINGS ----------
    preprocess(location_data, user_data, data_dir)
    
    # ---------- BUILD TRAINING DATA MATRICES ----------
    features, labels = get_train_data(location_data, user_data, data_dir)
    
    train_features, test_features, train_labels, test_labels = train_test_split(features, labels, test_size = 0.1)
    
    # ---------- RUN TRAINING LOOP ----------
    xgb_model = XGBRegressor(reg_lambda = 0.01, objective='reg:squarederror').fit(train_features, train_labels)
    
    xgb_model.save_model(output_path)

if __name__ == "__main__":
    train_model()
