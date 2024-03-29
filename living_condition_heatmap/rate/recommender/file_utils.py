import os
import json
import yaml

def read_file_in_dir_yaml(root_dir, file_name):
    path = os.path.join(root_dir, file_name)
    if os.path.isfile(path):
        with open(path) as file:
            data = yaml.safe_load(file)
        return data
    else:
        raise Exception("file doesn't exist: ", path)

def write_to_file_in_dir_yaml(root_dir, file_name, data):
    path = os.path.join(root_dir, file_name)
    with open(path, "w") as file:
        yaml.dump(data, file)
    

def read_file(path):
    if os.path.isfile(path):
        with open(path) as json_file:
            data = json.load(json_file)
        return data
    else:
        raise Exception("file doesn't exist: ", path)


def read_file_in_dir(root_dir, file_name):
    path = os.path.join(root_dir, file_name)
    return read_file(path)


def write_to_file(path, data):
    with open(path, "w") as outfile:
        json.dump(data, outfile)


def write_to_file_in_dir(root_dir, file_name, data):
    path = os.path.join(root_dir, file_name)
    write_to_file(path, data)


def log_to_file(path, log_str):
    with open(path, 'a') as f:
        f.write(log_str + '\n')


def log_to_file_in_dir(root_dir, file_name, log_str):
    path = os.path.join(root_dir, file_name)
    log_to_file(path, log_str)

