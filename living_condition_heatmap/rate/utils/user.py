import requests
from django.conf import settings


def get_user(request):
    token = request.META.get(settings.AUTHORIZATION_HEADER).split(" ")[1]
    url = settings.AUTHENTICATION_URL + token
    r = requests.get(url)
    user_key=r.json()["email"]
    return user_key