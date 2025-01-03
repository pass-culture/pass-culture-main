import logging

from flask_login import current_user
from flask_login import login_required

from pcapi.core.offers import exceptions
import pcapi.core.offers.api as offers_api
import pcapi.core.offers.repository as offers_repository
import pcapi.core.offers.validation as offers_validation
from pcapi.models import api_errors
from pcapi.repository import atomic
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import headline_offer_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils import rest

from . import blueprint


logger = logging.getLogger(__name__)


@private_api.route("/offers/headline", methods=["POST"])
@login_required
@spectree_serialize(
    on_success_status=204,
    api=blueprint.pro_private_schema,
)
@atomic()
def make_offer_headline_from_offers(body: headline_offer_serialize.HeadlineOfferCreationBodyModel) -> None:

    offer = offers_repository.get_offer_by_id(body.offer_id, load_options=["headline_offer"])

    if not offer:
        raise api_errors.ResourceNotFoundError
    offerer_id = offer.venue.managingOffererId

    rest.check_user_has_access_to_offerer(current_user, offerer_id)
    try:
        offers_validation.check_offerer_is_eligible_for_headline_offers(offerer_id)
        offers_validation.check_offer_is_eligible_to_be_headline(offer)
    except (
        exceptions.OffererCanNotHaveHeadlineOffer,
        exceptions.VirtualOfferCanNotBeHeadline,
    ) as error:
        messages = {
            exceptions.OffererCanNotHaveHeadlineOffer: "Vous ne pouvez pas créer d'offre à la une sur une entité juridique possédant plusieurs structures",
            exceptions.VirtualOfferCanNotBeHeadline: "Une offre virtuelle ne peut pas être mise à la une",
        }
        raise api_errors.ApiErrors(
            errors={"global": [messages[type(error)]]},
            status_code=400,
        )

    try:
        offers_api.make_offer_headline(offer)
    except (
        exceptions.OfferHasAlreadyAnActiveHeadlineOffer,
        exceptions.VenueHasAlreadyAnActiveHeadlineOffer,
        exceptions.InactiveOfferCanNotBeHeadline,
    ) as error:
        messages = {
            exceptions.OfferHasAlreadyAnActiveHeadlineOffer: "Cette offre est déjà mise à la une",
            exceptions.VenueHasAlreadyAnActiveHeadlineOffer: "Cette structure possède déjà une offre à la une",
            exceptions.InactiveOfferCanNotBeHeadline: "Cette offre est inactive et ne peut pas être mise à la une",
        }
        raise api_errors.ApiErrors(
            errors={"global": [messages[type(error)]]},
            status_code=400,
        )


@private_api.route("/offers/delete_headline", methods=["POST"])
@login_required
@spectree_serialize(
    on_success_status=204,
    api=blueprint.pro_private_schema,
)
@atomic()
def delete_headline_offer(body: headline_offer_serialize.HeadlineOfferDeleteBodyModel) -> None:
    rest.check_user_has_access_to_offerer(current_user, body.offerer_id)
    if active_headline_offer := offers_repository.get_offerers_active_headline_offer(body.offerer_id):
        offers_api.remove_headline_offer(active_headline_offer)
