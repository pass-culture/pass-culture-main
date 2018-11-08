import numpy
import requests

from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_offerer

PLACES = [
    {
        "address": "148 ROUTE DE BONDY",
        "city": "Aulnay-sous-bois",
        "latitude": 48.9204903,
        "longitude": 2.4877456,
        "postalCode": "93600",
    }
]

def create_grid_offerers(geo_interval=0.1,
                         geo_number=2,
                         starting_siren=222222222):
    logger.info('create_grid_offerers')

    incremented_siren = starting_siren

    offerers_by_name = {}
    for place in PLACES:
        longitudes = numpy.linspace(
            place['longitude'] - geo_interval,
            place['longitude'] + geo_interval,
            geo_number
        )
        for longitude in longitudes :
            latitudes = numpy.linspace(
                place['latitude'] - geo_interval,
                place['latitude'] + geo_interval,
                geo_number
            )
            for latitude in latitudes:
                url = 'https://api-adresse.data.gouv.fr/reverse/?lon='+str(longitude)+'&lat='+str(latitude)
                result = requests.get(url)
                obj = result.json()
                if 'features' in obj and obj['features']:
                    feature = obj['features'][0]
                    coordinates = feature['geometry']['coordinates']
                    properties = feature['properties']
                    name = "STRUCTURE " + str(incremented_siren)
                    offerers_by_name[name] = create_offerer(
                        address=properties['name'].upper() + "lat:" + str(coordinates[1]) + " lon:" + str(coordinates[0]),
                        city=properties['city'],
                        name=name,
                        postal_code=properties['postcode'],
                        siren=str(incremented_siren)
                    )

                    incremented_siren += 1

                    PcObject.check_and_save(*offerers_by_name.values())

    return offerers_by_name
