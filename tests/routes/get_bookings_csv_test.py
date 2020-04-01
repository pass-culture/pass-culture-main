from datetime import datetime
from unittest.mock import patch

from models import ApiErrors
from repository import repository
from tests.conftest import clean_database, TestClient
from tests.model_creators.generic_creators import create_booking, create_user, create_offerer, create_venue, \
    create_deposit, \
    create_user_offerer
from tests.model_creators.specific_creators import create_stock_from_offer, create_stock_with_thing_offer, \
    create_offer_with_thing_product, create_offer_with_event_product
from utils.human_ids import humanize


class Get:
    class Returns200:
        @clean_database
        def when_user_has_an_offerer_attached(self, app):
            # Given
            user = create_user(email='user+plus@email.fr')
            deposit = create_deposit(user, amount=500, source='public')
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
            booking1 = create_booking(user=user, stock=stock1, token='ABCDEF', venue=venue1)
            booking2 = create_booking(user=user, stock=stock1, token='ABCDEG', venue=venue1)
            booking3 = create_booking(user=user, stock=stock2, token='ABCDEH', venue=venue2)
            booking4 = create_booking(user=user, stock=stock3, token='ABCDEI', venue=venue3)
            booking5 = create_booking(user=user, stock=stock4, token='ABCDEJ', venue=venue3)
            booking6 = create_booking(user=user, stock=stock4, token='ABCDEK', venue=venue3)

            repository.save(deposit, booking1, booking2, booking3,
                            booking4, booking5, booking6, user_offerer1,
                            user_offerer2)

            # When
            response = TestClient(app.test_client()).with_auth(user.email).get(
                '/bookings/csv')

            # Then
            content_lines = response.data.decode('utf-8').split('\n')[1:-1]
            assert response.status_code == 200
            assert response.headers['Content-type'] == 'text/csv; charset=utf-8;'
            assert response.headers['Content-Disposition'] == 'attachment; filename=reservations_pass_culture.csv'
            assert len(content_lines) == 6

        @clean_database
        def when_user_has_no_offerer_attached(self, app):
            # Given
            user = create_user(email='user+plus@email.fr')
            repository.save(user)

            # When
            response = TestClient(app.test_client()).with_auth(user.email).get(
                '/bookings/csv')

            # Then
            content_lines = response.data.decode('utf-8').split('\n')[1:-1]
            assert response.status_code == 200
            assert len(content_lines) == 0

        @clean_database
        def when_user_has_an_offerer_attached_and_venue_id_argument_is_valid(self, app):
            # Given
            user = create_user(email='user+plus@email.fr')
            deposit = create_deposit(user, amount=500, source='public')
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
            stock1 = create_stock_from_offer(offer1, price=20, quantity=100)
            stock2 = create_stock_from_offer(offer2, price=16, quantity=150)
            stock3 = create_stock_from_offer(offer3, price=18, quantity=150)
            booking1 = create_booking(user=user, stock=stock1, token='ABCDEF', venue=venue1)
            booking2 = create_booking(user=user, stock=stock1, token='ABCDEG', venue=venue1)
            booking3 = create_booking(user=user, stock=stock2, token='ABCDEH', venue=venue2)
            booking4 = create_booking(user=user, stock=stock3, token='ABCDEI', venue=venue3)

            repository.save(deposit, booking1, booking2, booking3,
                            booking4, user_offerer1, user_offerer2)

            url = '/bookings/csv?venueId=%s' % (humanize(venue1.id))

            # When
            response = TestClient(app.test_client()).with_auth(user.email).get(url)

            # Then
            content_lines = response.data.decode('utf-8').split('\n')[1:-1]
            assert response.status_code == 200
            assert response.headers['Content-type'] == 'text/csv; charset=utf-8;'
            assert response.headers['Content-Disposition'] == 'attachment; filename=reservations_pass_culture.csv'
            assert len(content_lines) == 3

        @clean_database
        def when_user_is_filtering_on_digital_venues(self, app):
            # Given
            user = create_user(email='user+plus@email.fr')
            deposit = create_deposit(user, amount=500, source='public')

            offerer1 = create_offerer()
            user_offerer1 = create_user_offerer(user, offerer1, validation_token=None)

            virtual_venue = create_venue(offerer1, name='virtual venue', is_virtual=True, siret=None)
            physical_venue = create_venue(offerer1, siret='12345678912346')
            offer1 = create_offer_with_event_product(virtual_venue)
            offer2 = create_offer_with_thing_product(physical_venue)

            stock1 = create_stock_from_offer(offer1, price=20, quantity=100)
            stock2 = create_stock_from_offer(offer2, price=16, quantity=150)
            booking_on_physical_venue = create_booking(user=user, stock=stock1, token='ABCDEF', venue=physical_venue)
            booking_on_digital_venue = create_booking(user=user, stock=stock2, token='ABCDEH', venue=virtual_venue)

            repository.save(deposit, booking_on_physical_venue, booking_on_digital_venue, user_offerer1)

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .get('/bookings/csv?onlyDigitalVenues=true')

            # Then
            content_lines = response.data.decode('utf-8').split('\n')[1:-1]
            assert response.status_code == 200
            assert response.headers['Content-type'] == 'text/csv; charset=utf-8;'
            assert response.headers['Content-Disposition'] == 'attachment; filename=reservations_pass_culture.csv'
            assert len(content_lines) == 1
            assert 'virtual venue' in content_lines[0]

        @clean_database
        def when_user_is_filtering_on_offer_and_date(self, app):
            # Given
            user = create_user(email='user+plus@email.fr')
            deposit = create_deposit(user, amount=500, source='public')

            offerer1 = create_offerer()
            user_offerer1 = create_user_offerer(user, offerer1, validation_token=None)

            venue = create_venue(offerer1, is_virtual=True, siret=None, name='virtual venue')
            target_offer = create_offer_with_thing_product(venue, thing_name='thing')
            other_offer = create_offer_with_thing_product(venue)

            stock1 = create_stock_from_offer(target_offer, price=20, quantity=100)
            stock2 = create_stock_from_offer(other_offer, price=16, quantity=150)
            booking_on_other_offer = create_booking(user=user, stock=stock2, token='ABCDEF', venue=venue)
            booking_on_target_offer_and_date = create_booking(user=user, stock=stock1,
                                                              date_created=datetime.strptime("2020-05-01T00:00:00.000Z",
                                                                                             "%Y-%m-%dT%H:%M:%S.%fZ"),
                                                              token='ABCDEH', venue=venue)
            booking_on_other_date = create_booking(user=user, stock=stock1,
                                                   date_created=datetime.strptime("2020-04-30T00:00:00.000Z",
                                                                                  "%Y-%m-%dT%H:%M:%S.%fZ"),
                                                   token='ABCDEG', venue=venue)

            repository.save(deposit, booking_on_other_offer, booking_on_target_offer_and_date, booking_on_other_date,
                            user_offerer1)

            target_offer_id = humanize(target_offer.id)
            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .get(f'/bookings/csv?onlyDigitalVenues=true&offerId={target_offer_id}' \
                     '&dateFrom=2020-05-01T00:00:00.000Z&dateTo=2020-05-01T00:00:00.000Z')

            # Then
            content_lines = response.data.decode('utf-8').split('\n')[1:-1]
            assert response.status_code == 200
            assert response.headers['Content-type'] == 'text/csv; charset=utf-8;'
            assert response.headers['Content-Disposition'] == 'attachment; filename=reservations_pass_culture.csv'
            assert len(content_lines) == 1
            assert 'virtual venue' in content_lines[0]
            assert 'thing' in content_lines[0]

    class Returns400:
        @clean_database
        @patch('routes.bookings.check_rights_to_get_bookings_csv')
        def when_user_is_admin(self, check_rights_to_get_bookings_csv, app):
            # Given
            user_admin = create_user(can_book_free_offers=False, email='user+plus@email.fr', is_admin=True)
            repository.save(user_admin)

            api_errors = ApiErrors()
            api_errors.status_code = 400
            api_errors.add_error(
                'global',
                "Le statut d'administrateur ne permet pas d'accéder au suivi des réseravtions"
            )

            check_rights_to_get_bookings_csv.side_effect = api_errors

            # When
            response = TestClient(app.test_client()).with_auth(user_admin.email).get('/bookings/csv')

            # Then
            assert response.status_code == 400
