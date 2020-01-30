def check_distance_is_digit(distance):
    if not distance.isdigit():
        api_errors.add_error('distance', 'cela doit etre un nombre')
        raise api_errors

def check_latitude_is_defined(args):
    if 'latitude' not in args:
        api_errors.add_error('latitude', 'la latitude doit être précisée')

def check_longitude_is_defined(args):
    if 'longitude' not in args:
        api_errors.add_error('longitude', 'la longitude doit être précisée')
