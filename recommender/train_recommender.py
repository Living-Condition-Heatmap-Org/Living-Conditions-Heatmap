from file_utils import *
import numpy as np
import itertools
from collections import defaultdict
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
import random

'''
Takes two numpy arrays of real values and computes the cosine similarity between them
Cosine Similarity(a, b) = (a.b) / (2-norm(a) * 2-norm(b))
'''
def cosine_similarity(a: np.ndarray, b: np.ndarray):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def mse(y, y_pred):
  return np.mean((np.array(y) - np.array(y_pred))**2)
  
def one_hot_encoding(val_list, num_classes = None):
    if num_classes is None:
        num_classes = max(val_list) + 1
    identity = np.eye(num_classes)
    one_hots = identity[val_list].astype(int)
    return one_hots.tolist()

if __name__ == "__main__":
    root_dir = "data/"
    location_file = "export_dataframe.json"
    user_file = "user_ratings.json"
    output_file = "recommendations.json"
    
    print(one_hot_encoding([1,2,3]))
    
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
    print(type(data_per_location))
    print(type(loc_onehots))
    print(type(user_onehots))
    for (user_id, ratings_list) in user_data.items():
        for (loc_id, rating) in ratings_list:
            features.append(data_per_location[loc_id] + loc_onehots[loc_id] + user_onehots[int_id_per_user_id[user_id]])
            labels.append(rating)
            
    features = np.array(features, dtype=float)
    labels = np.array(labels, dtype=float)
    
    print(features.shape)
    print(labels.shape)
    
    train_features, test_features, train_labels, test_labels = train_test_split(features, labels, test_size = 0.1)
    
    xgb_model = XGBRegressor(reg_lambda = 0.01, objective='reg:squarederror').fit(train_features, train_labels)
    
    xgb_model.save_model('xgboost_model.json')
    
