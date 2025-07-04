import datetime
import decimal

from pcapi.core.bookings import api as bookings_api
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.api import booking as educational_api_booking
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.routes.backoffice.finance import validation
from pcapi.sandboxes.scripts.utils.helpers import log_func_duration
from pcapi.utils.chunks import get_chunks


def _price_event(event: finance_models.FinanceEvent) -> None:
    pricing = finance_api._price_event(event)
    db.session.add(pricing)
    event.status = finance_models.FinanceEventStatus.PRICED
    db.session.commit()


def _create_total_commercial_gesture_individual_offer(
    author_user: users_models.User,
    venue: offerers_models.Venue,
    users_count: int,
) -> None:
    # Create the users
    users = users_factories.BeneficiaryGrant18Factory.create_batch(users_count)

    # Empty the balances
    for user in users:
        booking = bookings_factories.BookingFactory.create(
            user=user,
            quantity=10,
            stock__price=decimal.Decimal("5.0"),
            stock__offer__venue=venue,
        )  # 50€
        bookings_api.mark_as_used(
            booking=booking,
            validation_author_type=bookings_models.BookingValidationAuthorType.OFFERER,
        )
        _price_event(booking.finance_events[0])

    # Create the bookings and cancel them
    bookings = []
    for i, user in enumerate(users):
        booking = bookings_factories.BookingFactory.create(
            user=user,
            stock__offer__venue=venue,
            stock__price=decimal.Decimal("10.1") + decimal.Decimal(i),
            quantity=1,
        )
        bookings_api.mark_as_used(
            booking=booking,
            validation_author_type=bookings_models.BookingValidationAuthorType.OFFERER,
        )
        _price_event(booking.finance_events[0])
        bookings_api.mark_as_cancelled(
            booking=booking,
            reason=bookings_models.BookingCancellationReasons.BACKOFFICE,
        )

        bookings.append(booking)

    # Empty the remaining credits leaving only 10 cents in each balance
    for user in users:
        booking = bookings_factories.BookingFactory.create(
            user=user,
            quantity=1,
            stock__price=decimal.Decimal("99.9"),
            stock__offer__venue=venue,
        )
        bookings_api.mark_as_used(
            booking=booking,
            validation_author_type=bookings_models.BookingValidationAuthorType.OFFERER,
        )
        _price_event(booking.finance_events[0])

    # Generate the commercial gestures
    for booking in bookings:
        amount = booking.total_amount
        if not (
            validation.check_commercial_gesture_bookings([booking])
            and validation.check_commercial_gesture_total_amount(amount, [booking])
        ):
            raise ValueError("Invalid values for commercial gesture creation")
        commercial_gesture = finance_api.create_finance_commercial_gesture(
            author=author_user,
            bookings=[booking],
            amount=amount,
            origin=finance_models.FinanceIncidentRequestOrigin.SUPPORT_JEUNE,
            comment="create_industrial_commercial_gestures in industrial sandbox",
        )

        finance_api.validate_finance_commercial_gesture(
            commercial_gesture,
            author=author_user,
        )
        _price_event(commercial_gesture.booking_finance_incidents[0].finance_events[0])


def _create_total_commercial_gesture_collective_offer(
    author_user: users_models.User,
    venue: offerers_models.Venue,
    users_count: int,
) -> None:
    year = (
        db.session.query(educational_models.EducationalYear).first()
        or educational_factories.EducationalYearFactory.create()
    )
    institution = (
        db.session.query(educational_models.EducationalInstitution).first()
        or educational_factories.EducationalInstitutionFactory.create()
    )
    deposit = (
        institution.deposits[0]
        if institution.deposits
        else educational_factories.EducationalDepositFactory.create(
            educationalInstitution=institution, educationalYear=year
        )
    )

    for i in range(users_count):
        # Create a regular "used" collective booking for the venue
        booking = educational_factories.UsedCollectiveBookingFactory.create(
            collectiveStock__collectiveOffer__venue=venue,
            collectiveStock__price=decimal.Decimal("14") + decimal.Decimal(i),
            collectiveStock__startDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=1),
            educationalInstitution=deposit.educationalInstitution,
            educationalYear=deposit.educationalYear,
        )
        finance_event = finance_factories.UsedCollectiveBookingFinanceEventFactory.create(
            venue=venue,
            collectiveBooking=booking,
        )
        _price_event(finance_event)

        # Create collective bookings
        booking = educational_factories.UsedCollectiveBookingFactory.create(
            collectiveStock__collectiveOffer__venue=venue,
            collectiveStock__price=decimal.Decimal("30") + decimal.Decimal(i),
            educationalInstitution=institution,
        )
        finance_event = finance_factories.UsedCollectiveBookingFinanceEventFactory.create(
            venue=venue,
            collectiveBooking=booking,
        )
        _price_event(finance_event)
        # Cancel the collective bookings
        educational_api_booking.cancel_collective_booking(
            collective_booking=booking,
            reason=educational_models.CollectiveBookingCancellationReasons.FINANCE_INCIDENT,
            _from="create_industrial_commercial_gestures collective booking cancel",
        )
        # Create the commercial gesture and validate it
        commercial_gesture = finance_api.create_finance_commercial_gesture_collective_booking(
            booking=booking,
            author=author_user,
            origin=finance_models.FinanceIncidentRequestOrigin.SUPPORT_JEUNE,
            comment="create_industrial_commercial_gestures in industrial sandbox",
        )
        finance_api.validate_finance_commercial_gesture(
            finance_incident=commercial_gesture,
            author=author_user,
        )

        # Pricing of the commercial gestures
        for booking_finance_incident in commercial_gesture.booking_finance_incidents:
            for event in booking_finance_incident.finance_events:
                _price_event(event)


def _create_partial_commercial_gesture_multiple_individual_offer(
    author_user: users_models.User,
    venue: offerers_models.Venue,
    users_count: int,
) -> None:
    # Create the users
    users = users_factories.BeneficiaryGrant18Factory.create_batch(users_count)
    # Empty the balances
    for user in users:
        booking = bookings_factories.BookingFactory.create(
            user=user,
            quantity=10,
            stock__price=decimal.Decimal("5.0"),
            stock__offer__venue=venue,
        )  # 50€
        bookings_api.mark_as_used(
            booking=booking,
            validation_author_type=bookings_models.BookingValidationAuthorType.OFFERER,
        )

        for finance_event in booking.finance_events:
            _price_event(finance_event)

    # Create the bookings to cancel
    bookings = []

    for i, user in enumerate(users):
        booking = bookings_factories.BookingFactory.create(
            user=user,
            stock__offer__venue=venue,
            stock__price=decimal.Decimal("10.1") + decimal.Decimal(i),
            quantity=1,
        )
        bookings_api.mark_as_used(
            booking=booking,
            validation_author_type=bookings_models.BookingValidationAuthorType.OFFERER,
        )
        for finance_event in booking.finance_events:
            _price_event(finance_event)

        bookings_api.mark_as_cancelled(
            booking=booking,
            reason=bookings_models.BookingCancellationReasons.BACKOFFICE,
        )

        bookings.append(booking)

    # Empty the remaining credits leaving only 10 cents in each balance
    for user in users:
        booking = bookings_factories.BookingFactory.create(
            user=user,
            quantity=1,
            stock__price=decimal.Decimal("99.9"),
            stock__offer__venue=venue,
        )
        bookings_api.mark_as_used(
            booking=booking,
            validation_author_type=bookings_models.BookingValidationAuthorType.OFFERER,
        )
        for finance_event in booking.finance_events:
            _price_event(finance_event)

    # Generate the commercial gestures
    for bookings_batch in get_chunks(bookings, 2):
        bookings = list(bookings_batch)
        amount = sum(booking.total_amount for booking in bookings) / 2
        validation.check_commercial_gesture_bookings(bookings)
        validation.check_commercial_gesture_total_amount(amount, bookings)
        commercial_gesture = finance_api.create_finance_commercial_gesture(
            author=author_user,
            bookings=bookings,
            amount=amount,
            origin=finance_models.FinanceIncidentRequestOrigin.SUPPORT_JEUNE,
            comment="create_industrial_commercial_gestures in industrial sandbox (partial commercial gesture)",
        )

        finance_api.validate_finance_commercial_gesture(
            commercial_gesture,
            author=author_user,
        )

        for booking_finance_incident in commercial_gesture.booking_finance_incidents:
            for finance_event in booking_finance_incident.finance_events:
                _price_event(finance_event)


def _generate_bookings_for_commercial_gesture_creation(venue: offerers_models.Venue, users_count: int) -> None:
    # Create the users
    users = users_factories.BeneficiaryGrant18Factory.create_batch(users_count)
    # Empty the balances
    for user in users:
        booking = bookings_factories.BookingFactory.create(
            user=user,
            quantity=10,
            stock__price=decimal.Decimal("5.0"),
            stock__offer__venue=venue,
        )  # 50€
        bookings_api.mark_as_used(
            booking=booking,
            validation_author_type=bookings_models.BookingValidationAuthorType.OFFERER,
        )

        for finance_event in booking.finance_events:
            _price_event(finance_event)

    # Create the bookings to cancel
    for i, user in enumerate(users):
        booking = bookings_factories.BookingFactory.create(
            user=user,
            stock__offer__venue=venue,
            stock__price=decimal.Decimal("10.1") + decimal.Decimal(i),
            quantity=1,
        )
        bookings_api.mark_as_used(
            booking=booking,
            validation_author_type=bookings_models.BookingValidationAuthorType.OFFERER,
        )
        for finance_event in booking.finance_events:
            _price_event(finance_event)

        bookings_api.mark_as_cancelled(
            booking=booking,
            reason=bookings_models.BookingCancellationReasons.BACKOFFICE,
        )

    # Empty the remaining credits leaving only 10 cents in each balance
    for user in users:
        booking = bookings_factories.BookingFactory.create(
            user=user,
            quantity=1,
            stock__price=decimal.Decimal("99.9"),
            stock__offer__venue=venue,
        )
        bookings_api.mark_as_used(
            booking=booking,
            validation_author_type=bookings_models.BookingValidationAuthorType.OFFERER,
        )
        for finance_event in booking.finance_events:
            _price_event(finance_event)

    ################################
    # Generate collective bookings #
    ################################
    year = (
        db.session.query(educational_models.EducationalYear).first()
        or educational_factories.EducationalYearFactory.create()
    )
    institution = (
        db.session.query(educational_models.EducationalInstitution).first()
        or educational_factories.EducationalInstitutionFactory.create()
    )
    deposit = (
        institution.deposits[0]
        if institution.deposits
        else educational_factories.EducationalDepositFactory.create(
            educationalInstitution=institution, educationalYear=year
        )
    )

    for i in range(users_count):
        # Create a regular "used" collective booking for the venue
        booking = educational_factories.UsedCollectiveBookingFactory.create(
            collectiveStock__collectiveOffer__venue=venue,
            collectiveStock__price=decimal.Decimal("14") + decimal.Decimal(i),
            collectiveStock__startDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=1),
            educationalInstitution=deposit.educationalInstitution,
            educationalYear=deposit.educationalYear,
        )
        finance_event = finance_factories.UsedCollectiveBookingFinanceEventFactory.create(
            venue=venue,
            collectiveBooking=booking,
        )
        _price_event(finance_event)

        # Create collective bookings
        booking = educational_factories.UsedCollectiveBookingFactory.create(
            collectiveStock__collectiveOffer__venue=venue,
            collectiveStock__price=decimal.Decimal("30") + decimal.Decimal(i),
            educationalInstitution=institution,
        )
        finance_event = finance_factories.UsedCollectiveBookingFinanceEventFactory.create(
            venue=venue,
            collectiveBooking=booking,
        )
        _price_event(finance_event)
        # Cancel the collective bookings
        educational_api_booking.cancel_collective_booking(
            collective_booking=booking,
            reason=educational_models.CollectiveBookingCancellationReasons.FINANCE_INCIDENT,
            _from="create_industrial_commercial_gestures collective booking cancel",
        )


@log_func_duration
def create_industrial_commercial_gestures() -> None:
    author_user = users_factories.UserFactory.create()
    offerer = offerers_factories.OffererFactory.create(name="Structure pour geste commerciaux")

    for i in range(2):
        bank_account = finance_factories.BankAccountFactory.create(offerer=offerer)
        venue = offerers_factories.VenueFactory.create(
            name="Lieu avec gestes commerciaux totaux pour réservations individuelles",
            managingOfferer=offerer,
            pricing_point="self",
            bank_account=bank_account,
        )
        _create_total_commercial_gesture_individual_offer(
            author_user=author_user,
            venue=venue,
            users_count=3 + i,
        )

    for i in range(2):
        bank_account = finance_factories.BankAccountFactory.create(offerer=offerer)
        venue = offerers_factories.VenueFactory.create(
            name="Lieu avec gestes commerciaux totaux pour réservations collectives",
            managingOfferer=offerer,
            pricing_point="self",
            bank_account=bank_account,
        )
        _create_total_commercial_gesture_collective_offer(
            author_user=author_user,
            venue=venue,
            users_count=3 + i,
        )

    for i in range(2):
        bank_account = finance_factories.BankAccountFactory.create(offerer=offerer)
        venue = offerers_factories.VenueFactory.create(
            name="Lieu avec gestes commerciaux partiels sur plusieurs réservations individuelles",
            managingOfferer=offerer,
            pricing_point="self",
            bank_account=bank_account,
        )
        _create_partial_commercial_gesture_multiple_individual_offer(
            author_user=author_user,
            venue=venue,
            users_count=3 + i,
        )

    cashflow_batch = finance_api.generate_cashflows_and_payment_files(cutoff=datetime.datetime.utcnow())
    finance_api.generate_invoices_and_debit_notes_legacy(cashflow_batch)
    db.session.flush()

    for i in range(2):
        bank_account = finance_factories.BankAccountFactory.create(offerer=offerer)
        venue = offerers_factories.VenueFactory.create(
            name="Lieu avec réservations individuelles et collectives pour création de gestes commerciaux",
            managingOfferer=offerer,
            pricing_point="self",
            bank_account=bank_account,
        )
        _generate_bookings_for_commercial_gesture_creation(venue=venue, users_count=3 + i)
