import csv
import datetime
import io
import pathlib
import zipfile
from decimal import Decimal
from unittest import mock

import pytest
import time_machine

from pcapi.core.bookings import api as bookings_api
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import subcategories
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import api
from pcapi.core.finance import exceptions
from pcapi.core.finance import factories
from pcapi.core.finance import models
from pcapi.core.finance import utils
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.reference import models as reference_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.models import db
from pcapi.repository import transaction
from pcapi.routes.backoffice.finance import validation
from pcapi.utils import db as db_utils
from pcapi.utils import human_ids

import tests
from tests.routes.backoffice.helpers import html_parser


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.features(WIP_ENABLE_NEW_FINANCE_WORKFLOW=False),
]


@pytest.fixture(name="clean_temp_files")
def clean_temp_files_fixture(tmp_path, monkeypatch):
    monkeypatch.setattr(api.tempfile, "mkdtemp", lambda: tmp_path)


def get_statuses(model):
    return {s for (s,) in db.session.query(model).with_entities(getattr(model, "status"))}


class PriceEventTest:
    def test_pricing_partial_overpayment_incident_workflow(self):
        # regular overpayment incident workflow:
        # 1. Offer is created by the offerer
        # 2. The offer is booked by the beneficiary
        # 3. The booking is used by the beneficiary
        # 4. The booking is reimbursed to the offerer
        # 5. It turns out that the booking didn't go as expected and the booking is overpriced
        # 6. Create an overpayment incident to to get back the money from the offerer
        venue = offerers_factories.VenueFactory(pricing_point="self")
        bank_account = factories.BankAccountFactory(offerer=venue.managingOfferer)
        offerers_factories.VenueBankAccountLinkFactory(venue=venue, bankAccount=bank_account)
        author_user = users_factories.UserFactory()

        user = users_factories.BeneficiaryGrant18Factory(deposit__amount=300)
        assert user.wallet_balance == Decimal("300")
        ###############################
        # Create an offer and book it #
        ###############################
        booking = bookings_factories.BookingFactory(
            user=user,
            quantity=13,
            stock__price=Decimal("5.0"),
            stock__offer__venue=venue,
        )  # 65€
        bookings_api.mark_as_used(
            booking=booking,
            validation_author_type=bookings_models.BookingValidationAuthorType.OFFERER,
        )
        finance_events = db.session.query(models.FinanceEvent).all()
        assert len(finance_events) == 1

        initial_finance_event = finance_events[0]
        pricing = api.price_event(initial_finance_event)

        assert pricing.amount == -65_00
        assert pricing.revenue == 65_00
        assert pricing.bookingId == booking.id
        assert pricing.status == models.PricingStatus.VALIDATED
        assert pricing.venueId == venue.id
        assert pricing.eventId == initial_finance_event.id

        assert len(pricing.lines) == 2
        assert {line.category for line in pricing.lines} == {
            models.PricingLineCategory.OFFERER_REVENUE,
            models.PricingLineCategory.OFFERER_CONTRIBUTION,
        }
        pricing_line_offerer_revenue = next(
            line for line in pricing.lines if line.category == models.PricingLineCategory.OFFERER_REVENUE
        )
        pricing_line_offerer_contribution = next(
            line for line in pricing.lines if line.category == models.PricingLineCategory.OFFERER_CONTRIBUTION
        )
        assert pricing_line_offerer_revenue.amount == -65_00
        assert pricing_line_offerer_contribution.amount == 0

        assert user.wallet_balance == Decimal("235.00")

        #################################################
        # Invoice the booking and reimburse the offerer #
        #################################################
        cashflow_batch = factories.CashflowBatchFactory(label="Batch")
        api._generate_cashflows(cashflow_batch)
        assert len(cashflow_batch.cashflows) == 1
        cashflow = cashflow_batch.cashflows[0]
        cashflow.status = models.CashflowStatus.UNDER_REVIEW
        db.session.add(cashflow)
        db.session.flush()

        api._generate_invoice_legacy(
            bank_account_id=bank_account.id, cashflow_ids=[cashflow.id for cashflow in cashflow_batch.cashflows]
        )
        assert booking.status == bookings_models.BookingStatus.REIMBURSED

        ##################################
        # Create an overpayment incident #
        ##################################
        incident = api.create_overpayment_finance_incident(
            bookings=[booking],
            author=author_user,
            origin=models.FinanceIncidentRequestOrigin.SUPPORT_PRO,
            comment="BO",
            amount=Decimal("30"),
        )

        assert incident.kind == models.IncidentType.OVERPAYMENT
        assert incident.status == models.IncidentStatus.CREATED
        assert incident.details["authorId"] == author_user.id
        assert incident.origin == models.FinanceIncidentRequestOrigin.SUPPORT_PRO
        assert incident.comment == "BO"

        booking_finance_incidents = db.session.query(models.BookingFinanceIncident).all()
        assert len(booking_finance_incidents) == 1
        booking_finance_incident = booking_finance_incidents[0]
        assert booking_finance_incident.beneficiaryId == user.id
        assert booking_finance_incident.bookingId == booking.id
        assert (
            booking_finance_incident.newTotalAmount == 35_00
        )  # = 65€ - 30€ (30€ being the amount to get back from the offerer and to give to the user's deposit)

        #####################################
        # Validate the overpayment incident #
        #####################################
        api.validate_finance_overpayment_incident(
            finance_incident=incident,
            force_debit_note=True,
            author=author_user,
        )

        finance_events = (
            db.session.query(models.FinanceEvent).filter(models.FinanceEvent.id != initial_finance_event.id).all()
        )
        assert len(finance_events) == 2
        assert {finance_event.motive for finance_event in finance_events} == {
            models.FinanceEventMotive.INCIDENT_REVERSAL_OF_ORIGINAL_EVENT,
            models.FinanceEventMotive.INCIDENT_NEW_PRICE,
        }
        finance_event_reversal = next(
            finance_event
            for finance_event in finance_events
            if finance_event.motive == models.FinanceEventMotive.INCIDENT_REVERSAL_OF_ORIGINAL_EVENT
        )
        assert finance_event_reversal.status == models.FinanceEventStatus.READY
        assert finance_event_reversal.bookingFinanceIncidentId == booking_finance_incident.id
        assert finance_event_reversal.bookingId is None
        assert finance_event_reversal.collectiveBookingId is None
        assert finance_event_reversal.pricingPointId == venue.id
        assert finance_event_reversal.venueId == venue.id

        finance_event_new_price = next(
            finance_event
            for finance_event in finance_events
            if finance_event.motive == models.FinanceEventMotive.INCIDENT_NEW_PRICE
        )
        assert finance_event_new_price.status == models.FinanceEventStatus.READY
        assert finance_event_new_price.bookingId is None
        assert finance_event_new_price.collectiveBookingId is None
        assert finance_event_new_price.pricingPointId == venue.id
        assert finance_event_new_price.bookingFinanceIncidentId == booking_finance_incident.id
        assert finance_event_new_price.venueId == venue.id

        reversal_pricing = api.price_event(finance_event_reversal)
        assert reversal_pricing.amount == 65_00
        assert reversal_pricing.revenue == 65_00
        assert reversal_pricing.bookingId is None
        assert reversal_pricing.collectiveBookingId is None
        assert reversal_pricing.eventId == finance_event_reversal.id
        assert reversal_pricing.venueId == venue.id
        assert reversal_pricing.status == models.PricingStatus.VALIDATED
        assert reversal_pricing.pricingPointId == venue.id
        assert len(reversal_pricing.lines) == 2
        assert {line.category for line in reversal_pricing.lines} == {
            models.PricingLineCategory.OFFERER_REVENUE,
            models.PricingLineCategory.OFFERER_CONTRIBUTION,
        }
        reversal_pricing_line_offerer_revenue = next(
            line for line in reversal_pricing.lines if line.category == models.PricingLineCategory.OFFERER_REVENUE
        )
        assert reversal_pricing_line_offerer_revenue.amount == 65_00
        reversal_pricing_line_offerer_contribution = next(
            line for line in reversal_pricing.lines if line.category == models.PricingLineCategory.OFFERER_CONTRIBUTION
        )
        assert reversal_pricing_line_offerer_contribution.amount == 0
        assert reversal_pricing_line_offerer_revenue.amount == 65_00

        new_price_pricing = api.price_event(finance_event_new_price)
        assert new_price_pricing.amount == -35_00
        assert new_price_pricing.revenue == 100_00
        assert new_price_pricing.bookingId is None
        assert new_price_pricing.collectiveBookingId is None
        assert new_price_pricing.eventId == finance_event_new_price.id
        assert new_price_pricing.venueId == venue.id
        assert new_price_pricing.status == models.PricingStatus.VALIDATED
        assert len(new_price_pricing.lines) == 2
        assert {line.category for line in new_price_pricing.lines} == {
            models.PricingLineCategory.OFFERER_REVENUE,
            models.PricingLineCategory.OFFERER_CONTRIBUTION,
        }
        new_price_pricing_line_offerer_revenue = next(
            line for line in new_price_pricing.lines if line.category == models.PricingLineCategory.OFFERER_REVENUE
        )
        new_price_pricing_line_offerer_contribution = next(
            line for line in new_price_pricing.lines if line.category == models.PricingLineCategory.OFFERER_CONTRIBUTION
        )
        assert new_price_pricing_line_offerer_revenue.amount == -35_00
        assert new_price_pricing_line_offerer_contribution.amount == 0

        assert user.wallet_balance == Decimal("265")
        assert booking.status == bookings_models.BookingStatus.REIMBURSED

    def test_compute_commercial_gesture_new_total_amount_multiple_bookings(self):
        venue = offerers_factories.VenueFactory(pricing_point="self")
        user = users_factories.BeneficiaryGrant18Factory(deposit__amount=300)
        author_user = users_factories.UserFactory()
        price_amount = Decimal("5.1")
        commercial_gesture_amount = Decimal("15.1")
        stock = offers_factories.StockFactory(price=price_amount, offer__venue=venue)

        booking1 = bookings_factories.BookingFactory(
            user=user,
            quantity=4,
            amount=price_amount,
            stock=stock,
        )
        booking2 = bookings_factories.BookingFactory(
            user=user,
            quantity=3,
            amount=price_amount,
            stock=stock,
        )
        booking3 = bookings_factories.BookingFactory(
            user=user,
            quantity=1,
            amount=price_amount,
            stock=stock,
        )
        bookings = [booking1, booking2, booking3]
        commercial_gesture = api.create_finance_commercial_gesture(
            bookings=bookings,
            amount=Decimal("15.1"),
            author=author_user,
            origin=models.FinanceIncidentRequestOrigin.SUPPORT_PRO,
            comment="test",
        )
        validation.check_commercial_gesture_bookings(bookings)
        validation.check_commercial_gesture_total_amount(commercial_gesture_amount, bookings)
        commercial_gesture = api.create_finance_commercial_gesture(
            author=author_user,
            bookings=bookings,
            amount=commercial_gesture_amount,
            origin=models.FinanceIncidentRequestOrigin.SUPPORT_PRO,
            comment="create_industrial_commercial_gestures in industrial sandbox (partial commercial gesture)",
        )
        assert commercial_gesture.due_amount_by_offerer == 15_10
        booking_finance_incidents = commercial_gesture.booking_finance_incidents
        assert len(booking_finance_incidents) == 3
        assert {b.bookingId for b in booking_finance_incidents} == {booking1.id, booking2.id, booking3.id}
        booking_finance_incident1 = next(b for b in booking_finance_incidents if b.bookingId == booking1.id)
        booking_finance_incident2 = next(b for b in booking_finance_incidents if b.bookingId == booking2.id)
        booking_finance_incident3 = next(b for b in booking_finance_incidents if b.bookingId == booking3.id)
        assert booking_finance_incident1.newTotalAmount == 12_85
        assert booking_finance_incident2.newTotalAmount == 9_63
        assert booking_finance_incident3.newTotalAmount == 3_22
        assert booking_finance_incident1.due_amount_by_offerer == 7_55
        assert booking_finance_incident2.due_amount_by_offerer == 5_67
        assert booking_finance_incident3.due_amount_by_offerer == 1_88

    def test_pricing_commercial_gesture_workflow(self):
        # regular commercial gesture workflow:
        # 1. Offer is created by the offerer
        # 2. The offer is booked by a beneficiary
        # 3. Something bad happened → the booking is cancelled
        # 4. The beneficiary consumes his credit
        # 5. Cannot give back the amount of the booking to the offerer from the beneficiary's deposit
        # 6. Create a commercial gesture incident to give back the money to the offerer
        venue = offerers_factories.VenueFactory(pricing_point="self")
        author_user = users_factories.UserFactory()

        user = users_factories.BeneficiaryGrant18Factory(deposit__amount=300)
        assert user.wallet_balance == Decimal("300")
        ############################
        # Empty the user's balance #
        ############################
        initial_booking = bookings_factories.BookingFactory(
            user=user,
            quantity=57,
            stock__price=Decimal("5.0"),
            stock__offer__venue=venue,
        )  # 285€
        bookings_api.mark_as_used(
            booking=initial_booking,
            validation_author_type=bookings_models.BookingValidationAuthorType.OFFERER,
        )
        finance_events = db.session.query(models.FinanceEvent).all()
        assert len(finance_events) == 1

        initial_booking_finance_event = finance_events[0]
        pricing = api.price_event(initial_booking_finance_event)

        assert pricing.amount == -285_00
        assert pricing.revenue == 285_00
        assert pricing.bookingId == initial_booking.id
        assert pricing.status == models.PricingStatus.VALIDATED
        assert pricing.venueId == venue.id
        assert pricing.eventId == initial_booking_finance_event.id

        pricing_lines = pricing.lines
        assert len(pricing_lines) == 2
        assert {line.category for line in pricing_lines} == {
            models.PricingLineCategory.OFFERER_REVENUE,
            models.PricingLineCategory.OFFERER_CONTRIBUTION,
        }
        pricing_line_offerer_revenue = next(
            line for line in pricing_lines if line.category == models.PricingLineCategory.OFFERER_REVENUE
        )
        pricing_line_offerer_contribution = next(
            line for line in pricing_lines if line.category == models.PricingLineCategory.OFFERER_CONTRIBUTION
        )

        assert pricing_line_offerer_revenue.amount == -285_00
        assert pricing_line_offerer_contribution.amount == 0

        assert user.wallet_balance == Decimal("15.0")

        ###############################
        # Create a booking and use it #
        ###############################
        stock = offers_factories.StockFactory(price=Decimal("10.1"), offer__venue=venue)
        booking = bookings_factories.BookingFactory(user=user, stock=stock)
        bookings_api.mark_as_used(
            booking=booking,
            validation_author_type=bookings_models.BookingValidationAuthorType.OFFERER,
        )
        booking_finance_events = (
            db.session.query(models.FinanceEvent)
            .filter(models.FinanceEvent.id != initial_booking_finance_event.id)
            .all()
        )
        assert len(booking_finance_events) == 1
        booking_finance_event = booking_finance_events[0]
        pricing = api.price_event(booking_finance_event)
        assert pricing.amount == -10_10
        assert pricing.revenue == 295_10
        assert pricing.bookingId == booking.id
        assert pricing.status == models.PricingStatus.VALIDATED
        assert pricing.venueId == venue.id
        assert pricing.eventId == booking_finance_event.id

        pricing_lines = pricing.lines
        assert len(pricing_lines) == 2
        assert {line.category for line in pricing_lines} == {
            models.PricingLineCategory.OFFERER_REVENUE,
            models.PricingLineCategory.OFFERER_CONTRIBUTION,
        }
        pricing_line_offerer_revenue = next(
            line for line in pricing_lines if line.category == models.PricingLineCategory.OFFERER_REVENUE
        )
        pricing_line_offerer_contribution = next(
            line for line in pricing_lines if line.category == models.PricingLineCategory.OFFERER_CONTRIBUTION
        )

        assert pricing_line_offerer_revenue.amount == -10_10
        assert pricing_line_offerer_contribution.amount == 0
        assert user.wallet_balance == Decimal("4.9")

        ######################
        # Cancel the booking #
        ######################
        bookings_api.mark_as_cancelled(
            booking=booking,
            reason=bookings_models.BookingCancellationReasons.BACKOFFICE,
        )

        assert booking.status == bookings_models.BookingStatus.CANCELLED
        assert booking_finance_event.status == models.FinanceEventStatus.CANCELLED
        assert booking_finance_event.pricingPointId == venue.id
        cancel_booking_finance_events = (
            db.session.query(models.FinanceEvent)
            .filter(
                models.FinanceEvent.id.not_in((initial_booking_finance_event.id, booking_finance_event.id)),
            )
            .all()
        )
        assert len(cancel_booking_finance_events) == 1
        cancel_booking_finance_event = cancel_booking_finance_events[0]
        assert cancel_booking_finance_event.motive == models.FinanceEventMotive.BOOKING_CANCELLED_AFTER_USE
        assert cancel_booking_finance_event.pricingPointId is None
        assert cancel_booking_finance_event.bookingId == booking.id
        assert cancel_booking_finance_event.status == models.FinanceEventStatus.NOT_TO_BE_PRICED
        assert pricing.status == models.PricingStatus.CANCELLED

        assert user.wallet_balance == Decimal("15.0")

        ###################################################
        # Additional booking to further empty the balance #
        ###################################################
        additional_booking = bookings_factories.BookingFactory(
            user=user,
            quantity=1,
            stock__price=Decimal("13.3"),
            stock__offer__venue=venue,
        )  # €13.3
        bookings_api.mark_as_used(
            booking=additional_booking,
            validation_author_type=bookings_models.BookingValidationAuthorType.OFFERER,
        )
        additional_finance_events = (
            db.session.query(models.FinanceEvent)
            .filter(
                models.FinanceEvent.id.not_in(
                    (initial_booking_finance_event.id, booking_finance_event.id, cancel_booking_finance_event.id)
                ),
            )
            .all()
        )
        assert len(additional_finance_events) == 1
        additional_finance_event = additional_finance_events[0]
        api.price_event(additional_finance_event)

        assert additional_finance_event.bookingId == additional_booking.id
        assert additional_finance_event.status == models.FinanceEventStatus.PRICED

        assert user.wallet_balance == Decimal("1.70")

        #################################
        # Create the commercial gesture #
        #################################
        commercial_gesture = api.create_finance_commercial_gesture(
            bookings=[booking],
            amount=Decimal("10.1"),
            author=author_user,
            origin=models.FinanceIncidentRequestOrigin.SUPPORT_PRO,
            comment="test",
        )
        assert commercial_gesture.kind == models.IncidentType.COMMERCIAL_GESTURE
        assert commercial_gesture.status == models.IncidentStatus.CREATED
        assert commercial_gesture.forceDebitNote is False
        assert commercial_gesture.details["authorId"] == author_user.id
        assert commercial_gesture.origin == models.FinanceIncidentRequestOrigin.SUPPORT_PRO
        assert commercial_gesture.comment == "test"
        assert commercial_gesture.venueId == venue.id
        assert len(commercial_gesture.booking_finance_incidents) == 1
        booking_finance_incident = commercial_gesture.booking_finance_incidents[0]
        assert booking_finance_incident.bookingId == booking.id
        assert booking_finance_incident.incidentId == commercial_gesture.id
        assert booking_finance_incident.due_amount_by_offerer == 10_10
        finance_event_count = (
            db.session.query(models.FinanceEvent)
            .filter(
                models.FinanceEvent.id.in_(
                    (
                        initial_booking_finance_event.id,
                        booking_finance_event.id,
                        cancel_booking_finance_event.id,
                        additional_finance_event.id,
                    ),
                ),
            )
            .count()
        )
        assert finance_event_count == 4

        ###################################
        # Validate the commercial gesture #
        ###################################
        api.validate_finance_commercial_gesture(commercial_gesture, author=author_user)
        assert commercial_gesture.status == models.IncidentStatus.VALIDATED
        commercial_gesture_finance_events = (
            db.session.query(models.FinanceEvent)
            .filter(
                models.FinanceEvent.id.not_in(
                    (
                        initial_booking_finance_event.id,
                        booking_finance_event.id,
                        cancel_booking_finance_event.id,
                        additional_finance_event.id,
                    ),
                ),
            )
            .all()
        )
        assert len(commercial_gesture_finance_events) == 1
        commercial_gesture_finance_event = commercial_gesture_finance_events[0]
        assert commercial_gesture_finance_event.motive == models.FinanceEventMotive.INCIDENT_COMMERCIAL_GESTURE
        assert commercial_gesture_finance_event.pricingPointId == venue.id
        assert commercial_gesture_finance_event.status == models.FinanceEventStatus.READY
        assert commercial_gesture_finance_event.venueId == venue.id
        assert commercial_gesture_finance_event.bookingFinanceIncident == booking_finance_incident

        commercial_gesture_pricing = api.price_event(commercial_gesture_finance_event)
        assert commercial_gesture_finance_event.status == models.FinanceEventStatus.PRICED
        assert commercial_gesture_pricing.status == models.PricingStatus.VALIDATED
        assert commercial_gesture_pricing.amount == -10_10
        assert commercial_gesture_pricing.revenue == 298_30
        assert commercial_gesture_pricing.eventId == commercial_gesture_finance_event.id
        assert commercial_gesture_pricing.venueId == venue.id
        assert commercial_gesture_pricing.pricingPointId == venue.id
        assert commercial_gesture_pricing.bookingId is None
        assert commercial_gesture_pricing.collectiveBookingId is None
        assert commercial_gesture_pricing.standardRule == "Remboursement total pour les gestes commerciaux"

        assert {line.category for line in commercial_gesture_pricing.lines} == {
            models.PricingLineCategory.COMMERCIAL_GESTURE,
            models.PricingLineCategory.OFFERER_CONTRIBUTION,
        }
        commercial_gesture_pricing_line_offerer_revenue = next(
            line
            for line in commercial_gesture_pricing.lines
            if line.category == models.PricingLineCategory.COMMERCIAL_GESTURE
        )
        commercial_gesture_pricing_line_offerer_contribution = next(
            line
            for line in commercial_gesture_pricing.lines
            if line.category == models.PricingLineCategory.OFFERER_CONTRIBUTION
        )
        assert commercial_gesture_pricing_line_offerer_revenue.amount == -10_10
        assert commercial_gesture_pricing_line_offerer_contribution.amount == 0

        assert user.wallet_balance == Decimal("1.70")


def _generate_finance_event_context(
    pricing_point: offerers_models.Venue,
    stock_beginning_datetime: datetime.datetime,
    booking_date_used: datetime.datetime,
) -> models.FinanceEvent:
    venue = offerers_factories.VenueFactory(pricing_point=pricing_point)
    stock = offers_factories.EventStockFactory(
        offer__venue=venue,
        beginningDatetime=stock_beginning_datetime,
        bookingLimitDatetime=booking_date_used - datetime.timedelta(days=1),
    )
    booking = bookings_factories.UsedBookingFactory(stock=stock, dateUsed=booking_date_used)
    event = factories.FinanceEventFactory(
        booking=booking,
        pricingOrderingDate=stock.beginningDatetime,
        status=models.FinanceEventStatus.PRICED,
        venue=venue,
    )
    factories.PricingFactory(event=event, booking=event.booking)
    return event


@time_machine.travel(datetime.datetime(datetime.datetime.utcnow().year, 2, 1, 12, 34, 26), tick=False)
@mock.patch("pcapi.connectors.googledrive.TestingBackend.create_file")
def test_generate_payment_files(mocked_gdrive_create_file, clean_temp_files):
    # The contents of generated files is unit-tested in other test
    # functions below.
    venue = offerers_factories.VenueFactory(
        pricing_point="self",
    )
    bank_account = factories.BankAccountFactory(offerer=venue.managingOfferer)
    offerers_factories.VenueBankAccountLinkFactory(venue=venue, bankAccount=bank_account)
    factories.PricingFactory(
        status=models.PricingStatus.VALIDATED,
        booking__stock__offer__venue=venue,
        valueDate=datetime.datetime.utcnow() - datetime.timedelta(minutes=1),
    )
    cutoff = datetime.datetime.utcnow()
    api.generate_cashflows_and_payment_files(cutoff)

    cashflow = db.session.query(models.Cashflow).one()
    assert cashflow.status == models.CashflowStatus.UNDER_REVIEW
    assert len(cashflow.logs) == 1
    assert cashflow.logs[0].statusBefore == models.CashflowStatus.PENDING
    assert cashflow.logs[0].statusAfter == models.CashflowStatus.UNDER_REVIEW

    current_year = datetime.datetime.utcnow().year
    gdrive_file_names = {call.args[1] for call in mocked_gdrive_create_file.call_args_list}
    assert gdrive_file_names == {
        f"bank_accounts_{current_year}0201_1334.csv",
        f"legacy_bank_accounts_{current_year}0201_1334.csv",
        f"down_payment_{cashflow.batch.label}_{current_year}0201_1334.csv",
    }


def test_generate_bank_accounts_file(clean_temp_files):
    now = datetime.datetime.utcnow()
    offerer = offerers_factories.OffererFactory(name="Nom de la structure")
    venue_1 = offerers_factories.VenueFactory(managingOfferer=offerer)
    venue_2 = offerers_factories.VenueFactory(
        name='Name1\n "with double quotes"   ', siret='siret 1 "t"', managingOfferer=offerer
    )
    venue_3 = offerers_factories.VenueFactory(managingOfferer=offerer)
    venue_4 = offerers_factories.VenueFactory(managingOfferer=offerer)
    venue_5 = offerers_factories.VenueFactory(managingOfferer=offerer)
    venue_6 = offerers_factories.VenueFactory(managingOfferer=offerer)
    bank_account_1 = factories.BankAccountFactory(
        label="old-label", iban="older-iban", bic="older-bic", offerer=offerer
    )
    bank_account_2 = factories.BankAccountFactory(label="some-label", iban="some-iban", bic="some-bic", offerer=offerer)
    bank_account_3 = factories.BankAccountFactory(
        label="newer-label", iban="newer-iban", bic="newer-bic", offerer=offerer
    )
    bank_account_4 = factories.BankAccountFactory(label="Fourth bank account", offerer=offerer)
    _bank_account_5 = factories.BankAccountFactory(label="Fifth bank account", offerer=offerer)
    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue_1,
        bankAccount=bank_account_1,
        timespan=[now - datetime.timedelta(days=30), now - datetime.timedelta(days=3)],
    )
    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue_2,
        bankAccount=bank_account_2,
        timespan=[now - datetime.timedelta(days=3), now - datetime.timedelta(days=1)],
    )
    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue_3,
        bankAccount=bank_account_3,
        timespan=[now - datetime.timedelta(days=3), now - datetime.timedelta(days=1)],
    )
    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue_4,
        bankAccount=bank_account_3,
        timespan=(now - datetime.timedelta(days=3), now - datetime.timedelta(days=1)),
    )
    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue_5,
        bankAccount=bank_account_4,
        timespan=(now - datetime.timedelta(days=3), now - datetime.timedelta(days=1)),
    )

    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue_6,
        bankAccount=bank_account_4,
        timespan=(now - datetime.timedelta(days=3), now - datetime.timedelta(days=1)),
    )

    n_queries = 1  # select reimbursement point data
    with assert_num_queries(n_queries):
        path = api._generate_bank_accounts_file(datetime.datetime.utcnow() - datetime.timedelta(days=2))

    with path.open(encoding="utf-8") as fp:
        reader = csv.DictReader(fp, quoting=csv.QUOTE_NONNUMERIC)
        rows = list(reader)
    assert len(rows) == 3
    for row, bank_account in zip(rows, [bank_account_2, bank_account_3, bank_account_4]):
        assert row == {
            "Numéro": "",
            "Actif": "True",
            "Traité": "False",
            "Identifiant des coordonnées bancaires": str(bank_account.id),
            "Nom du fournisseur - Libellé des coordonnées bancaires": f"{bank_account.offerer.name} - {bank_account.label}",
            "Statut": "A",
            "Famille de fournisseurs": "ACTEURCULT",
            "Condition de règlement": "30J",
            "Cycle du relevé": "15J",
            "Devise": "EUR",
            "Type de taux de change": "SPOT",
            "Courriel": "",
            "Site web": "",
            "Téléphone 1": "",
            "Téléphone 2": "",
            "Fax": "",
            "Langue": "fr-FR",
            "Adresse 1": "1 boulevard Poissonnière",
            "Adresse 2": "",
            "Ville": "Paris",
            "Pays": "FR",
            "Département": "",
            "Code postal": "75002",
            "Mode de règlement bis": "VSEPA",
            "IBAN": bank_account.iban,
            "Compte de trésorerie": "",
            "Nature économique": "",
            "BIC": bank_account.bic,
            "SIREN": bank_account.offerer.siren,
            "Numéro de TVA Intracom": "",
            "Zone de taxes": "EXO",
        }


def test_generate_legacy_bank_accounts_file(clean_temp_files):
    now = datetime.datetime.utcnow()
    offerer = offerers_factories.OffererFactory(name="Nom de la structure")
    venue_1 = offerers_factories.VenueFactory(managingOfferer=offerer)
    venue_2 = offerers_factories.VenueFactory(
        name='Name1\n "with double quotes"   ', siret='siret 1 "t"', managingOfferer=offerer
    )
    venue_3 = offerers_factories.VenueFactory(managingOfferer=offerer)
    venue_4 = offerers_factories.VenueFactory(managingOfferer=offerer)
    venue_5 = offerers_factories.VenueFactory(managingOfferer=offerer)
    venue_6 = offerers_factories.VenueFactory(managingOfferer=offerer)
    bank_account_1 = factories.BankAccountFactory(
        label="old-label", iban="older-iban", bic="older-bic", offerer=offerer
    )
    bank_account_2 = factories.BankAccountFactory(label="some-label", iban="some-iban", bic="some-bic", offerer=offerer)
    bank_account_3 = factories.BankAccountFactory(
        label="newer-label", iban="newer-iban", bic="newer-bic", offerer=offerer
    )
    bank_account_4 = factories.BankAccountFactory(label="Fourth bank account", offerer=offerer)
    _bank_account_5 = factories.BankAccountFactory(label="Fifth bank account", offerer=offerer)
    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue_1,
        bankAccount=bank_account_1,
        timespan=[now - datetime.timedelta(days=30), now - datetime.timedelta(days=3)],
    )
    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue_2,
        bankAccount=bank_account_2,
        timespan=[now - datetime.timedelta(days=3), now - datetime.timedelta(days=1)],
    )
    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue_3,
        bankAccount=bank_account_3,
        timespan=[now - datetime.timedelta(days=3), now - datetime.timedelta(days=1)],
    )
    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue_4,
        bankAccount=bank_account_3,
        timespan=(now - datetime.timedelta(days=3), now - datetime.timedelta(days=1)),
    )
    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue_5,
        bankAccount=bank_account_4,
        timespan=(now - datetime.timedelta(days=3), now - datetime.timedelta(days=1)),
    )

    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue_6,
        bankAccount=bank_account_4,
        timespan=(now - datetime.timedelta(days=3), now - datetime.timedelta(days=1)),
    )

    n_queries = 1  # select reimbursement point data
    with assert_num_queries(n_queries):
        path = api._generate_legacy_bank_accounts_file(datetime.datetime.utcnow() - datetime.timedelta(days=2))

    with path.open(encoding="utf-8") as fp:
        reader = csv.DictReader(fp, quoting=csv.QUOTE_NONNUMERIC)
        rows = list(reader)
    assert len(rows) == 3
    for row, bank_account in zip(rows, [bank_account_2, bank_account_3, bank_account_4]):
        assert row == {
            "Lieux liés au compte bancaire": ", ".join(
                map(str, sorted(link.venueId for link in bank_account.venueLinks))
            ),
            "Identifiant humanisé des coordonnées bancaires": human_ids.humanize(bank_account.id),
            "Identifiant des coordonnées bancaires": str(bank_account.id),
            "SIREN de la structure": bank_account.offerer.siren,
            "Nom de la structure - Libellé des coordonnées bancaires": f"{bank_account.offerer.name} - {bank_account.label}",
            "IBAN": bank_account.iban,
            "BIC": bank_account.bic,
        }


def test_generate_payments_file(clean_temp_files):
    actual_year = datetime.date.today().year
    used_date = datetime.datetime(actual_year, 2, 5)
    venue1 = offerers_factories.VenueFactory(
        name='Le Petit Rintintin "test"\n',
        siret='123456 "test"\n',
        pricing_point="self",
    )
    bank_account_1 = factories.BankAccountFactory(offerer=venue1.managingOfferer)
    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue1, bankAccount=bank_account_1, timespan=(datetime.datetime(actual_year, 1, 29),)
    )

    # Individual pricing
    factories.PricingFactory(
        amount=-1000,  # rate = 100 %
        booking__amount=10,
        booking__dateUsed=used_date,
        booking__stock__offer__name="Une histoire classique",
        booking__stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        booking__stock__offer__venue=venue1,
    )

    ## Individual incident
    # Individual booking, with an incident later
    incident_booking = bookings_factories.ReimbursedBookingFactory(
        amount=10,
        dateUsed=datetime.datetime(actual_year, 1, 30),
        stock__offer__name="Une histoire formidable",
        stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        stock__offer__venue=venue1,
    )
    used_event = factories.UsedBookingFinanceEventFactory(booking=incident_booking)

    # Original pricing
    factories.PricingFactory(
        booking=incident_booking,
        event=used_event,
        status=models.PricingStatus.INVOICED,
        venue=incident_booking.venue,
        valueDate=datetime.datetime(actual_year, 1, 31),
    )

    # Create finance incident on the booking above (incident amount: 1€)
    booking_finance_incident = factories.IndividualBookingFinanceIncidentFactory(
        booking=incident_booking, newTotalAmount=900
    )
    incident_events = api._create_finance_events_from_incident(
        booking_finance_incident, used_date + datetime.timedelta(days=2)
    )
    for event in incident_events:
        api.price_event(event)

    # A free booking that should not appear in the CSV file
    factories.PricingFactory(
        amount=0,
        booking__amount=0,
        booking__dateUsed=used_date,
        booking__stock__offer__name="Une histoire gratuite",
        booking__stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        booking__stock__offer__venue=venue1,
    )

    # Pricings for educational booking
    year1 = educational_factories.EducationalYearFactory()
    year2 = educational_factories.EducationalYearFactory()
    year3 = educational_factories.EducationalYearFactory()
    educational_institution = educational_factories.EducationalInstitutionFactory()
    educational_factories.EducationalDepositFactory(
        educationalInstitution=educational_institution,
        educationalYear=year1,
        ministry=educational_models.Ministry.AGRICULTURE.name,
    )
    deposit_menjs = educational_factories.EducationalDepositFactory(
        educationalInstitution=educational_institution,
        educationalYear=year2,
        ministry=educational_models.Ministry.EDUCATION_NATIONALE.name,
    )
    deposit_ma = educational_factories.EducationalDepositFactory(
        educationalInstitution=educational_institution,
        educationalYear=year3,
        ministry=educational_models.Ministry.ARMEES.name,
    )
    meg_program = educational_factories.EducationalInstitutionProgramFactory(name="MeG")
    meg_educational_institution = educational_factories.EducationalInstitutionFactory(
        programAssociations=[educational_factories.EducationalInstitutionProgramAssociationFactory(program=meg_program)]
    )
    deposit_meg = educational_factories.EducationalDepositFactory(
        educationalInstitution=meg_educational_institution,
        educationalYear=year2,
        ministry=educational_models.Ministry.EDUCATION_NATIONALE.name,
    )

    # The first and second pricings should be merged together in the csv file
    factories.CollectivePricingFactory(
        amount=-300,  # rate = 100 %
        collectiveBooking__collectiveStock__price=3,
        collectiveBooking__dateUsed=used_date,
        collectiveBooking__collectiveStock__startDatetime=used_date,
        collectiveBooking__collectiveStock__collectiveOffer__name="Une histoire plutôt bien",
        collectiveBooking__collectiveStock__collectiveOffer__venue=venue1,
        collectiveBooking__educationalInstitution=deposit_menjs.educationalInstitution,
        collectiveBooking__educationalYear=deposit_menjs.educationalYear,
    )
    factories.CollectivePricingFactory(
        amount=-700,  # rate = 100 %
        collectiveBooking__collectiveStock__price=7,
        collectiveBooking__dateUsed=used_date,
        collectiveBooking__collectiveStock__startDatetime=used_date,
        collectiveBooking__collectiveStock__collectiveOffer__name="Une histoire plutôt bien 2",
        collectiveBooking__collectiveStock__collectiveOffer__venue=venue1,
        collectiveBooking__educationalInstitution=deposit_menjs.educationalInstitution,
        collectiveBooking__educationalYear=deposit_menjs.educationalYear,
    )
    factories.CollectivePricingFactory(
        amount=-300,  # rate = 100 %
        collectiveBooking__collectiveStock__price=3,
        collectiveBooking__dateUsed=used_date,
        collectiveBooking__collectiveStock__startDatetime=used_date,
        collectiveBooking__collectiveStock__collectiveOffer__name="Une histoire militaire plutôt bien",
        collectiveBooking__collectiveStock__collectiveOffer__venue=venue1,
        collectiveBooking__educationalInstitution=deposit_ma.educationalInstitution,
        collectiveBooking__educationalYear=deposit_ma.educationalYear,
    )
    factories.CollectivePricingFactory(
        amount=-500,  # rate = 100 %
        collectiveBooking__collectiveStock__price=5,
        collectiveBooking__dateUsed=used_date,
        collectiveBooking__collectiveStock__startDatetime=used_date,
        collectiveBooking__collectiveStock__collectiveOffer__name="Une histoire militaire plutôt marseillaise",
        collectiveBooking__collectiveStock__collectiveOffer__venue=venue1,
        collectiveBooking__educationalInstitution=deposit_meg.educationalInstitution,
        collectiveBooking__educationalYear=deposit_meg.educationalYear,
    )

    venue2 = offerers_factories.VenueFactory(
        name="Le Gigantesque Cubitus\n",
        siret="99999999999999",
        pricing_point="self",
    )
    bank_account_2 = factories.BankAccountFactory(offerer=venue2.managingOfferer)
    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue2,
        bankAccount=bank_account_2,
        timespan=(datetime.datetime(actual_year, 1, 29), datetime.datetime(actual_year, 2, 8)),
    )
    bank_account_3 = factories.BankAccountFactory(offerer=venue2.managingOfferer)
    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue2, bankAccount=bank_account_3, timespan=(datetime.datetime(actual_year, 2, 8),)
    )

    # Individual pricing 18
    factories.PricingFactory(
        amount=-700,  # rate = 100 %
        booking__amount=7,
        booking__dateUsed=used_date,
        booking__stock__offer__name="Une histoire plutôt bien",
        booking__stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        booking__stock__offer__venue=venue2,
        booking__user__deposit__type=models.DepositType.GRANT_18,
    )

    # Double pricings for an underage individual booking
    underage_user = users_factories.UnderageBeneficiaryFactory()
    underage_user.deposits[0].amount = 10_000
    db.session.add(underage_user.deposits[0])
    db.session.commit()

    factories.PricingFactory(
        amount=-400,  # rate = 50 %
        booking__amount=8,
        booking__user=underage_user,
        booking__dateUsed=used_date,
        booking__stock__offer__name="Une histoire plutôt bien",
        booking__stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        booking__stock__offer__venue=venue2,
        standardRule="",
        customRule=factories.CustomReimbursementRuleFactory(rate=Decimal(0.5)),
    )
    factories.PricingFactory(
        amount=-400,  # rate = 50 %
        booking__amount=8,
        booking__user=underage_user,
        booking__dateUsed=used_date,
        booking__stock__offer__name="Une histoire plutôt bien en doublon",
        booking__stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        booking__stock__offer__venue=venue2,
        standardRule="",
        customRule=factories.CustomReimbursementRuleFactory(rate=Decimal(0.5)),
    )

    # Now the user gets a GRANT_17_18, and his used bookings are transfered to the new deposit
    underage_user.deposits[0].expirationDate = datetime.datetime.utcnow() - datetime.timedelta(days=5)
    db.session.add(underage_user.deposits[0])
    db.session.commit()
    users_factories.DepositGrantFactory(
        user=underage_user, expirationDate=datetime.datetime.utcnow() + datetime.timedelta(days=5)
    )

    factories.PricingFactory(
        amount=-800,  # rate = 50 %
        booking__amount=16,
        booking__user=underage_user,
        booking__dateUsed=used_date,
        booking__stock__offer__name="Une histoire plutôt bien en doublon",
        booking__stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        booking__stock__offer__venue=venue2,
        booking__usedRecreditType=None,
        standardRule="",
        customRule=factories.CustomReimbursementRuleFactory(rate=Decimal(0.5)),
    )

    # Pricings on different bank account but same venue
    factories.PricingFactory(
        amount=-700,  # rate = 100 %
        booking__amount=7,
        booking__dateUsed=used_date + datetime.timedelta(days=5),
        booking__stock__offer__name="Une histoire plutôt bien sur un autre compte bancaire",
        booking__stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        booking__stock__offer__venue=venue2,
        booking__user__deposit__type=models.DepositType.GRANT_18,
    )
    # And some with the new deposits
    factories.PricingFactory(
        amount=-500,  # rate = 100 %
        booking__amount=5,
        booking__dateUsed=used_date + datetime.timedelta(days=5),
        booking__stock__offer__name="Une histoire plutôt bien sur un recredit 18",
        booking__stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        booking__stock__offer__venue=venue2,
        booking__usedRecreditType=bookings_models.BookingRecreditType.RECREDIT_18,
    )
    factories.PricingFactory(
        amount=-200,  # rate = 100 %
        booking__amount=2,
        booking__dateUsed=used_date + datetime.timedelta(days=5),
        booking__stock__offer__name="Une histoire plutôt bien sur un recredit 17",
        booking__stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        booking__stock__offer__venue=venue2,
        booking__usedRecreditType=bookings_models.BookingRecreditType.RECREDIT_17,
    )

    ## New Caledonia
    # A Caledonian pricing, but in euro
    nc_offerer = offerers_factories.CaledonianOffererFactory(name="Structure de Nouvelle-Calédonie")
    nc_venue = offerers_factories.CaledonianVenueFactory(
        name="Au Kanak fringuant",
        pricing_point="self",
        managingOfferer=nc_offerer,
    )
    nc_bank_account = factories.CaledonianBankAccountFactory(offerer=nc_venue.managingOfferer)
    offerers_factories.VenueBankAccountLinkFactory(
        venue=nc_venue, bankAccount=nc_bank_account, timespan=(datetime.datetime(actual_year, 1, 29),)
    )

    factories.PricingFactory(
        amount=-1000,  # rate = 100 %
        booking__amount=10,
        booking__dateUsed=used_date,
        booking__stock__offer__name="Une histoire calédonienne",
        booking__stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        booking__stock__offer__venue=nc_venue,
    )

    ## Collective incident
    # Collective booking, with an incident later
    collective_booking = educational_factories.ReimbursedCollectiveBookingFactory(
        collectiveStock__price=12,
        dateUsed=datetime.datetime(actual_year, 1, 30),
        collectiveStock__startDatetime=used_date,
        collectiveStock__collectiveOffer__name="Une histoire militaire plutôt bien sur un autre compte bancaire",
        collectiveStock__collectiveOffer__venue=venue2,
        educationalInstitution=deposit_ma.educationalInstitution,
        educationalYear=deposit_ma.educationalYear,
    )
    collective_used_event = factories.UsedCollectiveBookingFinanceEventFactory(collectiveBooking=collective_booking)

    factories.CollectivePricingFactory(
        collectiveBooking=collective_booking,
        event=collective_used_event,
        status=models.PricingStatus.INVOICED,
        venue=collective_booking.venue,
        valueDate=datetime.datetime(actual_year, 1, 31),
    )

    # Create finance incident on the booking above
    collective_booking_finance_incident = factories.CollectiveBookingFinanceIncidentFactory(
        collectiveBooking=collective_booking, newTotalAmount=0
    )
    collective_incident_events = api._create_finance_events_from_incident(
        collective_booking_finance_incident, used_date + datetime.timedelta(days=7)
    )
    for event in collective_incident_events:
        api.price_event(event)

    cutoff = datetime.datetime(actual_year, 2, 15)
    batch = api.generate_cashflows(cutoff)

    n_queries = 3  # select pricings + select batch
    with assert_num_queries(n_queries):
        path = api._generate_payments_file(batch)

    with open(path, encoding="utf-8") as fp:
        reader = csv.DictReader(fp, quoting=csv.QUOTE_NONNUMERIC)
        rows = list(reader)

    assert len(rows) == 10
    assert {
        "Identifiant des coordonnées bancaires": str(bank_account_1.id),
        "Identifiant humanisé des coordonnées bancaires": human_ids.humanize(bank_account_1.id),
        "SIREN de la structure": bank_account_1.offerer.siren,
        "Nom de la structure - Libellé des coordonnées bancaires": f"{bank_account_1.offerer.name} - {bank_account_1.label}",
        "Type de réservation": "PR18+",
        "Ministère": "",
        "Montant net offreur": 10 - 1,  # 10 from pricing + [9 - 10 = -1] from incident
    } in rows
    assert {
        "Identifiant des coordonnées bancaires": str(bank_account_1.id),
        "Identifiant humanisé des coordonnées bancaires": human_ids.humanize(bank_account_1.id),
        "SIREN de la structure": bank_account_1.offerer.siren,
        "Nom de la structure - Libellé des coordonnées bancaires": f"{bank_account_1.offerer.name} - {bank_account_1.label}",
        "Type de réservation": "EACC",
        "Ministère": "EDUCATION_NATIONALE",
        "Montant net offreur": 3 + 7,
    } in rows
    assert {
        "Identifiant des coordonnées bancaires": str(bank_account_1.id),
        "Identifiant humanisé des coordonnées bancaires": human_ids.humanize(bank_account_1.id),
        "SIREN de la structure": bank_account_1.offerer.siren,
        "Nom de la structure - Libellé des coordonnées bancaires": f"{bank_account_1.offerer.name} - {bank_account_1.label}",
        "Type de réservation": "EACC",
        "Ministère": "ARMEES",
        "Montant net offreur": 3,
    } in rows
    assert {
        "Identifiant des coordonnées bancaires": str(bank_account_1.id),
        "Identifiant humanisé des coordonnées bancaires": human_ids.humanize(bank_account_1.id),
        "SIREN de la structure": bank_account_1.offerer.siren,
        "Nom de la structure - Libellé des coordonnées bancaires": f"{bank_account_1.offerer.name} - {bank_account_1.label}",
        "Type de réservation": "EACC",
        "Ministère": "MeG",
        "Montant net offreur": 5,
    } in rows
    assert {
        "Identifiant des coordonnées bancaires": str(bank_account_3.id),
        "Identifiant humanisé des coordonnées bancaires": human_ids.humanize(bank_account_3.id),
        "SIREN de la structure": bank_account_3.offerer.siren,
        "Nom de la structure - Libellé des coordonnées bancaires": f"{bank_account_3.offerer.name} - {bank_account_3.label}",
        "Type de réservation": "AR18+",
        "Ministère": "",
        "Montant net offreur": 7 + 7,
    } in rows
    assert {
        "Identifiant des coordonnées bancaires": str(bank_account_3.id),
        "Identifiant humanisé des coordonnées bancaires": human_ids.humanize(bank_account_3.id),
        "SIREN de la structure": bank_account_3.offerer.siren,
        "Nom de la structure - Libellé des coordonnées bancaires": f"{bank_account_3.offerer.name} - {bank_account_3.label}",
        "Type de réservation": "AR18-",
        "Ministère": "",
        "Montant net offreur": 4 + 4 + 8,
    } in rows
    assert {
        "Identifiant des coordonnées bancaires": str(bank_account_3.id),
        "Identifiant humanisé des coordonnées bancaires": human_ids.humanize(bank_account_3.id),
        "SIREN de la structure": bank_account_3.offerer.siren,
        "Nom de la structure - Libellé des coordonnées bancaires": f"{bank_account_3.offerer.name} - {bank_account_3.label}",
        "Type de réservation": "PR18+",
        "Ministère": "",
        "Montant net offreur": 5,
    } in rows
    assert {
        "Identifiant des coordonnées bancaires": str(bank_account_3.id),
        "Identifiant humanisé des coordonnées bancaires": human_ids.humanize(bank_account_3.id),
        "SIREN de la structure": bank_account_3.offerer.siren,
        "Nom de la structure - Libellé des coordonnées bancaires": f"{bank_account_3.offerer.name} - {bank_account_3.label}",
        "Type de réservation": "PR18-",
        "Ministère": "",
        "Montant net offreur": 2,
    } in rows
    assert {
        "Identifiant des coordonnées bancaires": str(nc_bank_account.id),
        "Identifiant humanisé des coordonnées bancaires": human_ids.humanize(nc_bank_account.id),
        "SIREN de la structure": nc_bank_account.offerer.rid7,
        "Nom de la structure - Libellé des coordonnées bancaires": f"{nc_bank_account.offerer.name} - {nc_bank_account.label}",
        "Type de réservation": "PR18+",
        "Ministère": "NC",
        "Montant net offreur": 10,  # not in XPF
    } in rows
    assert {
        "Identifiant des coordonnées bancaires": str(bank_account_3.id),
        "Identifiant humanisé des coordonnées bancaires": human_ids.humanize(bank_account_3.id),
        "SIREN de la structure": bank_account_3.offerer.siren,
        "Nom de la structure - Libellé des coordonnées bancaires": f"{bank_account_3.offerer.name} - {bank_account_3.label}",
        "Type de réservation": "EACC",
        "Ministère": "ARMEES",
        "Montant net offreur": -12,  # [0 - 12 = -12] from collective incident
    } in rows


@pytest.mark.usefixtures("clean_temp_files", "css_font_http_request_mock")
def test_invoices_csv_commercial_gesture():
    offerer = offerers_factories.OffererFactory(name="Association de coiffeurs", siren="853318959")
    bank_account = factories.BankAccountFactory(offerer=offerer)
    venue = offerers_factories.VenueFactory(
        pricing_point="self",
        managingOfferer=offerer,
        bank_account=bank_account,
        siret="85331845900023",
    )
    author_user = users_factories.UserFactory()

    user = users_factories.BeneficiaryGrant18Factory(deposit__amount=300)
    assert user.wallet_balance == Decimal("300")
    # Empty the user's balance
    initial_booking = bookings_factories.BookingFactory(
        user=user,
        quantity=57,
        stock__price=Decimal("5.0"),
        stock__offer__venue=venue,
    )  # 285€
    bookings_api.mark_as_used(
        booking=initial_booking,
        validation_author_type=bookings_models.BookingValidationAuthorType.OFFERER,
    )
    finance_events = db.session.query(models.FinanceEvent).all()
    assert len(finance_events) == 1
    initial_booking_finance_event = finance_events[0]
    api.price_event(initial_booking_finance_event)

    assert user.wallet_balance == Decimal("15.0")

    # Create a booking and use it
    stock = offers_factories.StockFactory(price=Decimal("10.1"), offer__venue=venue)
    booking = bookings_factories.BookingFactory(user=user, stock=stock)
    bookings_api.mark_as_used(
        booking=booking,
        validation_author_type=bookings_models.BookingValidationAuthorType.OFFERER,
    )
    booking_finance_events = (
        db.session.query(models.FinanceEvent).filter(models.FinanceEvent.id != initial_booking_finance_event.id).all()
    )
    assert len(booking_finance_events) == 1
    booking_finance_event = booking_finance_events[0]
    api.price_event(booking_finance_event)

    # Cancel the booking
    bookings_api.mark_as_cancelled(
        booking=booking,
        reason=bookings_models.BookingCancellationReasons.BACKOFFICE,
    )

    cancel_booking_finance_events = (
        db.session.query(models.FinanceEvent)
        .filter(
            models.FinanceEvent.id.not_in((initial_booking_finance_event.id, booking_finance_event.id)),
        )
        .all()
    )
    assert len(cancel_booking_finance_events) == 1
    cancel_booking_finance_event = cancel_booking_finance_events[0]

    # Additional booking to further empty the balance
    additional_booking = bookings_factories.BookingFactory(
        user=user,
        quantity=1,
        stock__price=Decimal("13.3"),
        stock__offer__venue=venue,
    )  # €13.3
    bookings_api.mark_as_used(
        booking=additional_booking,
        validation_author_type=bookings_models.BookingValidationAuthorType.OFFERER,
    )
    additional_finance_events = (
        db.session.query(models.FinanceEvent)
        .filter(
            models.FinanceEvent.id.not_in(
                (initial_booking_finance_event.id, booking_finance_event.id, cancel_booking_finance_event.id)
            ),
        )
        .all()
    )
    assert len(additional_finance_events) == 1
    additional_finance_event = additional_finance_events[0]
    api.price_event(additional_finance_event)

    # Create the commercial gesture
    commercial_gesture = api.create_finance_commercial_gesture(
        bookings=[booking],
        amount=Decimal("10.1"),
        author=author_user,
        origin=models.FinanceIncidentRequestOrigin.SUPPORT_PRO,
        comment="test",
    )
    # Validate the commercial gesture
    api.validate_finance_commercial_gesture(commercial_gesture, author=author_user)
    assert commercial_gesture.status == models.IncidentStatus.VALIDATED
    commercial_gesture_finance_events = (
        db.session.query(models.FinanceEvent)
        .filter(
            models.FinanceEvent.id.not_in(
                (
                    initial_booking_finance_event.id,
                    booking_finance_event.id,
                    cancel_booking_finance_event.id,
                    additional_finance_event.id,
                ),
            ),
        )
        .all()
    )
    assert len(commercial_gesture_finance_events) == 1
    commercial_gesture_finance_event = commercial_gesture_finance_events[0]
    api.price_event(commercial_gesture_finance_event)

    cutoff = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    batch = api.generate_cashflows_and_payment_files(cutoff)
    api.generate_invoices_and_debit_notes_legacy(batch)
    path = api.generate_invoice_file(batch)
    with zipfile.ZipFile(path) as zfile:
        invoices_files = [
            file_name for file_name in zfile.namelist() if file_name.startswith(f"invoices_{batch.label}")
        ]
        assert len(invoices_files) == 1
        with zfile.open(invoices_files[0]) as csv_bytefile:
            csv_textfile = io.TextIOWrapper(csv_bytefile)
            reader = csv.DictReader(csv_textfile, quoting=csv.QUOTE_NONNUMERIC)
            rows = list(reader)

    assert len(rows) == 3
    assert {r["Type de ticket de facturation"] for r in rows} == {
        "offerer contribution",
        "offerer revenue",
        "commercial gesture",
    }
    row_offerer_contribution = next(r for r in rows if r["Type de ticket de facturation"] == "offerer contribution")
    row_offerer_revenue = next(r for r in rows if r["Type de ticket de facturation"] == "offerer revenue")
    row_commercial_gesture = next(r for r in rows if r["Type de ticket de facturation"] == "commercial gesture")
    assert row_offerer_contribution["Somme des tickets de facturation"] == Decimal("0")
    assert row_offerer_revenue["Somme des tickets de facturation"] == Decimal("-29830.0")
    assert row_commercial_gesture["Somme des tickets de facturation"] == Decimal("-1010.0")


@pytest.mark.usefixtures("clean_temp_files", "css_font_http_request_mock")
def test_invoice_pdf_commercial_gesture(features, monkeypatch):
    invoice_htmls = []

    def _store_invoice_pdf(invoice_storage_id, invoice_html) -> None:
        invoice_htmls.append(invoice_html)

    monkeypatch.setattr(api, "_store_invoice_pdf", _store_invoice_pdf)

    offerer = offerers_factories.OffererFactory(name="Association de coiffeurs", siren="853318959")
    bank_account = factories.BankAccountFactory(offerer=offerer)
    venue = offerers_factories.VenueFactory(
        pricing_point="self",
        managingOfferer=offerer,
        bank_account=bank_account,
        siret="85331845900023",
    )
    author_user = users_factories.UserFactory()

    user = users_factories.BeneficiaryGrant18Factory(deposit__amount=300)
    # Empty the user's balance
    initial_booking = bookings_factories.BookingFactory(
        user=user,
        quantity=57,
        stock__price=Decimal("5.0"),
        stock__offer__venue=venue,
    )  # 285€
    bookings_api.mark_as_used(
        booking=initial_booking,
        validation_author_type=bookings_models.BookingValidationAuthorType.OFFERER,
    )
    assert len(initial_booking.finance_events) == 1
    api.price_event(initial_booking.finance_events[0])

    # Create a booking and use it
    stock = offers_factories.StockFactory(price=Decimal("10.1"), offer__venue=venue)
    booking = bookings_factories.BookingFactory(user=user, stock=stock)
    bookings_api.mark_as_used(
        booking=booking,
        validation_author_type=bookings_models.BookingValidationAuthorType.OFFERER,
    )
    assert len(booking.finance_events) == 1
    api.price_event(booking.finance_events[0])

    # Cancel the booking
    bookings_api.mark_as_cancelled(
        booking=booking,
        reason=bookings_models.BookingCancellationReasons.BACKOFFICE,
    )

    # Additional booking to further empty the balance
    additional_booking = bookings_factories.BookingFactory(
        user=user,
        quantity=1,
        stock__price=Decimal("13.3"),
        stock__offer__venue=venue,
    )  # €13.3
    bookings_api.mark_as_used(
        booking=additional_booking,
        validation_author_type=bookings_models.BookingValidationAuthorType.OFFERER,
    )
    assert len(additional_booking.finance_events) == 1
    api.price_event(additional_booking.finance_events[0])

    # Create the commercial gesture
    commercial_gesture = api.create_finance_commercial_gesture(
        bookings=[booking],
        amount=Decimal("10.1"),
        author=author_user,
        origin=models.FinanceIncidentRequestOrigin.SUPPORT_PRO,
        comment="test",
    )
    # Validate the commercial gesture
    api.validate_finance_commercial_gesture(commercial_gesture, author=author_user)
    assert commercial_gesture.status == models.IncidentStatus.VALIDATED
    assert len(commercial_gesture.booking_finance_incidents) == 1
    assert len(commercial_gesture.booking_finance_incidents[0].finance_events) == 1
    api.price_event(commercial_gesture.booking_finance_incidents[0].finance_events[0])

    cutoff = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    batch = api.generate_cashflows_and_payment_files(cutoff)
    api.generate_invoices_and_debit_notes_legacy(batch)

    invoices = db.session.query(models.Invoice).all()
    assert len(invoices) == 1
    invoice = invoices[0]
    assert len(invoice.lines) == 2
    assert {line.label for line in invoice.lines} == {"Réservations", "Gestes commerciaux"}

    bookings_line = next(line for line in invoice.lines if line.label == "Réservations")
    assert bookings_line.contributionAmount == 0
    assert bookings_line.group == {"label": "Barème général", "position": 1}
    assert bookings_line.rate == Decimal("1.0")
    assert bookings_line.reimbursedAmount == -298_30

    commercial_gestures_line = next(line for line in invoice.lines if line.label == "Gestes commerciaux")
    assert commercial_gestures_line.contributionAmount == 0
    assert commercial_gestures_line.group == {"label": "Barème général", "position": 1}
    assert commercial_gestures_line.rate == Decimal("1.0")
    assert commercial_gestures_line.reimbursedAmount == -10_10

    assert len(invoice_htmls) == 1
    invoice_html = invoice_htmls[0].encode("utf-8")

    ###################
    # Test main table #
    ###################
    main_table = html_parser.get_tag(invoice_html, class_=None, tag="table")
    general_rate_rows = html_parser.extract(main_table, tag="tr", class_="coloredSection")
    assert len(general_rate_rows) == 1
    general_rate_row = general_rate_rows[0]
    assert general_rate_row == "Barème général"
    main_table_soup = html_parser.get_soup(main_table)
    # remove the 1 column row to be able to parse the rest
    main_table_soup.find("tr", class_="coloredSection").decompose()
    main_table_rows = html_parser.extract_table_rows(str(main_table_soup).encode("utf-8"))
    assert {"Réservations", "Gestes commerciaux", "SOUS-TOTAL", "TOTAL"} == {r["Typologie"] for r in main_table_rows}
    bookings_row = next(r for r in main_table_rows if r["Typologie"] == "Réservations")
    commercial_gestures_row = next(r for r in main_table_rows if r["Typologie"] == "Gestes commerciaux")
    subtotal_row = next(r for r in main_table_rows if r["Typologie"] == "SOUS-TOTAL")
    total_row = next(r for r in main_table_rows if r["Typologie"] == "TOTAL")

    assert bookings_row["Montant de la contribution offreur (TTC)"] == "0,00 €"
    assert bookings_row["Montant des réservations validées (TTC)"] == "298,30 €"
    assert bookings_row["Montant remboursé (TTC)"] == "298,30 €"
    assert bookings_row["Taux de contribution offreur (%)"] == "0 %"
    assert bookings_row["Taux de remboursement (%)"] == "100 %"

    assert commercial_gestures_row["Montant de la contribution offreur (TTC)"] == "0,00 €"
    assert commercial_gestures_row["Montant des réservations validées (TTC)"] == "10,10 €"
    assert commercial_gestures_row["Montant remboursé (TTC)"] == "10,10 €"
    assert commercial_gestures_row["Taux de contribution offreur (%)"] == "0 %"
    assert commercial_gestures_row["Taux de remboursement (%)"] == "100 %"

    assert subtotal_row["Montant de la contribution offreur (TTC)"] == "0,00 €"
    assert subtotal_row["Montant des réservations validées (TTC)"] == "308,40 €"
    assert subtotal_row["Montant remboursé (TTC)"] == "308,40 €"

    assert total_row["Montant de la contribution offreur (TTC)"] == "0,00 €"
    assert total_row["Montant des réservations validées (TTC)"] == "308,40 €"
    assert total_row["Montant remboursé (TTC)"] == "308,40 €"

    ############################
    # Test total account table #
    ############################
    total_account_table = html_parser.get_tag(invoice_html, class_="totalAccountTable", tag="table")
    total_rate_rows = html_parser.extract(total_account_table, tag="tr", class_="coloredSection")
    assert len(total_rate_rows) == 1
    total_rate_row = total_rate_rows[0]
    assert total_rate_row == "TOTAL RÈGLEMENT PASS CULTURE 308,40 €"
    total_account_table_soup = html_parser.get_soup(total_account_table)
    # remove the 1 column row to be able to parse the rest
    total_account_table_soup.find("tr", class_="coloredSection").decompose()
    total_account_table_rows = html_parser.extract_table_rows(str(total_account_table_soup).encode("utf-8"))
    assert len(total_account_table_rows) == 1
    total_account_table_row = total_account_table_rows[0]
    assert total_account_table_row["Date"] == (invoice.date + datetime.timedelta(days=2)).strftime("%d/%m/%Y")
    assert total_account_table_row["Destinataire"] == bank_account.label
    assert total_account_table_row["Mode de règlement"] == f"Virement {bank_account.iban}"
    assert total_account_table_row["Montant réglé"] == "308,40 €"
    assert total_account_table_row["N° de virement"] == batch.label

    #####################################
    # Test reimbursement by venue table #
    #####################################
    reimbursement_by_venue_table = html_parser.get_tag(invoice_html, class_="reimbursementByVenueTable", tag="table")
    reimbursement_by_venue_rows = html_parser.extract_table_rows(reimbursement_by_venue_table)
    assert len(reimbursement_by_venue_rows) == 1
    reimbursement_by_venue_row = reimbursement_by_venue_rows[0]

    assert reimbursement_by_venue_row["Contribution offreur incidents (TTC)"] == "20,20 €"
    assert reimbursement_by_venue_row["Dont offres collectives (TTC)"] == "0,00 €"
    assert reimbursement_by_venue_row["Dont offres individuelles (TTC)"] == "308,40 €"
    assert reimbursement_by_venue_row["Incidents (TTC)"] == "10,10 €"
    assert reimbursement_by_venue_row["Structures"] == venue.name
    assert reimbursement_by_venue_row["Montant de la contribution offreur (TTC)"] == "0,00 €"
    assert reimbursement_by_venue_row["Montant des réservations validées (TTC)"] == "298,30 €"
    assert reimbursement_by_venue_row["Montant remboursé (TTC)"] == "308,40 €"


def test_generate_invoice_file(clean_temp_files):
    first_siret = "12345678900"
    venue = offerers_factories.VenueFactory(siret=first_siret, pricing_point="self")
    offerer1 = venue.managingOfferer
    bank_account_1 = factories.BankAccountFactory(offerer=offerer1)
    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue, bankAccount=bank_account_1, timespan=(datetime.datetime.utcnow(),)
    )
    pricing1 = factories.PricingFactory(
        status=models.PricingStatus.VALIDATED,
        booking__stock__offer__venue=venue,
        booking__user__deposit__type=models.DepositType.GRANT_18,
        amount=-1000,
    )
    pline11 = factories.PricingLineFactory(pricing=pricing1, amount=-1100)
    pline12 = factories.PricingLineFactory(
        pricing=pricing1,
        amount=100,
        category=models.PricingLineCategory.OFFERER_CONTRIBUTION,
    )

    # add a pricing with identical pricing line values, to make sure it's taken into account
    pricing_with_same_values_as_pricing_1 = factories.PricingFactory(
        status=models.PricingStatus.VALIDATED,
        booking__stock__offer__venue=venue,
        booking__user__deposit__type=models.DepositType.GRANT_18,
        amount=-1000,
    )
    pline11_identical = factories.PricingLineFactory(pricing=pricing_with_same_values_as_pricing_1, amount=-1100)
    pline12_identical = factories.PricingLineFactory(
        pricing=pricing_with_same_values_as_pricing_1,
        amount=100,
        category=models.PricingLineCategory.OFFERER_CONTRIBUTION,
    )

    pricing2 = factories.PricingFactory(
        status=models.PricingStatus.VALIDATED,
        booking__stock__offer__venue=venue,
        booking__user__deposit__type=models.DepositType.GRANT_18,
        amount=-1000,
    )
    pline21 = factories.PricingLineFactory(pricing=pricing2, amount=-1100)
    pline22 = factories.PricingLineFactory(
        pricing=pricing2,
        amount=100,
        category=models.PricingLineCategory.OFFERER_CONTRIBUTION,
    )

    pricing3 = factories.PricingFactory(
        status=models.PricingStatus.VALIDATED,
        booking__stock__offer__venue=venue,
        booking__usedRecreditType=bookings_models.BookingRecreditType.RECREDIT_17,
        amount=-1000,
    )
    pline31 = factories.PricingLineFactory(pricing=pricing3, amount=-1100)
    pline32 = factories.PricingLineFactory(
        pricing=pricing3,
        amount=100,
        category=models.PricingLineCategory.OFFERER_CONTRIBUTION,
    )

    pricing4 = factories.PricingFactory(
        status=models.PricingStatus.VALIDATED,
        booking__stock__offer__venue=venue,
        booking__usedRecreditType=bookings_models.BookingRecreditType.RECREDIT_18,
        amount=-1000,
    )
    pline41 = factories.PricingLineFactory(pricing=pricing4, amount=-1100)
    pline42 = factories.PricingLineFactory(
        pricing=pricing4,
        amount=100,
        category=models.PricingLineCategory.OFFERER_CONTRIBUTION,
    )

    # eac pricing
    year1 = educational_factories.EducationalYearFactory()
    educational_institution = educational_factories.EducationalInstitutionFactory()
    deposit = educational_factories.EducationalDepositFactory(
        educationalInstitution=educational_institution,
        educationalYear=year1,
        ministry=educational_models.Ministry.AGRICULTURE.name,
    )
    collective_pricing = factories.CollectivePricingFactory(
        amount=-3000,
        collectiveBooking__collectiveStock__collectiveOffer__venue=venue,
        collectiveBooking__collectiveStock__startDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=5),
        collectiveBooking__educationalInstitution=deposit.educationalInstitution,
        collectiveBooking__educationalYear=deposit.educationalYear,
        status=models.PricingStatus.VALIDATED,
    )
    coll_pline1 = factories.PricingLineFactory(pricing=collective_pricing, amount=-3300)
    coll_pline2 = factories.PricingLineFactory(
        pricing=collective_pricing,
        amount=300,
        category=models.PricingLineCategory.OFFERER_CONTRIBUTION,
    )

    # eac related to a program
    educational_program = educational_factories.EducationalInstitutionProgramFactory(label="Marseille en grand")
    educational_institution_with_program = educational_factories.EducationalInstitutionFactory(
        programAssociations=[
            educational_factories.EducationalInstitutionProgramAssociationFactory(program=educational_program)
        ]
    )
    deposit_with_program = educational_factories.EducationalDepositFactory(
        educationalInstitution=educational_institution_with_program,
        educationalYear=year1,
        ministry=educational_models.Ministry.AGRICULTURE.name,
    )
    program_pricing = factories.CollectivePricingFactory(
        amount=-2345,
        collectiveBooking__collectiveStock__collectiveOffer__venue=venue,
        collectiveBooking__collectiveStock__startDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=8),
        collectiveBooking__educationalInstitution=educational_institution_with_program,
        collectiveBooking__educationalYear=deposit_with_program.educationalYear,
        status=models.PricingStatus.VALIDATED,
    )
    program_pline = factories.PricingLineFactory(pricing=program_pricing, amount=-2345)

    # eac related to a program left
    #
    one_year_ago = datetime.datetime.utcnow() - datetime.timedelta(days=365)
    two_years_ago = datetime.datetime.utcnow() - datetime.timedelta(days=2 * 365)
    educational_institution_with_program_left = educational_factories.EducationalInstitutionFactory(
        programAssociations=[
            educational_factories.EducationalInstitutionProgramAssociationFactory(
                program=educational_program, timespan=db_utils.make_timerange(start=two_years_ago, end=one_year_ago)
            )
        ]
    )
    deposit_with_program_left = educational_factories.EducationalDepositFactory(
        educationalInstitution=educational_institution_with_program_left,
        educationalYear=year1,
        ministry=educational_models.Ministry.AGRICULTURE.name,
    )
    program_pricing_left = factories.CollectivePricingFactory(
        amount=-600,
        collectiveBooking__collectiveStock__collectiveOffer__venue=venue,
        collectiveBooking__collectiveStock__startDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=8),
        collectiveBooking__educationalInstitution=educational_institution_with_program_left,
        collectiveBooking__educationalYear=deposit_with_program_left.educationalYear,
        status=models.PricingStatus.VALIDATED,
    )
    program_pline_left = factories.PricingLineFactory(pricing=program_pricing_left, amount=-600)

    # Create booking for overpayment finance incident
    incident_booking = bookings_factories.ReimbursedBookingFactory(
        amount=18,
        dateUsed=datetime.datetime.utcnow(),
        stock__offer__name="Une histoire plutôt bien",
        stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        stock__offer__venue=venue,
    )

    used_event = factories.UsedBookingFinanceEventFactory(booking=incident_booking)
    incident_booking_original_pricing = factories.PricingFactory(
        booking=incident_booking,
        event=used_event,
        status=models.PricingStatus.INVOICED,
        valueDate=datetime.datetime.utcnow(),
        amount=-1800,
    )
    factories.PricingLineFactory(pricing=incident_booking_original_pricing, amount=-1800)
    factories.PricingLineFactory(
        pricing=incident_booking_original_pricing,
        amount=0,
        category=models.PricingLineCategory.OFFERER_CONTRIBUTION,
    )

    # Create finance incident on the booking above (incident amount: 2€)
    booking_finance_incident = factories.IndividualBookingFinanceIncidentFactory(
        booking=incident_booking, newTotalAmount=1600
    )
    incident_events = api._create_finance_events_from_incident(booking_finance_incident, datetime.datetime.utcnow())

    incidents_pricings = []
    for event in incident_events:
        incidents_pricings.append(api.price_event(event))

    cashflow1 = factories.CashflowFactory(
        bankAccount=bank_account_1,
        pricings=[
            pricing1,
            pricing_with_same_values_as_pricing_1,
            pricing2,
            collective_pricing,
            program_pricing,
            program_pricing_left,
            pricing3,
            pricing4,
            *incidents_pricings,
        ],
        status=models.CashflowStatus.ACCEPTED,
    )
    invoice1 = factories.InvoiceFactory(
        bankAccount=bank_account_1,
        cashflows=[cashflow1],
    )

    nc_venue = offerers_factories.CaledonianVenueFactory(pricing_point="self")
    nc_offerer = nc_venue.managingOfferer
    nc_bank_account = factories.CaledonianBankAccountFactory(offerer=nc_offerer)
    offerers_factories.VenueBankAccountLinkFactory(
        venue=nc_venue, bankAccount=nc_bank_account, timespan=(datetime.datetime.utcnow(),)
    )
    underage_user = users_factories.UnderageBeneficiaryFactory()
    nc_pricing = factories.PricingFactory(
        status=models.PricingStatus.VALIDATED,
        booking__stock__offer__venue=nc_venue,
        booking__user=underage_user,
        amount=-1000,
    )
    nc_pline_1 = factories.PricingLineFactory(pricing=nc_pricing, amount=-1100)
    nc_pline_2 = factories.PricingLineFactory(
        pricing=nc_pricing,
        amount=100,
        category=models.PricingLineCategory.OFFERER_CONTRIBUTION,
    )
    # add the same pricing, that was transferred from a 15-17 to a 17-18
    nc_pricing_transferred = factories.PricingFactory(
        status=models.PricingStatus.VALIDATED,
        booking__stock__offer__venue=nc_venue,
        booking__user__deposit__type=models.DepositType.GRANT_17_18,
        booking__usedRecreditType=None,
        amount=-1000,
    )
    nc_pline_1_transferred = factories.PricingLineFactory(pricing=nc_pricing_transferred, amount=-1100)
    nc_pline_2_transferred = factories.PricingLineFactory(
        pricing=nc_pricing_transferred,
        amount=100,
        category=models.PricingLineCategory.OFFERER_CONTRIBUTION,
    )
    nc_cashflow = factories.CashflowFactory(
        bankAccount=nc_bank_account,
        pricings=[nc_pricing, nc_pricing_transferred],
        status=models.CashflowStatus.ACCEPTED,
        batch=cashflow1.batch,
    )
    nc_invoice = factories.InvoiceFactory(
        bankAccount=nc_bank_account,
        cashflows=[nc_cashflow],
    )

    # The file should contain only cashflows from the selected batch.
    # This second invoice should not appear.
    second_siret = "12345673900"
    venue2 = offerers_factories.VenueFactory(siret=second_siret, pricing_point="self")
    offerer2 = venue2.managingOfferer
    bank_account_2 = factories.BankAccountFactory(offerer=offerer2)
    offerers_factories.VenueBankAccountLinkFactory(venue=venue2, bankAccount=bank_account_2)
    pline5 = factories.PricingLineFactory()
    pricing5 = pline5.pricing
    cashflow2 = factories.CashflowFactory(
        bankAccount=bank_account_2,
        pricings=[pricing5],
        status=models.CashflowStatus.ACCEPTED,
    )
    factories.InvoiceFactory(
        bankAccount=bank_account_2,
        cashflows=[cashflow2],
        reference="not displayed because on a different date",
        date=datetime.datetime(2022, 1, 1),
    )

    # Freeze time so that we can guess the timestamp of the CSV file.
    with time_machine.travel(datetime.datetime(2023, 2, 1, 12, 34, 26)):
        path = api.generate_invoice_file(cashflow1.batch)
    with zipfile.ZipFile(path) as zfile:
        with zfile.open(f"invoices_{cashflow1.batch.label}_20230201_1334.csv") as csv_bytefile:
            csv_textfile = io.TextIOWrapper(csv_bytefile)
            reader = csv.DictReader(csv_textfile, quoting=csv.QUOTE_NONNUMERIC)
            rows = list(reader)

    assert len(rows) == 11
    assert rows[0] == {
        "Identifiant des coordonnées bancaires": str(bank_account_1.id),
        "Identifiant humanisé des coordonnées bancaires": human_ids.humanize(bank_account_1.id),
        "Date du justificatif": datetime.date.today().isoformat(),
        "Référence du justificatif": invoice1.reference,
        "Type de ticket de facturation": pline11.category.value,
        "Type de réservation": "AR18+",
        "Ministère": "",
        "Somme des tickets de facturation": pline11.amount + pline11_identical.amount + pline21.amount,
    }
    assert rows[1] == {
        "Identifiant des coordonnées bancaires": str(bank_account_1.id),
        "Identifiant humanisé des coordonnées bancaires": human_ids.humanize(bank_account_1.id),
        "Date du justificatif": datetime.date.today().isoformat(),
        "Référence du justificatif": invoice1.reference,
        "Type de ticket de facturation": pline12.category.value,
        "Type de réservation": "AR18+",
        "Ministère": "",
        "Somme des tickets de facturation": pline12.amount + pline12_identical.amount + pline22.amount,
    }
    assert rows[2] == {
        "Identifiant des coordonnées bancaires": str(bank_account_1.id),
        "Identifiant humanisé des coordonnées bancaires": human_ids.humanize(bank_account_1.id),
        "Date du justificatif": datetime.date.today().isoformat(),
        "Référence du justificatif": invoice1.reference,
        "Type de ticket de facturation": pline41.category.value,
        "Type de réservation": "PR18+",
        "Ministère": "",
        "Somme des tickets de facturation": pline41.amount + 200,  # 200 is the incident amount,
    }
    assert rows[3] == {
        "Identifiant des coordonnées bancaires": str(bank_account_1.id),
        "Identifiant humanisé des coordonnées bancaires": human_ids.humanize(bank_account_1.id),
        "Date du justificatif": datetime.date.today().isoformat(),
        "Référence du justificatif": invoice1.reference,
        "Type de ticket de facturation": pline42.category.value,
        "Type de réservation": "PR18+",
        "Ministère": "",
        "Somme des tickets de facturation": pline42.amount,
    }
    assert rows[4] == {
        "Identifiant des coordonnées bancaires": str(bank_account_1.id),
        "Identifiant humanisé des coordonnées bancaires": human_ids.humanize(bank_account_1.id),
        "Date du justificatif": datetime.date.today().isoformat(),
        "Référence du justificatif": invoice1.reference,
        "Type de ticket de facturation": pline31.category.value,
        "Type de réservation": "PR18-",
        "Ministère": "",
        "Somme des tickets de facturation": pline31.amount,
    }
    assert rows[5] == {
        "Identifiant des coordonnées bancaires": str(bank_account_1.id),
        "Identifiant humanisé des coordonnées bancaires": human_ids.humanize(bank_account_1.id),
        "Date du justificatif": datetime.date.today().isoformat(),
        "Référence du justificatif": invoice1.reference,
        "Type de ticket de facturation": pline32.category.value,
        "Type de réservation": "PR18-",
        "Ministère": "",
        "Somme des tickets de facturation": pline32.amount,
    }
    # New Caledonia
    assert rows[6] == {
        "Identifiant des coordonnées bancaires": str(nc_bank_account.id),
        "Identifiant humanisé des coordonnées bancaires": human_ids.humanize(nc_bank_account.id),
        "Date du justificatif": datetime.date.today().isoformat(),
        "Référence du justificatif": nc_invoice.reference,
        "Type de ticket de facturation": nc_pline_1.category.value,
        "Type de réservation": "AR18-",
        "Ministère": "NC",
        "Somme des tickets de facturation": nc_pline_1.amount + nc_pline_1_transferred.amount,
    }
    assert rows[7] == {
        "Identifiant des coordonnées bancaires": str(nc_bank_account.id),
        "Identifiant humanisé des coordonnées bancaires": human_ids.humanize(nc_bank_account.id),
        "Date du justificatif": datetime.date.today().isoformat(),
        "Référence du justificatif": nc_invoice.reference,
        "Type de ticket de facturation": nc_pline_2.category.value,
        "Type de réservation": "AR18-",
        "Ministère": "NC",
        "Somme des tickets de facturation": nc_pline_2.amount + nc_pline_2_transferred.amount,
    }
    # collective pricing lines
    assert rows[8] == {
        "Identifiant des coordonnées bancaires": str(bank_account_1.id),
        "Identifiant humanisé des coordonnées bancaires": human_ids.humanize(bank_account_1.id),
        "Date du justificatif": datetime.date.today().isoformat(),
        "Référence du justificatif": invoice1.reference,
        "Type de ticket de facturation": coll_pline1.category.value,
        "Type de réservation": "EACC",
        "Ministère": "AGRICULTURE",
        "Somme des tickets de facturation": coll_pline1.amount + program_pline_left.amount,
    }
    assert rows[9] == {
        "Identifiant des coordonnées bancaires": str(bank_account_1.id),
        "Identifiant humanisé des coordonnées bancaires": human_ids.humanize(bank_account_1.id),
        "Date du justificatif": datetime.date.today().isoformat(),
        "Référence du justificatif": invoice1.reference,
        "Type de ticket de facturation": coll_pline2.category.value,
        "Type de réservation": "EACC",
        "Ministère": "AGRICULTURE",
        "Somme des tickets de facturation": coll_pline2.amount,
    }
    assert rows[10] == {
        "Identifiant des coordonnées bancaires": str(bank_account_1.id),
        "Identifiant humanisé des coordonnées bancaires": human_ids.humanize(bank_account_1.id),
        "Date du justificatif": datetime.date.today().isoformat(),
        "Référence du justificatif": invoice1.reference,
        "Type de ticket de facturation": program_pline.category.value,
        "Type de réservation": "EACC",
        "Ministère": educational_program.label,
        "Somme des tickets de facturation": program_pline.amount,
    }


class GenerateDebitNotesTest:
    @mock.patch("pcapi.core.finance.api._generate_debit_note_html")
    @mock.patch("pcapi.core.finance.api._store_invoice_pdf")
    @pytest.mark.usefixtures("clean_temp_files")
    def test_when_there_is_no_debit_note_to_generate(self, _mocked1, _mocked2):
        user = users_factories.RichBeneficiaryFactory()
        venue_kwargs = {
            "pricing_point": "self",
        }
        venue = offerers_factories.VenueFactory(**venue_kwargs)
        book_offer = offers_factories.OfferFactory(venue=venue, subcategoryId=subcategories.LIVRE_PAPIER.id)
        factories.CustomReimbursementRuleFactory(amount=2850, offer=book_offer)

        incident_booking1_event = factories.UsedBookingFinanceEventFactory(
            booking__stock=offers_factories.StockFactory(offer=book_offer, price=30, quantity=1),
            booking__user=user,
            booking__amount=30,
            booking__quantity=1,
        )

        api.price_event(incident_booking1_event)
        incident_booking1_event.booking.pricings[0].status = models.PricingStatus.INVOICED
        db.session.flush()

        booking_total_incident = factories.IndividualBookingFinanceIncidentFactory(
            incident__status=models.IncidentStatus.VALIDATED,
            incident__forceDebitNote=True,
            incident__venue=venue,
            booking=incident_booking1_event.booking,
            newTotalAmount=-incident_booking1_event.booking.total_amount * 100,
        )
        incident_event = api._create_finance_events_from_incident(booking_total_incident, datetime.datetime.utcnow())

        api.price_event(incident_event[0])

        batch = api.generate_cashflows_and_payment_files(datetime.datetime.utcnow())

        with pytest.raises(exceptions.NoInvoiceToGenerate):
            api.generate_invoices_and_debit_notes_legacy(batch)

        invoices = db.session.query(models.Invoice).all()
        assert len(invoices) == 0


@pytest.fixture(name="invoice_data")
def invoice_test_data():
    venue_kwargs = {
        "pricing_point": "self",
    }
    offerer = offerers_factories.OffererFactory(name="Association de coiffeurs", siren="853318459")
    venue = offerers_factories.VenueFactory(
        publicName="Coiffeur justificaTIF",
        name="Coiffeur explicaTIF",
        siret="85331845900023",
        bookingEmail="pro@example.com",
        managingOfferer=offerer,
        **venue_kwargs,
    )
    bank_account = factories.BankAccountFactory(
        offerer=offerer, iban="FR2710010000000000000000064", label="Compte bancaire Coiffeur"
    )
    offerers_factories.VenueBankAccountLinkFactory(venue=venue, bankAccount=bank_account)

    thing_offer1 = offers_factories.ThingOfferFactory(venue=venue)
    thing_offer2 = offers_factories.ThingOfferFactory(venue=venue)
    book_offer1 = offers_factories.OfferFactory(venue=venue, subcategoryId=subcategories.LIVRE_PAPIER.id)
    book_offer2 = offers_factories.OfferFactory(venue=venue, subcategoryId=subcategories.LIVRE_PAPIER.id)
    digital_offer1 = offers_factories.DigitalOfferFactory(venue=venue)
    digital_offer2 = offers_factories.DigitalOfferFactory(venue=venue)
    custom_rule_offer1 = offers_factories.ThingOfferFactory(venue=venue)
    factories.CustomReimbursementRuleFactory(rate=0.94, offer=custom_rule_offer1)
    custom_rule_offer2 = offers_factories.ThingOfferFactory(venue=venue)
    factories.CustomReimbursementRuleFactory(amount=2200, offer=custom_rule_offer2)

    stocks = [
        offers_factories.StockFactory(offer=thing_offer1, price=30),
        offers_factories.StockFactory(offer=book_offer1, price=20),
        offers_factories.StockFactory(offer=thing_offer2, price=19_950),
        offers_factories.StockFactory(offer=thing_offer2, price=81.3),
        offers_factories.StockFactory(offer=book_offer2, price=40),
        offers_factories.StockFactory(offer=digital_offer1, price=27),
        offers_factories.StockFactory(offer=digital_offer2, price=31),
        offers_factories.StockFactory(offer=custom_rule_offer1, price=20),
        offers_factories.StockFactory(offer=custom_rule_offer2, price=23),
    ]

    return bank_account, stocks, venue


@pytest.fixture(name="invoice_nc_data")
def invoice_nc_test_data():
    venue_kwargs = {
        "pricing_point": "self",
    }
    offerer = offerers_factories.CaledonianOffererFactory(name="Association de coiffeurs", siren="NC8533184")
    venue = offerers_factories.CaledonianVenueFactory(
        publicName="Coiffeur justificaTIF",
        name="Coiffeur explicaTIF",
        siret="NC8533184234XX",
        bookingEmail="pro@example.com",
        managingOfferer=offerer,
        **venue_kwargs,
    )
    bank_account = factories.CaledonianBankAccountFactory(
        offerer=offerer, iban="NC5307528000009880000000100", label="Compte bancaire Coiffeur"
    )
    offerers_factories.VenueBankAccountLinkFactory(venue=venue, bankAccount=bank_account)

    thing_offer1 = offers_factories.ThingOfferFactory(venue=venue)
    thing_offer2 = offers_factories.ThingOfferFactory(venue=venue)
    book_offer1 = offers_factories.OfferFactory(venue=venue, subcategoryId=subcategories.LIVRE_PAPIER.id)
    book_offer2 = offers_factories.OfferFactory(venue=venue, subcategoryId=subcategories.LIVRE_PAPIER.id)
    digital_offer1 = offers_factories.DigitalOfferFactory(venue=venue)
    digital_offer2 = offers_factories.DigitalOfferFactory(venue=venue)
    custom_rule_offer1 = offers_factories.ThingOfferFactory(venue=venue)
    factories.CustomReimbursementRuleFactory(rate=0.94, offer=custom_rule_offer1)
    custom_rule_offer2 = offers_factories.ThingOfferFactory(venue=venue)
    factories.CustomReimbursementRuleFactory(amount=2200, offer=custom_rule_offer2)

    stocks = [
        offers_factories.StockFactory(offer=thing_offer1, price=30),
        offers_factories.StockFactory(offer=book_offer1, price=20),
        offers_factories.StockFactory(offer=thing_offer2, price=19_950),
        offers_factories.StockFactory(offer=thing_offer2, price=81.3),
        offers_factories.StockFactory(offer=book_offer2, price=40),
        offers_factories.StockFactory(offer=digital_offer1, price=27),
        offers_factories.StockFactory(offer=digital_offer2, price=31),
        offers_factories.StockFactory(offer=custom_rule_offer1, price=20),
        offers_factories.StockFactory(offer=custom_rule_offer2, price=23),
    ]

    return bank_account, stocks, venue


class GenerateInvoicesTest:
    # Mock slow functions that we are not interested in.
    @mock.patch("pcapi.core.finance.api._generate_invoice_html")
    @mock.patch("pcapi.core.finance.api._store_invoice_pdf")
    @pytest.mark.usefixtures("clean_temp_files")
    def test_basics(self, _mocked1, _mocked2):
        stock1 = offers_factories.ThingStockFactory(offer__venue__pricing_point="self")
        finance_event1 = factories.UsedBookingFinanceEventFactory(booking__stock=stock1)
        booking1 = finance_event1.booking
        stock2 = offers_factories.ThingStockFactory(offer__venue__pricing_point="self")
        finance_event2 = factories.UsedBookingFinanceEventFactory(booking__stock=stock2)
        booking2 = finance_event2.booking
        for finance_event in (finance_event1, finance_event2):
            b_a = factories.BankAccountFactory()
            offerers_factories.VenueBankAccountLinkFactory(venue=finance_event.booking.venue, bankAccount=b_a)

        # Cashflows for booking1 and booking2 will be UNDER_REVIEW.
        api.price_event(finance_event1)
        api.price_event(finance_event2)
        batch = api.generate_cashflows_and_payment_files(datetime.datetime.utcnow())

        api.generate_invoices_and_debit_notes_legacy(batch)

        invoices = db.session.query(models.Invoice).all()
        assert len(invoices) == 2
        invoiced_bookings = {inv.cashflows[0].pricings[0].booking for inv in invoices}
        assert invoiced_bookings == {booking1, booking2}
        assert {invoice.status for invoice in invoices} == {models.InvoiceStatus.PAID}

    @mock.patch("pcapi.core.finance.api._generate_invoice_html")
    @mock.patch("pcapi.core.finance.api._store_invoice_pdf")
    def test_invoice_cashflows_with_0_amount(self, _generate_invoice_html, _store_invoice_pdf):
        stock = offers_factories.ThingStockFactory(offer__venue__pricing_point="self")
        finance_event = factories.UsedBookingFinanceEventFactory(booking__stock=stock)
        booking = finance_event.booking
        bank_account = factories.BankAccountFactory()
        offerers_factories.VenueBankAccountLinkFactory(venue=finance_event.booking.venue, bankAccount=bank_account)
        factories.CustomReimbursementRuleFactory(rate=0, venue=finance_event.booking.venue)

        api.price_event(finance_event)
        batch = api.generate_cashflows_and_payment_files(datetime.datetime.utcnow())

        api.generate_invoices_and_debit_notes_legacy(batch)

        invoices = db.session.query(models.Invoice).all()
        assert len(invoices) == 1
        invoice = invoices[0]
        assert len(invoice.cashflows) == 1
        cashflow = invoice.cashflows[0]
        assert cashflow.amount == 0

        assert len(cashflow.pricings) == 1
        pricing = cashflow.pricings[0]
        assert pricing.booking == booking

    @mock.patch("pcapi.core.finance.api._generate_invoice_html")
    @mock.patch("pcapi.core.finance.api._store_invoice_pdf")
    @pytest.mark.usefixtures("clean_temp_files")
    def test_with_free_pricings(self, _generate_invoice_html, _store_invoice_pdf):
        normal_venue = offerers_factories.VenueFactory(pricing_point="self")
        normal_bank_account = factories.BankAccountFactory(offerer=normal_venue.managingOfferer)
        offerers_factories.VenueBankAccountLinkFactory(venue=normal_venue, bankAccount=normal_bank_account)
        user = users_factories.BeneficiaryGrant18Factory(deposit__amount=300)
        normal_booking = bookings_factories.BookingFactory(
            user=user,
            quantity=1,
            stock__price=Decimal("10"),
            stock__offer__venue=normal_venue,
        )  # 10€
        normal_free_booking = bookings_factories.BookingFactory(
            user=user,
            quantity=1,
            stock__price=Decimal("0"),
            stock__offer__venue=normal_venue,
        )  # 0€
        bookings_api.mark_as_used(
            booking=normal_booking,
            validation_author_type=bookings_models.BookingValidationAuthorType.OFFERER,
        )
        bookings_api.mark_as_used(
            booking=normal_free_booking,
            validation_author_type=bookings_models.BookingValidationAuthorType.OFFERER,
        )

        free_venue = offerers_factories.VenueFactory(pricing_point="self")
        free_bank_account = factories.BankAccountFactory(offerer=free_venue.managingOfferer)
        offerers_factories.VenueBankAccountLinkFactory(venue=free_venue, bankAccount=free_bank_account)
        user = users_factories.BeneficiaryGrant18Factory(deposit__amount=300)
        free_booking = bookings_factories.BookingFactory(
            user=user,
            quantity=1,
            stock__price=Decimal("0"),
            stock__offer__venue=free_venue,
        )  # 0€
        bookings_api.mark_as_used(
            booking=free_booking,
            validation_author_type=bookings_models.BookingValidationAuthorType.OFFERER,
        )

        finance_events = db.session.query(models.FinanceEvent).all()
        assert len(finance_events) == 3

        booking_pricing_dict = dict()
        for fe in finance_events:
            booking_pricing_dict[fe.bookingId] = api.price_event(fe)

        normal_pricing = booking_pricing_dict[normal_booking.id]
        normal_free_pricing = booking_pricing_dict[normal_free_booking.id]
        free_pricing = booking_pricing_dict[free_booking.id]

        for pricing in [normal_free_pricing, free_pricing]:
            assert pricing.amount == 0
            assert pricing.status == models.PricingStatus.VALIDATED

            assert len(pricing.lines) == 2
            assert {line.category for line in pricing.lines} == {
                models.PricingLineCategory.OFFERER_REVENUE,
                models.PricingLineCategory.OFFERER_CONTRIBUTION,
            }
            pricing_line_offerer_revenue = next(
                line for line in pricing.lines if line.category == models.PricingLineCategory.OFFERER_REVENUE
            )
            pricing_line_offerer_contribution = next(
                line for line in pricing.lines if line.category == models.PricingLineCategory.OFFERER_CONTRIBUTION
            )
            assert pricing_line_offerer_revenue.amount == 0
            assert pricing_line_offerer_contribution.amount == 0

        #################################################
        # Invoice the booking and reimburse the offerer #
        #################################################
        batch = api.generate_cashflows_and_payment_files(datetime.datetime.utcnow() + datetime.timedelta(days=3))
        assert len(batch.cashflows) == 1

        api.generate_invoices_and_debit_notes_legacy(batch)

        assert 1 == db.session.query(models.Invoice).count()
        for pricing in [normal_pricing, normal_free_pricing, free_pricing]:
            assert pricing.status == models.PricingStatus.INVOICED


class GenerateInvoiceTest:
    EXPECTED_NUM_QUERIES = (
        # 1   # feature flags are already cached by BeneficiaryGrant18Factory.beneficiaryImports
        1  # lock reimbursement point
        + 1  # select cashflows, pricings, pricing_lines, and custom_reimbursement_rules
        + 1  # select and lock ReferenceScheme
        + 1  # update ReferenceScheme
        + 1  # insert invoice
        + 1  # insert invoice lines
        + 1  # insert invoice_cashflows
        + 1  # update Cashflow.status and add CashflowLog
        + 1  # update Pricing.status and add PricingLog
        + 1  # select Booking.id
        + 1  # update Booking.status
        + 1  # update CollectiveBooking.status
    )

    def test_one_regular_rule_one_rate(self):
        venue1 = offerers_factories.VenueFactory()
        bank_account = factories.BankAccountFactory()
        offerers_factories.VenueBankAccountLinkFactory(venue=venue1, bankAccount=bank_account)
        venue2 = offerers_factories.VenueFactory(
            managingOfferer=venue1.managingOfferer,
            pricing_point="self",
        )
        offerers_factories.VenueBankAccountLinkFactory(venue=venue2, bankAccount=bank_account)

        offer = offers_factories.ThingOfferFactory(venue=venue2)
        stock = offers_factories.ThingStockFactory(offer=offer, price=20)
        finance_event1 = factories.UsedBookingFinanceEventFactory(booking__stock=stock)
        finance_event2 = factories.UsedBookingFinanceEventFactory(booking__stock=stock)
        api.price_event(finance_event1)
        api.price_event(finance_event2)
        batch = api.generate_cashflows(datetime.datetime.utcnow())
        api.generate_payment_files(batch)  # mark cashflows as UNDER_REVIEW
        cashflow_ids = [c.id for c in db.session.query(models.Cashflow).all()]

        with transaction():
            current_year = datetime.date.today().year
            scheme = reference_models.ReferenceScheme.get_and_lock("invoice.reference", current_year)
            scheme.reset_next_number()

        bank_account_id = bank_account.id
        with assert_num_queries(self.EXPECTED_NUM_QUERIES):
            invoice = api._generate_invoice_legacy(
                bank_account_id=bank_account_id,
                cashflow_ids=cashflow_ids,
            )

        year = invoice.date.year % 100
        assert invoice.reference == f"F{year}0000001"
        assert invoice.bankAccount == bank_account
        assert invoice.amount == -40 * 100
        assert len(invoice.lines) == 1
        line = invoice.lines[0]
        assert line.group == {"label": "Barème général", "position": 1}
        assert line.contributionAmount == 0
        assert line.reimbursedAmount == -40 * 100
        assert line.rate == 1
        assert line.label == "Réservations"

    def test_two_regular_rules_two_rates(self):
        venue1 = offerers_factories.VenueFactory()
        bank_account = factories.BankAccountFactory(offerer=venue1.managingOfferer)
        offerers_factories.VenueBankAccountLinkFactory(venue=venue1, bankAccount=bank_account)
        venue2 = offerers_factories.VenueFactory(
            managingOfferer=venue1.managingOfferer,
            pricing_point="self",
        )
        offerers_factories.VenueBankAccountLinkFactory(venue=venue2, bankAccount=bank_account)

        offer = offers_factories.ThingOfferFactory(venue=venue2)
        stock1 = offers_factories.ThingStockFactory(offer=offer, price=19_850)
        stock2 = offers_factories.ThingStockFactory(offer=offer, price=160)
        user_1 = users_factories.RichBeneficiaryFactory()
        user_2 = users_factories.RichBeneficiaryFactory()
        finance_event1 = factories.UsedBookingFinanceEventFactory(booking__stock=stock1, booking__user=user_1)
        finance_event2 = factories.UsedBookingFinanceEventFactory(booking__stock=stock2, booking__user=user_2)
        api.price_event(finance_event1)
        api.price_event(finance_event2)
        batch = api.generate_cashflows(datetime.datetime.utcnow())
        api.generate_payment_files(batch)  # mark cashflows as UNDER_REVIEW
        cashflow_ids = [c.id for c in db.session.query(models.Cashflow).all()]

        bank_account_id = bank_account.id
        with assert_num_queries(self.EXPECTED_NUM_QUERIES):
            invoice = api._generate_invoice_legacy(
                bank_account_id=bank_account_id,
                cashflow_ids=cashflow_ids,
            )

        assert invoice.bankAccount == bank_account
        # 100% of 19_850*100 + 95% of 160*100 aka 152*100
        assert invoice.amount == -20_002 * 100
        assert len(invoice.lines) == 2
        invoice_lines = sorted(invoice.lines, key=lambda x: x.rate, reverse=True)

        line_rate_1 = invoice_lines[0]
        assert line_rate_1.group == {"label": "Barème général", "position": 1}
        assert line_rate_1.contributionAmount == 0
        assert line_rate_1.reimbursedAmount == -19_850 * 100
        assert line_rate_1.rate == 1
        assert line_rate_1.label == "Réservations"
        line_rate_0_95 = invoice_lines[1]
        assert line_rate_0_95.group == {"label": "Barème général", "position": 1}
        assert line_rate_0_95.contributionAmount == 8 * 100
        assert line_rate_0_95.reimbursedAmount == -152 * 100
        assert line_rate_0_95.rate == Decimal("0.95")
        assert line_rate_0_95.label == "Réservations"

    def test_one_custom_rule(self):
        venue1 = offerers_factories.VenueFactory()
        bank_account = factories.BankAccountFactory(offerer=venue1.managingOfferer)
        offerers_factories.VenueBankAccountLinkFactory(venue=venue1, bankAccount=bank_account)
        venue2 = offerers_factories.VenueFactory(
            managingOfferer=venue1.managingOfferer,
            pricing_point="self",
        )
        offerers_factories.VenueBankAccountLinkFactory(venue=venue2, bankAccount=bank_account)

        offer = offers_factories.ThingOfferFactory(venue=venue2)
        stock = offers_factories.ThingStockFactory(offer=offer, price=23)
        factories.CustomReimbursementRuleFactory(amount=2200, offer=offer)
        finance_event1 = factories.UsedBookingFinanceEventFactory(booking__stock=stock)
        finance_event2 = factories.UsedBookingFinanceEventFactory(booking__stock=stock)
        api.price_event(finance_event1)
        api.price_event(finance_event2)
        batch = api.generate_cashflows(datetime.datetime.utcnow())
        api.generate_payment_files(batch)  # mark cashflows as UNDER_REVIEW
        cashflow_ids = [c.id for c in db.session.query(models.Cashflow).all()]

        bank_account_id = bank_account.id
        with assert_num_queries(self.EXPECTED_NUM_QUERIES):
            invoice = api._generate_invoice_legacy(
                bank_account_id=bank_account_id,
                cashflow_ids=cashflow_ids,
            )

        assert invoice.bankAccount == bank_account
        assert invoice.amount == -4400
        assert len(invoice.lines) == 1
        line = invoice.lines[0]
        assert line.group == {"label": "Barème dérogatoire", "position": 4}
        assert line.contributionAmount == 200
        assert line.reimbursedAmount == -4400
        assert line.rate == Decimal("0.9565")
        assert line.label == "Réservations"

    def test_full_offerer_contribution(self):
        venue = offerers_factories.VenueFactory(pricing_point="self")

        bank_account = factories.BankAccountFactory(offerer=venue.managingOfferer)
        offerers_factories.VenueBankAccountLinkFactory(venue=venue, bankAccount=bank_account)

        offer = offers_factories.ThingOfferFactory(venue=venue)
        factories.CustomReimbursementRuleFactory(rate=0, offer=offer)

        stock = offers_factories.EventStockFactory(
            offer=offer,
            beginningDatetime=datetime.datetime.utcnow(),
            price=23,
        )
        booking = bookings_factories.UsedBookingFactory(stock=stock)
        finance_event = factories.FinanceEventFactory(
            booking=booking,
            pricingOrderingDate=stock.beginningDatetime,
            status=models.FinanceEventStatus.READY,
            venue=venue,
        )

        api.price_event(finance_event)
        batch = api.generate_cashflows(datetime.datetime.utcnow())
        api.generate_payment_files(batch)
        cashflow_ids = [c.id for c in db.session.query(models.Cashflow).all()]

        bank_account_id = bank_account.id
        with assert_num_queries(self.EXPECTED_NUM_QUERIES):
            invoice = api._generate_invoice_legacy(
                bank_account_id=bank_account_id,
                cashflow_ids=cashflow_ids,
            )

        assert invoice.bankAccount == bank_account
        assert invoice.amount == 0

        assert len(invoice.lines) == 1
        line = invoice.lines[0]
        assert line.group == {"label": "Barème dérogatoire", "position": 4}
        assert line.reimbursedAmount == 0
        assert line.contributionAmount == 2300
        assert line.rate == Decimal("0")
        assert line.label == "Réservations"

    def test_100_per_cent_offerer_contribution_mixed(self):
        venue1 = offerers_factories.VenueFactory(pricing_point="self")
        bank_account = factories.BankAccountFactory(offerer=venue1.managingOfferer)
        offerers_factories.VenueBankAccountLinkFactory(venue=venue1, bankAccount=bank_account)
        venue2 = offerers_factories.VenueFactory(managingOfferer=venue1.managingOfferer, pricing_point="self")
        offerers_factories.VenueBankAccountLinkFactory(venue=venue2, bankAccount=bank_account)

        offer1 = offers_factories.DigitalOfferFactory(venue=venue1)
        stock1 = offers_factories.EventStockFactory(
            offer=offer1, beginningDatetime=datetime.datetime.utcnow(), price=10
        )
        offer2 = offers_factories.ThingOfferFactory(venue=venue2)
        stock2 = offers_factories.ThingStockFactory(offer=offer2, price=50)
        factories.CustomReimbursementRuleFactory(amount=600, offer=offer2)
        finance_event1 = factories.UsedBookingFinanceEventFactory(booking__stock=stock1)
        finance_event2 = factories.UsedBookingFinanceEventFactory(booking__stock=stock2)
        api.price_event(finance_event1)
        api.price_event(finance_event2)
        batch = api.generate_cashflows(datetime.datetime.utcnow())
        api.generate_payment_files(batch)
        cashflow_ids = [c.id for c in db.session.query(models.Cashflow).all()]

        bank_account_id = bank_account.id
        with assert_num_queries(self.EXPECTED_NUM_QUERIES):
            invoice = api._generate_invoice_legacy(
                bank_account_id=bank_account_id,
                cashflow_ids=cashflow_ids,
            )

        assert invoice.bankAccount == bank_account
        assert invoice.amount == -600

        assert len(invoice.lines) == 2
        assert {line.reimbursedAmount for line in invoice.lines} == {0, -600}
        line1 = next(line for line in invoice.lines if line.reimbursedAmount == 0)
        line2 = next(line for line in invoice.lines if line.reimbursedAmount == -600)

        assert line1.group == {"label": "Barème non remboursé", "position": 3}
        assert line1.contributionAmount == 1000
        assert line1.rate == Decimal("0")
        assert line1.label == "Réservations"

        assert line2.group == {"label": "Barème dérogatoire", "position": 4}
        assert line2.contributionAmount == 4400
        assert line2.rate == Decimal("0.12")
        assert line2.label == "Réservations"

    def test_many_rules_and_rates_two_cashflows(self, invoice_data):
        bank_account, stocks, _venue = invoice_data
        finance_events = []
        user = users_factories.RichBeneficiaryFactory()
        for stock in stocks:
            finance_event = factories.UsedBookingFinanceEventFactory(
                booking__stock=stock,
                booking__user=user,
            )
            finance_events.append(finance_event)
        for finance_event in finance_events[:3]:
            api.price_event(finance_event)
        batch = api.generate_cashflows(cutoff=datetime.datetime.utcnow())
        api.generate_payment_files(batch)  # mark cashflows as UNDER_REVIEW
        for finance_event in finance_events[3:]:
            api.price_event(finance_event)
        batch = api.generate_cashflows(cutoff=datetime.datetime.utcnow())
        api.generate_payment_files(batch)  # mark cashflows as UNDER_REVIEW
        cashflow_ids = [c.id for c in db.session.query(models.Cashflow).all()]

        bank_account_id = bank_account.id
        with assert_num_queries(self.EXPECTED_NUM_QUERIES):
            invoice = api._generate_invoice_legacy(
                bank_account_id=bank_account_id,
                cashflow_ids=cashflow_ids,
            )

        assert len(invoice.cashflows) == 2
        assert invoice.bankAccount == bank_account
        assert invoice.amount == -20_156_04
        # général 100%, général 95%, livre 100%, livre 95%, pas remboursé, custom 1, custom 2
        assert len(invoice.lines) == 7

        # sort by group position asc then rate desc, as displayed in the PDF
        invoice_lines = sorted(invoice.lines, key=lambda k: (k.group["position"], -k.rate))

        line0 = invoice_lines[0]
        assert line0.group == {"label": "Barème général", "position": 1}
        assert line0.contributionAmount == 0
        assert line0.reimbursedAmount == -19_980 * 100  # 19_950 + 30
        assert line0.rate == Decimal("1.0000")
        assert line0.label == "Réservations"

        line1 = invoice_lines[1]
        assert line1.group == {"label": "Barème général", "position": 1}
        assert line1.contributionAmount == 406
        assert line1.reimbursedAmount == -7724
        assert line1.rate == Decimal("0.9500")
        assert line1.label == "Réservations"

        line2 = invoice_lines[2]
        assert line2.group == {"label": "Barème livres", "position": 2}
        assert line2.contributionAmount == 0
        assert line2.reimbursedAmount == -20 * 100
        assert line2.rate == Decimal("1.0000")
        assert line2.label == "Réservations"

        line3 = invoice_lines[3]
        assert line3.group == {"label": "Barème livres", "position": 2}
        assert line3.contributionAmount == 2 * 100
        assert line3.reimbursedAmount == -38 * 100
        assert line3.rate == Decimal("0.9500")
        assert line3.label == "Réservations"

        line4 = invoice_lines[4]
        assert line4.group == {"label": "Barème non remboursé", "position": 3}
        assert line4.contributionAmount == 58 * 100
        assert line4.reimbursedAmount == 0
        assert line4.rate == Decimal("0.0000")
        assert line4.label == "Réservations"

        line5 = invoice_lines[5]
        assert line5.group == {"label": "Barème dérogatoire", "position": 4}
        assert line5.contributionAmount == 100
        assert line5.reimbursedAmount == -22 * 100
        assert line5.rate == Decimal("0.9565")
        assert line5.label == "Réservations"

        line6 = invoice_lines[6]
        assert line6.group == {"label": "Barème dérogatoire", "position": 4}
        assert line6.contributionAmount == 120
        assert line6.reimbursedAmount == -1880
        assert line6.rate == Decimal("0.9400")
        assert line6.label == "Réservations"

    def test_with_free_offer(self):
        venue1 = offerers_factories.VenueFactory()
        bank_account = factories.BankAccountFactory(offerer=venue1.managingOfferer)
        offerers_factories.VenueBankAccountLinkFactory(venue=venue1, bankAccount=bank_account)
        venue2 = offerers_factories.VenueFactory(
            managingOfferer=venue1.managingOfferer,
            pricing_point="self",
        )
        offerers_factories.VenueBankAccountLinkFactory(venue=venue2, bankAccount=bank_account)

        # 2 offers that have a distinct reimbursement rate rule.
        offer1 = offers_factories.ThingOfferFactory(
            venue=venue2,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        )
        stock1 = offers_factories.StockFactory(offer=offer1, price=20)
        finance_event1 = factories.UsedBookingFinanceEventFactory(booking__stock=stock1)
        offer2 = offers_factories.ThingOfferFactory(
            venue=venue2,
            subcategoryId=subcategories.TELECHARGEMENT_MUSIQUE.id,
        )
        stock2 = offers_factories.StockFactory(offer=offer2, price=0)
        finance_event2 = factories.UsedBookingFinanceEventFactory(booking__stock=stock2)
        api.price_event(finance_event1)
        api.price_event(finance_event2)
        batch = api.generate_cashflows(datetime.datetime.utcnow())
        api.generate_payment_files(batch)  # mark cashflows as UNDER_REVIEW
        cashflow_ids = [c.id for c in db.session.query(models.Cashflow).all()]

        bank_account_id = bank_account.id
        with assert_num_queries(self.EXPECTED_NUM_QUERIES):
            invoice = api._generate_invoice_legacy(
                bank_account_id=bank_account_id,
                cashflow_ids=cashflow_ids,
            )

        assert invoice.amount == -20 * 100
        assert len(invoice.lines) == 1
        line = invoice.lines[0]
        assert line.group == {"label": "Barème général", "position": 1}
        assert line.contributionAmount == 0
        assert line.reimbursedAmount == -20 * 100
        assert line.rate == 1
        assert line.label == "Réservations"

    def test_update_statuses_and_booking_reimbursement_date(self):
        offerer = offerers_factories.OffererFactory(name="Association de coiffeurs", siren="853318459")
        bank_account = factories.BankAccountFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(
            pricing_point="self", managingOfferer=offerer, bank_account=bank_account
        )
        offer = offers_factories.ThingOfferFactory(venue=venue)
        stock = offers_factories.ThingStockFactory(offer=offer)
        indiv_finance_event1 = factories.UsedBookingFinanceEventFactory(booking__stock=stock)
        indiv_booking1 = indiv_finance_event1.booking
        indiv_finance_event2 = factories.UsedBookingFinanceEventFactory(booking__stock=stock)
        indiv_booking2 = indiv_finance_event2.booking
        past = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        collective_finance_event1 = factories.UsedCollectiveBookingFinanceEventFactory(
            collectiveBooking__collectiveStock__startDatetime=past,
            collectiveBooking__collectiveStock__collectiveOffer__venue=venue,
        )
        collective_booking1 = collective_finance_event1.collectiveBooking
        collective_finance_event2 = factories.UsedCollectiveBookingFinanceEventFactory(
            collectiveBooking__collectiveStock__startDatetime=past,
            collectiveBooking__collectiveStock__collectiveOffer__venue=venue,
        )
        collective_booking2 = collective_finance_event2.collectiveBooking
        for e in (collective_finance_event1, collective_finance_event2, indiv_finance_event1, indiv_finance_event2):
            api.price_event(e)
        batch = api.generate_cashflows(datetime.datetime.utcnow())
        api.generate_payment_files(batch)  # mark cashflow as UNDER_REVIEW
        cashflow = db.session.query(models.Cashflow).one()
        pricings = db.session.query(models.Pricing).all()
        assert cashflow.status == models.CashflowStatus.UNDER_REVIEW
        assert cashflow.logs[0].statusBefore == models.CashflowStatus.PENDING
        assert cashflow.logs[0].statusAfter == models.CashflowStatus.UNDER_REVIEW
        indiv_booking2.status = bookings_models.BookingStatus.CANCELLED
        collective_booking2.status = educational_models.CollectiveBookingStatus.CANCELLED
        db.session.flush()

        invoice = api._generate_invoice_legacy(
            bank_account_id=bank_account.id,
            cashflow_ids=[cashflow.id],
        )

        assert invoice.status == models.InvoiceStatus.PAID
        assert cashflow.status == models.CashflowStatus.ACCEPTED
        assert cashflow.logs[1].statusBefore == models.CashflowStatus.UNDER_REVIEW
        assert cashflow.logs[1].statusAfter == models.CashflowStatus.ACCEPTED
        for pricing in pricings:
            assert pricing.logs[1].statusBefore == models.PricingStatus.PROCESSED
            assert pricing.logs[1].statusAfter == models.PricingStatus.INVOICED
            assert pricing.logs[1].reason == models.PricingLogReason.GENERATE_INVOICE
        cashflow_statuses = get_statuses(models.Cashflow)
        assert cashflow_statuses == {models.CashflowStatus.ACCEPTED}
        pricing_statuses = get_statuses(models.Pricing)
        assert pricing_statuses == {models.PricingStatus.INVOICED}
        assert indiv_booking1.status == bookings_models.BookingStatus.REIMBURSED  # updated
        assert indiv_booking1.reimbursementDate == invoice.date  # updated
        assert indiv_booking2.status == bookings_models.BookingStatus.CANCELLED  # not updated
        assert indiv_booking2.reimbursementDate == invoice.date  # updated
        assert collective_booking1.status == educational_models.CollectiveBookingStatus.REIMBURSED  # updated
        assert collective_booking1.reimbursementDate == invoice.date  # updated
        assert collective_booking2.status == educational_models.CollectiveBookingStatus.CANCELLED  # not updated
        assert collective_booking2.reimbursementDate == invoice.date  # updated


class PrepareInvoiceContextTest:
    def test_context(self, invoice_data):
        bank_account, stocks, _venue = invoice_data
        user = users_factories.RichBeneficiaryFactory()
        for stock in stocks:
            finance_event = factories.UsedBookingFinanceEventFactory(
                booking__stock=stock,
                booking__user=user,
            )
            api.price_event(finance_event)
        batch = api.generate_cashflows(cutoff=datetime.datetime.utcnow())
        api.generate_payment_files(batch)  # mark cashflows as UNDER_REVIEW
        cashflow_ids = [c.id for c in db.session.query(models.Cashflow).all()]
        invoice = api._generate_invoice_legacy(
            bank_account_id=bank_account.id,
            cashflow_ids=cashflow_ids,
        )
        batch = db.session.query(models.CashflowBatch).get(batch.id)

        context = api._prepare_invoice_context(invoice, batch)

        general, books, not_reimbursed, custom = tuple(g for g in context["groups"])
        assert general.used_bookings_subtotal == 2006130
        assert general.contribution_subtotal == 406
        assert general.reimbursed_amount_subtotal == -2005724

        assert books.used_bookings_subtotal == 6000
        assert books.contribution_subtotal == 200
        assert books.reimbursed_amount_subtotal == -5800

        assert not_reimbursed.used_bookings_subtotal == 5800
        assert not_reimbursed.contribution_subtotal == 5800
        assert not_reimbursed.reimbursed_amount_subtotal == 0

        assert custom.used_bookings_subtotal == 4300
        assert custom.contribution_subtotal == 220
        assert custom.reimbursed_amount_subtotal == -4080

        assert context["invoice"] == invoice
        assert context["total_used_bookings_amount"] == 2022230
        assert context["total_contribution_amount"] == 6626
        assert context["total_reimbursed_amount"] == -2015604

    def test_get_invoice_period_second_half(self):
        cutoff = utils.get_cutoff_as_datetime(datetime.date(2020, 3, 31))
        start_period, end_period = api.get_invoice_period(cutoff)
        assert start_period == datetime.date(2020, 3, 16)
        assert end_period == datetime.date(2020, 3, 31)

    def test_get_invoice_period_first_half(self):
        cutoff = utils.get_cutoff_as_datetime(datetime.date(2020, 3, 15))
        start_period, end_period = api.get_invoice_period(cutoff)
        assert start_period == datetime.date(2020, 3, 1)
        assert end_period == datetime.date(2020, 3, 15)

    def test_common_name_is_not_empty_public_name(self):
        offerer = offerers_factories.OffererFactory(name="Association de coiffeurs", siren="853318459")
        bank_account = factories.BankAccountFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(
            publicName="",
            name="common name should not be empty",
            siret="85331845900023",
            bookingEmail="pro@example.com",
            managingOfferer=offerer,
            pricing_point="self",
            bank_account=bank_account,
        )

        thing_offer = offers_factories.ThingOfferFactory(venue=venue)
        stock = offers_factories.StockFactory(offer=thing_offer, price=30)

        user = users_factories.RichBeneficiaryFactory()
        finance_event = factories.UsedBookingFinanceEventFactory(
            booking__stock=stock,
            booking__user=user,
        )
        api.price_event(finance_event)
        batch = api.generate_cashflows(cutoff=datetime.datetime.utcnow())
        api.generate_payment_files(batch)  # mark cashflows as UNDER_REVIEW
        cashflow_ids = [c.id for c in db.session.query(models.Cashflow).all()]
        invoice = api._generate_invoice_legacy(
            bank_account_id=bank_account.id,
            cashflow_ids=cashflow_ids,
        )
        batch = db.session.query(models.CashflowBatch).get(batch.id)

        context = api._prepare_invoice_context(invoice, batch)

        reimbursements = list(context["reimbursements_by_venue"])
        assert len(reimbursements) == 1
        assert reimbursements[0]["venue_name"] == "common name should not be empty"


class GenerateDebitNoteHtmlTest:
    TEST_FILES_PATH = pathlib.Path(tests.__path__[0]) / "files"

    def generate_and_compare_invoice(self, features, bank_account, venue, expected_generated_file_name):
        user = users_factories.RichBeneficiaryFactory()
        book_offer = offers_factories.OfferFactory(venue=venue, subcategoryId=subcategories.LIVRE_PAPIER.id)
        factories.CustomReimbursementRuleFactory(amount=2850, offer=book_offer)

        incident_booking1_event = factories.UsedBookingFinanceEventFactory(
            booking__stock=offers_factories.StockFactory(offer=book_offer, price=30, quantity=1),
            booking__user=user,
            booking__amount=30,
            booking__quantity=1,
        )
        api.price_event(incident_booking1_event)

        incident_booking2_event = factories.UsedBookingFinanceEventFactory(
            booking__stock=offers_factories.StockFactory(offer=book_offer, price=30, quantity=1),
            booking__user=user,
            booking__amount=30,
            booking__quantity=1,
        )
        api.price_event(incident_booking2_event)

        # Mark incident bookings as already invoiced
        incident_booking1_event.booking.pricings[0].status = models.PricingStatus.INVOICED
        incident_booking2_event.booking.pricings[0].status = models.PricingStatus.INVOICED

        db.session.flush()

        incident_events = []
        # create total overpayment incident (30 €)
        booking_total_incident = factories.IndividualBookingFinanceIncidentFactory(
            incident__status=models.IncidentStatus.VALIDATED,
            incident__forceDebitNote=True,
            incident__venue=venue,
            booking=incident_booking1_event.booking,
            newTotalAmount=-incident_booking1_event.booking.total_amount * 100,
        )
        incident_events += api._create_finance_events_from_incident(booking_total_incident, datetime.datetime.utcnow())

        # create partial overpayment incident
        booking_partial_incident = factories.IndividualBookingFinanceIncidentFactory(
            incident__status=models.IncidentStatus.VALIDATED,
            incident__forceDebitNote=False,
            incident__venue=venue,
            booking=incident_booking2_event.booking,
            newTotalAmount=2000,
        )
        incident_events += api._create_finance_events_from_incident(
            booking_partial_incident, datetime.datetime.utcnow()
        )

        for event in incident_events:
            api.price_event(event)

        batch = api.generate_cashflows(cutoff=datetime.datetime.utcnow())
        api.generate_payment_files(batch)  # mark cashflows as UNDER_REVIEW

        cashflows = db.session.query(models.Cashflow).order_by(models.Cashflow.id).all()
        cashflow_ids = [c.id for c in cashflows]
        invoice = api._generate_invoice_legacy(
            bank_account_id=bank_account.id,
            cashflow_ids=cashflow_ids,
            is_debit_note=True,
        )
        batch = db.session.query(models.CashflowBatch).get(batch.id)
        invoice_html = api._generate_debit_note_html(invoice, batch)

        with open(self.TEST_FILES_PATH / "invoice" / expected_generated_file_name, "r", encoding="utf-8") as f:
            expected_invoice_html = f.read()
        # We need to replace Cashflow IDs and dates that were used when generating the expected html

        expected_invoice_html = expected_invoice_html.replace(
            'content: "Relevé n°A240000001 du 28/01/2024";',
            f'content: "Relevé n°{invoice.reference} du {(cashflows[0].batch.cutoff + datetime.timedelta(days=2)).strftime("%d/%m/%Y")}";',
        )
        assert expected_invoice_html == invoice_html

    def test_basics(self, features, invoice_data):
        bank_account, stocks, venue = invoice_data

        del stocks  # we don't need it

        self.generate_and_compare_invoice(features, bank_account, venue, "rendered_debit_note.html")

    def test_nc_invoice(self, features, invoice_nc_data):
        bank_account, stocks, venue = invoice_nc_data

        del stocks  # we don't need it

        self.generate_and_compare_invoice(features, bank_account, venue, "rendered_nc_debit_note.html")


class GenerateInvoiceHtmlTest:
    TEST_FILES_PATH = pathlib.Path(tests.__path__[0]) / "files"

    def generate_and_compare_invoice(self, features, stocks, bank_account, venue, is_caledonian):
        user = users_factories.RichBeneficiaryFactory()
        book_offer = offers_factories.OfferFactory(venue=venue, subcategoryId=subcategories.LIVRE_PAPIER.id)
        factories.CustomReimbursementRuleFactory(amount=2850, offer=book_offer)

        for stock in stocks:
            finance_event = factories.UsedBookingFinanceEventFactory(
                booking__stock=stock,
                booking__user=user,
            )
            api.price_event(finance_event)

        duo_offer = offers_factories.OfferFactory(venue=venue, isDuo=True)
        duo_stock = offers_factories.StockFactory(offer=duo_offer, price=1)
        duo_booking = bookings_factories.UsedBookingFactory(stock=duo_stock, quantity=2)
        duo_finance_event = factories.UsedBookingFinanceEventFactory(booking=duo_booking)
        api.price_event(duo_finance_event)

        incident_booking1_event = factories.UsedBookingFinanceEventFactory(
            booking__stock=offers_factories.StockFactory(offer=book_offer, price=30, quantity=1),
            booking__user=user,
            booking__amount=30,
            booking__quantity=1,
        )
        api.price_event(incident_booking1_event)

        incident_booking2_event = factories.UsedBookingFinanceEventFactory(
            booking__stock=offers_factories.StockFactory(offer=book_offer, price=30, quantity=1),
            booking__user=user,
            booking__amount=30,
            booking__quantity=1,
        )
        api.price_event(incident_booking2_event)

        if not is_caledonian:
            incident_collective_booking_event = factories.UsedCollectiveBookingFinanceEventFactory(
                collectiveBooking__collectiveStock__price=30,
                collectiveBooking__collectiveStock__collectiveOffer__venue=venue,
                pricingOrderingDate=datetime.datetime.utcnow(),
            )
            api.price_event(incident_collective_booking_event)

        # Mark incident bookings as already invoiced
        incident_booking1_event.booking.pricings[0].status = models.PricingStatus.INVOICED
        incident_booking2_event.booking.pricings[0].status = models.PricingStatus.INVOICED

        if not is_caledonian:
            incident_collective_booking_event.pricings[0].status = models.PricingStatus.INVOICED

        incident_events = []
        # create total overpayment incident (30 €)
        booking_total_incident = factories.IndividualBookingFinanceIncidentFactory(
            incident__status=models.IncidentStatus.VALIDATED,
            booking=incident_booking1_event.booking,
            newTotalAmount=0,
        )
        incident_events += api._create_finance_events_from_incident(booking_total_incident, datetime.datetime.utcnow())

        # create partial overpayment incident
        booking_partial_incident = factories.IndividualBookingFinanceIncidentFactory(
            incident__status=models.IncidentStatus.VALIDATED,
            booking=incident_booking2_event.booking,
            newTotalAmount=2000,
        )
        incident_events += api._create_finance_events_from_incident(
            booking_partial_incident, datetime.datetime.utcnow()
        )

        if not is_caledonian:
            # create collective total overpayment incident (30 €)
            collective_booking_total_incident = factories.CollectiveBookingFinanceIncidentFactory(
                incident__status=models.IncidentStatus.VALIDATED,
                collectiveBooking=incident_collective_booking_event.collectiveBooking,
                newTotalAmount=0,
            )
            incident_events += api._create_finance_events_from_incident(
                collective_booking_total_incident, datetime.datetime.utcnow()
            )

        for event in incident_events:
            api.price_event(event)

        batch = api.generate_cashflows(cutoff=datetime.datetime.utcnow())
        api.generate_payment_files(batch)  # mark cashflows as UNDER_REVIEW
        cashflows = db.session.query(models.Cashflow).order_by(models.Cashflow.id).all()
        cashflow_ids = [c.id for c in cashflows]
        invoice = api._generate_invoice_legacy(
            bank_account_id=bank_account.id,
            cashflow_ids=cashflow_ids,
        )

        batch = db.session.query(models.CashflowBatch).get(batch.id)
        invoice_html = api._generate_invoice_html(invoice, batch)

        expected_generated_file_name = "rendered_nc_invoice.html" if is_caledonian else "rendered_invoice.html"

        with open(self.TEST_FILES_PATH / "invoice" / expected_generated_file_name, "r", encoding="utf-8") as f:
            expected_invoice_html = f.read()

        # We need to replace Cashflow IDs and dates that were used when generating the expected html
        expected_invoice_html = expected_invoice_html.replace(
            '<td class="cashflow_batch_label">1</td>',
            f'<td class="cashflow_batch_label">{cashflows[0].batch.label}</td>',
        )
        expected_invoice_html = expected_invoice_html.replace(
            '<td class="cashflow_creation_date">23/12/2021</td>',
            f'<td class="cashflow_creation_date">{(invoice.date + datetime.timedelta(days=2)).strftime("%d/%m/%Y")}</td>',
        )
        expected_invoice_html = expected_invoice_html.replace(
            'content: "Relevé n°F220000001 du 01/02/2022";',
            f'content: "Relevé n°{invoice.reference} du {(cashflows[0].batch.cutoff + datetime.timedelta(days=2)).strftime("%d/%m/%Y")}";',
        )
        start_period, end_period = api.get_invoice_period(cashflows[0].batch.cutoff)
        expected_invoice_html = expected_invoice_html.replace(
            "Remboursement des réservations validées entre le 01/01/22 et le 14/01/22, sauf cas exceptionnels.",
            f"Remboursement des réservations validées entre le {start_period.strftime('%d/%m/%y')} et le {end_period.strftime('%d/%m/%y')}, sauf cas exceptionnels.",
        )
        assert expected_invoice_html == invoice_html

    def test_basics(self, features, invoice_data):
        bank_account, stocks, venue = invoice_data
        pricing_point = db.session.query(offerers_models.Venue).get(venue.current_pricing_point_id)
        only_educational_venue = offerers_factories.VenueFactory(
            name="Coiffeur collecTIF",
            pricing_point=pricing_point,
            bank_account=bank_account,
        )
        only_collective_booking_finance_event = factories.UsedCollectiveBookingFinanceEventFactory(
            collectiveBooking__collectiveStock__price=666,
            collectiveBooking__collectiveStock__collectiveOffer__venue=only_educational_venue,
            collectiveBooking__collectiveStock__startDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=1),
            collectiveBooking__venue=only_educational_venue,
        )
        collective_booking_finance_event1 = factories.UsedCollectiveBookingFinanceEventFactory(
            collectiveBooking__collectiveStock__price=5000,
            collectiveBooking__collectiveStock__collectiveOffer__venue=venue,
            collectiveBooking__collectiveStock__startDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=1),
            collectiveBooking__venue=venue,
        )
        collective_booking_finance_event2 = factories.UsedCollectiveBookingFinanceEventFactory(
            collectiveBooking__collectiveStock__price=250,
            collectiveBooking__collectiveStock__collectiveOffer__venue=venue,
            collectiveBooking__collectiveStock__startDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=1),
            collectiveBooking__venue=venue,
        )
        api.price_event(only_collective_booking_finance_event)
        api.price_event(collective_booking_finance_event1)
        api.price_event(collective_booking_finance_event2)

        self.generate_and_compare_invoice(features, stocks, bank_account, venue, False)

    def test_nc_invoice(self, features, invoice_nc_data):
        bank_account, stocks, venue = invoice_nc_data

        self.generate_and_compare_invoice(features, stocks, bank_account, venue, True)
