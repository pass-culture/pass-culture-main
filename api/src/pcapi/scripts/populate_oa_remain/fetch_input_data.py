import csv
import gc
import os
import time

from sqlalchemy import text
from sqlalchemy.engine import Row

from pcapi.app import app
from pcapi.connectors.api_adresse import ResultColumn
from pcapi.models import db
from pcapi.utils import requests


app.app_context().push()
output_directory = os.environ.get("OUTPUT_DIRECTORY")
HEADER_OFFSET = 147
THRESHOLD_TO_ACCEPT_RESULT = 0.6


def fetch_distinct_addresses_with_ids() -> list[Row]:
    addresses = db.session.execute(
        text(
            """
            SELECT venue."street", venue."city", venue."postalCode", array_agg(venue.id) as venues_ids 
            FROM venue WHERE venue."offererAddressId" is NULL AND venue."isVirtual" is false
            GROUP BY venue."street", venue."city", venue."postalCode"
        """
        )
    )
    return list(addresses)


def fetch_input_data(unique_file_name: str) -> None:
    start = time.time()
    header = [
        "old_street",
        "old_city",
        "old_postal_code",
        "venues_ids",
        ResultColumn.LATITUDE.value,
        ResultColumn.LONGITUDE.value,
        ResultColumn.RESULT_ID.value,
        ResultColumn.RESULT_NAME.value,
        ResultColumn.RESULT_POSTCODE.value,
        ResultColumn.RESULT_CITY.value,
        ResultColumn.RESULT_CITYCODE.value,
        "score",
    ]

    old_addresses = fetch_distinct_addresses_with_ids()
    with open(unique_file_name, "a", encoding="utf-8") as input_data:
        writer = csv.DictWriter(input_data, fieldnames=header)
        nb = 0
        for address in old_addresses:
            params = {
                "q": f"{address.street} {address.city} {address.postalCode}",
                "limit": 1,
                "autocomplete": False,
                "type": "housenumber",
            }
            data_to_write = {"score": 0}
            delta = time.time() - start
            if (nb > 40 and delta < 60) or delta > 60:
                print(f"waiting {abs(60 - delta)} seconds")
                time.sleep(abs(60 - delta))  # for delta > 60 the sleep will be the time of one request
                start = time.time()
                nb = 0
            response = requests.get("https://api-adresse.data.gouv.fr/search", params=params, timeout=60)
            nb += 1
            if response.status_code != 200:
                continue
            if len(response.json().get("features")) > 0:
                address_found = response.json()["features"][0]["properties"]
                lon, lat = response.json()["features"][0]["geometry"]["coordinates"]
                data_to_write = {
                    "old_street": address.street,
                    "old_city": address.city,
                    "old_postal_code": address.postalCode,
                    "venues_ids": address.venues_ids,
                    ResultColumn.LATITUDE.value: lat,
                    ResultColumn.LONGITUDE.value: lon,
                    ResultColumn.RESULT_ID.value: address_found["id"],
                    ResultColumn.RESULT_NAME.value: address_found["name"],
                    ResultColumn.RESULT_POSTCODE.value: address_found["postcode"],
                    ResultColumn.RESULT_CITY.value: address_found["city"],
                    ResultColumn.RESULT_CITYCODE.value: address_found["citycode"],
                    "score": address_found["score"],
                }
            writer.writerow(data_to_write)
            gc.collect()
