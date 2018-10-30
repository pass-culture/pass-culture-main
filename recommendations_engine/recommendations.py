""" recommendations """
from datetime import datetime, timedelta

import dateutil.parser
from sqlalchemy import func

from domain.types import get_type_values_from_sublabels
from models import ApiErrors, Recommendation, Offer, Mediation, PcObject
from recommendations_engine import get_offers_for_recommendations_discovery
from repository import offer_queries
from repository.offer_queries import get_offers_for_recommendations_search, find_searchable_offer
from repository.recommendation_queries import find_recommendations_for_user_matching_offers_and_search
from utils.logger import logger


class OfferNotFoundException(Exception):
    pass


def give_requested_recommendation_to_user(user, offer_id, mediation_id):
    recommendation = None

    if mediation_id or offer_id:
        recommendation = _find_recommendation(offer_id, mediation_id)
        if recommendation is None:
            recommendation = _create_recommendation_from_ids(user, offer_id, mediation_id=mediation_id)
            logger.info('Creating Recommendation with offer_id=%s mediation_id=%s' % (offer_id, mediation_id))

    return recommendation


def create_recommendations_for_discovery(limit=3, user=None, coords=None):
    if user and user.is_authenticated:
        recommendation_count = Recommendation.query.filter_by(user=user) \
            .count()

    recommendations = []
    tuto_mediations = {}

    for to in Mediation.query.filter(Mediation.tutoIndex != None).all():
        tuto_mediations[to.tutoIndex] = to

    inserted_tuto_mediations = 0
    offers = get_offers_for_recommendations_discovery(limit, user=user, coords=coords)
    for (index, offer) in enumerate(offers):

        while recommendation_count + index + inserted_tuto_mediations \
                in tuto_mediations:
            insert_tuto_mediation(user,
                                  tuto_mediations[recommendation_count + index
                                                  + inserted_tuto_mediations])
            inserted_tuto_mediations += 1
        recommendations.append(_create_recommendation(user, offer))
    return recommendations


def insert_tuto_mediation(user, tuto_mediation):
    recommendation = Recommendation()
    recommendation.user = user
    recommendation.mediation = tuto_mediation
    recommendation.validUntilDate = datetime.utcnow() + timedelta(weeks=2)
    PcObject.check_and_save(recommendation)


def _no_mediation_or_mediation_does_not_match_offer(mediation, offer_id):
    return mediation is None or (offer_id and (mediation.offerId != offer_id))


def _find_recommendation(offer_id, mediation_id):
    logger.info('Requested Recommendation with offer_id=%s mediation_id=%s' % (offer_id, mediation_id))
    query = Recommendation.query.filter(Recommendation.validUntilDate > datetime.utcnow())
    if offer_id:
        query = query.join(Offer)
    mediation = Mediation.query.filter_by(id=mediation_id).first()
    offer = Offer.query.filter_by(id=offer_id).first()

    if mediation_id:
        if _no_mediation_or_mediation_does_not_match_offer(mediation, offer_id):
            logger.info('Mediation not found or found but not matching offer for offer_id=%s mediation_id=%s'
                        % (offer_id, mediation_id))
            raise OfferNotFoundException()

        query = query.filter(Recommendation.mediationId == mediation_id)

    if offer_id:
        if offer is None:
            logger.info('Offer not found for offer_id=%s' % (offer_id,))
            raise OfferNotFoundException()

        query = query.filter(Offer.id == offer_id)

    return query.first()


def _create_recommendation_from_ids(user, offer_id, mediation_id=None):
    mediation = Mediation.query.filter_by(id=mediation_id).first()
    offer = find_searchable_offer(offer_id)
    if offer_id and not offer:
        raise OfferNotFoundException
    return _create_recommendation(user, offer, mediation=mediation)


def _create_recommendation(user, offer, mediation=None):
    recommendation = Recommendation()
    recommendation.user = user

    if offer:
        recommendation.offer = offer
    else:
        offer = offer_queries.find_offer_by_id(mediation.offerId)
        recommendation.offer = offer

    if mediation:
        recommendation.mediation = mediation
    else:
        mediation = Mediation.query \
            .filter(Mediation.offer == offer) \
            .order_by(func.random()) \
            .first()
        recommendation.mediation = mediation

    if recommendation.mediation:
        recommendation.validUntilDate = datetime.utcnow() + timedelta(days=3)
    else:
        recommendation.validUntilDate = datetime.utcnow() + timedelta(days=1)

    if offer.lastStock and offer.lastStock.bookingLimitDatetime:
        recommendation.validUntilDate = min(
            recommendation.validUntilDate,
            offer.lastStock.bookingLimitDatetime - timedelta(minutes=1)
        )

    PcObject.check_and_save(recommendation)
    return recommendation


def get_search(kwargs):
    return '&'.join([key + '=' + str(value) for (key, value) in kwargs.items()])


def create_recommendations_for_search(user, **kwargs):
    offers = get_offers_for_recommendations_search(**kwargs)
    offer_ids = [offer.id for offer in offers]
    search = get_search(kwargs)
    existing_recommendations = find_recommendations_for_user_matching_offers_and_search(user.id, offer_ids, search)
    offer_ids_with_already_created_recommendations = [reco.offerId for reco in existing_recommendations]
    recommendations = []
    recommendations_to_save = []

    for offer in offers:
        if offer.id in offer_ids_with_already_created_recommendations:
            recommendation_index = offer_ids_with_already_created_recommendations.index(offer.id)
            recommendation = existing_recommendations[recommendation_index]
        else:
            recommendation = _create_recommendation(user, offer)
            recommendation.search = search
            recommendations_to_save.append(recommendation)

        recommendations.append(recommendation)

    if recommendations_to_save:
        PcObject.check_and_save(*recommendations_to_save)

    return recommendations


def get_recommendation_search_params(kwargs):
    search_params = {}

    api_errors = ApiErrors()

    if 'page' in kwargs and kwargs['page']:
        search_params['page'] = int(kwargs['page'])

    if 'keywords' in kwargs and kwargs['keywords']:
        search_params['keywords'] = kwargs['keywords']

    if 'categories' in kwargs and kwargs['categories']:
        type_sublabels = kwargs['categories']
        search_params['type_values'] = get_type_values_from_sublabels(type_sublabels)

    if 'date' in kwargs and kwargs['date'] and \
            'days' in kwargs and kwargs['days']:
        date = dateutil.parser.parse(kwargs['date'])
        days_intervals = kwargs['days'].split(',')
        search_params['days_intervals'] = [
            [date + timedelta(days=int(day)) for day in days.split('-')]
            for days in days_intervals
        ]

    if 'latitude' in kwargs and kwargs['latitude']:
        search_params['latitude'] = float(kwargs['latitude'])

    if 'longitude' in kwargs and kwargs['longitude']:
        search_params['longitude'] = float(kwargs['longitude'])

    if 'distance' in kwargs and kwargs['distance']:
        if not kwargs['distance'].isdigit():
            api_errors.addError('distance', 'cela doit etre un nombre')
            raise api_errors
        search_params['max_distance'] = float(kwargs['distance'])

    return search_params
