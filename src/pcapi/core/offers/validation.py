from datetime import datetime
from io import BytesIO
from typing import Optional

from PIL import Image

from pcapi.models import Offer
from pcapi.models import Stock
from pcapi.models.api_errors import ApiErrors

from . import exceptions


EDITABLE_FIELDS_FOR_ALLOCINE_OFFER = {"isDuo"}
EDITABLE_FIELDS_FOR_ALLOCINE_STOCK = {"bookingLimitDatetime", "price", "quantity"}


def check_offer_is_editable(offer: Offer):
    if not offer.isEditable:
        error = ApiErrors()
        error.status_code = 400
        error.add_error("global", "Les offres importées ne sont pas modifiables")
        raise error


def check_update_only_allowed_offer_fields_for_allocine_offer(updated_fields: set) -> None:
    rejected_fields = updated_fields - EDITABLE_FIELDS_FOR_ALLOCINE_OFFER
    if rejected_fields:
        api_error = ApiErrors()
        for field in rejected_fields:
            api_error.add_error(field, "Vous ne pouvez pas modifier ce champ")

        raise api_error


def check_stocks_are_editable_for_offer(offer: Offer) -> None:
    if offer.isFromProvider:
        api_errors = ApiErrors()
        api_errors.add_error("global", "Les offres importées ne sont pas modifiables")
        raise api_errors


def check_required_dates_for_stock(
    offer: Offer,
    beginning: Optional[datetime],
    booking_limit_datetime: Optional[datetime],
) -> None:
    if offer.isThing:
        if beginning:
            raise ApiErrors(
                {
                    "global": [
                        "Impossible de mettre une date de début si l'offre " "ne porte pas sur un événement",
                    ]
                }
            )
    else:
        if not beginning:
            raise ApiErrors({"beginningDatetime": ["Ce paramètre est obligatoire"]})

        if not booking_limit_datetime:
            raise ApiErrors({"bookingLimitDatetime": ["Ce paramètre est obligatoire"]})


def check_stock_is_updatable(stock: Stock) -> None:
    check_offer_is_editable(stock.offer)

    if stock.isEventExpired:
        api_errors = ApiErrors()
        api_errors.add_error("global", "Les événements passés ne sont pas modifiables")
        raise api_errors


def check_stock_is_deletable(stock: Stock) -> None:
    check_offer_is_editable(stock.offer)

    if not stock.isEventDeletable:
        raise exceptions.TooLateToDeleteStock()


def check_update_only_allowed_stock_fields_for_allocine_offer(updated_fields: set) -> None:
    if not updated_fields.issubset(EDITABLE_FIELDS_FOR_ALLOCINE_STOCK):
        api_errors = ApiErrors()
        api_errors.status_code = 400
        api_errors.add_error("global", "Pour les offres importées, certains champs ne sont pas modifiables")
        raise api_errors


def check_mediation_thumb_quality(image_as_bytes: bytes) -> None:
    image = Image.open(BytesIO(image_as_bytes))
    if image.width < 400 or image.height < 400:
        raise ApiErrors({"thumb": ["L'image doit faire 400 * 400 px minimum"]})
