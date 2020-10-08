from datetime import datetime, timedelta
from typing import List

from sqlalchemy import and_
from sqlalchemy.sql.expression import select

from pcapi.models import BookingSQLEntity, FavoriteSQLEntity, MediationSQLEntity, OfferSQLEntity, Recommendation
from pcapi.models.api_errors import ResourceNotFoundError
from pcapi.models.db import db
from pcapi.repository import mediation_queries
from pcapi.repository.offer_queries import find_searchable_offer
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.logger import logger

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
    logger.debug(lambda: 'Requested Recommendation with offer_id=%s mediation_id=%s' % (
        offer_id, mediation_id))
    query = Recommendation.query.filter((Recommendation.userId == user_id)
                                        & (Recommendation.search == None))
    if offer_id:
        query = query.join(OfferSQLEntity)
    mediation = mediation_queries.find_by_id(mediation_id)
    offer = find_searchable_offer(offer_id)

    if mediation_id:
        if _has_no_mediation_or_mediation_does_not_match_offer(mediation, offer_id):
            logger.debug(lambda: 'Mediation not found or found but not matching offer for offer_id=%s mediation_id=%s'
                                 % (offer_id, mediation_id))
            raise ResourceNotFoundError()

        query = query.filter(Recommendation.mediationId == mediation_id)

    if offer_id:
        if offer is None:
            logger.debug(lambda: 'Offer not found for offer_id=%s' % (offer_id,))
            raise ResourceNotFoundError()

        query = query.filter(OfferSQLEntity.id == offer_id)

    return query.first()


def get_recommendations_for_offers(offer_ids: List[int]) -> List[Recommendation]:
    return Recommendation.query \
        .filter(Recommendation.offerId.in_(offer_ids)) \
        .all()


def delete_useless_recommendations(limit: int = 500000) -> None:
    favorite_query = (select([FavoriteSQLEntity.offerId])).alias('favorite_query')
    is_unread = Recommendation.dateRead == None
    is_older_than_one_week = Recommendation.dateCreated < EIGHT_DAYS_AGO
    has_no_booking = BookingSQLEntity.recommendationId == None
    not_favorite_predicate = Recommendation.offerId.notin_(favorite_query)

    connection = db.engine.connect()

    query = select([Recommendation.id]). \
        select_from(Recommendation.__table__
                    .join(BookingSQLEntity, Recommendation.id == BookingSQLEntity.recommendationId, True)) \
        .where(
        and_(is_unread,
             is_older_than_one_week,
             not_favorite_predicate,
             has_no_booking)
    )

    has_next = True
    increment = 1
    while has_next:
        recommendations = connection.execute(query).fetchmany(limit)
        recommendation_ids = [recommendation[0] for recommendation in recommendations]
        delete_query = Recommendation.__table__.delete().where(Recommendation.id.in_(recommendation_ids))
        db.session.execute(delete_query)
        db.session.commit()

        logger.info(f'delete_useless_recommendations 5x{increment}00000 recommendations deleted')
        increment += 1
        if len(recommendations) < limit:
            has_next = False
