from datetime import datetime, timedelta
from urllib.parse import urlencode

from models import PcObject, EventType
from routes.serialization import serialize
from tests.conftest import clean_database, TestClient
from tests.test_utils import create_stock_with_thing_offer, \
    create_venue, create_offerer, \
    create_user, create_booking, create_offer_with_event_product, \
    create_event_occurrence, create_stock_from_event_occurrence, create_user_offerer, create_stock_with_event_offer
from utils.human_ids import humanize


class Get:
    class Returns200:
        @clean_database
        def when_user_has_rights_and_regular_offer(self, app):
            # Given
            user = create_user(public_name='John Doe', email='user@email.fr')
            admin_user = create_user(email='admin@email.fr')
            offerer = create_offerer()
            user_offerer = create_user_offerer(admin_user, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='Event Name', event_type=EventType.CINEMA)
            event_occurrence = create_event_occurrence(offer)
            stock = create_stock_from_event_occurrence(event_occurrence, price=0)
            booking = create_booking(user, stock, venue=venue)

            PcObject.save(user_offerer, booking)

            expected_json = {'bookingId': humanize(booking.id),
                             'date': serialize(booking.stock.beginningDatetime),
                             'email': 'user@email.fr',
                             'isUsed': False,
                             'offerName': 'Event Name',
                             'userName': 'John Doe',
                             'venueDepartementCode': '93'}

            # When
            response = TestClient(app.test_client()).with_auth('admin@email.fr').get(
                '/bookings/token/{}'.format(booking.token))
            # Then
            assert response.status_code == 200
            response_json = response.json
            assert response_json == expected_json

        @clean_database
        def when_user_has_rights_and_regular_offer_and_token_in_lower_case(self, app):
            # Given
            user = create_user(public_name='John Doe', email='user@email.fr')
            admin_user = create_user(email='admin@email.fr')
            offerer = create_offerer()
            user_offerer = create_user_offerer(admin_user, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='Event Name', event_type=EventType.CINEMA)
            event_occurrence = create_event_occurrence(offer)
            stock = create_stock_from_event_occurrence(event_occurrence, price=0)
            booking = create_booking(user, stock, venue=venue)

            PcObject.save(user_offerer, booking)

            expected_json = {'bookingId': humanize(booking.id),
                             'date': serialize(booking.stock.beginningDatetime),
                             'email': 'user@email.fr',
                             'isUsed': False,
                             'offerName': 'Event Name',
                             'userName': 'John Doe',
                             'venueDepartementCode': '93'}

            # When
            booking_token = booking.token.lower()
            response = TestClient(app.test_client()).with_auth('admin@email.fr').get(
                '/bookings/token/{}'.format(booking_token))

            # Then
            assert response.status_code == 200
            response_json = response.json
            assert response_json == expected_json

        @clean_database
        def when_activation_event_and_user_has_rights(self, app):
            # Given
            user = create_user(email='user@email.fr', phone_number='0698765432', date_of_birth=datetime(2001, 2, 1))
            admin_user = create_user(email='admin@email.fr', is_admin=True, can_book_free_offers=False)
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='Offre d\'activation',
                                                    event_type=EventType.ACTIVATION)
            event_occurrence = create_event_occurrence(offer)
            stock = create_stock_from_event_occurrence(event_occurrence, price=0)
            booking = create_booking(user, stock, venue=venue)

            PcObject.save(admin_user, booking)

            expected_json = {'bookingId': humanize(booking.id),
                             'date': serialize(booking.stock.beginningDatetime),
                             'dateOfBirth': '2001-02-01T00:00:00Z',
                             'email': 'user@email.fr',
                             'isUsed': False,
                             'offerName': 'Offre d\'activation',
                             'phoneNumber': '0698765432',
                             'userName': 'John Doe',
                             'venueDepartementCode': '93'}

            # When
            response = TestClient(app.test_client()) \
                .with_auth('admin@email.fr') \
                .get('/bookings/token/{}'.format(booking.token))

            # Then
            assert response.status_code == 200
            response_json = response.json
            assert response_json == expected_json

        @clean_database
        def when_user_has_rights_and_email_with_special_characters_url_encoded(self, app):
            # Given
            user = create_user(email='user+plus@email.fr')
            user_admin = create_user(email='admin@email.fr')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user_admin, offerer, is_admin=True)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='Event Name')
            event_occurrence = create_event_occurrence(offer)
            stock = create_stock_from_event_occurrence(event_occurrence, price=0)
            booking = create_booking(user, stock, venue=venue)

            PcObject.save(user_offerer, booking)
            url_email = urlencode({'email': 'user+plus@email.fr'})
            url = '/bookings/token/{}?{}'.format(booking.token, url_email)

            # When
            response = TestClient(app.test_client()).with_auth('admin@email.fr').get(url)
            # Then
            assert response.status_code == 200

    class Returns204:
        @clean_database
        def when_user_not_logged_in_and_gives_right_email(self, app):
            # Given
            user = create_user(email='user@email.fr')
            admin_user = create_user(email='admin@email.fr')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='Event Name')
            event_occurrence = create_event_occurrence(offer)
            stock = create_stock_from_event_occurrence(event_occurrence, price=0)
            booking = create_booking(user, stock, venue=venue)

            PcObject.save(admin_user, booking)

            # When
            url = '/bookings/token/{}?email={}'.format(booking.token, 'user@email.fr')
            response = TestClient(app.test_client()).get(url)

            # Then
            assert response.status_code == 204

        @clean_database
        def when_user_not_logged_in_and_give_right_email_and_event_offer_id(self, app):
            # Given
            user = create_user(email='user@email.fr')
            admin_user = create_user(email='admin@email.fr')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='Event Name')
            event_occurrence = create_event_occurrence(offer)
            stock = create_stock_from_event_occurrence(event_occurrence, price=0)
            booking = create_booking(user, stock, venue=venue)

            PcObject.save(admin_user, booking)
            url = '/bookings/token/{}?email={}&offer_id={}'.format(booking.token, 'user@email.fr',
                                                                   humanize(offer.id))

            # When
            response = TestClient(app.test_client()).get(url)

            # Then
            assert response.status_code == 204

        @clean_database
        def when_not_logged_in_and_give_right_email_and_offer_id_thing(self, app):
            # Given
            user = create_user(email='user@email.fr')
            admin_user = create_user(email='admin@email.fr')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue, offer=None, price=0)
            booking = create_booking(user, stock, venue=venue)

            PcObject.save(admin_user, booking)
            url = '/bookings/token/{}?email={}&offer_id={}'.format(booking.token, 'user@email.fr',
                                                                   humanize(stock.offerId))

            # When
            response = TestClient(app.test_client()).get(url)
            # Then
            assert response.status_code == 204

    class Returns404:

        @clean_database
        def when_token_user_has_rights_but_token_not_found(self, app):
            # Given
            admin_user = create_user(email='admin@email.fr')
            PcObject.save(admin_user)

            # When
            response = TestClient(app.test_client()).with_auth('admin@email.fr').get(
                '/bookings/token/{}'.format('12345'))
            # Then
            assert response.status_code == 404
            assert response.json['global'] == ["Cette contremarque n'a pas été trouvée"]

        @clean_database
        def when_user_not_logged_in_and_wrong_email(self, app):
            # Given
            user = create_user(email='user@email.fr')
            admin_user = create_user(email='admin@email.fr')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='Event Name')
            event_occurrence = create_event_occurrence(offer)
            stock = create_stock_from_event_occurrence(event_occurrence, price=0)
            booking = create_booking(user, stock, venue=venue)

            PcObject.save(admin_user, booking)

            # When
            url = '/bookings/token/{}?email={}'.format(booking.token, 'toto@email.fr')
            response = TestClient(app.test_client()).with_auth('admin@email.fr').get(url)
            # Then
            assert response.status_code == 404
            assert response.json['global'] == ["Cette contremarque n'a pas été trouvée"]

        @clean_database
        def when_user_not_logged_in_right_email_and_wrong_offer(self, app):
            # Given
            user = create_user(email='user@email.fr')
            admin_user = create_user(email='admin@email.fr')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue, offer=None, price=0)
            booking = create_booking(user, stock, venue=venue)

            PcObject.save(admin_user, booking)
            url = '/bookings/token/{}?email={}&offer_id={}'.format(booking.token, 'user@email.fr',
                                                                   humanize(123))

            # When
            response = TestClient(app.test_client()).get(url)

            # Then
            assert response.status_code == 404
            assert response.json['global'] == ["Cette contremarque n'a pas été trouvée"]

        @clean_database
        def when_user_has_rights_and_email_with_special_characters_not_url_encoded(self, app):
            # Given
            user = create_user(email='user+plus@email.fr')
            user_admin = create_user(email='admin@email.fr')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user_admin, offerer, is_admin=True)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='Event Name')
            event_occurrence = create_event_occurrence(offer)
            stock = create_stock_from_event_occurrence(event_occurrence, price=0)
            booking = create_booking(user, stock, venue=venue)

            PcObject.save(user_offerer, booking)
            url = '/bookings/token/{}?email={}'.format(booking.token, user.email)

            # When
            response = TestClient(app.test_client()).with_auth('admin@email.fr').get(url)
            # Then
            assert response.status_code == 404

    class Returns400:

        @clean_database
        def when_user_not_logged_in_and_doesnt_give_email(self, app):
            # Given
            user = create_user(email='user@email.fr')
            admin_user = create_user(email='admin@email.fr')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='Event Name')
            event_occurrence = create_event_occurrence(offer)
            stock = create_stock_from_event_occurrence(event_occurrence, price=0)
            booking = create_booking(user, stock, venue=venue)

            PcObject.save(admin_user, booking)

            url = '/bookings/token/{}'.format(booking.token)
            # When
            response = TestClient(app.test_client()).get(url)
            # Then
            assert response.status_code == 400
            error_message = response.json
            assert error_message['email'] == [
                'Vous devez préciser l\'email de l\'utilisateur quand vous n\'êtes pas connecté(e)']

        @clean_database
        def when_user_doesnt_have_rights_and_token_exists(self, app):
            # Given
            user = create_user(email='user@email.fr')
            querying_user = create_user(email='querying@email.fr')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='Event Name')
            event_occurrence = create_event_occurrence(offer)
            stock = create_stock_from_event_occurrence(event_occurrence, price=0)
            booking = create_booking(user, stock, venue=venue)

            PcObject.save(querying_user, booking)

            # When
            response = TestClient(app.test_client()).with_auth('querying@email.fr').get(
                '/bookings/token/{}'.format(booking.token))
            # Then
            assert response.status_code == 400
            assert response.json['global'] == ["Cette contremarque n'a pas été trouvée"]


    class Returns403:
        @clean_database
        def when_booking_is_on_stock_with_beginning_datetime_in_more_than_72_hours(self, app):
            # Given
            in_73_hours = datetime.utcnow() + timedelta(hours=73)
            in_74_hours = datetime.utcnow() + timedelta(hours=74)
            in_72_hours = datetime.utcnow() + timedelta(hours=72)
            user = create_user(email='user@email.fr')
            admin_user = create_user(email='admin@email.fr')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0, beginning_datetime=in_73_hours,
                                                  end_datetime=in_74_hours, booking_limit_datetime=in_72_hours)
            booking = create_booking(user, stock, venue=venue)

            PcObject.save(admin_user, booking)
            url = '/bookings/token/{}?email={}&offer_id={}'.format(booking.token, 'user@email.fr',
                                                                   humanize(stock.offerId))

            # When
            response = TestClient(app.test_client()).get(url)
            # Then
            assert response.status_code == 403
            assert response.json['beginningDatetime'] == [
                'Vous ne pouvez pas valider cette contremarque plus de 72h avant le début de l\'évènement']


    class Returns410:
        @clean_database
        def when_booking_is_already_validated(self, app):
            # Given
            user = create_user(email='user@email.fr')
            admin_user = create_user(email='admin@email.fr')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue, offer=None, price=0)
            booking = create_booking(user, stock, venue=venue, is_used=True)

            PcObject.save(admin_user, booking)
            url = '/bookings/token/{}?email={}&offer_id={}'.format(booking.token, 'user@email.fr',
                                                                   humanize(stock.offerId))

            # When
            response = TestClient(app.test_client()).get(url)
            # Then
            assert response.status_code == 410
            assert response.json['booking'] == ['Cette réservation a déjà été validée']

        @clean_database
        def when_booking_is_cancelled(self, app):
            # Given
            user = create_user(email='user@email.fr')
            admin_user = create_user(email='admin@email.fr')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue, offer=None, price=0)
            booking = create_booking(user, stock, venue=venue, is_cancelled=True)

            PcObject.save(admin_user, booking)
            url = '/bookings/token/{}?email={}&offer_id={}'.format(booking.token, 'user@email.fr',
                                                                   humanize(stock.offerId))

            # When
            response = TestClient(app.test_client()).get(url)
            # Then
            assert response.status_code == 410
            assert response.json['booking'] == ['Cette réservation a été annulée']
