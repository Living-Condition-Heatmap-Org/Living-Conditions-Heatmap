from .file_utils import *
import numpy as np
import itertools
from collections import defaultdict
from ..utils.rating import get_user_ratings


'''
Takes two numpy arrays of real values and computes the cosine similarity between them
Cosine Similarity(a, b) = (a.b) / (2-norm(a) * 2-norm(b))
'''
def cosine_similarity(a: np.ndarray, b: np.ndarray):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def use_get_user_ratings():
    return get_user_ratings()


if __name__ == "__main__":
    root_dir = "data/"
    location_file = "export_dataframe.json"
    user_file = "user_ratings.json"
    output_file = "recommendations.json"
    
    location_data = read_file_in_dir(root_dir, location_file)
    user_data = read_file_in_dir(root_dir, user_file)
    
    data_per_location = [np.array([grocery[1], school[1], transit[1]]) for (coordinate, grocery, school, transit) in location_data['data']]
    
    num_users = len(user_data)
    num_locations = len(data_per_location)
    
    print("Calculating pairwise similarities...")
    pairwise_similarity = {}
    for ((i,loc_data_i), (j,loc_data_j)) in itertools.product(enumerate(data_per_location), repeat=2):
        if i != j:
            pairwise_similarity[i,j] = cosine_similarity(loc_data_i, loc_data_j)
   
    print("Calculating user-dependent values...")
    output = defaultdict(list)
    num_recommendation_scores = 0
    for user_id, user_ratings in user_data.items():
        rated_loc_ids = [loc_id for (loc_id, rating) in user_ratings]
        other_loc_ids = list(range(num_locations))
        for id in sorted(rated_loc_ids, reverse=True):
            del other_loc_ids[id]
                
        for other_id in other_loc_ids:
            weighted_sims = []
            sum_of_weights = 0
            for (loc_id, rating) in user_ratings:
                weighted_sims.append(rating * pairwise_similarity[other_id, loc_id])
                sum_of_weights += rating
            val = sum(weighted_sims) / sum_of_weights
            output[user_id].append([other_id, val])
            num_recommendation_scores += 1
         
    print("Sorting recommendations...")
    for user_id in output:
        output[user_id].sort(key=lambda l: l[1], reverse=True)
            
    print(f"Found {num_recommendation_scores} total recommendations scores over {num_users} users and {num_locations} locations.")
    write_to_file_in_dir(root_dir, output_file, output)
