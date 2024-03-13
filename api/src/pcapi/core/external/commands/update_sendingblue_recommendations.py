from sqlalchemy.orm import joinedload

from pcapi.core.external.attributes import models as attributes_models
from pcapi.core.external.sendinblue import update_contact_recommendations
from pcapi.core.offers import models as offers_models
import pcapi.core.users.models as users_models
from pcapi.utils.urls import offer_app_link


def get_recommendation_offer_ids(users: list[users_models.User]) -> list[tuple[users_models.User, list[int]]]:
    return [(user, []) for user in users]  # TODO https://passculture.atlassian.net/browse/PC-28408


def get_offers_recommendations_from_ids(offer_ids: set[int]) -> dict[int, attributes_models.Recommendation]:
    offers = (
        offers_models.Offer.query.filter(offers_models.Offer.id.in_(offer_ids))
        .options(joinedload(offers_models.Offer.product))
        .options(joinedload(offers_models.Offer.mediations))
    )
    recommendations = {}
    for offer in offers:
        recommendations[offer.id] = attributes_models.Recommendation(
            url=offer_app_link(offer.id),
            name=offer.name,
            description=offer.description,
            image_url=offer.image.url if offer.image else None,
            external_url=offer.url,
        )

    return recommendations


def update_contacts_recommendations(list_of_users: list[users_models.User]) -> None:
    user_recommendations_ids = get_recommendation_offer_ids(list_of_users)
    all_recommendations_ids = []
    for _, recommendation_ids in user_recommendations_ids:
        all_recommendations_ids += recommendation_ids
    recommendations = get_offers_recommendations_from_ids(set(all_recommendations_ids))
    for user, recommendations_ids in user_recommendations_ids:
        user_recommendations = [recommendations[recommendation_id] for recommendation_id in recommendations_ids]
        update_contact_recommendations(user, user_recommendations)
