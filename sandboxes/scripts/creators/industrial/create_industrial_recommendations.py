from models.event import Event
from models.mediation import Mediation
from models.thing import Thing
from models.offer_type import EventType
from models.pc_object import PcObject
from recommendations_engine.offers import get_department_codes_from_user
from repository.offer_queries import get_active_offers_by_type
from utils.logger import logger
from utils.test_utils import create_recommendation

RECOMMENDATION_MODULO = 2

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

        user_has_recommendation_on_something_else_than_activation_offers = any([
            user_tag in user_name
            for user_tag in
            [
                "has-confirmed-activation",
                "has-booked-some",
                "has-no-more-money"
            ]
        ])

        if not user_has_recommendation_on_something_else_than_activation_offers:
            continue


        department_codes = get_department_codes_from_user(user)

        active_event_offer_ids = [
            o.id for o in get_active_offers_by_type(
                Event,
                department_codes=department_codes,
                user=user
            )
        ]
        active_thing_offer_ids = [
            o.id for o in get_active_offers_by_type(
                Thing,
                department_codes=department_codes,
                user=user
            )
        ]

        already_recommended_event_offer_ids = active_event_offer_ids[::RECOMMENDATION_MODULO]
        already_recommended_thing_offer_ids = active_thing_offer_ids[::RECOMMENDATION_MODULO]

        print('already_recommended_event_offer_ids', already_recommended_event_offer_ids)
        print('already_recommended_thing_offer_ids', already_recommended_thing_offer_ids)

        for (offer_name, offer) in list(offers_by_name.items()):

            if isinstance(offer.eventOrThing, Event) \
                and offer.id not in already_recommended_event_offer_ids:
                continue
            elif isinstance(offer.eventOrThing, Thing) \
                and offer.id not in already_recommended_thing_offer_ids:
                continue

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
