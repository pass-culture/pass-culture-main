from datetime import datetime
from typing import Optional

from pcapi.models import Offer
from pcapi.models import StockSQLEntity
from pcapi.models.api_errors import ApiErrors

from . import exceptions


EDITABLE_FIELDS_FOR_ALLOCINE_STOCK = {"bookingLimitDatetime", "price", "quantity"}


def check_offer_is_editable(offer: Offer):
    if not offer.isEditable:
        error = ApiErrors()
        error.status_code = 400
        error.add_error("global", "Les offres importées ne sont pas modifiables")
        raise error


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


def check_stock_is_updatable(stock: StockSQLEntity) -> None:
    check_offer_is_editable(stock.offer)

    if stock.isEventExpired:
        api_errors = ApiErrors()
        api_errors.add_error("global", "Les événements passés ne sont pas modifiables")
        raise api_errors


def check_stock_is_deletable(stock: StockSQLEntity) -> None:
    check_offer_is_editable(stock.offer)

    if not stock.isEventDeletable:
        raise exceptions.TooLateToDeleteStock()


def check_update_only_allowed_stock_fields_for_allocine_offer(updated_fields: set) -> None:
    if not updated_fields.issubset(EDITABLE_FIELDS_FOR_ALLOCINE_STOCK):
        api_errors = ApiErrors()
        api_errors.status_code = 400
        api_errors.add_error("global", "Pour les offres importées, certains champs ne sont pas modifiables")
        raise api_errors
