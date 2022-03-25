from typing import Tuple

from sqlalchemy.orm import joinedload

from pcapi.core.bookings.models import Booking
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import CollectiveOfferTemplate
from pcapi.core.educational.models import CollectiveStock
from pcapi.core.educational.models import EducationalBooking
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock


def verify_collective_bookings_duplication() -> Tuple[bool, list[int], list[int]]:
    print("Veryfing bookings...")

    missing_collective_bookings_booking_ids = []
    invalid_collective_bookings_booking_ids = []

    educational_bookings: list[EducationalBooking] = EducationalBooking.query.options(
        joinedload(EducationalBooking.booking)
    ).all()

    collective_bookings: list[CollectiveBooking] = CollectiveBooking.query.all()
    collective_bookings_per_id = {
        collective_booking.bookingId: collective_booking for collective_booking in collective_bookings
    }

    for educational_booking in educational_bookings:
        associated_collective_booking = collective_bookings_per_id.get(educational_booking.booking.id)

        if associated_collective_booking is None:
            missing_collective_bookings_booking_ids.append(educational_booking.booking.id)
            continue

        booking: Booking = educational_booking.booking

        data_to_verify = {
            "dateUsed": booking.dateUsed,
            "venueId": booking.venueId,
            "offererId": booking.offererId,
            "cancellationDate": booking.cancellationDate,
            "cancellationLimitDate": booking.cancellationLimitDate,
            "cancellationReason": booking.cancellationReason.value if booking.cancellationReason else None,
            "status": educational_booking.status.value if educational_booking.status else booking.status.value,
            "reimbursementDate": booking.reimbursementDate,
            "educationalInstitutionId": educational_booking.educationalInstitutionId,
            "educationalYearId": educational_booking.educationalYearId,
            "confirmationDate": educational_booking.confirmationDate,
            "confirmationLimitDate": educational_booking.confirmationLimitDate,
            "educationalRedactorId": educational_booking.educationalRedactorId,
        }

        for key, value in data_to_verify.items():
            if key == "cancellationReason":
                is_equal = (
                    associated_collective_booking.cancellationReason.value == value
                    if associated_collective_booking.cancellationReason
                    else associated_collective_booking.cancellationReason == value
                )
                if not is_equal:
                    invalid_collective_bookings_booking_ids.append(educational_booking.booking.id)
                    break

                continue

            if key == "status":
                is_equal = associated_collective_booking.status.value == value
                if not is_equal:
                    invalid_collective_bookings_booking_ids.append(educational_booking.booking.id)
                    break

                continue

            if getattr(associated_collective_booking, key) != value:
                invalid_collective_bookings_booking_ids.append(educational_booking.booking.id)
                break

    if len(missing_collective_bookings_booking_ids) > 0:
        print(
            f"\033[91mERROR: Missing duplicated collective bookings for ids: {missing_collective_bookings_booking_ids}\033[0m"
        )

    if len(invalid_collective_bookings_booking_ids) > 0:
        print(
            f"\033[91mERROR: Invalid duplicated collective bookings for ids: {invalid_collective_bookings_booking_ids}\033[0m"
        )

    if len(missing_collective_bookings_booking_ids) > 0 or len(invalid_collective_bookings_booking_ids) > 0:
        return (False, missing_collective_bookings_booking_ids, invalid_collective_bookings_booking_ids)

    return (True, missing_collective_bookings_booking_ids, invalid_collective_bookings_booking_ids)


def verify_collective_offers_duplication() -> Tuple[bool, list[int], list[int], list[int], list[int]]:
    print("Veryfing offers...")

    missing_collective_offers_offer_ids: list[int] = []
    invalid_collective_offers_offer_ids: list[int] = []
    missing_collective_offer_templates_offer_ids: list[int] = []
    invalid_collective_offer_templates_offer_ids: list[int] = []

    educational_offers: list[Offer] = (
        Offer.query.filter(Offer.isEducational == True).options(joinedload(Offer.stocks)).all()
    )

    collective_offers: list[CollectiveOffer] = CollectiveOffer.query.all()
    collective_offer_templates: list[CollectiveOfferTemplate] = CollectiveOfferTemplate.query.all()

    collective_offers_per_id = {collective_offer.offerId: collective_offer for collective_offer in collective_offers}
    collective_offer_templates_per_id = {
        collective_offer_template.offerId: collective_offer_template
        for collective_offer_template in collective_offer_templates
    }

    for educational_offer in educational_offers:
        is_showcase = educational_offer.extraData.get("isShowcase", False) if educational_offer.extraData else False

        array_of_ids = collective_offer_templates_per_id if is_showcase else collective_offers_per_id
        associated_collective_offer_or_offer_template = array_of_ids.get(educational_offer.id)

        if associated_collective_offer_or_offer_template is None:
            array_of_missing_ids = (
                missing_collective_offer_templates_offer_ids if is_showcase else missing_collective_offers_offer_ids
            )
            array_of_missing_ids.append(educational_offer.id)
            continue

        extraData: dict = educational_offer.extraData

        data_to_verify = {
            "isActive": educational_offer.isActive,
            "venueId": educational_offer.venueId,
            "name": educational_offer.name,
            "bookingEmail": educational_offer.bookingEmail,
            "description": educational_offer.description,
            "durationMinutes": educational_offer.durationMinutes,
            "subcategoryId": educational_offer.subcategoryId,
            "students": set(extraData.get("students", [])) if extraData else [],
            "contactEmail": extraData.get("contactEmail", None) if extraData else None,
            "contactPhone": extraData.get("contactPhone", None) if extraData else None,
            "offerVenue": extraData.get("offerVenue", None) if extraData else None,
        }

        if is_showcase:
            data_to_verify["priceDetail"] = (
                educational_offer.activeStocks[0].educationalPriceDetail if educational_offer.activeStocks else None
            )

        for key, value in data_to_verify.items():
            array_if_invalid_ids = (
                invalid_collective_offer_templates_offer_ids if is_showcase else invalid_collective_offers_offer_ids
            )

            if key == "students":
                collective_offer_students = set(
                    student.value for student in associated_collective_offer_or_offer_template.students
                )

                if collective_offer_students != value:
                    array_if_invalid_ids.append(educational_offer.id)
                    break

                continue

            if key == "offerVenue":
                offer_venue_data_to_verify = {
                    "addressType": value.get("addressType", None),
                    "otherAddress": value.get("otherAddress", None),
                    "venueId": value.get("venueId", None),
                }

                for offer_venue_key, offer_venue_value in offer_venue_data_to_verify.items():
                    if associated_collective_offer_or_offer_template.offerVenue[offer_venue_key] != offer_venue_value:
                        array_if_invalid_ids.append(educational_offer.id)
                        break

                continue

            if getattr(associated_collective_offer_or_offer_template, key) != value:
                array_if_invalid_ids.append(educational_offer.id)
                break

    if len(missing_collective_offer_templates_offer_ids) > 0:
        print(
            f"\033[91mERROR: Missing duplicated collective offer template for ids: {missing_collective_offer_templates_offer_ids}\033[0m"
        )

    if len(invalid_collective_offer_templates_offer_ids) > 0:
        print(
            f"\033[91mERROR: Invalid duplicated collective offer template for ids: {invalid_collective_offer_templates_offer_ids}\033[0m"
        )

    if len(missing_collective_offers_offer_ids) > 0:
        print(
            f"\033[91mERROR: Missing duplicated collective offer for ids: {missing_collective_offers_offer_ids}\033[0m"
        )

    if len(invalid_collective_offers_offer_ids) > 0:
        print(
            f"\033[91mERROR: Invalid duplicated collective offer for ids: {invalid_collective_offers_offer_ids}\033[0m"
        )

    if (
        len(missing_collective_offer_templates_offer_ids) > 0
        or len(invalid_collective_offer_templates_offer_ids) > 0
        or len(missing_collective_offers_offer_ids) > 0
        or len(invalid_collective_offers_offer_ids) > 0
    ):
        return (
            False,
            missing_collective_offer_templates_offer_ids,
            invalid_collective_offer_templates_offer_ids,
            missing_collective_offers_offer_ids,
            invalid_collective_offers_offer_ids,
        )

    return (
        True,
        missing_collective_offer_templates_offer_ids,
        invalid_collective_offer_templates_offer_ids,
        missing_collective_offers_offer_ids,
        invalid_collective_offers_offer_ids,
    )


def verify_collective_stocks_duplication() -> Tuple[bool, list[int], list[int]]:
    print("Veryfing stocks...")

    missing_collective_stocks_stock_ids: list[int] = []
    invalid_collective_stocks_stock_ids: list[int] = []

    educational_stocks: list[Stock] = (
        Stock.query.join(Stock.offer).filter(Offer.isEducational == True, Stock.isSoftDeleted == False).all()
    )

    collective_stocks: list[CollectiveStock] = CollectiveStock.query.all()
    collective_stocks_per_id = {collective_stock.stockId: collective_stock for collective_stock in collective_stocks}

    for educational_stock in educational_stocks:
        # if offer is showcase we dont check the stock because a CollectiveOfferTemplate does not have any stock
        if educational_stock.offer.extraData and educational_stock.offer.extraData.get("isShowcase", False) is True:
            continue

        associated_collective_stock = collective_stocks_per_id.get(educational_stock.id)

        if associated_collective_stock is None:
            missing_collective_stocks_stock_ids.append(educational_stock.id)
            continue

        data_to_verify = {
            "beginningDatetime": educational_stock.beginningDatetime,
            "price": educational_stock.price,
            "bookingLimitDatetime": educational_stock.bookingLimitDatetime,
            "numberOfTickets": educational_stock.numberOfTickets,
            "priceDetail": educational_stock.educationalPriceDetail,
        }

        for key, value in data_to_verify.items():
            if getattr(associated_collective_stock, key) != value:
                invalid_collective_stocks_stock_ids.append(educational_stock.id)
                break

    if len(missing_collective_stocks_stock_ids) > 0:
        print(
            f"\033[91mERROR: Missing duplicated collective stocks for ids: {missing_collective_stocks_stock_ids}\033[0m"
        )

    if len(invalid_collective_stocks_stock_ids) > 0:
        print(
            f"\033[91mERROR: Invalid duplicated collective stocks for ids: {invalid_collective_stocks_stock_ids}\033[0m"
        )

    if len(missing_collective_stocks_stock_ids) > 0 or len(invalid_collective_stocks_stock_ids) > 0:
        return (False, missing_collective_stocks_stock_ids, invalid_collective_stocks_stock_ids)

    return (True, missing_collective_stocks_stock_ids, invalid_collective_stocks_stock_ids)


def verify_collective_data_duplication() -> bool:
    (collective_bookings_verification_success, _, _) = verify_collective_bookings_duplication()
    (collective_offers_verification_success, _, _, _, _) = verify_collective_offers_duplication()
    (collective_stocks_verification_success, _, _) = verify_collective_stocks_duplication()

    if (
        collective_bookings_verification_success
        and collective_offers_verification_success
        and collective_stocks_verification_success
    ):
        return True

    return False
