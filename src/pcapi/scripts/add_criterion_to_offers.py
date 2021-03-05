from typing import List

from flask import current_app as app

from pcapi.connectors import redis
from pcapi.core.offers.models import Offer
from pcapi.models import Criterion
from pcapi.models import OfferCriterion
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
from pcapi.repository import feature_queries
from pcapi.utils.logger import logger


def add_criterion_to_offers(criteria: List[Criterion], isbn: str) -> bool:
    isbn = isbn.replace("-", "").replace(" ", "")

    offer_ids_tuples = (
        Offer.query.filter(Offer.extraData["isbn"].astext == isbn)
        .filter(Offer.isActive.is_(True))
        .with_entities(Offer.id)
        .all()
    )
    offer_ids = [offer_id[0] for offer_id in offer_ids_tuples]

    if not offer_ids:
        return False

    for criterion in criteria:
        logger.info("Adding criterion %s to %d offers", criterion, len(offer_ids))

        offer_criteria: List[OfferCriterion] = []
        offer_criteria.extend(OfferCriterion(offerId=offer_id, criterionId=criterion.id) for offer_id in offer_ids)

        db.session.bulk_save_objects(offer_criteria)
        db.session.commit()

    if feature_queries.is_active(FeatureToggle.SYNCHRONIZE_ALGOLIA):
        for offer_id in offer_ids:
            redis.add_offer_id(client=app.redis_client, offer_id=offer_id)

    return True
