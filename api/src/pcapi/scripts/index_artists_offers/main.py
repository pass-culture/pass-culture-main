"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions): 

https://github.com/pass-culture/pass-culture-main/blob/pc-35323-reindex-offers-for-artists/api/src/pcapi/scripts/index_artists_offers/main.py

"""

import argparse
import logging

from sqlalchemy.orm import load_only

from pcapi.app import app
from pcapi.core.artist.models import ArtistProductLink
from pcapi.core.offers.models import Offer, Product
from pcapi.core.search import IndexationReason, async_index_offer_ids
from pcapi.models import db


logger = logging.getLogger(__name__)


def get_artists_offers():
    return Offer.query.join(Product).join(ArtistProductLink).options(load_only(Offer.id))


def main(not_dry: bool) -> None:
    if not_dry:
        async_index_offer_ids(get_artists_offers(), IndexationReason.OFFER_MANUAL_REINDEXATION)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main(not_dry=args.not_dry)

    logger.info("Finished")
