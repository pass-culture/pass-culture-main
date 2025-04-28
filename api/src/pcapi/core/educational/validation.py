import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from pcapi.core.bookings import exceptions as booking_exceptions
from pcapi.core.educational import exceptions
from pcapi.core.educational import models
from pcapi.core.educational import repository
from pcapi.core.educational.api import national_program as national_program_api
from pcapi.models import api_errors
from pcapi.models import db


if TYPE_CHECKING:
    from pcapi.routes.public.collective.serialization.offers import OfferVenueModel


def validate_offer_venue(offer_venue: "OfferVenueModel | None") -> None:
    if offer_venue is None:
        return
    errors = {}
    if offer_venue.addressType == models.OfferAddressType.OFFERER_VENUE:
        if offer_venue.venueId is None:
            errors["offerVenue.venueId"] = (
                "Ce champ est obligatoire si 'addressType' vaut " f"'{models.OfferAddressType.OFFERER_VENUE.value}'"
            )
    elif offer_venue.venueId is not None:
        errors["offerVenue.venueId"] = (
            "Ce champ est interdit si 'addressType' ne vaut pas " f"'{models.OfferAddressType.OFFERER_VENUE.value}'"
        )

    if offer_venue.addressType == models.OfferAddressType.OTHER:
        if not offer_venue.otherAddress:
            errors["offerVenue.otherAddress"] = (
                "Ce champ est obligatoire si 'addressType' vaut " f"'{models.OfferAddressType.OTHER.value}'"
            )
    elif offer_venue.otherAddress:
        errors["offerVenue.otherAddress"] = (
            "Ce champ est interdit si 'addressType' ne vaut pas " f"'{models.OfferAddressType.OTHER.value}'"
        )
    if errors:
        raise api_errors.ApiErrors(errors=errors, status_code=404)


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
        raise exceptions.CollectiveStockNotBookable()


def check_collective_booking_status(collective_booking: models.CollectiveBooking) -> None:
    if collective_booking.status == models.CollectiveBookingStatus.CANCELLED:
        raise exceptions.BookingIsCancelled()


def check_confirmation_limit_date_has_not_passed(booking: models.CollectiveBooking) -> None:
    if booking.has_confirmation_limit_date_passed():
        raise booking_exceptions.ConfirmationLimitDateHasPassed()


def check_collective_booking_status_pending(booking: models.CollectiveBooking) -> None:
    if booking.status is not models.CollectiveBookingStatus.PENDING:
        raise exceptions.CollectiveOfferStockBookedAndBookingNotPending(booking.status, booking.id)


def check_collective_offer_number_of_collective_stocks(
    collective_offer: models.CollectiveOffer,
) -> None:
    if collective_offer.collectiveStock:
        raise exceptions.CollectiveStockAlreadyExists()


def check_user_can_prebook_collective_stock(uai: str, stock: models.CollectiveStock) -> None:
    offer_institution = stock.collectiveOffer.institution
    if offer_institution is not None and offer_institution.institutionId != uai:
        raise exceptions.CollectiveStockNotBookableByUser()


def check_institution_id_exists(institution_id: int) -> models.EducationalInstitution | None:
    institution = db.session.query(models.EducationalInstitution).get(institution_id)
    if not institution:
        raise exceptions.EducationalInstitutionNotFound()
    return institution


def check_collective_offer_action_is_allowed(
    offer: models.CollectiveOffer, action: models.CollectiveOfferAllowedAction
) -> None:
    if action not in offer.allowedActions:
        raise exceptions.CollectiveOfferForbiddenAction(action=action)


def check_collective_offer_template_action_is_allowed(
    offer: models.CollectiveOfferTemplate, action: models.CollectiveOfferTemplateAllowedAction
) -> None:
    if action not in offer.allowedActions:
        raise exceptions.CollectiveOfferTemplateForbiddenAction(action=action)


def check_collective_offer_name_length_is_valid(offer_name: str) -> None:
    if len(offer_name) > models.MAX_COLLECTIVE_NAME_LENGTH:
        raise api_errors.ApiErrors(
            errors={
                "name": [f"Le titre de l’offre doit faire au maximum {models.MAX_COLLECTIVE_NAME_LENGTH} caractères."]
            }
        )


def check_collective_offer_description_length_is_valid(offer_description: str) -> None:
    if len(offer_description) > models.MAX_COLLECTIVE_DESCRIPTION_LENGTH:
        raise api_errors.ApiErrors(
            {
                "description": [
                    f"La description de l’offre doit faire au maximum {models.MAX_COLLECTIVE_DESCRIPTION_LENGTH} caractères."
                ]
            }
        )


def check_start_and_end_dates_in_same_educational_year(
    start_datetime: datetime.datetime, end_datetime: datetime.datetime
) -> None:
    start_year = repository.find_educational_year_by_date(start_datetime)
    if not start_year:
        raise exceptions.StartEducationalYearMissing()

    if start_datetime == end_datetime:
        return

    end_year = repository.find_educational_year_by_date(end_datetime)
    if not end_year:
        raise exceptions.EndEducationalYearMissing()

    if start_year.id != end_year.id:
        raise exceptions.StartAndEndEducationalYearDifferent()


def check_start_is_before_end(start_datetime: datetime.datetime, end_datetime: datetime.datetime) -> None:
    # each date may have a timezone (if coming e.g from a route input) or not (if coming from the DB)
    # so we need to set a timezone to each date in order to compare them

    # if start or end datetime does not have a timezone, it is assumed to be UTC
    check_start = start_datetime
    if check_start.tzinfo is None:
        check_start = check_start.replace(tzinfo=datetime.timezone.utc)

    check_end = end_datetime
    if check_end.tzinfo is None:
        check_end = check_end.replace(tzinfo=datetime.timezone.utc)

    if check_end < check_start:
        raise exceptions.EndDatetimeBeforeStartDatetime()


def validate_national_program(
    national_program_id: int | None,
    domains: list[models.EducationalDomain] | None,
    check_program_is_active: bool = True,
) -> None:
    if not national_program_id:
        return

    if not domains:
        raise exceptions.MissingDomains()

    national_program = national_program_api.get_national_program(national_program_id)

    if not national_program:
        raise exceptions.NationalProgramNotFound()

    if check_program_is_active and not national_program.isActive:
        raise exceptions.InactiveNationalProgram()

    valid_national_program_ids = {np.id for domain in domains for np in domain.nationalPrograms}
    if national_program_id not in valid_national_program_ids:
        raise exceptions.IllegalNationalProgram()
