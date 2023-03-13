from rate.models import Rating

def get_user_ratings():
    ratings = Rating.objects.all()
    ratings = list(ratings)
    rating_dict = {}
    for rating in ratings:
        user_key = str(rating.user_key)
        if user_key not in rating_dict:
            rating_dict[user_key] = [(rating.lat_lng_key, rating.rate)]
        else:
            rating_dict[user_key].append((rating.lat_lng_key, rating.rate))
    return rating_dict
