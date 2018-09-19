from math import sqrt
from sqlalchemy import func

def distance(latitude1, longitude1, latitude2, longitude2):
    return sqrt(((float(latitude2) - float(latitude1)) ** 2) +
                ((float(longitude2) - float(longitude1)) ** 2))

def get_geo_distance_in_kilometers(lat1, lon1, lat2, lon2):
    return 6366 * 2 * func.asin(func.sqrt(func.pow (func.sin((lat1-lat2)/2) , 2) + func.cos(lat1)*func.cos(lat2)* func.pow( func.sin((lon1-lon2)/2) , 2)))
