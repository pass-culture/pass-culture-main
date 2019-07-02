from datetime import datetime

from models import PcObject
from tests.conftest import clean_database, TestClient
from tests.test_utils import create_stock_with_thing_offer, \
    create_deposit, create_venue, create_offerer, \
    create_user, create_booking, create_user_offerer, create_offer_with_thing_product, create_stock_from_offer, \
    create_offer_with_event_product
from utils.human_ids import humanize


class Get:
    class Returns200:
        @clean_database
        def when_user_has_an_offerer_attached(self, app):
            # Given
            user = create_user(email='user+plus@email.fr')
            deposit = create_deposit(user, datetime.utcnow(), amount=500, source='public')
            offerer1 = create_offerer()
            offerer2 = create_offerer(siren='123456788')
            user_offerer1 = create_user_offerer(user, offerer1, validation_token=None)
            user_offerer2 = create_user_offerer(user, offerer2, validation_token=None)
            venue1 = create_venue(offerer1)
            venue2 = create_venue(offerer1, siret='12345678912346')
            venue3 = create_venue(offerer2, siret='12345678912347')
            stock1 = create_stock_with_thing_offer(offerer=offerer1, venue=venue1, price=10)
            stock2 = create_stock_with_thing_offer(offerer=offerer1, venue=venue2, price=11)
            stock3 = create_stock_with_thing_offer(offerer=offerer2, venue=venue3, price=12)
            stock4 = create_stock_with_thing_offer(offerer=offerer2, venue=venue3, price=13)
            booking1 = create_booking(user, stock1, venue=venue1, token='ABCDEF')
            booking2 = create_booking(user, stock1, venue=venue1, token='ABCDEG')
            booking3 = create_booking(user, stock2, venue=venue2, token='ABCDEH')
            booking4 = create_booking(user, stock3, venue=venue3, token='ABCDEI')
            booking5 = create_booking(user, stock4, venue=venue3, token='ABCDEJ')
            booking6 = create_booking(user, stock4, venue=venue3, token='ABCDEK')

            PcObject.save(deposit, booking1, booking2, booking3,
                          booking4, booking5, booking6, user_offerer1,
                          user_offerer2)

            # When
            response = TestClient(app.test_client()).with_auth(user.email).get(
                '/bookings/csv')
            content_lignes = response.data.decode('utf-8').split('\n')[1:-1]

            # Then
            assert response.status_code == 200
            assert response.headers['Content-type'] == 'text/csv; charset=utf-8;'
            assert response.headers['Content-Disposition'] == 'attachment; filename=reservations_pass_culture.csv'
            assert len(content_lignes) == 6

        @clean_database
        def when_user_has_no_offerer_attached(self, app):
            # Given
            user = create_user(email='user+plus@email.fr')
            PcObject.save(user)

            # When
            response = TestClient(app.test_client()).with_auth(user.email).get(
                '/bookings/csv')
            content_lines = response.data.decode('utf-8').split('\n')[1:-1]

            # Then
            assert response.status_code == 200
            assert len(content_lines) == 0

        @clean_database
        def when_user_has_an_offerer_attached_and_venue_id_argument_is_valid(self, app):
            # Given
            user = create_user(email='user+plus@email.fr')
            deposit = create_deposit(user, datetime.utcnow(), amount=500, source='public')
            offerer1 = create_offerer()
            offerer2 = create_offerer(siren='123456788')
            user_offerer1 = create_user_offerer(user, offerer1, validation_token=None)
            user_offerer2 = create_user_offerer(user, offerer2, validation_token=None)
            venue1 = create_venue(offerer1)
            venue2 = create_venue(offerer1, siret='12345678912346')
            venue3 = create_venue(offerer2, siret='12345678912347')
            offer1 = create_offer_with_event_product(venue1)
            offer2 = create_offer_with_thing_product(venue1)
            offer3 = create_offer_with_thing_product(venue2)
            stock1 = create_stock_from_offer(offer1, available=100, price=20)
            stock2 = create_stock_from_offer(offer2, available=150, price=16)
            stock3 = create_stock_from_offer(offer3, available=150, price=18)
            booking1 = create_booking(user, stock1, venue=venue1, token='ABCDEF')
            booking2 = create_booking(user, stock1, venue=venue1, token='ABCDEG')
            booking3 = create_booking(user, stock2, venue=venue2, token='ABCDEH')
            booking4 = create_booking(user, stock3, venue=venue3, token='ABCDEI')

            PcObject.save(deposit, booking1, booking2, booking3,
                          booking4, user_offerer1, user_offerer2)

            # When
            url = '/bookings/csv?venueId=%s' % (humanize(venue1.id))
            response = TestClient(app.test_client()).with_auth(user.email).get(url)
            content_lines = response.data.decode('utf-8').split('\n')[1:-1]

            # Then
            assert response.status_code == 200
            assert response.headers['Content-type'] == 'text/csv; charset=utf-8;'
            assert response.headers['Content-Disposition'] == 'attachment; filename=reservations_pass_culture.csv'
            assert len(content_lines) == 3

        @clean_database
        def when_user_is_filtering_on_digital_venues(self, app):
            # Given
            user = create_user(email='user+plus@email.fr')
            deposit = create_deposit(user, datetime.utcnow(), amount=500, source='public')

            offerer1 = create_offerer()
            user_offerer1 = create_user_offerer(user, offerer1, validation_token=None)

            virtual_venue = create_venue(offerer1, is_virtual=True, siret=None)
            physical_venue = create_venue(offerer1, siret='12345678912346')
            offer1 = create_offer_with_event_product(virtual_venue)
            offer2 = create_offer_with_thing_product(physical_venue)

            stock1 = create_stock_from_offer(offer1, available=100, price=20)
            stock2 = create_stock_from_offer(offer2, available=150, price=16)
            booking_on_physical_venue = create_booking(user, stock1, venue=virtual_venue, token='ABCDEF')
            booking_on_digital_venue = create_booking(user, stock2, venue=physical_venue, token='ABCDEH')

            PcObject.save(deposit, booking_on_physical_venue, booking_on_digital_venue, user_offerer1)

            # When
            url = '/bookings/csv?onlyDigitalVenues=true'
            response = TestClient(app.test_client()).with_auth(user.email).get(url)
            content_lines = response.data.decode('utf-8').split('\n')[1:-1]

            # Then
            assert response.status_code == 200
            assert response.headers['Content-type'] == 'text/csv; charset=utf-8;'
            assert response.headers['Content-Disposition'] == 'attachment; filename=reservations_pass_culture.csv'
            assert len(content_lines) == 1
