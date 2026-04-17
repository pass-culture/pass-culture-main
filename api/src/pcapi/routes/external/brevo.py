import json
import logging
from decimal import Decimal

import sqlalchemy as sa
from flask import request
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import load_only

import pcapi.connectors.recommendation as recommendation_api
import pcapi.core.geography.repository as geography_repository
from pcapi import settings
from pcapi.connectors.serialization.brevo_serializers import brevo_webhook
from pcapi.connectors.serialization.brevo_serializers import require_brevo_token_as_query_param
from pcapi.core.categories import subcategories
from pcapi.core.external.attributes.api import update_external_user
from pcapi.core.finance.conf import GRANTED_DEPOSIT_AMOUNT_18_v2
from pcapi.core.finance.models import Deposit
from pcapi.core.history import api as history_api
from pcapi.core.offers import models as offers_models
from pcapi.core.offers.utils import offer_app_link
from pcapi.core.users.api import get_domains_credit
from pcapi.core.users.models import User
from pcapi.core.users.repository import find_user_by_email
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.api_errors import ResourceNotFoundError
from pcapi.models.feature import FeatureToggle
from pcapi.routes.apis import public_api
from pcapi.routes.external.serialization import brevo as serializers
from pcapi.serialization.decorator import spectree_serialize


logger = logging.getLogger(__name__)

RECOMMENDATION_SUBCATEGORIES = [
    subcategories.ABO_BIBLIOTHEQUE.id,
    subcategories.ABO_CONCERT.id,
    subcategories.ABO_MEDIATHEQUE.id,
    subcategories.ABO_PRATIQUE_ART.id,
    subcategories.ABO_SPECTACLE.id,
    subcategories.ATELIER_PRATIQUE_ART.id,
    subcategories.CONCERT.id,
    subcategories.CONFERENCE.id,
    subcategories.DECOUVERTE_METIERS.id,
    subcategories.EVENEMENT_MUSIQUE.id,
    subcategories.EVENEMENT_PATRIMOINE.id,
    subcategories.FESTIVAL_ART_VISUEL.id,
    subcategories.FESTIVAL_CINE.id,
    subcategories.FESTIVAL_LIVRE.id,
    subcategories.FESTIVAL_MUSIQUE.id,
    subcategories.FESTIVAL_SPECTACLE.id,
    subcategories.MUSEE_VENTE_DISTANCE.id,
    subcategories.RENCONTRE.id,
    subcategories.SALON.id,
    subcategories.SPECTACLE_REPRESENTATION.id,
    subcategories.VISITE_GUIDEE.id,
    subcategories.VISITE_LIBRE.id,
]


def _toggle_marketing_email_subscription(subscribe: bool) -> None:
    user_email = request.json.get("email")
    if not user_email:
        raise ApiErrors(
            {"email": "Email missing in request payload"},
            status_code=400,
        )

    user = find_user_by_email(user_email)
    if user is None:
        # Nothing to do - Return success status code to avoid enumeration
        return

    history_api.ObjectUpdateSnapshot(user, user).trace_update(
        {"marketing_email": subscribe},
        target=user.get_notification_subscriptions(),
        field_name_template="notificationSubscriptions.{}",
    ).add_action()

    user.set_marketing_email_subscription(subscribe)

    db.session.add(user)
    db.session.commit()

    # Brevo is already up-to-date from originating automation, update marketing preference in Batch
    update_external_user(user, skip_brevo=True)


@public_api.route("/webhooks/sendinblue/unsubscribe", methods=["POST"])
@spectree_serialize(on_success_status=204)
def brevo_unsubscribe_user_legacy() -> None:
    """
    TODO (prouzet, 2026-04-16): remove this route when automations are migrated to /webhooks/brevo/unsubscribe
    """
    _toggle_marketing_email_subscription(False)


@public_api.route("/webhooks/sendinblue/subscribe", methods=["POST"])
@spectree_serialize(on_success_status=204)
def brevo_subscribe_user_legacy() -> None:
    """
    TODO (prouzet, 2026-04-16): remove this route when automations are migrated to /webhooks/brevo/subscribe
    """
    _toggle_marketing_email_subscription(True)


@public_api.route("/webhooks/brevo/unsubscribe", methods=["POST"])
@require_brevo_token_as_query_param
@spectree_serialize(on_success_status=204)
def brevo_unsubscribe_user() -> None:
    """
    Automation scenario is configured in Brevo to call this webhook after user unsubscribes.
    Blacklist status and MARKETING_EMAIL_SUBSCRIPTION are updated in the scenario, so we don't need to sync them again.
    """
    _toggle_marketing_email_subscription(False)


@public_api.route("/webhooks/brevo/subscribe", methods=["POST"])
@require_brevo_token_as_query_param
@spectree_serialize(on_success_status=204)
def brevo_subscribe_user() -> None:
    """
    Automation scenario is configured in Brevo to call this webhook after user unsubscribes.
    Blacklist status and MARKETING_EMAIL_SUBSCRIPTION are updated in the scenario, so we don't need to sync them again.
    """
    _toggle_marketing_email_subscription(True)


@public_api.route("/webhooks/brevo/importcontacts/<int:list_id>/<int:iteration>", methods=["POST"])
@require_brevo_token_as_query_param
@spectree_serialize(on_success_status=204)
def brevo_notify_importcontacts(list_id: int, iteration: int) -> None:
    """
    Called by Brevo once an import process is finished.
    https://developers.brevo.com/reference/importcontacts-1

    Unfortunately there is no information in query string and the body is empty, so we can't check a process id.
    The id of the list in Brevo is added to the URL when set in notifyUrl so we can at least print the list id.
    This webhook is for investigation purpose only.
    """
    logger.info("Brevo import_contacts finished", extra={"list_id": list_id, "iteration": iteration})


@public_api.route("/webhooks/brevo/recommendations/<int:user_id>", methods=["GET"])
@brevo_webhook
@spectree_serialize(
    on_success_status=200, response_model=serializers.BrevoOffersResponse, on_error_statuses=[404, 500, 502, 504]
)
def brevo_get_user_recommendations(user_id: int) -> serializers.BrevoOffersResponse:
    """This route is called by Brevo on sending an email to a user to get recommended offers."""

    if FeatureToggle.WIP_ENABLE_NEW_BREVO_RECOMMENDATION_WEBHOOK.is_active():
        return _brevo_get_user_recommendations(user_id)

    return _old_brevo_get_user_recommendations(user_id)


def _brevo_get_user_recommendations(user_id: int) -> serializers.BrevoOffersResponse:
    user = db.session.scalar(
        sa.select(User)
        .where(User.id == user_id)
        .options(load_only(User.address, User.departementCode, User.postalCode))
        .options(
            joinedload(User.deposits).load_only(
                Deposit.amount,
                Deposit.dateCreated,
                Deposit.expirationDate,
                Deposit.type,
                Deposit.userId,
                Deposit.version,
            )
        )
    )
    if not user:
        raise ResourceNotFoundError()

    price_max = Decimal(GRANTED_DEPOSIT_AMOUNT_18_v2)
    user_domains_credit = get_domains_credit(user)
    if user_domains_credit:
        price_max = user_domains_credit.all.remaining

    user_location = geography_repository.get_coordinates_from_address(user.address, user.postalCode)
    if not user_location:
        logger.info("Couldn't find user location", extra={"user_id": user.id})

    body = {
        "subcategories": RECOMMENDATION_SUBCATEGORIES,
        "price_max": float(price_max),
    }
    try:
        raw_response = recommendation_api.get_playlist(user, params=user_location, body=body)
    except (recommendation_api.RecommendationApiException, recommendation_api.RecommendationApiTimeoutException) as exc:
        logger.error("Request to recommendation API failed", extra={"error": str(exc)})
        raise ApiErrors(status_code=503)

    try:
        decoded = json.loads(raw_response.decode(encoding="utf-8"))
    except json.decoder.JSONDecodeError as exc:
        logger.error(
            "Failed decoding recommendation API response",
            extra={"error": str(exc), "response": raw_response.decode(encoding="utf-8")},
        )
        raise ApiErrors(status_code=500)

    offer_ids = [int(offer_id) for offer_id in decoded.get("playlist_recommended_offers", [])]
    offer_ids = offer_ids[: settings.BREVO_NUMBER_OF_OFFERS_IN_EXTERNAL_FEED]
    query = (
        sa.select(offers_models.Offer)
        .where(offers_models.Offer.id.in_(offer_ids))
        .options(load_only(offers_models.Offer.name))
        .options(
            joinedload(offers_models.Offer.mediations).load_only(
                offers_models.Mediation.credit,
                offers_models.Mediation.dateCreated,
                offers_models.Mediation.isActive,
                offers_models.Mediation.thumbCount,
            )
        )
        .options(
            joinedload(offers_models.Offer.product)
            .load_only()
            .joinedload(offers_models.Product.productMediations)
            .load_only(
                offers_models.ProductMediation.imageType,
                offers_models.ProductMediation.uuid,
            )
        )
    )
    offers = db.session.scalars(query).unique().all()

    return serializers.BrevoOffersResponse(
        offers=[
            serializers.RecommendedOffer(
                image=offer.thumbUrl,
                name=offer.name,
                url=offer_app_link(offer),
            )
            for offer in offers
        ]
    )


def _old_brevo_get_user_recommendations(user_id: int) -> serializers.BrevoOffersResponse:
    user = db.session.query(User).filter(User.id == user_id).one_or_none()
    if not user:
        raise ResourceNotFoundError()

    user_location = geography_repository.get_coordinates_from_address(user.address, user.postalCode)
    if not user_location:
        logger.info("Couldn't find user location", extra={"user_id": user.id})

    try:
        raw_response = recommendation_api.get_playlist(user, params=user_location)
    except recommendation_api.RecommendationApiTimeoutException:
        raise ApiErrors(status_code=504)
    except recommendation_api.RecommendationApiException:
        raise ApiErrors(status_code=502)

    try:
        decoded = json.loads(raw_response.decode(encoding="utf-8"))
    except json.decoder.JSONDecodeError as exc:
        logger.error("Failed decoding recommendation API response: %s", str(exc))
        raise ApiErrors(status_code=500)

    offer_ids = [int(offer_id) for offer_id in decoded.get("playlist_recommended_offers", [])]
    offer_ids = offer_ids[: settings.BREVO_NUMBER_OF_OFFERS_IN_EXTERNAL_FEED]
    offers = (
        db.session.query(offers_models.Offer)
        .filter(offers_models.Offer.id.in_(offer_ids))
        .options(joinedload(offers_models.Offer.mediations))
        .options(joinedload(offers_models.Offer.product).joinedload(offers_models.Product.productMediations))
        .all()
    )

    return serializers.BrevoOffersResponse(
        offers=[
            serializers.RecommendedOffer(
                image=offer.thumbUrl,
                name=offer.name,
                url=offer_app_link(offer),
            )
            for offer in offers
        ]
    )
