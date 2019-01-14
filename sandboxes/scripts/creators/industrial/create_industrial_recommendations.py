from models.mediation import Mediation
from models.offer_type import EventType
from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_recommendation


def create_industrial_recommendations(mediations_by_name, offers_by_name, users_by_name):
    logger.info('create_industrial_recommendations')

    recommendations_by_name = {}

    first_mediation = Mediation.query.filter_by(tutoIndex=0).one()
    second_mediation = Mediation.query.filter_by(tutoIndex=1).one()
    tuto_mediations = [first_mediation, second_mediation]

    activation_mediation_items = [
        mediation_item
        for mediation_item in mediations_by_name.items()
        if mediation_item[1].offer.eventOrThing.offerType['value'] == str(EventType.ACTIVATION)
    ]

    for (user_name, user) in users_by_name.items():

        user_has_no_recommendation = \
            user.firstName != "PC Test Jeune" or \
            "has-signed-up" in user_name

        if user_has_no_recommendation:
            continue

        for (tuto_index, tuto_mediation) in enumerate(tuto_mediations):
            recommendation_name = 'Tuto {} / {}'.format(
                tuto_index,
                user_name
            )
            recommendations_by_name[recommendation_name] = \
                create_recommendation(
                    date_read="2018-12-17T15:59:11.689Z",
                    mediation=tuto_mediation,
                    user=user
                )

        (mediation_name, mediation) = activation_mediation_items[0]
        recommendation_name = '{} / {}'.format(
            mediation_name,
            user_name
        )
        recommendations_by_name[recommendation_name] = \
            create_recommendation(
                is_clicked=True,
                mediation=mediation,
                offer=mediation.offer,
                user=user
            )

        user_has_more_than_activation_recommendation = any([
            user_tag in user_name
            for user_tag in
            [
                "has-confirmed-activation",
                "has-booked-some",
                "has-no-more-money"
            ]
        ])

        if not user_has_more_than_activation_recommendation:
            continue

        already_recommended_offer_items = list(offers_by_name.items())[::10]
        for (offer_name, offer) in already_recommended_offer_items:
            recommendation_name = '{} / {}'.format(
                offer_name,
                user_name
            )
            recommendations_by_name[recommendation_name] = \
                create_recommendation(
                    offer=offer,
                    user=user
                )

    PcObject.check_and_save(*recommendations_by_name.values())

    logger.info('created {} recommendations'.format(len(recommendations_by_name)))

    return recommendations_by_name
