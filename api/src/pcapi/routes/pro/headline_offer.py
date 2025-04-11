import logging

from flask_login import current_user
from flask_login import login_required

from pcapi.core.offers import exceptions
import pcapi.core.offers.api as offers_api
import pcapi.core.offers.repository as offers_repository
from pcapi.models import api_errors
from pcapi.repository import atomic
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import headline_offer_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils import rest

from . import blueprint


logger = logging.getLogger(__name__)


@private_api.route("/offers/upsert_headline", methods=["POST"])
@login_required
@spectree_serialize(
    response_model=headline_offer_serialize.HeadLineOfferResponseModel,
    on_success_status=201,
    api=blueprint.pro_private_schema,
)
@atomic()
def upsert_headline_offer(
    body: headline_offer_serialize.HeadlineOfferCreationBodyModel,
) -> headline_offer_serialize.HeadLineOfferResponseModel:

    offer = offers_repository.get_offer_by_id(body.offer_id, load_options=["headline_offer", "venue"])

    if not offer:
        raise api_errors.ResourceNotFoundError
    offerer_id = offer.venue.managingOffererId

    rest.check_user_has_access_to_offerer(current_user, offerer_id)
    try:
        headline_offer = offers_api.upsert_headline_offer(offer)
    except exceptions.CannotRemoveHeadlineOffer:
        raise api_errors.ApiErrors(
            errors={"global": ["Une erreur est survenue au moment du retrait de l'offre à la une"]},
        )
    except exceptions.OffererCanNotHaveHeadlineOffer:
        raise api_errors.ApiErrors(
            errors={
                "global": [
                    "Vous ne pouvez pas créer d'offre à la une sur une entité juridique possédant plusieurs structures"
                ]
            },
        )
    except exceptions.VirtualOfferCanNotBeHeadline:
        raise api_errors.ApiErrors(
            errors={"global": ["Une offre virtuelle ne peut pas être mise à la une"]},
        )
    except exceptions.OfferHasAlreadyAnActiveHeadlineOffer:
        raise api_errors.ApiErrors(
            errors={"global": ["Cette offre est déjà mise à la une"]},
        )
    except exceptions.VenueHasAlreadyAnActiveHeadlineOffer:
        raise api_errors.ApiErrors(
            errors={"global": ["Cette structure possède déjà une offre à la une"]},
        )
    except exceptions.InactiveOfferCanNotBeHeadline:
        raise api_errors.ApiErrors(
            errors={"global": ["Cette offre est inactive et ne peut pas être mise à la une"]},
        )
    except exceptions.OfferWithoutImageCanNotBeHeadline:
        raise api_errors.ApiErrors(
            errors={"global": ["Une offre doit avoir une image pour être mise à la une"]},
        )
    return headline_offer_serialize.HeadLineOfferResponseModel.from_orm(headline_offer.offer)


@private_api.route("/offers/delete_headline", methods=["POST"])
@login_required
@spectree_serialize(
    on_success_status=204,
    api=blueprint.pro_private_schema,
)
@atomic()
def delete_headline_offer(body: headline_offer_serialize.HeadlineOfferDeleteBodyModel) -> None:
    rest.check_user_has_access_to_offerer(current_user, body.offerer_id)
    if active_headline_offer := offers_repository.get_current_headline_offer(body.offerer_id):
        try:
            offers_api.remove_headline_offer(active_headline_offer)
            logger.info(
                "Headline Offer Deactivation",
                extra={
                    "analyticsSource": "app-pro",
                    "HeadlineOfferId": active_headline_offer.id,
                    "Reason": "Headline offer has been deactivated by user",
                },
                technical_message_id="headline_offer_deactivation",
            )
        except exceptions.CannotRemoveHeadlineOffer:
            raise api_errors.ApiErrors(
                errors={"global": ["Une erreur est survenue au moment du retrait de l'offre à la une"]},
            )
