""" distance """
import math

from sqlalchemy import func

EARTH_RADIUS_KM = 6378.137


def distance(latitude1, longitude1, latitude2, longitude2):
    return math.sqrt(((float(latitude2) - float(latitude1)) ** 2) +
                     ((float(longitude2) - float(longitude1)) ** 2))


def get_geo_distance_in_kilometers(lat1, lon1, lat2, lon2, module=math):
    d_lat = (lat2 * math.pi) / 180 - (lat1 * math.pi) / 180
    d_lon = (lon2 * math.pi) / 180 - (lon1 * math.pi) / 180
    a = module.sin(d_lat / 2) * module.sin(d_lat / 2) + \
        module.cos((lat1 * math.pi) / 180) * module.cos((lat2 * math.pi) / 180) * \
        module.sin(d_lon / 2) * module.sin(d_lon / 2)
    c = 2 * module.atan2(module.sqrt(a), module.sqrt(1 - a))
    d = EARTH_RADIUS_KM * c

    return d


def get_sql_geo_distance_in_kilometers(lat1, lon1, lat2, lon2):
    return get_geo_distance_in_kilometers(lat1, lon1, lat2, lon2, module=func)
