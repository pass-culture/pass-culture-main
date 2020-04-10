from typing import List

from models.db import db
from models.seen_offers import SeenOffers
from repository import repository
from utils.human_ids import dehumanize


def update_seen_offers(seen_offers: List) -> None:
    if seen_offers:
        new_seen_offers = []
        for seen_offer in seen_offers:

            seen_offer_id = dehumanize(seen_offer['id'])
            if SeenOffers.query.filter_by(id=seen_offer_id).count() > 0:
                SeenOffers.query.filter_by(id=seen_offer_id).update({"dateSeen": seen_offer['dateSeen']})
            else:
                new_seen_offer = SeenOffers()
                new_seen_offer.userId = dehumanize(seen_offer['userId'])
                new_seen_offer.offerId = dehumanize(seen_offer['offerId'])
                new_seen_offer.dateSeen = seen_offer['dateSeen']
                new_seen_offers.append(new_seen_offer)

            repository.save(*new_seen_offers)

        db.session.commit()
