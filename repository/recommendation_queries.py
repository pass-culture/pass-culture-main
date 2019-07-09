from datetime import datetime
from sqlalchemy import func, or_, and_
from sqlalchemy.sql.expression import literal

from models import Mediation, \
                   Offer, \
                   Recommendation, \
                   Stock
from models.db import db
from utils.config import BLOB_SIZE
from utils.human_ids import dehumanize


def find_unseen_tutorials_for_user(seen_recommendation_ids, user):
    return Recommendation.query.join(Mediation) \
        .filter(
        (Mediation.tutoIndex != None)
        & (Recommendation.user == user)
        & ~Recommendation.id.in_(seen_recommendation_ids)) \
        .order_by(Mediation.tutoIndex) \
        .all()


def count_read_recommendations_for_user(user, limit=None):
    query =  Recommendation.query.filter((Recommendation.user == user)
                                         & (Recommendation.dateRead != None))
    if limit:
        query = query.with_entities(literal(1)) \
                     .limit(limit) \
                     .from_self()
    return query.count()


def count_recommendation(user):
    return keep_only_bookable_stocks() \
        .filter((Recommendation.user == user) & (Recommendation.dateRead != None)) \
        .count()


def find_all_unread_recommendations(user, seen_recommendation_ids, limit=BLOB_SIZE):
    query = keep_only_bookable_stocks()
    query = filter_unseen_valid_recommendations_for_user(query, user, seen_recommendation_ids)
    query = query.filter(Recommendation.dateRead == None) \
        .group_by(Recommendation) \
        .order_by(func.random()) \
        .limit(limit)

    return query.all()


def find_all_read_recommendations(user, seen_recommendation_ids, limit=BLOB_SIZE):
    query = keep_only_bookable_stocks()
    query = filter_unseen_valid_recommendations_for_user(query, user, seen_recommendation_ids)
    query = query.filter(Recommendation.dateRead != None) \
        .group_by(Recommendation) \
        .order_by(func.random()) \
        .limit(limit)

    return query.all()


def find_recommendations_for_user_matching_offers_and_search(user_id=None, offer_ids=None, search=None):
    query = Recommendation.query

    if user_id is not None:
        query = query.filter(Recommendation.userId == user_id)

    if offer_ids is not None:
        query = query.filter(Recommendation.offerId.in_(offer_ids))

    if search is not None:
        query = query.filter(Recommendation.search == search)

    return query.all()


def keep_only_bookable_stocks():
    stock_is_still_bookable = or_(Stock.bookingLimitDatetime > datetime.utcnow(), Stock.bookingLimitDatetime == None)
    stock_is_not_soft_deleted = Stock.isSoftDeleted == False
    return Recommendation.query \
        .join(Offer) \
        .join(Stock) \
        .filter(and_(stock_is_not_soft_deleted,
         stock_is_still_bookable))





def filter_unseen_valid_recommendations_for_user(query, user, seen_recommendation_ids):
    recommendation_is_valid = (
            (Recommendation.validUntilDate == None) | (Recommendation.validUntilDate > datetime.utcnow()))
    mediation_is_not_tuto = (Mediation.tutoIndex == None)
    recommendation_is_not_seen = ~Recommendation.id.in_(seen_recommendation_ids)
    recommendation_is_not_from_search = (Recommendation.search == None)
    new_query = query \
        .outerjoin(Mediation, Mediation.id == Recommendation.mediationId) \
        .filter((Recommendation.user == user)
                & recommendation_is_not_from_search
                & recommendation_is_not_seen
                & mediation_is_not_tuto
                & recommendation_is_valid)
    return new_query


def update_read_recommendations(read_recommendations):
    if read_recommendations:
        for read_recommendation in read_recommendations:
            recommendation_id = dehumanize(read_recommendation['id'])
            Recommendation.query.filter_by(id=recommendation_id) \
                .update({"dateRead": read_recommendation['dateRead']})
        db.session.commit()


def invalidate_recommendations(offer: Offer):
    Recommendation.query.filter((Recommendation.offerId == offer.id)
                                & (Recommendation.validUntilDate > datetime.utcnow())) \
        .update({'validUntilDate': datetime.utcnow()})
    db.session.commit()
