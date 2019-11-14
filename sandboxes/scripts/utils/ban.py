import requests


def get_locations_from_postal_code(postal_code):
    url = 'https://api-adresse.data.gouv.fr/search/?q=postcode={}'.format(postal_code)
    result = requests.get(url)
    obj = result.json()
    locations = []
    for feature in obj['features']:
        location = {
            "address": feature['properties']['name'],
            "city": feature['properties']['city'],
            "latitude": feature['geometry']['coordinates'][1],
            "longitude": feature['geometry']['coordinates'][0],
            "postalCode": feature['properties']['postcode']
        }
        locations.append(location)
    return locations
