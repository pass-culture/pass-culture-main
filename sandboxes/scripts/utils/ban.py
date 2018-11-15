import numpy
import requests

from utils.logger import logger
from utils.test_utils import create_offerer

def get_location_from_ban_feature(feature):
    coordinates = feature['geometry']['coordinates']
    properties = feature['properties']

    location_latitude = coordinates[1]
    location_longitude = coordinates[0]

    return {
        "address": properties['name'],
        "city": properties['city'],
        "latitude": location_latitude,
        "longitude": location_longitude,
        "postalCode": properties['postcode']
    }

def get_closest_location_info_with_lat_lon(latitude, longitude):
    url = 'https://api-adresse.data.gouv.fr/reverse/?lon={}&lat={}'.format(longitude,latitude)
    result = requests.get(url)
    obj = result.json()
    if 'features' in obj and obj['features']:
        feature = obj['features'][0]
        location = get_location_from_ban_feature(feature)
        logger.warning("Able to find a reverse address for these coordinates {} {}".format(longitude,latitude))
        return location
    logger.warning("Unable to find a reverse address for these coordinates {} {}".format(longitude,latitude))

def get_surrounding_locations_from_place(
    place,
    lat_lon_radius=0.05,
    number_of_different_lat_lon_points=2,
):
    locations = []
    longitudes = numpy.linspace(
        place['longitude'] - lat_lon_radius,
        place['longitude'] + lat_lon_radius,
        number_of_different_lat_lon_points
    )
    for longitude in longitudes :
        latitudes = numpy.linspace(
            place['latitude'] - lat_lon_radius,
            place['latitude'] + lat_lon_radius,
            number_of_different_lat_lon_points
        )
        for latitude in latitudes:
            location = get_closest_location_info_with_lat_lon(latitude, longitude)
            if location:
                locations.append(location)
    return locations

def get_locations_from_postal_code(postal_code):
    url = 'https://api-adresse.data.gouv.fr/search/?q=postcode={}'.format(postal_code)
    result = requests.get(url)
    obj = result.json()
    locations = []
    for feature in obj['features']:
        location = get_location_from_ban_feature(feature)
        locations.append(location)
    return locations
