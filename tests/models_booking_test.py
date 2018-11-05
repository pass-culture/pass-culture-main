from models import Booking, Offer, Stock, Thing, User

from unittest.mock import Mock

def test_booking_completed_url_gets_normalized():
    # Given

    thing = Thing()
    thing.url = 'javascript:alert("plop")'

    offer = Offer()
    offer.id = 1
    offer.thing = thing

    stock = Stock()

    user = User()
    user.email = 'bob@bob.com'

    booking = Booking()
    booking.token = 'ABCDEF'
    booking.stock = stock
    booking.stock.offer = offer
    booking.user = user

    # When
    completedUrl = booking.completedUrl

    # Then
    assert completedUrl == 'http://javascript:alert("plop")'
