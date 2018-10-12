from datetime import datetime

import pytest

from models import PcObject
from models.payment import Payment
from scripts.payments import do_generate_payments
from tests.conftest import clean_database
from utils.test_utils import create_offerer, create_venue, create_thing_offer, create_stock_from_offer, \
    create_booking, create_user, create_deposit, create_payment


@pytest.mark.standalone
@clean_database
def test_do_generate_payments(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_thing_offer(venue)
    stock = create_stock_from_offer(offer)
    user = create_user()
    deposit = create_deposit(user, datetime.utcnow(), amount=500)
    booking1 = create_booking(user, stock, venue, is_used=True)
    booking2 = create_booking(user, stock, venue, is_used=True)
    booking3 = create_booking(user, stock, venue, is_used=True)
    payment1 = create_payment(booking2, offerer, 10)

    PcObject.check_and_save(deposit, booking1, booking3, payment1)

    initial_payment_count = Payment.query.count()

    # When
    do_generate_payments()

    # Then
    assert Payment.query.count() - initial_payment_count == 2