import numpy as np

'''
cosine_similarity
---------------------------
Takes two numpy arrays of real values and computes the cosine similarity between them
Cosine Similarity(a, b) = (a.b) / (2-norm(a) * 2-norm(b))
'''
def cosine_similarity(a: np.ndarray, b: np.ndarray):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

'''
mse
---------------------------
Takes two vectors of real numbers of equal length and returns the mean-squared error
input -
    y: vector of real numbers
    y_pred: vector of real numbers
output -
    mse_err: the mean-squared error between y and y_pred
'''
def mse(y, y_pred):
    mse_err = np.mean((np.array(y) - np.array(y_pred))**2)
    return mse_err
  
'''
one_hot_encoding
---------------------------
Takes a list of integers and optional number of classes and outputs the corresponding matrix where each row is the one-hot encoding of the entry in the input list at that index
input -
    val_list: list of integers to one-hot encode
    num_classes: the number of classes to use, defaults to 1 + max value. ensures the matrix is the correct size if the examples are not full
output -
    one_hots: 2d list which is val_list except each entry is replaced by the one-hot encoding vector of itself
'''
def one_hot_encoding(val_list, num_classes = None):
    if num_classes is None:
        num_classes = max(val_list) + 1
    identity = np.eye(num_classes)
    one_hots = identity[val_list].astype(int)
    one_hots = one_hots.tolist()
    return one_hots
