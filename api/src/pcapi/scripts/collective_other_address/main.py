import csv
import logging
import os
import typing

from sqlalchemy.sql.expression import func

from pcapi.app import app
from pcapi.connectors import api_adresse
from pcapi.core.educational import models as educational_models
from pcapi.models import db


logger = logging.getLogger(__name__)

app.app_context().push()

if __name__ == "__main__":
    # try with a sample of 100 collective offers
    collective_offers: typing.Iterable[educational_models.CollectiveOffer] = (
        db.session.query(educational_models.CollectiveOffer)
        .filter(educational_models.CollectiveOffer.offerVenue.op("->>")("addressType") == "other")
        .order_by(func.random())
        .limit(100)
    )

    lines = []
    for collective_offer in collective_offers:
        text = collective_offer.offerVenue["otherAddress"].replace("\n", " ").replace(",", " ")
        lines.append({"nom": text})

    payload = api_adresse.format_payload(headers=["nom"], lines=lines)

    backend = api_adresse.ApiAdresseBackend()
    result = backend.search_csv(payload=payload, columns=["nom"])

    with open(f"{os.environ.get('OUTPUT_DIRECTORY')}/result.csv", "w", encoding="utf-8") as result_file:
        writer = None
        for row in result:
            if writer is None:
                writer = csv.DictWriter(result_file, fieldnames=row.keys(), delimiter=",")
                writer.writeheader()

            writer.writerow(row)
