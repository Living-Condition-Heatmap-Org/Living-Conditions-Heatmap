# Create your models here.
from django.db import models

# Create your models here.

def validate_rate(score):
    return score in [0, 1, 2, 3, 4, 5]

class Rating(models.Model):
    user_key = models.TextField() # users' email
    lat_lng_key = models.PositiveBigIntegerField()
    rate = models.PositiveSmallIntegerField(validators=[validate_rate])
