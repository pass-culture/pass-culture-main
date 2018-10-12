from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from domain.payments import create_payment_for_booking, filter_out_already_paid_for_bookings
from domain.reimbursement import BookingReimbursement, ReimbursementRules
from models import Offer, Venue, Booking
from models.payment import Payment
from models.payment_status import TransactionStatus
from utils.test_utils import create_booking, create_stock, create_user, create_offerer


@pytest.mark.standalone
def test_create_payment_for_booking_with_common_information():
    # given
    user = create_user()
    stock = create_stock(price=10, available=5)
    booking = create_booking(user, stock=stock, quantity=1)
    booking.stock.offer = Offer()
    booking.stock.offer.venue = Venue()
    booking.stock.offer.venue.managingOfferer = create_offerer(iban='B135TGGEG532TG', bic='LAJR93')
    booking_reimbursement = BookingReimbursement(booking, ReimbursementRules.PHYSICAL_OFFERS, Decimal(10))

    # when
    payment = create_payment_for_booking(booking_reimbursement)

    # then
    assert payment.booking == booking
    assert payment.amount == Decimal(10)
    assert payment.reimbursementRule == ReimbursementRules.PHYSICAL_OFFERS.value.description
    assert payment.comment == None
    assert payment.author == 'batch'


@pytest.mark.standalone
def test_create_payment_for_booking_when_iban_is_on_offerer():
    # given
    user = create_user()
    stock = create_stock(price=10, available=5)
    booking = create_booking(user, stock=stock, quantity=1)
    booking.stock.offer = Offer()
    booking.stock.offer.venue = Venue()
    booking.stock.offer.venue.managingOfferer = create_offerer(name='Test Offerer', iban='B135TGGEG532TG', bic='LAJR93')
    booking_reimbursement = BookingReimbursement(booking, ReimbursementRules.PHYSICAL_OFFERS, Decimal(10))

    # when
    payment = create_payment_for_booking(booking_reimbursement)

    # then
    assert payment.iban == 'B135TGGEG532TG'
    assert payment.bic == 'LAJR93'
    assert payment.recipient == 'Test Offerer'


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
def test_create_payment_for_booking_with_pending_status():
    # given
    one_second = timedelta(seconds=1)
    now = datetime.utcnow()
    user = create_user()
    stock = create_stock(price=10, available=5)
    booking = create_booking(user, stock=stock, quantity=1)
    booking.stock.offer = Offer()
    booking.stock.offer.venue = Venue()
    booking.stock.offer.venue.managingOfferer = create_offerer(iban='B135TGGEG532TG', bic='LAJR93')
    booking_reimbursement = BookingReimbursement(booking, ReimbursementRules.PHYSICAL_OFFERS, Decimal(10))

    # when
    payment = create_payment_for_booking(booking_reimbursement)

    # then
    assert len(payment.statuses) == 1
    assert payment.statuses[0].status == TransactionStatus.PENDING
    assert payment.statuses[0].detail is None
    assert now - one_second < payment.statuses[0].date < now + one_second


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
