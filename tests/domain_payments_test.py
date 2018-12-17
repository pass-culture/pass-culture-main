from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock

import pytest
from freezegun import freeze_time

from domain.payments import create_payment_for_booking, filter_out_already_paid_for_bookings, create_payment_details
from domain.reimbursement import BookingReimbursement, ReimbursementRules
from models import Offer, Venue, Booking
from models.payment import Payment
from models.payment_status import TransactionStatus
from utils.test_utils import create_booking, create_stock, create_user, create_offerer, create_venue, create_payment, \
    create_thing_offer


@pytest.mark.standalone
def test_create_payment_for_booking_with_common_information():
    # given
    user = create_user()
    stock = create_stock(price=10, available=5)
    booking = create_booking(user, stock=stock, quantity=1)
    booking.stock.offer = Offer()
    booking.stock.offer.venue = Venue()
    booking.stock.offer.venue.managingOfferer = create_offerer(iban='CF13QSDFGH456789', bic='QSDFGH8Z555')
    booking_reimbursement = BookingReimbursement(booking, ReimbursementRules.PHYSICAL_OFFERS, Decimal(10))

    # when
    payment = create_payment_for_booking(booking_reimbursement)

    # then
    assert payment.booking == booking
    assert payment.amount == Decimal(10)
    assert payment.reimbursementRule == ReimbursementRules.PHYSICAL_OFFERS.value.description
    assert payment.reimbursementRate == ReimbursementRules.PHYSICAL_OFFERS.value.rate
    assert payment.comment == None
    assert payment.author == 'batch'


@pytest.mark.standalone
def test_create_payment_for_booking_when_iban_is_on_venue_should_take_payment_info_from_venue():
    # given
    user = create_user()
    stock = create_stock(price=10, available=5)
    booking = create_booking(user, stock=stock, quantity=1)
    booking.stock.offer = Offer()
    offerer = create_offerer(name='Test Offerer', iban='B135TGGEG532TG', bic='LAJR93')
    booking.stock.offer.venue = create_venue(
        offerer,
        siret='12345678912345',
        name='Test Venue',
        iban='KD98765RFGHZ788',
        bic='LOKIJU76'
    )
    booking.stock.offer.venue.managingOfferer = offerer
    booking_reimbursement = BookingReimbursement(booking, ReimbursementRules.PHYSICAL_OFFERS, Decimal(10))

    # when
    payment = create_payment_for_booking(booking_reimbursement)

    # then
    assert payment.iban == 'KD98765RFGHZ788'
    assert payment.bic == 'LOKIJU76'


@pytest.mark.standalone
def test_create_payment_for_booking_when_no_iban_on_venue_should_take_payment_info_from_offerer():
    # given
    user = create_user()
    stock = create_stock(price=10, available=5)
    booking = create_booking(user, stock=stock, quantity=1)
    booking.stock.offer = Offer()
    offerer = create_offerer(
        name='Test Offerer',
        siren='123456789',
        iban='CF13QSDFGH456789',
        bic='QSDFGH8Z555'
    )
    booking.stock.offer.venue = create_venue(offerer, name='Test Venue', iban=None, bic=None)
    booking.stock.offer.venue.managingOfferer = offerer
    booking_reimbursement = BookingReimbursement(booking, ReimbursementRules.PHYSICAL_OFFERS, Decimal(10))

    # when
    payment = create_payment_for_booking(booking_reimbursement)

    # then
    assert payment.iban == 'CF13QSDFGH456789'
    assert payment.bic == 'QSDFGH8Z555'


@pytest.mark.standalone
def test_create_payment_for_booking_takes_recipient_name_and_siren_from_offerer():
    # given
    user = create_user()
    stock = create_stock(price=10, available=5)
    booking = create_booking(user, stock=stock, quantity=1)
    booking.stock.offer = Offer()
    offerer = create_offerer(
        name='Test Offerer',
        siren='123456789',
        iban='CF13QSDFGH456789',
        bic='QSDFGH8Z555'
    )
    booking.stock.offer.venue = create_venue(offerer, name='Test Venue', iban=None, bic=None)
    booking.stock.offer.venue.managingOfferer = offerer
    booking_reimbursement = BookingReimbursement(booking, ReimbursementRules.PHYSICAL_OFFERS, Decimal(10))

    # when
    payment = create_payment_for_booking(booking_reimbursement)

    # then
    assert payment.recipientName == 'Test Offerer'
    assert payment.recipientSiren == '123456789'


@pytest.mark.standalone
def test_create_payment_for_booking_with_not_processable_status_when_iban_is_missing_on_offerer():
    # given
    user = create_user()
    stock = create_stock(price=10, available=5)
    booking = create_booking(user, stock=stock, quantity=1)
    booking.stock.offer = Offer()
    booking.stock.offer.venue = Venue()
    booking.stock.offer.venue.managingOfferer = create_offerer(name='Test Offerer', iban=None, bic=None)
    booking_reimbursement = BookingReimbursement(booking, ReimbursementRules.PHYSICAL_OFFERS, Decimal(10))

    # when
    payment = create_payment_for_booking(booking_reimbursement)

    # then
    assert len(payment.statuses) == 1
    assert payment.statuses[0].status == TransactionStatus.NOT_PROCESSABLE
    assert payment.statuses[0].detail == 'IBAN et BIC manquants sur l\'offreur'


@pytest.mark.standalone
@freeze_time('2018-10-15 09:21:34')
def test_create_payment_for_booking_with_pending_status():
    # given
    one_second = timedelta(seconds=1)
    now = datetime.utcnow()
    user = create_user()
    stock = create_stock(price=10, available=5)
    booking = create_booking(user, stock=stock, quantity=1)
    booking.stock.offer = Offer()
    booking.stock.offer.venue = Venue()
    booking.stock.offer.venue.managingOfferer = create_offerer(iban='CF13QSDFGH456789', bic='QSDFGH8Z555')
    booking_reimbursement = BookingReimbursement(booking, ReimbursementRules.PHYSICAL_OFFERS, Decimal(10))

    # when
    payment = create_payment_for_booking(booking_reimbursement)

    # then
    assert len(payment.statuses) == 1
    assert payment.statuses[0].status == TransactionStatus.PENDING
    assert payment.statuses[0].detail is None
    assert payment.statuses[0].date == datetime(2018, 10, 15, 9, 21, 34)


@pytest.mark.standalone
def test_filter_out_already_paid_for_bookings():
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


@pytest.mark.standalone
class CreatePaymentDetailsTest:
    def test_contains_info_on_bank_transaction(selfself):
        # given
        user = create_user()
        booking = create_booking(user)
        offerer = create_offerer(iban='123456789')
        payment = create_payment(booking, offerer, 35, transaction_message_id='1234', transaction_end_ot_end_id='5678')

        # when
        details = create_payment_details(payment, find_booking_date_used=Mock())

        # then
        assert details.payment_iban == '123456789'
        assert details.transaction_message_id == '1234'
        assert details.transaction_end_to_end_id == '5678'
        assert details.reimbursed_amount == 35
        assert details.reimbursement_rate == 0.5

    @pytest.mark.standalone
    def test_contains_info_on_user_who_booked(self):
        # given
        user = create_user(idx=3, email='jane.doe@test.com')
        booking = create_booking(user)
        offerer = create_offerer(iban='123456789')
        payment = create_payment(booking, offerer, 35)

        # when
        details = create_payment_details(payment, find_booking_date_used=Mock())

        # then
        assert details.booking_user_id == 3
        assert details.booking_user_email == 'jane.doe@test.com'

    @pytest.mark.standalone
    def test_contains_info_on_booking(self):
        # given
        user = create_user(idx=3, email='jane.doe@test.com')
        offerer = create_offerer(iban='123456789', siren='987654321', name='Joe le Libraire')
        venue = create_venue(offerer)
        offer = create_thing_offer(venue)
        stock = create_stock(price=12, available=5, offer=offer)
        booking = create_booking(user, stock, date_created=datetime(2018, 2, 5), quantity=2, idx=5)
        payment = create_payment(booking, offerer, 35)
        find_date = Mock()
        find_date.return_value = datetime(2018, 2, 19)

        # when
        details = create_payment_details(payment, find_booking_date_used=find_date)

        # then
        assert details.booking_date == datetime(2018, 2, 5)
        assert details.booking_amount == stock.price * booking.quantity
        assert details.booking_used_date == datetime(2018, 2, 19)

    @pytest.mark.standalone
    def test_contains_info_on_offerer(self):
        # given
        user = create_user(idx=3, email='jane.doe@test.com')
        offerer = create_offerer(iban='123456789', siren='987654321', name='Joe le Libraire')
        venue = create_venue(offerer)
        offer = create_thing_offer(venue)
        stock = create_stock(price=12, available=5, offer=offer)
        booking = create_booking(user, stock, date_created=datetime(2018, 2, 5), quantity=2, idx=5)
        payment = create_payment(booking, offerer, 35)
        find_date = Mock()
        find_date.return_value = datetime(2018, 2, 19)

        # when
        details = create_payment_details(payment, find_booking_date_used=find_date)

        # then
        assert details.offerer_name == 'Joe le Libraire'
        assert details.offerer_siren == '987654321'

    @pytest.mark.standalone
    def test_contains_info_on_venue(self):
        # given
        user = create_user(idx=3, email='jane.doe@test.com')
        offerer = create_offerer(iban='123456789', siren='987654321', name='Joe le Libraire')
        venue = create_venue(offerer, name='Jack le Sculpteur', siret='1234567891234')
        offer = create_thing_offer(venue)
        stock = create_stock(price=12, available=5, offer=offer)
        booking = create_booking(user, stock, date_created=datetime(2018, 2, 5), quantity=2, idx=5)
        payment = create_payment(booking, offerer, 35)
        find_date = Mock()
        find_date.return_value = datetime(2018, 2, 19)

        # when
        details = create_payment_details(payment, find_booking_date_used=find_date)

        # then
        assert details.venue_name == 'Jack le Sculpteur'
        assert details.venue_siret == '1234567891234'

    @pytest.mark.standalone
    def test_contains_info_on_offer(self):
        # given
        user = create_user(idx=3, email='jane.doe@test.com')
        offerer = create_offerer(iban='123456789', siren='987654321', name='Joe le Libraire')
        venue = create_venue(offerer, name='Jack le Sculpteur', siret='1234567891234')
        offer = create_thing_offer(venue)
        stock = create_stock(price=12, available=5, offer=offer)
        booking = create_booking(user, stock, date_created=datetime(2018, 2, 5), quantity=2, idx=5)
        payment = create_payment(booking, offerer, 35)
        find_date = Mock()
        find_date.return_value = datetime(2018, 2, 19)

        # when
        details = create_payment_details(payment, find_booking_date_used=find_date)

        # then
        assert details.offer_name == 'Test Book'
        assert details.offer_type == 'Audiovisuel (Films sur supports physiques et VOD)'
