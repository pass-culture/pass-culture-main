from models.offer_type import EventType
from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_recommendation

def create_industrial_recommendations(mediations_by_name, offers_by_name, users_by_name):
    logger.info('create_industrial_recommendations')

    recommendations_by_name = {}

    activation_mediation_items = [
        mediation_item
        for mediation_item in mediations_by_name.items()
        if mediation_item[1].offer.eventOrThing.offerType['value'] == str(EventType.ACTIVATION)
    ]

    for (user_name, user) in users_by_name.items():

        user_should_not_have_yet_recommendations_in_its_user_story = \
            user.firstName != "PC Test Jeune" or \
            "has-signed-up" in user_name or \
            "has-confirmed-activation" in user_name

        if user_should_not_have_yet_recommendations_in_its_user_story:
            continue

        (mediation_name, mediation) = activation_mediation_items[0]
        recommendation_name = '{} / {}'.format(
            mediation_name,
            user_name
        )
        recommendations_by_name[recommendation_name] = \
            create_recommendation(
                mediation=mediation,
                offer=mediation.offer,
                user=user
            )

    PcObject.check_and_save(*recommendations_by_name.values())

    logger.info('created {} recommendations'.format(len(recommendations_by_name)))

    return recommendations_by_name
