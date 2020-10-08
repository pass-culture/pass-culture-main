from repository import repository
import pytest
from tests.conftest import TestClient
from model_creators.generic_creators import create_booking, create_user, create_offerer, create_venue, \
    create_stock
from model_creators.specific_creators import create_offer_with_thing_product
from utils.human_ids import humanize


class Get:
    class Returns200:
        @pytest.mark.usefixtures("db_session")
        def expect_booking_to_have_completed_url(self, app):
            # Given
            user = create_user(email='user@example.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue,
                                                    url='https://host/path/{token}?offerId={offerId}&email={email}')
            stock = create_stock(offer=offer, price=0)
            booking = create_booking(user=user, stock=stock, token='ABCDEF', venue=venue)
            repository.save(booking)

            # When
            response = TestClient(app.test_client()).with_auth(user.email).get(
                '/bookings/' + humanize(booking.id))

            # Then
            assert response.status_code == 200
            response_json = response.json
            assert response_json[
                       'completedUrl'] == 'https://host/path/ABCDEF?offerId=%s&email=user@example.com' % humanize(
                offer.id)
            assert 'stock' in response_json
            assert 'offer' in response_json['stock']
            assert 'venue' in response_json['stock']['offer']
            assert 'validationToken' not in response_json['stock']['offer']
