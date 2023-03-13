from file_utils import *
import random

'''
This file generates a number of ratings of locations per user and saves the results into a .json. The format of the resulting .json is user_id: [location_index, rating] where rating is in [1,2,3,4,5]
'''


if __name__ == "__main__":
    root_dir = "data/"
    input_file_name = "export_dataframe.json"
    output_file_name = "user_ratings.json"
    
    data = read_file_in_dir(root_dir, input_file_name)
    
    ratings_per_user = {}
    
    num_users = 2000
    num_ratings_per_user = 5
    num_locations = len(data['data'])
    assert(num_locations >= num_ratings_per_user)
    
    for user_id in range(num_users):
        sample_locations = random.sample(population=range(num_locations), k=num_ratings_per_user)
        sample_ratings = random.choices(population=range(5), k=num_ratings_per_user)
        ratings_per_user[user_id] = list(zip(sample_locations, sample_ratings))

    write_to_file_in_dir(root_dir, output_file_name, ratings_per_user)
