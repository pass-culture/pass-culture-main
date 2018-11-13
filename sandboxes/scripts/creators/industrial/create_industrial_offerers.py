import numpy

from models.pc_object import PcObject
from sandboxes.scripts.utils.ban import get_closest_location_info_with_lat_lon
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

def create_industrial_offerers(
        lat_lon_radius=0.1,
        number_of_different_lat_lon_points=2,
        starting_siren=222222222
):
    logger.info('create_industrial_offerers')

    incremented_siren = starting_siren

    offerers_by_name = {}
    for place in PLACES:
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

                closest_location = get_closest_location_info_with_lat_lon(latitude, longitude)

                if closest_location is None:
                    continue

                name = "STRUCTURE " + str(incremented_siren)
                name += " lat:" + str(closest_location['latitude']) + \
                        " lon:" + str(closest_location['longitude'])

                offerers_by_name[name] = create_offerer(
                    address=closest_location['address'].upper(),
                    city=closest_location['city'],
                    name=name,
                    postal_code=closest_location['postalCode'],
                    siren=str(incremented_siren)
                )

                incremented_siren += 1

    PcObject.check_and_save(*offerers_by_name.values())

    return offerers_by_name
