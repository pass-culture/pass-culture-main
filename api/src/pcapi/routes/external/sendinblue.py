import json
import logging

from flask import abort
from flask import request
from sqlalchemy.orm import joinedload

from pcapi import settings
import pcapi.connectors.recommendation as recommendation_api
from pcapi.core.external.attributes.api import update_external_user
import pcapi.core.geography.repository as geography_repository
from pcapi.core.history import api as history_api
from pcapi.core.offers import models as offers_models
from pcapi.core.users.models import User
from pcapi.core.users.repository import find_user_by_email
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.feature import FeatureToggle
from pcapi.repository import repository
from pcapi.routes.apis import public_api
from pcapi.routes.external.serialization import sendinblue as serializers
from pcapi.serialization.decorator import spectree_serialize
from pcapi.validation.routes.users_authentifications import brevo_webhook


logger = logging.getLogger(__name__)


def _toggle_marketing_email_subscription(subscribe: bool) -> None:
    user_email = request.json.get("email")  # type: ignore[union-attr]
    if not user_email:
        raise ApiErrors(
            {"email": "Email missing in request payload"},
            status_code=400,
        )

    user = find_user_by_email(user_email)
    if user is None:
        raise ApiErrors({"User": "user not found for email %s" % user_email}, status_code=400)

    history_api.ObjectUpdateSnapshot(user, user).trace_update(
        {"marketing_email": subscribe},
        target=user.get_notification_subscriptions(),
        field_name_template="notificationSubscriptions.{}",
    ).add_action()

    user.set_marketing_email_subscription(subscribe)

    repository.save(user)

    # Sendinblue is already up-to-date from originating automation, update marketing preference in Batch
    update_external_user(user, skip_sendinblue=True)


@public_api.route("/webhooks/sendinblue/unsubscribe", methods=["POST"])
@spectree_serialize(on_success_status=204)
def sendinblue_unsubscribe_user() -> None:
    """
    Automation scenario is configured in Sendinblue to call this webhook after user unsubscribes.
    Blacklist status and MARKETING_EMAIL_SUBSCRIPTION are updated in the scenario, so we don't need to sync them again.
    """
    _toggle_marketing_email_subscription(False)


@public_api.route("/webhooks/sendinblue/subscribe", methods=["POST"])
@spectree_serialize(on_success_status=204)
def sendinblue_subscribe_user() -> None:
    """
    Automation scenario is configured in Sendinblue to call this webhook after user unsubscribes.
    Blacklist status and MARKETING_EMAIL_SUBSCRIPTION are updated in the scenario, so we don't need to sync them again.
    """
    _toggle_marketing_email_subscription(True)


@public_api.route("/webhooks/sendinblue/importcontacts/<int:list_id>/<int:iteration>", methods=["POST"])
@spectree_serialize(on_success_status=204)
def sendinblue_notify_importcontacts(list_id: int, iteration: int) -> None:
    """
    Called by Sendinblue once an import process is finished.
    https://developers.brevo.com/reference/importcontacts-1

    Unfortunately there is no information in query string and the body is empty, so we can't check a process id.
    The id of the list in Sendinblue is added to the URL when set in notifyUrl so we can at least print the list id.
    This webhook is for investigation purpose only.
    """
    logger.info("ContactsApi->import_contacts finished", extra={"list_id": list_id, "iteration": iteration})


@public_api.route("/webhooks/brevo/recommendations/<int:user_id>", methods=["GET"])
@brevo_webhook
@spectree_serialize(
    on_success_status=200, response_model=serializers.BrevoOffersResponse, on_error_statuses=[404, 500, 502, 504]
)
def brevo_get_user_recommendations(user_id: int) -> serializers.BrevoOffersResponse:
    """This route is called by Brevo on sending an email to a user to get recommended offers."""

    if not FeatureToggle.WIP_ENABLE_BREVO_RECOMMENDATION_ROUTE.is_active():
        abort(404)

    user = db.session.query(User).filter(User.id == user_id).one_or_none()
    if not user:
        abort(404)

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

    return serializers.BrevoOffersResponse(offers=[serializers.RecommendedOffer.from_orm(offer) for offer in offers])
