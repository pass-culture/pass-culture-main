from datetime import datetime
from decimal import Decimal
import uuid

from freezegun import freeze_time
import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.offerers.models import Offerer
import pcapi.core.offers.factories as offers_factories
from pcapi.domain.payments import UnmatchedPayments
from pcapi.domain.payments import apply_banishment
from pcapi.domain.payments import create_payment_details
from pcapi.domain.payments import create_payment_for_booking
from pcapi.domain.payments import filter_out_already_paid_for_bookings
from pcapi.domain.payments import filter_out_bookings_without_cost
from pcapi.domain.payments import keep_only_not_processable_payments
from pcapi.domain.payments import make_transaction_label
from pcapi.domain.reimbursement import BookingReimbursement
from pcapi.domain.reimbursement import ReimbursementRules
from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_payment
from pcapi.model_creators.generic_creators import create_stock
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.models import Booking
from pcapi.models.payment import Payment
from pcapi.models.payment_status import TransactionStatus
from pcapi.utils.human_ids import humanize


@freeze_time("2021-01-01 12:00:00")
@pytest.mark.usefixtures("db_session")
class CreatePaymentForBookingTest:
    def test_basics(self):
        offerer = offers_factories.OffererFactory(name="offerer", siren="123456")
        booking = bookings_factories.BookingFactory(stock__offer__venue__managingOfferer=offerer)
        reimbursement = BookingReimbursement(booking, ReimbursementRules.PHYSICAL_OFFERS, Decimal(10))
        batch_date = datetime.utcnow()

        payment = create_payment_for_booking(reimbursement, batch_date)

        assert payment.bookingId == booking.id
        assert payment.amount == 10
        assert payment.reimbursementRule == ReimbursementRules.PHYSICAL_OFFERS.value.description
        assert payment.reimbursementRate == ReimbursementRules.PHYSICAL_OFFERS.value.rate
        assert payment.comment is None
        assert payment.author == "batch"
        assert payment.transactionLabel == "pass Culture Pro - remboursement 1ère quinzaine 01-2021"
        assert payment.batchDate == batch_date
        assert payment.iban is None
        assert payment.bic is None
        assert payment.recipientName == "offerer"
        assert payment.recipientSiren == "123456"

    def test_use_iban_and_bic_from_venue(self):
        booking = bookings_factories.BookingFactory()
        venue = booking.stock.offer.venue
        offers_factories.BankInformationFactory(venue=venue, iban="iban1", bic="bic1")
        offers_factories.BankInformationFactory(offerer=venue.managingOfferer, iban="iban2", bic="bic2")
        reimbursement = BookingReimbursement(booking, ReimbursementRules.PHYSICAL_OFFERS, Decimal(10))
        batch_date = datetime.utcnow()

        payment = create_payment_for_booking(reimbursement, batch_date)

        assert payment.iban == "IBAN1"
        assert payment.bic == "BIC1"

    def test_use_iban_and_bic_from_offerer(self):
        booking = bookings_factories.BookingFactory()
        offerer = booking.stock.offer.venue.managingOfferer
        offers_factories.BankInformationFactory(offerer=offerer, iban="iban", bic="bic")
        reimbursement = BookingReimbursement(booking, ReimbursementRules.PHYSICAL_OFFERS, Decimal(10))
        batch_date = datetime.utcnow()

        payment = create_payment_for_booking(reimbursement, batch_date)

        assert payment.iban == "IBAN"
        assert payment.bic == "BIC"


class FilterOutAlreadyPaidForBookingsTest:
    def test_it_returns_reimbursements_on_bookings_with_no_existing_payments(self):
        # Given
        booking_paid = Booking()
        booking_paid.payments = [Payment()]
        booking_reimbursement1 = BookingReimbursement(booking_paid, ReimbursementRules.PHYSICAL_OFFERS, Decimal(10))
        booking_not_paid = Booking()
        booking_reimbursement2 = BookingReimbursement(booking_not_paid, ReimbursementRules.PHYSICAL_OFFERS, Decimal(10))
        booking_reimbursements = [booking_reimbursement1, booking_reimbursement2]

        # When
        bookings_not_paid = filter_out_already_paid_for_bookings(booking_reimbursements)

        # Then
        assert len(bookings_not_paid) == 1
        assert not bookings_not_paid[0].booking.payments

    def test_it_returns_an_empty_list_if_everything_has_been_reimbursed(self):
        # Given
        booking_paid1 = Booking()
        booking_paid1.payments = [Payment()]
        booking_reimbursement1 = BookingReimbursement(booking_paid1, ReimbursementRules.PHYSICAL_OFFERS, Decimal(10))

        booking_paid2 = Booking()
        booking_paid2.payments = [Payment()]
        booking_reimbursement2 = BookingReimbursement(booking_paid2, ReimbursementRules.PHYSICAL_OFFERS, Decimal(10))

        # When
        bookings_not_paid = filter_out_already_paid_for_bookings([booking_reimbursement1, booking_reimbursement2])

        # Then
        assert bookings_not_paid == []

    def test_it_returns_an_empty_list_if_an_empty_list_is_given(self):
        # When
        bookings_not_paid = filter_out_already_paid_for_bookings([])

        # Then
        assert bookings_not_paid == []


class FilterOutBookingsWithoutCostTest:
    def test_it_returns_reimbursements_on_bookings_with_reimbursed_value_greater_than_zero(self):
        # given
        reimbursement1 = BookingReimbursement(Booking(), ReimbursementRules.PHYSICAL_OFFERS, Decimal(10))
        reimbursement2 = BookingReimbursement(Booking(), ReimbursementRules.PHYSICAL_OFFERS, Decimal(0))

        # when
        bookings_reimbursements_with_cost = filter_out_bookings_without_cost([reimbursement1, reimbursement2])

        # then
        assert len(bookings_reimbursements_with_cost) == 1
        assert bookings_reimbursements_with_cost[0].reimbursed_amount > Decimal(0)

    def test_it_returns_an_empty_list_if_everything_has_a_cost(self):
        # given
        reimbursement1 = BookingReimbursement(Booking(), ReimbursementRules.PHYSICAL_OFFERS, Decimal(0))
        reimbursement2 = BookingReimbursement(Booking(), ReimbursementRules.PHYSICAL_OFFERS, Decimal(0))

        # when
        bookings_reimbursements_with_cost = filter_out_bookings_without_cost([reimbursement1, reimbursement2])

        # then
        assert bookings_reimbursements_with_cost == []

    def test_it_returns_an_empty_list_if_an_empty_list_is_given(self):
        # when
        bookings_reimbursements_with_cost = filter_out_bookings_without_cost([])

        # then
        assert bookings_reimbursements_with_cost == []


class KeepOnlyNotProcessablePaymentsTest:
    def test_it_returns_only_payments_with_current_status_as_not_processable(self):
        # given
        user = create_user()
        booking = create_booking(user=user)
        offerer = create_offerer()
        payments = [
            create_payment(booking, offerer, 30, status=TransactionStatus.PENDING),
            create_payment(booking, offerer, 30, status=TransactionStatus.NOT_PROCESSABLE),
            create_payment(booking, offerer, 30, status=TransactionStatus.ERROR),
        ]

        # when
        pending_payments = keep_only_not_processable_payments(payments)

        # then
        assert len(pending_payments) == 1
        assert pending_payments[0].currentStatus.status == TransactionStatus.NOT_PROCESSABLE

    def test_it_returns_an_empty_list_if_everything_has_no_not_processable_payment(self):
        # given
        user = create_user()
        booking = create_booking(user=user)
        offerer = create_offerer()
        payments = [
            create_payment(booking, offerer, 30, status=TransactionStatus.SENT),
            create_payment(booking, offerer, 30, status=TransactionStatus.SENT),
            create_payment(booking, offerer, 30, status=TransactionStatus.ERROR),
        ]

        # when
        pending_payments = keep_only_not_processable_payments(payments)

        # then
        assert pending_payments == []

    def test_it_returns_an_empty_list_if_an_empty_list_is_given(self):
        # when
        pending_payments = keep_only_not_processable_payments([])

        # then
        assert pending_payments == []


class CreatePaymentDetailsTest:
    def test_contains_info_on_bank_transaction(self):
        # given
        user = create_user()
        booking = create_booking(user=user)
        offerer = create_offerer()
        payment = create_payment(
            booking, offerer, 35, payment_message_name="1234", transaction_end_to_end_id=uuid.uuid4(), iban="123456789"
        )

        # when
        details = create_payment_details(payment)

        # then
        assert details.payment_iban == "123456789"
        assert details.payment_message_name == "1234"
        assert details.transaction_end_to_end_id == payment.transactionEndToEndId
        assert details.reimbursed_amount == 35
        assert details.reimbursement_rate == 0.5

    def test_contains_info_on_user_who_booked(self):
        # given
        user = create_user(email="jane.doe@test.com", idx=3)
        booking = create_booking(user=user)
        offerer = create_offerer()
        payment = create_payment(booking, offerer, 35)

        # when
        details = create_payment_details(payment)

        # then
        assert details.booking_user_id == 3
        assert details.booking_user_email == "jane.doe@test.com"

    def test_contains_info_on_booking(self):
        # given
        user = create_user(email="jane.doe@test.com", idx=3)
        offerer = create_offerer(siren="987654321", name="Joe le Libraire")
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=12, quantity=5)
        booking = create_booking(
            user=user,
            stock=stock,
            date_created=datetime(2018, 2, 5),
            date_used=datetime(2018, 2, 19),
            idx=5,
            quantity=2,
        )
        payment = create_payment(booking=booking, offerer=offerer, amount=35)

        # when
        details = create_payment_details(payment)

        # then
        assert details.booking_date == datetime(2018, 2, 5)
        assert details.booking_amount == stock.price * booking.quantity
        assert details.booking_used_date == datetime(2018, 2, 19)

    def test_contains_info_on_offerer(self):
        # given
        user = create_user(email="jane.doe@test.com", idx=3)
        offerer = create_offerer(siren="987654321", name="Joe le Libraire")
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=12, quantity=5)
        booking = create_booking(user=user, stock=stock, date_created=datetime(2018, 2, 5), idx=5, quantity=2)
        payment = create_payment(booking, offerer, 35)

        # when
        details = create_payment_details(payment)

        # then
        assert details.offerer_name == "Joe le Libraire"
        assert details.offerer_siren == "987654321"

    def test_contains_info_on_venue(self):
        # given
        user = create_user(email="jane.doe@test.com", idx=3)
        offerer = create_offerer(siren="987654321", name="Joe le Libraire")
        venue = create_venue(offerer, name="Jack le Sculpteur", siret="1234567891234", idx=1)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=12, quantity=5)
        booking = create_booking(user=user, stock=stock, date_created=datetime(2018, 2, 5), idx=5, quantity=2)
        payment = create_payment(booking, offerer, 35)

        # when
        details = create_payment_details(payment)

        # then
        assert details.venue_name == "Jack le Sculpteur"
        assert details.venue_siret == "1234567891234"
        assert details.venue_humanized_id == humanize(venue.id)

    def test_contains_info_on_offer(self):
        # given
        user = create_user(email="jane.doe@test.com", idx=3)
        offerer = create_offerer(siren="987654321", name="Joe le Libraire")
        venue = create_venue(offerer, name="Jack le Sculpteur", siret="1234567891234")
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=12, quantity=5)
        booking = create_booking(user=user, stock=stock, date_created=datetime(2018, 2, 5), idx=5, quantity=2)
        payment = create_payment(booking, offerer, 35)

        # when
        details = create_payment_details(payment)

        # then
        assert details.offer_name == "Test Book"
        assert details.offer_type == "Audiovisuel - films sur supports physiques et VOD"


class PaymentTransactionLabelTest:
    @pytest.mark.parametrize("date", [datetime(2018, 7, d) for d in range(1, 15)])
    def test_in_first_half_of_a_month(self, date):
        # when
        message = make_transaction_label(date)

        # then
        assert message == "pass Culture Pro - remboursement 1ère quinzaine 07-2018"

    @pytest.mark.parametrize("date", [datetime(2018, 7, d) for d in range(15, 31)])
    def test_in_second_half_of_a_month(self, date):
        # when
        message = make_transaction_label(date)

        # then
        assert message == "pass Culture Pro - remboursement 2nde quinzaine 07-2018"


class ApplyBanishmentTest:
    def test_payments_matching_given_ids_must_be_banned(self):
        # given
        payments = [
            create_payment(Booking(), Offerer(), 10, idx=111),
            create_payment(Booking(), Offerer(), 10, idx=222),
            create_payment(Booking(), Offerer(), 10, idx=333),
            create_payment(Booking(), Offerer(), 10, idx=444),
        ]
        ids_to_ban = [222, 333]

        # when
        banned_payments, _retry_payments = apply_banishment(payments, ids_to_ban)

        # then
        assert len(banned_payments) == 2
        for p in banned_payments:
            assert p.currentStatus.status == TransactionStatus.BANNED
            assert p.id in ids_to_ban

    def test_payments_not_matching_given_ids_must_be_retried(self):
        # given
        payments = [
            create_payment(Booking(), Offerer(), 10, idx=111),
            create_payment(Booking(), Offerer(), 10, idx=222),
            create_payment(Booking(), Offerer(), 10, idx=333),
            create_payment(Booking(), Offerer(), 10, idx=444),
        ]
        ids_to_ban = [222, 333]

        # when
        _banned_payments, retry_payments = apply_banishment(payments, ids_to_ban)

        # then
        assert len(retry_payments) == 2
        for p in retry_payments:
            assert p.currentStatus.status == TransactionStatus.RETRY
            assert p.id not in ids_to_ban

    def test_no_payments_to_retry_if_all_are_banned(self):
        # given
        payments = [
            create_payment(Booking(), Offerer(), 10, idx=111),
            create_payment(Booking(), Offerer(), 10, idx=222),
        ]
        ids_to_ban = [111, 222]

        # when
        banned_payments, retry_payments = apply_banishment(payments, ids_to_ban)

        # then
        assert len(banned_payments) == 2
        assert retry_payments == []

    def test_no_payments_are_returned_if_no_ids_are_provided(self):
        # given
        payments = [
            create_payment(Booking(), Offerer(), 10, idx=111),
            create_payment(Booking(), Offerer(), 10, idx=222),
        ]
        ids_to_ban = []

        # when
        banned_payments, retry_payments = apply_banishment(payments, ids_to_ban)

        # then
        assert banned_payments == []
        assert retry_payments == []

    def test_value_error_is_raised_if_payments_ids_do_not_match_payments(self):
        # given
        payments = [
            create_payment(Booking(), Offerer(), 10, idx=111),
            create_payment(Booking(), Offerer(), 10, idx=222),
        ]
        ids_to_ban = [222, 333]

        # when
        with pytest.raises(UnmatchedPayments) as e:
            apply_banishment(payments, ids_to_ban)

        # then
        assert e.value.payment_ids == {333}
