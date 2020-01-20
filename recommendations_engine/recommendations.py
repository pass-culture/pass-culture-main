import random
from datetime import timedelta
from typing import Dict, List

import dateutil.parser

from domain.types import get_active_product_type_values_from_sublabels
from models import Recommendation, Mediation, PcObject, User, DiscoveryView, Offer
from models.db import db
from recommendations_engine import get_offers_for_recommendations_discovery
from repository import mediation_queries
from repository.mediation_queries import get_all_tuto_mediations
from repository.offer_queries import get_offers_for_recommendations_search, find_searchable_offer
from repository.recommendation_queries import count_read_recommendations_for_user, \
    find_recommendation_already_created_on_discovery
from utils.logger import logger
from validation.recommendations import check_distance_is_digit, \
    check_latitude_is_defined, \
    check_longitude_is_defined

MAX_OF_MAX_DISTANCE = "20000"


def give_requested_recommendation_to_user(user, offer_id, mediation_id):
    recommendation = None

    if mediation_id or offer_id:
        recommendation = find_recommendation_already_created_on_discovery(
            offer_id, mediation_id, user.id)
        if recommendation is None:
            with db.session.no_autoflush:
                recommendation = _create_recommendation_from_ids(user, offer_id, mediation_id=mediation_id)
            PcObject.save(recommendation)
            logger.debug(lambda: 'Creating Recommendation with offer_id=%s mediation_id=%s' % (offer_id, mediation_id))

    return recommendation


def create_recommendations_for_discovery(user: User, pagination_params: Dict, limit: int = 3) -> List[Recommendation]:
    recommendations = []
    tuto_mediations_by_index = {}

    max_tuto_index = 0
    for tuto_mediation in get_all_tuto_mediations():
        tuto_mediations_by_index[tuto_mediation.tutoIndex] = tuto_mediation
        max_tuto_index = tuto_mediation.tutoIndex

    read_recommendations_count = count_read_recommendations_for_user(user,
                                                                     limit=max_tuto_index)

    inserted_tuto_mediations = 0
    offers = get_offers_for_recommendations_discovery(
        limit=limit,
        pagination_params=pagination_params,
        user=user,
    )

    for (index, offer) in enumerate(offers):
        while read_recommendations_count + index + inserted_tuto_mediations \
                in tuto_mediations_by_index:
            tuto_mediation_index = read_recommendations_count \
                                   + index \
                                   + inserted_tuto_mediations
            _create_tuto_mediation_if_non_existent_for_user(
                user,
                tuto_mediations_by_index[tuto_mediation_index]
            )
            inserted_tuto_mediations += 1
        recommendations.append(_create_recommendation(user, offer))
    PcObject.save(*recommendations)
    return recommendations


def _create_tuto_mediation_if_non_existent_for_user(user: User, tuto_mediation: Mediation):
    already_existing_tuto_recommendation = Recommendation.query \
        .filter_by(mediation=tuto_mediation, user=user) \
        .first()
    if already_existing_tuto_recommendation:
        return

    recommendation = Recommendation()
    recommendation.user = user
    recommendation.mediation = tuto_mediation
    PcObject.save(recommendation)


def _create_recommendation_from_ids(user, offer_id, mediation_id=None):
    mediation = None

    if mediation_id:
        mediation = mediation_queries.find_by_id(mediation_id)

    offer = mediation.offer if mediation else find_searchable_offer(offer_id)

    return _create_recommendation(user, offer, mediation=mediation)


def _create_recommendation(user: User, offer: Offer, mediation: Mediation = None) -> Recommendation:
    recommendation = Recommendation()
    recommendation.user = user

    recommendation.offer = offer

    if mediation:
        recommendation.mediation = mediation
    else:
        active_mediations = [m for m in offer.mediations if m.isActive]
        if active_mediations:
            recommendation.mediation = random.choice(active_mediations)

    return recommendation


# TODO: when using discovery view use this function instead of _create_recommedantion
# in create_recommendations_for_discovery
def _create_recommendation_from_offers(user: User, reco_view: DiscoveryView,
                                       mediation: Mediation = None) -> Recommendation:
    recommendation = Recommendation()
    recommendation.user = user

    recommendation.offerId = reco_view.id

    if mediation:
        recommendation.mediation = mediation
    else:
        recommendation.mediationId = reco_view.mediationId
    return recommendation


def _get_search(kwargs: dict) -> str:
    return '&'.join([key + '=' + str(value) for (key, value) in kwargs.items()])


def create_recommendations_for_search(user, **kwargs):
    offers = get_offers_for_recommendations_search(**kwargs)
    search = _get_search(kwargs)

    recommendations = []

    for offer in offers:
        recommendation = _create_recommendation(user, offer)
        recommendation.search = search
        recommendations.append(recommendation)

    PcObject.save(*recommendations)
    return recommendations


def get_recommendation_search_params(request_args: dict) -> dict:
    search_params = {}

    if 'date' in request_args and request_args['date']:
        date = dateutil.parser.parse(request_args['date'])
        search_params['days_intervals'] = [
            [date, date + timedelta(days=int(1))]]

    if 'days' in request_args and request_args['days']:
        date = dateutil.parser.parse(request_args['date'])
        days_intervals = request_args['days'].split(',')
        search_params['days_intervals'] = [
            [date + timedelta(days=int(day)) for day in days.split('-')]
            for days in days_intervals
        ]

    if 'keywords' in request_args and request_args['keywords']:
        search_params['keywords_string'] = request_args['keywords']

    if 'distance' in request_args and request_args['distance']:
        check_distance_is_digit(request_args['distance'])
        if request_args['distance'] != MAX_OF_MAX_DISTANCE:
            check_latitude_is_defined(request_args)
            search_params['latitude'] = float(request_args['latitude'])
            check_longitude_is_defined(request_args)
            search_params['longitude'] = float(request_args['longitude'])
            search_params['max_distance'] = float(request_args['distance'])

    if 'page' in request_args and request_args['page']:
        search_params['page'] = int(request_args['page'])

    if 'categories' in request_args and request_args['categories']:
        type_sublabels = request_args['categories']
        search_params['type_values'] = get_active_product_type_values_from_sublabels(
            type_sublabels)

    return search_params
