from datetime import datetime

import pytest

from models import PcObject
from repository.booking_queries import compute_total_booking_value_of_offerer
from tests.conftest import clean_database
from utils.test_utils import create_offerer, create_venue, create_stock_with_thing_offer, create_booking, create_user, \
    create_deposit


@clean_database
@pytest.mark.standalone
def test_compute_total_booking_value_of_offerer(app):
    # given
    user = create_user()
    create_deposit(user, datetime.utcnow(), amount=1600)
    offerer1 = create_offerer(siren='123456789')
    offerer2 = create_offerer(siren='987654321')
    venue1 = create_venue(offerer1)
    venue2 = create_venue(offerer2)
    stock1 = create_stock_with_thing_offer(offerer1, venue1, thing_offer=None, price=200)
    stock2 = create_stock_with_thing_offer(offerer1, venue1, thing_offer=None, price=300)
    stock3 = create_stock_with_thing_offer(offerer2, venue2, thing_offer=None, price=400)
    booking1 = create_booking(user, stock1, recommendation=None, quantity=2)
    booking2 = create_booking(user, stock2, recommendation=None, quantity=1)
    booking3 = create_booking(user, stock3, recommendation=None, quantity=2)

    PcObject.check_and_save(booking1, booking2, booking3)

    # when
    total = compute_total_booking_value_of_offerer(offerer1.id)

    # then
    assert total == 700
