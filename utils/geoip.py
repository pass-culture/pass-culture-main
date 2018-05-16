"""geoip"""
import gzip
import requests

DB_FILE_LOCATION = 'data/GeoLite2-City.mmdb'
DB_FILE_URL = 'http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz'

def download_fresh_db():
    req = requests.get(DB_FILE_URL, stream=True)
    gzip_file_location = "{}.gz".format(DB_FILE_LOCATION)

    with open(gzip_file_location,'wb') as f:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()

    with open(DB_FILE_LOCATION, 'wb') as f:
        with gzip.open(gzip_file_location, 'rb') as g:
            f.write(g.read())
