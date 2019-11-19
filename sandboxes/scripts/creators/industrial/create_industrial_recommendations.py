from models.mediation import Mediation
from models.pc_object import PcObject
from recommendations_engine.offers import get_departement_codes_from_user
from repository.offer_queries import get_active_offers
from sandboxes.scripts.utils.select import remove_every
from sandboxes.scripts.utils.storage_utils import store_public_object_from_sandbox_assets
from tests.test_utils import create_recommendation
from utils.logger import logger

ACTIVE_OFFERS_WITH_RECOMMENDATION_PER_USER_REMOVE_MODULO = 2


def create_industrial_recommendations(mediations_by_name, offers_by_name, users_by_name):
    logger.info('create_industrial_recommendations')

    recommendations_by_name = {}

    first_mediation = Mediation.query.filter_by(tutoIndex=0).one()
    second_mediation = Mediation.query.filter_by(tutoIndex=1).one()
    tuto_mediations = [first_mediation, second_mediation]

    for (user_name, user) in users_by_name.items():

        user_has_no_recommendation = \
            user.firstName != "PC Test Jeune" or \
            "has-signed-up" in user_name or \
            "has-filled-cultural-survey" in user_name

        if user_has_no_recommendation:
            continue

        for (tuto_index, tuto_mediation) in enumerate(tuto_mediations):
            recommendation_name = 'Tuto {} / {}'.format(
                tuto_index,
                user_name
            )
            recommendations_by_name[recommendation_name] = \
                create_recommendation(
                    user=user, mediation=tuto_mediation, date_read="2018-12-17T15:59:11.689Z")

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

        departement_codes = get_departement_codes_from_user(user)

        active_offer_ids = [
            offer.id for offer in
            get_active_offers(
                departement_codes=departement_codes,
                limit=None,
                pagination_params={'page': 1, 'seed': 0.5},
                user=user
            )
        ]
        active_offer_ids.sort()

        # every (OFFER_WITH_RECOMMENDATION_PER_USER_MODULO_RATIO - 1)/OFFER_WITH_RECOMMENDATION_PER_USER_MODULO_RATIO
        # offers will have a recommendation for this user
        recommended_offer_ids = remove_every(
            active_offer_ids,
            ACTIVE_OFFERS_WITH_RECOMMENDATION_PER_USER_REMOVE_MODULO
        )

        for (offer_name, offer) in list(offers_by_name.items()):

            if offer.id not in recommended_offer_ids:
                continue
            elif offer.venue.managingOfferer.validationToken:
                continue

            recommendation_name = '{} / {}'.format(
                offer_name,
                user_name
            )

            if offer.mediations:
                mediation = offer.mediations[0]
            else:
                mediation = None

            recommendations_by_name[recommendation_name] = \
                create_recommendation(
                    offer=offer, user=user, mediation=mediation)

    PcObject.save(*recommendations_by_name.values())

    for recommendation in recommendations_by_name.values():
        if recommendation.offer:
            offer = recommendation.offer
            if not offer.mediations:
                store_public_object_from_sandbox_assets(
                    "thumbs",
                    offer.product,
                    offer.product.type
                )

    logger.info('created {} recommendations'.format(
        len(recommendations_by_name)))

    return recommendations_by_name
