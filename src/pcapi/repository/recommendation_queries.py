from datetime import datetime, timedelta
from typing import List

from pcapi.models import MediationSQLEntity, OfferSQLEntity, Recommendation
from pcapi.models.api_errors import ResourceNotFoundError
from pcapi.models.db import db
from pcapi.repository import mediation_queries
from pcapi.repository.offer_queries import find_searchable_offer
from pcapi.utils.human_ids import dehumanize

EIGHT_DAYS_AGO = datetime.utcnow() - timedelta(days=8)


def update_read_recommendations(read_recommendations: List) -> None:
    if read_recommendations:
        for read_recommendation in read_recommendations:
            recommendation_id = dehumanize(read_recommendation['id'])
            Recommendation.query.filter_by(id=recommendation_id) \
                .update({"dateRead": read_recommendation['dateRead']})
        db.session.commit()


def _has_no_mediation_or_mediation_does_not_match_offer(mediation: MediationSQLEntity, offer_id: str) -> bool:
    return mediation is None or (offer_id and (mediation.offerId != offer_id))


def find_recommendation_already_created_on_discovery(offer_id: str, mediation_id: str, user_id: int) -> Recommendation:
    query = Recommendation.query.filter((Recommendation.userId == user_id)
                                        & (Recommendation.search == None))
    if offer_id:
        query = query.join(OfferSQLEntity)
    offer = find_searchable_offer(offer_id)

    if mediation_id:
        mediation = mediation_queries.find_by_id(mediation_id)
        if _has_no_mediation_or_mediation_does_not_match_offer(mediation, offer_id):
            raise ResourceNotFoundError()

        query = query.filter(Recommendation.mediationId == mediation_id)

    if offer_id:
        if offer is None:
            raise ResourceNotFoundError()

        query = query.filter(OfferSQLEntity.id == offer_id)

    return query.first()


def get_recommendations_for_offers(offer_ids: List[int]) -> List[Recommendation]:
    return Recommendation.query \
        .filter(Recommendation.offerId.in_(offer_ids)) \
        .all()
