import numpy as np

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
