from django.core.validators import RegexValidator
from django.db import models

# Create your models here.

# (+/-)XX.xxxx (+/-)YYY.yyyy
# Latitude -> [-90.0000, +90.0000]
# Longitude -> [-180.0000, +180.0000]
LAT_FORMAT = '[01](900000|[0-8][0-9]{5})'
LNG_FORMAT = '[01](1800000|1[0-7][0-9]{5}|0[0-9]{6})'
LAT_LNG_FORMAT = '1' + LAT_FORMAT + LNG_FORMAT

def validate_ws_score(score):
    return 0 <= score <= 100

def validate_hl_score(score):
    return 50 <= score <= 100

class Location(models.Model):
    lat_lng_key = models.PositiveBigIntegerField(primary_key=True, validators=[RegexValidator(LAT_LNG_FORMAT)])
    walk_score = models.PositiveSmallIntegerField(validators=[validate_ws_score], null=True)
    bike_score = models.PositiveSmallIntegerField(validators=[validate_ws_score], null=True)
    transit_score = models.PositiveSmallIntegerField(validators=[validate_ws_score], null=True)
    sound_score = models.PositiveSmallIntegerField(validators=[validate_hl_score], null=True)
    grocery_dist = models.FloatField()
    school_dist = models.FloatField()
    transit_dist = models.FloatField()