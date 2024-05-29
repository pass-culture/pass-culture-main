import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from pcapi.core.bookings import exceptions as booking_exceptions
from pcapi.core.educational import exceptions
from pcapi.core.educational import models
from pcapi.core.educational import repository
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import validation as offers_validation
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.serialization import collective_offers_serialize


if TYPE_CHECKING:
    from pcapi.routes.public.collective.serialization.offers import OfferVenueModel


def validate_offer_venue(offer_venue: "OfferVenueModel | None") -> None:
    if offer_venue is None:
        return
    errors = {}
    if offer_venue.addressType == collective_offers_serialize.OfferAddressType.OFFERER_VENUE:
        if offer_venue.venueId is None:
            errors["offerVenue.venueId"] = (
                "Ce champ est obligatoire si 'addressType' vaut "
                f"'{collective_offers_serialize.OfferAddressType.OFFERER_VENUE.value}'"
            )
    elif offer_venue.venueId is not None:
        errors["offerVenue.venueId"] = (
            "Ce champ est interdit si 'addressType' ne vaut pas "
            f"'{collective_offers_serialize.OfferAddressType.OFFERER_VENUE.value}'"
        )

    if offer_venue.addressType == collective_offers_serialize.OfferAddressType.OTHER:
        if not offer_venue.otherAddress:
            errors["offerVenue.otherAddress"] = (
                "Ce champ est obligatoire si 'addressType' vaut "
                f"'{collective_offers_serialize.OfferAddressType.OTHER.value}'"
            )
    elif offer_venue.otherAddress:
        errors["offerVenue.otherAddress"] = (
            "Ce champ est interdit si 'addressType' ne vaut pas "
            f"'{collective_offers_serialize.OfferAddressType.OTHER.value}'"
        )
    if errors:
        raise ApiErrors(
            errors=errors,
            status_code=404,
        )


def check_institution_fund(
    educational_institution_id: int,
    educational_year_id: str,
    booking_amount: Decimal,
    deposit: models.EducationalDeposit,
) -> None:
    spent_amount = repository.get_confirmed_collective_bookings_amount(educational_institution_id, educational_year_id)
    total_amount = booking_amount + spent_amount
    deposit.check_has_enough_fund(total_amount)


def check_ministry_fund(
    educational_year_id: str,
    booking_amount: Decimal,
    booking_date: datetime.datetime,
    ministry: models.Ministry | None,
) -> None:
    if booking_date.month < 9:
        return
    spent_amount = repository.get_confirmed_collective_bookings_amount_for_ministry(
        educational_year_id=educational_year_id, ministry=ministry
    )
    total_spent_amount = spent_amount + booking_amount
    yearly_available_amount = repository.get_ministry_budget_for_year(
        educational_year_id=educational_year_id, ministry=ministry
    )
    # on sptember-december period we only have 4/12 of the budget
    available_amount = yearly_available_amount / 3
    if total_spent_amount > available_amount:
        raise exceptions.InsufficientMinistryFund()


def check_collective_stock_is_bookable(stock: models.CollectiveStock) -> None:
    if not stock.isBookable:
        raise exceptions.StockNotBookable(stock.id)


def check_collective_booking_status(collective_booking: models.CollectiveBooking) -> None:
    if collective_booking.status == models.CollectiveBookingStatus.CANCELLED:
        raise exceptions.BookingIsCancelled()


def check_confirmation_limit_date_has_not_passed(booking: models.CollectiveBooking) -> None:
    if booking.has_confirmation_limit_date_passed():
        raise booking_exceptions.ConfirmationLimitDateHasPassed()


def check_collective_stock_is_editable(stock: models.CollectiveStock) -> None:
    offers_validation.check_validation_status(stock.collectiveOffer)
    for booking in stock.collectiveBookings:
        if booking.status is not models.CollectiveBookingStatus.CANCELLED:
            offers_validation.check_event_expiration(stock)
            break


def check_if_edition_lower_price_possible(stock: models.CollectiveStock, price: float) -> None:
    if price > float(stock.price):
        raise exceptions.PriceRequesteCantBedHigherThanActualPrice()


def check_collective_booking_status_pending(booking: models.CollectiveBooking) -> None:
    if booking.status is not models.CollectiveBookingStatus.PENDING:
        raise exceptions.CollectiveOfferStockBookedAndBookingNotPending(booking.status, booking.id)


def check_collective_offer_number_of_collective_stocks(
    collective_offer: models.CollectiveOffer,
) -> None:
    if collective_offer.collectiveStock:
        raise exceptions.CollectiveStockAlreadyExists()


def check_if_offer_is_not_public_api(offer: models.CollectiveOffer) -> None:
    if offer.providerId:
        raise exceptions.CollectiveOfferIsPublicApi()


def check_user_can_prebook_collective_stock(uai: str, stock: models.CollectiveStock) -> None:
    offer_institution = stock.collectiveOffer.institution
    if offer_institution is not None and offer_institution.institutionId != uai:
        raise exceptions.CollectiveStockNotBookableByUser()


def check_institution_id_exists(institution_id: int) -> None:
    if not models.EducationalInstitution.query.filter_by(id=institution_id).one_or_none():
        raise exceptions.EducationalInstitutionNotFound()


def check_if_offer_not_used_or_reimbursed(offer: models.CollectiveOffer) -> None:
    if offer.collectiveStock:
        for booking in offer.collectiveStock.collectiveBookings:
            if (
                booking.status is models.CollectiveBookingStatus.USED
                or booking.status is models.CollectiveBookingStatus.REIMBURSED
            ):
                raise offers_exceptions.OfferUsedOrReimbursedCantBeEdit()
