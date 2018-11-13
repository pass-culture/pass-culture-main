import requests

from utils.test_utils import create_offerer

def get_closest_location_info_with_lat_lon(latitude, longitude):
    url = 'https://api-adresse.data.gouv.fr/reverse/?lon='+str(longitude)+'&lat='+str(latitude)
    result = requests.get(url)
    obj = result.json()
    if 'features' in obj and obj['features']:
        feature = obj['features'][0]
        coordinates = feature['geometry']['coordinates']
        properties = feature['properties']

        # These lat lon can be a bit slighter different from the
        # one we used for reversing
        location_latitude = coordinates[1]
        location_longitude = coordinates[0]

        return {
            "address": properties['name'],
            "city": properties['city'],
            "latitude": location_latitude,
            "longitude": location_longitude,
            "postalCode": properties['postcode']
        }
