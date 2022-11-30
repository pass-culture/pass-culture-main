import logging

from pcapi import repository
from pcapi import settings
from pcapi.core.finance import utils as finance_utils
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.models import api_errors
from pcapi.serialization.decorator import spectree_serialize
from pcapi.validation.routes.users_authentifications import api_key_required
from pcapi.validation.routes.users_authentifications import current_api_key

from . import blueprint
from . import serialization


logger = logging.getLogger(__name__)

PRODUCT_OFFERS_TAG = "Product offers"


def _retrieve_venue_from_location(
    location: serialization.DigitalLocation | serialization.PhysicalLocation,
) -> offerers_models.Venue:
    offerer_id = current_api_key.offererId  # type: ignore[attr-defined]
    if isinstance(location, serialization.PhysicalLocation):
        venue = offerers_models.Venue.query.filter(
            offerers_models.Venue.id == location.venue_id,
            offerers_models.Venue.managingOffererId == offerer_id,
        ).one_or_none()
        if not venue:
            raise api_errors.ApiErrors(
                {"venueId": ["There is no venue with this id associated to your API key"]}, status_code=404
            )

    else:
        venue = offerers_models.Venue.query.filter(
            offerers_models.Venue.managingOffererId == offerer_id, offerers_models.Venue.isVirtual
        ).one_or_none()
        if not venue:
            logger.error("No digital venue found for offerer %s", offerer_id)
            raise api_errors.ApiErrors(
                {
                    "global": [
                        f"The digital venue associated to your API key could not be automatically determined. Please contact support at {settings.SUPPORT_PRO_EMAIL_ADDRESS}."
                    ]
                },
                status_code=400,
            )
    return venue


def _compute_extra_data(body: serialization.ProductOfferCreationBody) -> dict[str, str]:
    extra_data = {}
    for extra_data_field in serialization.ExtraDataModel.__fields__:
        field_value = getattr(body.category_related_fields, extra_data_field, None)
        if field_value:
            extra_data[extra_data_field] = field_value

    return extra_data


@blueprint.v1_blueprint.route("/products", methods=["POST"])
@spectree_serialize(api=blueprint.v1_schema, tags=[PRODUCT_OFFERS_TAG])
@api_key_required
def post_product_offer(body: serialization.ProductOfferCreationBody) -> serialization.OfferResponse:
    """
    Post a product offer.
    """
    venue = _retrieve_venue_from_location(body.location)

    try:
        with repository.transaction():
            offer = offers_api.create_offer(
                audio_disability_compliant=body.disability_compliance.audio_disability_compliant,
                booking_email=body.booking_email,
                description=body.description,
                external_ticket_office_url=body.external_ticket_office_url,
                extra_data=_compute_extra_data(body),
                is_duo=body.accept_double_bookings,
                mental_disability_compliant=body.disability_compliance.mental_disability_compliant,
                motor_disability_compliant=body.disability_compliance.motor_disability_compliant,
                name=body.name,
                subcategory_id=body.category_related_fields.subcategory_id,
                url=body.location.url if isinstance(body.location, serialization.DigitalLocation) else None,
                venue=venue,
                visual_disability_compliant=body.disability_compliance.visual_disability_compliant,
            )
            if body.stock:
                offers_api.create_stock(
                    offer=offer,
                    price=finance_utils.to_euros(body.stock.price),
                    quantity=body.stock.quantity if body.stock.quantity != "unlimited" else None,
                )

    except offers_exceptions.OfferCreationBaseException as error:
        raise api_errors.ApiErrors(error.errors, status_code=400)

    return serialization.OfferResponse.from_orm(offer)
