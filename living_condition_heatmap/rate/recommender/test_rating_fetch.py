import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(os.path.dirname(SCRIPT_DIR)))

from rate.utils.rating import get_user_ratings

if __name__ == "__main__":
    print(get_user_ratings)
