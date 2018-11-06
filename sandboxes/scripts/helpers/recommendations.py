from models import Mediation, Recommendation, User
from models.pc_object import PcObject
from utils.human_ids import dehumanize
from utils.logger import logger

def create_or_find_recommendation(recommendation_mock, mediation=None, user=None):
    if mediation is None:
        mediation = Mediation.query.get(dehumanize(recommendation_mock['mediationId']))

    if user is None:
        user = User.query.get(dehumanize(recommendation_mock['userId']))

    logger.info("look recommendation " + str(mediation) + " " + user.email)

    recommendation = Recommendation.query.filter_by(
        mediationId=mediation.id,
        userId=user.id,
    ).first()

    if recommendation is None:
        recommendation = Recommendation(from_dict=recommendation_mock)
        recommendation.mediation = mediation
        recommendation.user = user
        if 'id' in recommendation_mock:
            recommendation.id = dehumanize(recommendation_mock['id'])
        PcObject.check_and_save(recommendation)
        logger.info("created recommendation " + str(recommendation))
    else:
        logger.info('--already here-- recommendation' + str(recommendation))

    return recommendation

def create_or_find_recommendations(*recommendation_mocks):
    recommendations_count = str(len(recommendation_mocks))

    logger.info("recommendation mocks " + recommendations_count)

    recommendations = []
    for (recommendation_index, recommendation_mock) in enumerate(recommendation_mocks):
        logger.info(str(recommendation_index) + "/" + recommendations_count)
        recommendation = create_or_find_recommendation(recommendation_mock)
        recommendations.append(recommendation)

    return recommendations
