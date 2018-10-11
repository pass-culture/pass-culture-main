from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from domain.payments import create_payment_for_booking
from domain.reimbursement import BookingReimbursement, ReimbursementRules
from models import Offer, Venue
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
    booking.stock.offer.venue.offerer = create_offerer(iban='B135TGGEG532TG')
    booking_reimbursement = BookingReimbursement(booking, ReimbursementRules.PHYSICAL_OFFERS.value, Decimal(10))

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
    booking.stock.offer.venue.offerer = create_offerer(name='Test Offerer', iban='B135TGGEG532TG')
    booking_reimbursement = BookingReimbursement(booking, ReimbursementRules.PHYSICAL_OFFERS.value, Decimal(10))

    # when
    payment = create_payment_for_booking(booking_reimbursement)

    # then
    assert payment.iban == 'B135TGGEG532TG'
    assert payment.recipient == 'Test Offerer'


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
    booking.stock.offer.venue.offerer = create_offerer(iban='B135TGGEG532TG')
    booking_reimbursement = BookingReimbursement(booking, ReimbursementRules.PHYSICAL_OFFERS.value, Decimal(10))

    # when
    payment = create_payment_for_booking(booking_reimbursement)

    # then
    assert len(payment.statuses) == 1
    assert payment.statuses[0].status == TransactionStatus.PENDING
    assert payment.statuses[0].detail is None
    assert now - one_second < payment.statuses[0].date < now + one_second
