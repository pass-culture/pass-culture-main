import logging
from math import ceil
import time

import sqlalchemy as sa

from pcapi import settings
from pcapi.connectors.acceslibre import AccesLibreApiException
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.utils import requests


logger = logging.getLogger(__name__)
BATCH_SIZE = 100
API_KEY = settings.ACCESLIBRE_API_KEY
BASE_URL = settings.ACCESLIBRE_API_URL
HEADERS = {"Authorization": f"Api-Key {API_KEY}"}


def get_venues_without_acceslibre_url() -> list[offerers_models.Venue]:
    return (
        offerers_models.Venue.query.join(offerers_models.AccessibilityProvider)
        .options(
            sa.orm.load_only(
                offerers_models.Venue.name,
                offerers_models.Venue.publicName,
                offerers_models.Venue.siret,
                offerers_models.Venue.banId,
                offerers_models.Venue.city,
                offerers_models.Venue.street,
            )
        )
        .filter(
            offerers_models.Venue.isPermanent == True,
            offerers_models.Venue.isVirtual == False,
            offerers_models.AccessibilityProvider.externalAccessibilityUrl.is_(None),
        )
        .order_by(offerers_models.Venue.id.asc())
        .all()
    )


def main(dry_run: bool = True, start_from_batch: int = 1) -> None:
    venues_without_acceslibre_url = get_venues_without_acceslibre_url()
    num_batches = ceil(len(venues_without_acceslibre_url) / BATCH_SIZE)

    start_batch_index = start_from_batch - 1
    for i in range(start_batch_index, num_batches):
        batch_start = i * BATCH_SIZE
        batch_end = (i + 1) * BATCH_SIZE
        for venue in venues_without_acceslibre_url[batch_start:batch_end]:
            # Fetch web_url from venue at acceslibre
            slug = venue.accessibilityProvider.externalAccessibilityId
            url = BASE_URL + slug + "/"
            try:
                response = requests.get(url, headers=HEADERS, timeout=3)
                results = response.json()
            except AccesLibreApiException as e:
                logger.info(e)
                continue
            time.sleep(0.3)
            if response.status_code != 200:
                logger.info("No match found at acceslibre for Venue %s ", venue.id)
                continue
            venue.accessibilityProvider.externalAccessibilityUrl = results["web_url"]
            db.session.add(venue)

        if not dry_run:
            try:
                db.session.commit()
            except sa.exc.SQLAlchemyError:
                logger.exception("Could not update batch %d", i + 1)
                db.session.rollback()
        else:
            db.session.rollback()
