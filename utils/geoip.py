"""geoip"""
import geoip2.database
import os

DB_FILE_LOCATION = os.getcwd() + '/geoip/GeoLite2-City.mmdb'

geolocation_reader = geoip2.database.Reader(DB_FILE_LOCATION)

def get_db_reader():
    return geoip2.database.Reader(DB_FILE_LOCATION)

def get_geolocation(ip):
    return geolocation_reader.city(ip).location
