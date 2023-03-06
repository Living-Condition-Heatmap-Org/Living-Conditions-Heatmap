# transfer the latitude and longitude to the str
# Digit 0 is a dummy digit to allow for leading zero(s).
# Digit 1 is a sign digit for latitude; 0 = +; 1 = -.
# Digits 2 and 3 are the integer part of the latitude
# Digits 4-7 are the fractional part of the latitude
# Digit 8 is a sign digit for longitude; 0 = +; 1 = -.
# Digits 9-11 are the integer part of the longitude
# Digits 12-15 are the fractional part of the longitude
# e.g. (lat, lon) = (+45.1234, -123.4567) -> 1045123411234567 (1_0_45_1234_1_123_4567)
def format_location(latitude, longitude):
    result = "1"
    if latitude >= 0:
        result += "0"
    else:
        result += "1"
    latitude = abs(latitude)
    result += str(int(latitude))
    result += str(round(latitude - int(latitude), 4))[2:]
    if longitude >= 0:
        result += "0"
    else:
        result += "1"
    longitude = abs(longitude)
    result += str(int(longitude))
    result += str(round(longitude - int(longitude), 4))[2:]
    return int(result)

if __name__ == "__main__":
    print(format_location(+45.1234, -123.4567))