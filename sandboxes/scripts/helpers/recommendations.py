from models import Recommendation
from models.pc_object import PcObject
from utils.logger import logger

def create_or_find_recommendation(recommendation_mock, mediation=None, user=None, store=None):
    if mediation is None:
        mediation = store['mediations_by_key'][recommendation_mock['mediationKey']]

    if user is None:
        user = store['users_by_key'][recommendation_mock['userKey']]

    recommendation = Recommendation.query.filter_by(
        mediationId=mediation.id,
        userId=user.id,
    ).first()

    if query.count() == 0:
        recommendation = Recommendation(from_dict=recommendation_mock)
        recommendation.mediation = mediation
        recommendation.user = user
        PcObject.check_and_save(recommendation)
        logger.info("created recommendation " + str(recommendation))
    else:
        logger.info('--already here-- recommendation' + str(recommendation))

    return recommendation

def create_or_find_recommendations(*recommendation_mocks, store=None):
    if store is None:
        store = {}

    recommendations_count = str(len(recommendation_mocks))

    logger.info("recommendation mocks " + recommendations_count)
    store['recommendations_by_key'] = {}

    for (recommendation_index, recommendation_mock) in enumerate(recommendation_mocks):
        logger.info("look recommendation " + store['mediations_by_key'][recommendation_mock['mediationKey']].offer.eventOrThing.name + " " + str(recommendation_index) + "/" + recommendations_count)
        recommendation = create_or_find_recommendation(recommendation_mock, store=store)
        store['recommendations_by_key'][recommendation_mock['key']] = recommendation
