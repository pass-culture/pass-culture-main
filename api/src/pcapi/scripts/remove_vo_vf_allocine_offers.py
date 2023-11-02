import time

import sqlalchemy as sa
from sqlalchemy.orm import load_only

from pcapi.core.offers.models import Offer
from pcapi.core.providers.models import AllocinePivot
from pcapi.core.search.backends import algolia
from pcapi.models import db


def remove_vo_vf_allocine_offers(dry_run: bool = True) -> None:
    start = time.time()
    total_offers = 0
    search_backend = algolia.AlgoliaBackend()
    rows = AllocinePivot.query.with_entities(AllocinePivot.venueId).all()
    venueIds = [row[0] for row in rows]
    print(f"Fetch all venueIds {time.time() - start:.2f}s")
    for i, venueId in enumerate(venueIds):
        before = time.time()
        offers = (
            Offer.query.filter(Offer.venueId == venueId)
            .filter(Offer.isActive.is_(True))
            .filter(sa.or_(Offer.name.endswith(" - VO"), Offer.name.endswith(" - VF")))
            .options(load_only(Offer.id, Offer.isActive))
            .all()
        )
        total_offers += len(offers)
        for offer in offers:
            offer.isActive = False

        if dry_run:
            db.session.rollback()
        else:
            db.session.add_all(offers)
            db.session.commit()
            search_backend.unindex_offer_ids([offer.id for offer in offers])

        after = time.time()
        print(
            f"{after - before:.2f}s\t"
            f"Venue {i} / {len(venueIds)} {len(offers)} offers ({100 * i / len(venueIds):.2f}%)\t"
            f"Total offers {total_offers}\tTotal time {time.time() - start:.2f}s"
        )

    print(f"Total time: {time.time() - start:.2f}s")


remove_vo_vf_allocine_offers()
