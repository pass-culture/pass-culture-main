import datetime
import decimal
import logging
from unittest.mock import patch
import uuid

from pcapi.core.bookings import api as bookings_api
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import factories as finance_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.routes.backoffice.finance import validation


logger = logging.getLogger(__name__)


INDIVIDUAL_INCIDENT_PARAMS = [
    {
        "with_other_venue": True,
        "with_over_revenue_threshold_booking": True,
        "multiple_bookings": False,
        "force_debit_note": False,
        "is_partial": True,
        "comment": "Incident individuel partiel avec plusieurs barêmes",
    },
    {
        "with_other_venue": False,
        "with_over_revenue_threshold_booking": False,
        "multiple_bookings": False,
        "force_debit_note": False,
        "is_partial": False,
        "comment": "Incident individuel total",
    },
    {
        "with_other_venue": False,
        "with_over_revenue_threshold_booking": False,
        "multiple_bookings": True,
        "force_debit_note": False,
        "is_partial": False,
        "comment": "Incident individuel total sur plusieurs réservations",
    },
    {
        "with_other_venue": False,
        "with_over_revenue_threshold_booking": False,
        "multiple_bookings": False,
        "force_debit_note": True,
        "is_partial": True,
        "comment": "Incident individuel partiel avec note de débit",
    },
    {
        "with_other_venue": True,
        "with_over_revenue_threshold_booking": True,
        "multiple_bookings": False,
        "force_debit_note": True,
        "is_partial": False,
        "comment": "Incident individuel total avec plusieurs barêmes et note de débit",
    },
    {
        "with_other_venue": False,
        "with_over_revenue_threshold_booking": True,
        "multiple_bookings": True,
        "force_debit_note": True,
        "is_partial": False,
        "comment": "Incident individuel total sur plusieurs réservations, avec plusieurs barêmes et note de débit",
    },
]


def _check_individual_incident_params() -> None:
    for params in INDIVIDUAL_INCIDENT_PARAMS:
        if params["is_partial"] and params["multiple_bookings"]:
            raise ValueError("Incident not created: an incident can't be partial and have multiple bookings")


_check_individual_incident_params()

COLLECTIVE_INCIDENT_PARAMS = [
    {
        "with_other_venue": False,
        "with_over_revenue_threshold_booking": True,
        "multiple_bookings": False,
        "force_debit_note": False,
        "comment": "Incident collectif total avec plusieurs barêmes",
    },
    {
        "with_other_venue": False,
        "with_over_revenue_threshold_booking": False,
        "multiple_bookings": False,
        "force_debit_note": True,
        "comment": "Incident collectif total avec note de débit",
    },
]


def _create_one_individual_incident(
    offerer: offerers_models.Offerer,
    pro: users_models.User,
    iteration: int,
    with_other_venue: bool,
    with_over_revenue_threshold_booking: bool,
    multiple_bookings: bool,
    force_debit_note: bool,
    is_partial: bool,
    comment: str,
) -> None:
    bank_account = finance_factories.BankAccountFactory(offerer=offerer)
    name_suffix = " - note de débit" if force_debit_note else ""
    venue = offerers_factories.VenueFactory(
        name=f"{iteration} - Lieu avec beaucoup d'incidents{name_suffix}",
        managingOfferer=offerer,
        pricing_point="self",
        bank_account=bank_account,
    )

    special_bookings = []
    if with_over_revenue_threshold_booking:
        # This is a quick way to have a Venue reach the revenue threshold to reach the next ReimbursementRule
        special_bookings = bookings_factories.BookingFactory.create_batch(
            1,
            stock__offer__venue=venue,
            stock__price=decimal.Decimal("19990"),  # 19.99k€
            user__firstName=f"martin.cident_{uuid.uuid4()}@example.com",
            user__deposit__source="create_industrial_incidents() in industrial sandbox",
            user__deposit__amount=decimal.Decimal("20300"),  # 20.3k€
        )

    other_venue = None
    if with_other_venue:
        other_venue = offerers_factories.VenueFactory(
            name=f"{iteration} - Autre lieu avec beaucoup d'incidents",
            managingOfferer=offerer,
            pricing_point=venue,
            bank_account=bank_account,
        )

    incident_bookings = bookings_factories.BookingFactory.create_batch(
        size=2 if multiple_bookings else 1,
        stock__offer__venue=other_venue or venue,
        stock__price=decimal.Decimal("30"),
        user__deposit__source="create_industrial_incidents() in industrial sandbox",
    )

    bookings = special_bookings + incident_bookings
    for booking in bookings:
        bookings_api.mark_as_used(
            booking=booking,
            validation_author_type=bookings_models.BookingValidationAuthorType.OFFERER,
        )
        for finance_event in booking.finance_events:
            finance_api.price_event(finance_event)

    # Mark incident bookings as `REIMBURSED`
    batch = finance_api.generate_cashflows_and_payment_files(cutoff=datetime.datetime.utcnow())
    finance_api.generate_invoices(batch)

    assert {b.status for b in bookings} == {bookings_models.BookingStatus.REIMBURSED}, [
        (b.id, b.status) for b in bookings
    ]

    if not force_debit_note:
        # Generate new "used" booking to be visible on the invoice/payment files
        new_bookings = bookings_factories.BookingFactory.create_batch(
            size=3,
            stock__offer__venue=venue,
            stock__price=decimal.Decimal("20") + decimal.Decimal(iteration),
            user__firstName=f"valent.incident_{uuid.uuid4()}@example.com",
        )
        for booking in new_bookings:
            bookings_api.mark_as_used(
                booking=booking,
                validation_author_type=bookings_models.BookingValidationAuthorType.OFFERER,
            )
            finance_api.price_event(booking.finance_events[0])

    amount = None if len(bookings) > 1 else decimal.Decimal("10")
    check_bookings = validation.check_incident_bookings(incident_bookings)
    check_amount = True if amount is None else validation.check_total_amount(amount, incident_bookings)
    if not (check_bookings and check_amount):
        raise ValueError("Couldn't create overpayment incident, invalid parameters")

    # Create the overpayment incidents and validate them
    finance_incident = finance_api.create_overpayment_finance_incident(
        bookings=incident_bookings,
        author=pro,
        origin=comment,
        amount=amount,
    )
    finance_api.validate_finance_overpayment_incident(
        finance_incident=finance_incident,
        force_debit_note=force_debit_note,
        author=pro,
    )
    for booking_finance_incident in finance_incident.booking_finance_incidents:
        for finance_event in booking_finance_incident.finance_events:
            finance_api.price_event(finance_event)

    batch = finance_api.generate_cashflows_and_payment_files(cutoff=datetime.datetime.utcnow())
    if not force_debit_note:
        finance_api.generate_invoices(batch)
    finance_api.generate_debit_notes(batch)


def _create_one_collective_incident(
    offerer: offerers_models.Offerer,
    pro: users_models.User,
    iteration: int,
    with_other_venue: bool,
    with_over_revenue_threshold_booking: bool,
    multiple_bookings: bool,
    force_debit_note: bool,
    comment: str,
) -> None:
    bank_account = finance_factories.BankAccountFactory(offerer=offerer)
    venue = offerers_factories.VenueFactory(
        name=f"{iteration} - Lieu avec beaucoup d'incidents collectifs",
        managingOfferer=offerer,
        pricing_point="self",
        bank_account=bank_account,
    )
    # TODO(jeremieb): find a better solution to avoid institution creation
    # from UsedCollectiveBookingFactory
    institution = (
        educational_models.EducationalInstitution.query.first() or educational_factories.EducationalInstitutionFactory()
    )
    year = educational_models.EducationalYear.query.first() or educational_factories.EducationalYearFactory()
    deposit = (
        institution.deposits[0]
        if institution.deposits
        else educational_factories.EducationalDepositFactory(educationalInstitution=institution, educationalYear=year)
    )
    other_venue = None
    if with_other_venue:
        other_venue = offerers_factories.VenueFactory(
            name=f"{iteration} - Autre lieu avec beaucoup d'incidents collectifs",
            managingOfferer=offerer,
            pricing_point=venue,
            bank_account=bank_account,
        )

    special_bookings = []
    if with_over_revenue_threshold_booking:
        # This is a quick way to have a Venue reach the revenue threshold to reach the next ReimbursementRule
        special_bookings = educational_factories.UsedCollectiveBookingFactory.create_batch(
            1,
            collectiveStock__collectiveOffer__venue=venue,
            collectiveStock__price=decimal.Decimal("19990"),
            collectiveStock__beginningDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=1),
            educationalInstitution=deposit.educationalInstitution,
            educationalYear=deposit.educationalYear,
        )

    incident_bookings = educational_factories.UsedCollectiveBookingFactory.create_batch(
        size=2 if multiple_bookings else 1,
        collectiveStock__collectiveOffer__venue=other_venue or venue,
        collectiveStock__price=decimal.Decimal("30"),
        collectiveStock__beginningDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=1),
        educationalInstitution=deposit.educationalInstitution,
        educationalYear=deposit.educationalYear,
    )

    bookings = special_bookings + incident_bookings
    for booking in bookings:
        finance_event = finance_factories.UsedCollectiveBookingFinanceEventFactory(
            venue=venue,
            collectiveBooking=booking,
        )
        finance_api.price_event(finance_event)

    # Mark incident bookings as `REIMBURSED`
    batch = finance_api.generate_cashflows_and_payment_files(cutoff=datetime.datetime.utcnow())
    finance_api.generate_invoices(batch)

    assert {booking.status for booking in bookings} == {educational_models.CollectiveBookingStatus.REIMBURSED}, [
        (booking.id, booking.status) for booking in bookings
    ]

    # Generate new "used" booking to be visible on the invoice/payment files
    for i in range(3):
        new_booking = educational_factories.UsedCollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue=other_venue or venue,
            collectiveStock__price=decimal.Decimal("20") + decimal.Decimal(i),
            collectiveStock__beginningDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=1),
            educationalInstitution=deposit.educationalInstitution,
            educationalYear=deposit.educationalYear,
        )
        finance_event = finance_factories.UsedCollectiveBookingFinanceEventFactory(
            venue=venue,
            collectiveBooking=new_booking,
        )
        finance_api.price_event(finance_event)

    for booking in incident_bookings:
        finance_incident = finance_api.create_overpayment_finance_incident_collective_booking(
            booking=booking,
            author=pro,
            origin=comment,
        )
        with patch("pcapi.core.finance.api.educational_api_booking.notify_reimburse_collective_booking"):
            finance_api.validate_finance_overpayment_incident(
                finance_incident=finance_incident,
                force_debit_note=force_debit_note,
                author=pro,
            )
        for booking_finance_incident in finance_incident.booking_finance_incidents:
            for finance_event in booking_finance_incident.finance_events:
                finance_api.price_event(finance_event)

    batch = finance_api.generate_cashflows_and_payment_files(cutoff=datetime.datetime.utcnow())
    finance_api.generate_invoices(batch)
    finance_api.generate_debit_notes(batch)


def create_industrial_incidents() -> None:
    offerer = offerers_factories.OffererFactory(name="Structure avec beaucoup d'incidents")
    pro = users_factories.ProFactory(email="pctest.pro.incidents@example.com")
    offerers_factories.UserOffererFactory(offerer=offerer, user=pro)

    for i, params in enumerate(INDIVIDUAL_INCIDENT_PARAMS):
        _create_one_individual_incident(
            offerer,
            pro,
            i,
            bool(params["with_other_venue"]),
            bool(params["with_over_revenue_threshold_booking"]),
            bool(params["multiple_bookings"]),
            bool(params["force_debit_note"]),
            bool(params["is_partial"]),
            str(params["comment"]),
        )
        logger.info("Created individual incident")

    for i, params in enumerate(COLLECTIVE_INCIDENT_PARAMS):
        _create_one_collective_incident(
            offerer,
            pro,
            i,
            bool(params["with_other_venue"]),
            bool(params["with_over_revenue_threshold_booking"]),
            bool(params["multiple_bookings"]),
            bool(params["force_debit_note"]),
            str(params["comment"]),
        )
        logger.info("Created collective incident")
