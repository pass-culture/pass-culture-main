import csv
import gc
import io
import os

from sqlalchemy import text
from sqlalchemy.engine import Row

from pcapi.app import app
from pcapi.models import db
from pcapi.utils import requests


app.app_context().push()
output_directory = os.environ.get("OUTPUT_DIRECTORY")
HEADER_OFFSET = 147


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


def fetch_input_data(batch_size: int, unique_file_name: str) -> None:
    header = ["old_street", "old_city", "old_postal_code", "venues_ids"]

    old_addresses = fetch_distinct_addresses_with_ids()
    total = len(old_addresses)
    ranges = [(i, i + batch_size) for i in range(0, total, batch_size)]

    for lower_bound, upper_bound in ranges:
        f = io.StringIO()

        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for address in old_addresses[lower_bound:upper_bound]:
            writer.writerow(
                {
                    "old_street": address.street,
                    "old_city": address.city,
                    "old_postal_code": address.postalCode,
                    "venues_ids": address.venues_ids,
                }
            )

        files = [
            ("data", f.getvalue()),
            # Tell API Adresse to use `old_street` and `old_postal_code` columns for the search
            ("street", (None, "old_street")),
            ("postalCode", (None, "old_postal_code")),
            # Tell API Adresse we only want the following columns in the response
            (
                "result_columns",
                (
                    None,
                    "latitude",
                ),
            ),
            (
                "result_columns",
                (
                    None,
                    "longitude",
                ),
            ),
            (
                "result_columns",
                (
                    None,
                    "result_id",
                ),
            ),
            (
                "result_columns",
                (
                    None,
                    "result_name",
                ),
            ),
            (
                "result_columns",
                (
                    None,
                    "result_postcode",
                ),
            ),
            (
                "result_columns",
                (
                    None,
                    "result_city",
                ),
            ),
            (
                "result_columns",
                (
                    None,
                    "result_citycode",
                ),
            ),
            (
                "result_columns",
                (
                    None,
                    "result_status",
                ),
            ),
        ]

        response = requests.post("https://api-adresse.data.gouv.fr/search/csv", files=files, timeout=60)
        gc.collect()
        with open(unique_file_name, "a", encoding="utf-8") as input_data:
            if response.status_code != 200:
                # Don't write the content of the response and return early
                # We can process data previously fetched and retry later
                return
            content = response.content.decode()
            if lower_bound != 0:
                content = content[HEADER_OFFSET:]

            input_data.writelines(content)
