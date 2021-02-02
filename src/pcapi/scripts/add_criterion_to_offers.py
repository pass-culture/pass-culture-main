from typing import Iterable

from flask import current_app as app
from sqlalchemy import or_

from pcapi.connectors import redis
from pcapi.core.offers.models import Offer
from pcapi.models import Criterion
from pcapi.models import OfferCriterion
from pcapi.repository import repository
from pcapi.utils.logger import logger


def add_criterion_to_offers(
    criterion_name: str, isbns: Iterable[str] = None, offer_ids: Iterable[str] = None, batch_size: int = 100
) -> None:
    if isbns is None:
        isbns = []
    if offer_ids is None:
        offer_ids = []

    isbns = [isbn.replace("-", "").replace(" ", "") for isbn in isbns]

    criterion = Criterion.query.filter_by(name=criterion_name).one()

    offers = (
        Offer.query.filter(or_(Offer.id.in_(offer_ids), Offer.extraData["isbn"].astext.in_(isbns)))
        .filter(Offer.isActive.is_(True))
        .all()
    )

    if not offers:
        logger.info("Did not match any offer: double-check the ISBN's")
        return

    logger.info("Adding criterion %s to %d offers", criterion, len(offers))

    offer_criteria = []
    for offer in offers:
        offer_criteria.append(OfferCriterion(offer=offer, criterion=criterion))

        if len(offer_criteria) > batch_size:
            repository.save(*offer_criteria)
            offer_criteria = []

    repository.save(*offer_criteria)

    logger.info("Reindexing %d offers after addition of criterion %s", len(offers), criterion_name)
    for offer in offers:
        redis.add_offer_id(client=app.redis_client, offer_id=offer.id)
