import uuid
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock

import pytest
from freezegun import freeze_time

from domain.payments import create_payment_for_booking, filter_out_already_paid_for_bookings, create_payment_details, \
    create_all_payments_details, make_transaction_label, group_payments_by_status, \
    filter_out_bookings_without_cost, keep_only_pending_payments, keep_only_not_processable_payments, apply_banishment, \
    UnmatchedPayments
from domain.reimbursement import BookingReimbursement, ReimbursementRules
from models import OfferSQLEntity, VenueSQLEntity, BookingSQLEntity, Offerer
from models.payment import Payment
from models.payment_status import TransactionStatus
from model_creators.generic_creators import create_booking, create_user, create_stock, create_offerer, \
    create_venue, \
    create_payment, create_bank_information
from model_creators.specific_creators import create_offer_with_thing_product
from utils.human_ids import humanize


@freeze_time('2018-10-15 09:21:34')
def test_create_payment_for_booking_with_common_information(app):
    # given
    user = create_user()
    stock = create_stock(price=10, quantity=5)
    booking = create_booking(user=user, quantity=1, stock=stock)
    booking.stock.offer = OfferSQLEntity()
    booking.stock.offer.venue = VenueSQLEntity()
    offerer = create_offerer()
    offerer_bank_information = create_bank_information(bic='QSDFGH8Z555', iban='CF13QSDFGH456789', offerer=offerer)
    booking.stock.offer.venue.managingOfferer = offerer
    booking_reimbursement = BookingReimbursement(booking, ReimbursementRules.PHYSICAL_OFFERS, Decimal(10))

    # when
    payment = create_payment_for_booking(booking_reimbursement)

    # then
    assert payment.booking == booking
    assert payment.amount == Decimal(10)
    assert payment.reimbursementRule == ReimbursementRules.PHYSICAL_OFFERS.value.description
    assert payment.reimbursementRate == ReimbursementRules.PHYSICAL_OFFERS.value.rate
    assert payment.comment is None
    assert payment.author == 'batch'
    assert payment.transactionLabel == 'pass Culture Pro - remboursement 2nde quinzaine 10-2018'


def test_create_payment_for_booking_when_iban_is_on_venue_should_take_payment_info_from_venue(app):
    # given
    user = create_user()
    stock = create_stock(price=10, quantity=5)
    offerer = create_offerer(name='Test Offerer')
    venue = create_venue(offerer, name='Test Venue', )
    booking = create_booking(user=user, quantity=1, stock=stock)

    offerer_bank_information = create_bank_information(bic='Lajr93', iban='B135TGGEG532TG', offerer=offerer)
    venue_bank_information = create_bank_information(bic='LokiJU76', iban='KD98765RFGHZ788', venue=venue)

    booking.stock.offer = OfferSQLEntity()
    booking.stock.offer.venue = venue
    booking.stock.offer.venue.managingOfferer = offerer
    booking_reimbursement = BookingReimbursement(booking, ReimbursementRules.PHYSICAL_OFFERS, Decimal(10))

    # when
    payment = create_payment_for_booking(booking_reimbursement)

    # then
    assert payment.iban == 'KD98765RFGHZ788'
    assert payment.bic == 'LOKIJU76'


def test_create_payment_for_booking_when_no_iban_on_venue_should_take_payment_info_from_offerer(app):
    # given
    user = create_user()
    stock = create_stock(price=10, quantity=5)
    offerer = create_offerer(name='Test Offerer')
    venue = create_venue(offerer, name='Test Venue')

    offerer_bank_information = create_bank_information(bic='QsdFGH8Z555', iban='cf13QSDFGH456789', offerer=offerer)
    venue_bank_information = create_bank_information(bic=None, iban=None, venue=venue)

    booking = create_booking(user=user, quantity=1, stock=stock)
    booking.stock.offer = OfferSQLEntity()
    booking.stock.offer.venue = venue
    booking.stock.offer.venue.managingOfferer = offerer
    booking_reimbursement = BookingReimbursement(booking, ReimbursementRules.PHYSICAL_OFFERS, Decimal(10))

    # when
    payment = create_payment_for_booking(booking_reimbursement)

    # then
    assert payment.iban == 'CF13QSDFGH456789'
    assert payment.bic == 'QSDFGH8Z555'


def test_create_payment_for_booking_takes_recipient_name_and_siren_from_offerer(app):
    # given
    user = create_user()
    stock = create_stock(price=10, quantity=5)
    booking = create_booking(user=user, quantity=1, stock=stock)
    booking.stock.offer = OfferSQLEntity()
    offerer = create_offerer(name='Test Offerer', siren='123456789')
    venue = create_venue(offerer, name='Test Venue')

    offerer_bank_information = create_bank_information(bic='QSDFGH8Z555', iban='CF13QSDFGH456789', offerer=offerer)
    venue_bank_information = create_bank_information(bic=None, iban=None, venue=venue)

    booking.stock.offer.venue = venue
    booking.stock.offer.venue.managingOfferer = offerer
    booking_reimbursement = BookingReimbursement(booking, ReimbursementRules.PHYSICAL_OFFERS, Decimal(10))

    # when
    payment = create_payment_for_booking(booking_reimbursement)

    # then
    assert payment.recipientName == 'Test Offerer'
    assert payment.recipientSiren == '123456789'


def test_create_payment_for_booking_with_not_processable_status_when_no_bank_information_linked_to_venue_or_offerer():
    # given
    user = create_user()
    stock = create_stock(price=10, quantity=5)
    booking = create_booking(user=user, quantity=1, stock=stock)
    booking.stock.offer = OfferSQLEntity()
    booking.stock.offer.venue = VenueSQLEntity()
    booking.stock.offer.venue.managingOfferer = create_offerer(name='Test Offerer')
    booking_reimbursement = BookingReimbursement(booking, ReimbursementRules.PHYSICAL_OFFERS, Decimal(10))

    # when
    payment = create_payment_for_booking(booking_reimbursement)

    # then
    assert len(payment.statuses) == 1
    assert payment.statuses[0].status == TransactionStatus.NOT_PROCESSABLE
    assert payment.statuses[0].detail == 'IBAN et BIC manquants sur l\'offreur'


@freeze_time('2018-10-15 09:21:34')
def test_create_payment_for_booking_with_pending_status(app):
    # given
    user = create_user()
    stock = create_stock(price=10, quantity=5)
    booking = create_booking(user=user, quantity=1, stock=stock)
    booking.stock.offer = OfferSQLEntity()
    booking.stock.offer.venue = VenueSQLEntity()
    offerer = create_offerer()
    booking.stock.offer.venue.managingOfferer = offerer
    offerer_bank_information = create_bank_information(bic='QSDFGH8Z555', iban='CF13QSDFGH456789', offerer=offerer)
    booking_reimbursement = BookingReimbursement(booking, ReimbursementRules.PHYSICAL_OFFERS, Decimal(10))

    # when
    payment = create_payment_for_booking(booking_reimbursement)

    # then
    assert len(payment.statuses) == 1
    assert payment.statuses[0].status == TransactionStatus.PENDING
    assert payment.statuses[0].detail is None
    assert payment.statuses[0].date == datetime(2018, 10, 15, 9, 21, 34)


class FilterOutAlreadyPaidForBookingsTest:
    def test_it_returns_reimbursements_on_bookings_with_no_existing_payments(self):
        # Given
        booking_paid = BookingSQLEntity()
        booking_paid.payments = [Payment()]
        booking_reimbursement1 = BookingReimbursement(booking_paid, ReimbursementRules.PHYSICAL_OFFERS, Decimal(10))
        booking_not_paid = BookingSQLEntity()
        booking_reimbursement2 = BookingReimbursement(booking_not_paid, ReimbursementRules.PHYSICAL_OFFERS, Decimal(10))
        booking_reimbursements = [booking_reimbursement1, booking_reimbursement2]

        # When
        bookings_not_paid = filter_out_already_paid_for_bookings(booking_reimbursements)

        # Then
        assert len(bookings_not_paid) == 1
        assert not bookings_not_paid[0].booking.payments

    def test_it_returns_an_empty_list_if_everything_has_been_reimbursed(self):
        # Given
        booking_paid1 = BookingSQLEntity()
        booking_paid1.payments = [Payment()]
        booking_reimbursement1 = BookingReimbursement(booking_paid1, ReimbursementRules.PHYSICAL_OFFERS, Decimal(10))

        booking_paid2 = BookingSQLEntity()
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


class FilterOutBookingsWithoutCost:
    def test_it_returns_reimbursements_on_bookings_with_reimbursed_value_greater_than_zero(self):
        # given
        reimbursement1 = BookingReimbursement(BookingSQLEntity(), ReimbursementRules.PHYSICAL_OFFERS, Decimal(10))
        reimbursement2 = BookingReimbursement(BookingSQLEntity(), ReimbursementRules.PHYSICAL_OFFERS, Decimal(0))

        # when
        bookings_reimbursements_with_cost = filter_out_bookings_without_cost([reimbursement1, reimbursement2])

        # then
        assert len(bookings_reimbursements_with_cost) == 1
        assert bookings_reimbursements_with_cost[0].reimbursed_amount > Decimal(0)

    def test_it_returns_an_empty_list_if_everything_has_a_cost(self):
        # given
        reimbursement1 = BookingReimbursement(BookingSQLEntity(), ReimbursementRules.PHYSICAL_OFFERS, Decimal(0))
        reimbursement2 = BookingReimbursement(BookingSQLEntity(), ReimbursementRules.PHYSICAL_OFFERS, Decimal(0))

        # when
        bookings_reimbursements_with_cost = filter_out_bookings_without_cost([reimbursement1, reimbursement2])

        # then
        assert bookings_reimbursements_with_cost == []

    def test_it_returns_an_empty_list_if_an_empty_list_is_given(self):
        # when
        bookings_reimbursements_with_cost = filter_out_bookings_without_cost([])

        # then
        assert bookings_reimbursements_with_cost == []


class KeepOnlyPendingPaymentsTest:
    def test_it_returns_only_payments_with_current_status_as_pending(self):
        # given
        user = create_user()
        booking = create_booking(user=user)
        offerer = create_offerer()
        payments = [
            create_payment(booking, offerer, 30, status=TransactionStatus.PENDING),
            create_payment(booking, offerer, 30, status=TransactionStatus.NOT_PROCESSABLE),
            create_payment(booking, offerer, 30, status=TransactionStatus.ERROR)
        ]

        # when
        pending_payments = keep_only_pending_payments(payments)

        # then
        assert len(pending_payments) == 1
        assert pending_payments[0].currentStatus.status == TransactionStatus.PENDING

    def test_it_returns_an_empty_list_if_everything_has_no_pending_payment(self):
        # given
        user = create_user()
        booking = create_booking(user=user)
        offerer = create_offerer()
        payments = [
            create_payment(booking, offerer, 30, status=TransactionStatus.SENT),
            create_payment(booking, offerer, 30, status=TransactionStatus.SENT),
            create_payment(booking, offerer, 30, status=TransactionStatus.ERROR)
        ]

        # when
        pending_payments = keep_only_pending_payments(payments)

        # then
        assert pending_payments == []

    def test_it_returns_an_empty_list_if_an_empty_list_is_given(self):
        # when
        pending_payments = keep_only_pending_payments([])

        # then
        assert pending_payments == []


class KeepOnlyNotProcessablePaymentsTest:
    def test_it_returns_only_payments_with_current_status_as_not_processable(self):
        # given
        user = create_user()
        booking = create_booking(user=user)
        offerer = create_offerer()
        payments = [
            create_payment(booking, offerer, 30, status=TransactionStatus.PENDING),
            create_payment(booking, offerer, 30, status=TransactionStatus.NOT_PROCESSABLE),
            create_payment(booking, offerer, 30, status=TransactionStatus.ERROR)
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
            create_payment(booking, offerer, 30, status=TransactionStatus.ERROR)
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
        payment = create_payment(booking, offerer, 35, payment_message_name='1234',
                                 transaction_end_to_end_id=uuid.uuid4(), iban='123456789')

        # when
        details = create_payment_details(payment, find_booking_date_used=Mock())

        # then
        assert details.payment_iban == '123456789'
        assert details.payment_message_name == '1234'
        assert details.transaction_end_to_end_id == payment.transactionEndToEndId
        assert details.reimbursed_amount == 35
        assert details.reimbursement_rate == 0.5

    def test_contains_info_on_user_who_booked(self):
        # given
        user = create_user(email='jane.doe@test.com', idx=3)
        booking = create_booking(user=user)
        offerer = create_offerer()
        payment = create_payment(booking, offerer, 35)

        # when
        details = create_payment_details(payment, find_booking_date_used=Mock())

        # then
        assert details.booking_user_id == 3
        assert details.booking_user_email == 'jane.doe@test.com'

    def test_contains_info_on_booking(self):
        # given
        user = create_user(email='jane.doe@test.com', idx=3)
        offerer = create_offerer(siren='987654321', name='Joe le Libraire')
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=12, quantity=5)
        booking = create_booking(user=user, stock=stock, date_created=datetime(2018, 2, 5), idx=5, quantity=2)
        payment = create_payment(booking=booking, offerer=offerer, amount=35)
        find_date = Mock()
        find_date.return_value = datetime(2018, 2, 19)

        # when
        details = create_payment_details(payment, find_booking_date_used=find_date)

        # then
        assert details.booking_date == datetime(2018, 2, 5)
        assert details.booking_amount == stock.price * booking.quantity
        assert details.booking_used_date == datetime(2018, 2, 19)

    def test_contains_info_on_offerer(self):
        # given
        user = create_user(email='jane.doe@test.com', idx=3)
        offerer = create_offerer(siren='987654321', name='Joe le Libraire')
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=12, quantity=5)
        booking = create_booking(user=user, stock=stock, date_created=datetime(2018, 2, 5), idx=5, quantity=2)
        payment = create_payment(booking, offerer, 35)
        find_date = Mock()
        find_date.return_value = datetime(2018, 2, 19)

        # when
        details = create_payment_details(payment, find_booking_date_used=find_date)

        # then
        assert details.offerer_name == 'Joe le Libraire'
        assert details.offerer_siren == '987654321'

    def test_contains_info_on_venue(self):
        # given
        user = create_user(email='jane.doe@test.com', idx=3)
        offerer = create_offerer(siren='987654321', name='Joe le Libraire')
        venue = create_venue(offerer, name='Jack le Sculpteur', siret='1234567891234', idx=1)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=12, quantity=5)
        booking = create_booking(user=user, stock=stock, date_created=datetime(2018, 2, 5), idx=5, quantity=2)
        payment = create_payment(booking, offerer, 35)
        find_date = Mock()
        find_date.return_value = datetime(2018, 2, 19)

        # when
        details = create_payment_details(payment, find_booking_date_used=find_date)

        # then
        assert details.venue_name == 'Jack le Sculpteur'
        assert details.venue_siret == '1234567891234'
        assert details.venue_humanized_id == humanize(venue.id)

    def test_contains_info_on_offer(self):
        # given
        user = create_user(email='jane.doe@test.com', idx=3)
        offerer = create_offerer(siren='987654321', name='Joe le Libraire')
        venue = create_venue(offerer, name='Jack le Sculpteur', siret='1234567891234')
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=12, quantity=5)
        booking = create_booking(user=user, stock=stock, date_created=datetime(2018, 2, 5), idx=5, quantity=2)
        payment = create_payment(booking, offerer, 35)
        find_date = Mock()
        find_date.return_value = datetime(2018, 2, 19)

        # when
        details = create_payment_details(payment, find_booking_date_used=find_date)

        # then
        assert details.offer_name == 'Test Book'
        assert details.offer_type == 'Audiovisuel - films sur supports physiques et VOD'


class CreateAllPaymentsDetailsTest:
    def test_returns_an_empty_list_if_no_payments_given(self):
        # when
        details = create_all_payments_details([], find_booking_date_used=Mock())

        # then
        assert details == []

    def test_returns_as_much_payment_details_as_there_are_payments_given(self):
        # given
        offerer1, offerer2 = create_offerer(), create_offerer()
        user1, user2 = create_user(), create_user()
        payments = [
            create_payment(create_booking(user=user1), offerer1, 10),
            create_payment(create_booking(user=user1), offerer1, 20),
            create_payment(create_booking(user=user2), offerer2, 30)
        ]

        # when
        details = create_all_payments_details(payments, find_booking_date_used=Mock())

        # then
        assert len(details) == 3


class PaymentTransactionLabelTest:
    @pytest.mark.parametrize('date', [datetime(2018, 7, d) for d in range(1, 15)])
    def test_in_first_half_of_a_month(self, date):
        # when
        message = make_transaction_label(date)

        # then
        assert message == 'pass Culture Pro - remboursement 1ère quinzaine 07-2018'

    @pytest.mark.parametrize('date', [datetime(2018, 7, d) for d in range(15, 31)])
    def test_in_second_half_of_a_month(self, date):
        # when
        message = make_transaction_label(date)

        # then
        assert message == 'pass Culture Pro - remboursement 2nde quinzaine 07-2018'


class GroupPaymentsByStatusTest:
    def test_payments_are_grouped_by_current_statuses_names(self):
        # given
        user = create_user()
        booking = create_booking(user=user)
        offerer = create_offerer()
        payment1 = create_payment(booking, offerer, 10)
        payment2 = create_payment(booking, offerer, 20)
        payment3 = create_payment(booking, offerer, 30)
        payment4 = create_payment(booking, offerer, 40)
        payment1.setStatus(TransactionStatus.SENT)
        payment2.setStatus(TransactionStatus.NOT_PROCESSABLE)
        payment3.setStatus(TransactionStatus.ERROR)
        payment4.setStatus(TransactionStatus.ERROR)
        payments = [payment1, payment2, payment3, payment4]

        # when
        groups = group_payments_by_status(payments)

        # then
        assert len(groups['SENT']) == 1
        assert len(groups['NOT_PROCESSABLE']) == 1
        assert len(groups['ERROR']) == 2


class ApplyBanishmentTest:
    def test_payments_matching_given_ids_must_be_banned(self):
        # given
        payments = [
            create_payment(BookingSQLEntity(), Offerer(), 10, idx=111),
            create_payment(BookingSQLEntity(), Offerer(), 10, idx=222),
            create_payment(BookingSQLEntity(), Offerer(), 10, idx=333),
            create_payment(BookingSQLEntity(), Offerer(), 10, idx=444)
        ]
        ids_to_ban = [222, 333]

        # when
        banned_payments, retry_payments = apply_banishment(payments, ids_to_ban)

        # then
        assert len(banned_payments) == 2
        for p in banned_payments:
            assert p.currentStatus.status == TransactionStatus.BANNED
            assert p.id in ids_to_ban

    def test_payments_not_matching_given_ids_must_be_retried(self):
        # given
        payments = [
            create_payment(BookingSQLEntity(), Offerer(), 10, idx=111),
            create_payment(BookingSQLEntity(), Offerer(), 10, idx=222),
            create_payment(BookingSQLEntity(), Offerer(), 10, idx=333),
            create_payment(BookingSQLEntity(), Offerer(), 10, idx=444)
        ]
        ids_to_ban = [222, 333]

        # when
        banned_payments, retry_payments = apply_banishment(payments, ids_to_ban)

        # then
        assert len(retry_payments) == 2
        for p in retry_payments:
            assert p.currentStatus.status == TransactionStatus.RETRY
            assert p.id not in ids_to_ban

    def test_no_payments_to_retry_if_all_are_banned(self):
        # given
        payments = [
            create_payment(BookingSQLEntity(), Offerer(), 10, idx=111),
            create_payment(BookingSQLEntity(), Offerer(), 10, idx=222)
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
            create_payment(BookingSQLEntity(), Offerer(), 10, idx=111),
            create_payment(BookingSQLEntity(), Offerer(), 10, idx=222)
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
            create_payment(BookingSQLEntity(), Offerer(), 10, idx=111),
            create_payment(BookingSQLEntity(), Offerer(), 10, idx=222)
        ]
        ids_to_ban = [222, 333]

        # when
        with pytest.raises(UnmatchedPayments) as e:
            apply_banishment(payments, ids_to_ban)

        # then
        assert e.value.payment_ids == {333}
