from datetime import timedelta, datetime

from domain.reimbursement import ReimbursementRules
from models import PcObject, ThingType, EventType
from models.pc_object import serialize
from tests.conftest import clean_database, TestClient
from tests.routes.output import JSON_OUTPUT, remove_ids
from tests.test_utils import create_booking, \
    create_deposit, \
    create_offer_with_event_product, \
    create_offerer, \
    create_stock_from_offer, \
    create_stock_with_event_offer, \
    create_stock_with_thing_offer, \
    create_offer_with_thing_product, \
    create_user, \
    create_user_offerer, \
    create_venue, \
    create_product_with_thing_type, create_product_with_event_type, create_stock_from_event_occurrence, \
    create_event_occurrence
from utils.human_ids import dehumanize, humanize


class Get:
    class Returns200:
        @clean_database
        def expect_json_output(self, app):
            # given
            user_pro = create_user(can_book_free_offers=False)
            user = create_user(email='test@email.com')
            deposit = create_deposit(user, amount=24000)
            PcObject.save(deposit)
            offerer = create_offerer()
            user_offerer = create_user_offerer(user_pro, offerer)
            PcObject.save(user_offerer)

            venue = create_venue(offerer)
            stock1 = create_stock_with_event_offer(offerer, venue, price=20)
            stock2 = create_stock_with_thing_offer(offerer, venue, offer=None, price=40)
            stock3 = create_stock_with_thing_offer(offerer, venue, offer=None, price=22950)
            booking1 = create_booking(user, stock1, venue, recommendation=None, quantity=2)
            booking2 = create_booking(user, stock2, venue, recommendation=None, quantity=2)
            booking3 = create_booking(user, stock3, venue, recommendation=None, quantity=1)
            PcObject.save(booking1, booking2, booking3)

            # when
            response = TestClient(app.test_client()) \
                .with_auth(user_pro.email) \
                .get(
                '/offerers/%s/bookings?order_by_column=booking_id&order=desc' % humanize(offerer.id))

            # then
            assert response.status_code == 200
            assert remove_ids(response.json) == remove_ids(JSON_OUTPUT)

        @clean_database
        def when_user_managing_offerer_and_returns_bookings_with_their_reimbursements_ordered_newest_to_oldest(self,
                                                                                                               app):
            # given
            now = datetime.utcnow()
            user_pro = create_user(can_book_free_offers=False)
            user = create_user(email='test@email.com')
            deposit = create_deposit(user, amount=24000)
            PcObject.save(deposit)
            offerer = create_offerer()
            user_offerer = create_user_offerer(user_pro, offerer)
            PcObject.save(user_offerer)

            venue = create_venue(offerer)
            stock1 = create_stock_with_event_offer(offerer, venue, price=20)
            stock2 = create_stock_with_thing_offer(offerer, venue, offer=None, price=40)
            stock3 = create_stock_with_thing_offer(offerer, venue, offer=None, price=22950)
            booking1 = create_booking(user, stock1, venue, recommendation=None, quantity=2)
            booking2 = create_booking(user, stock2, venue, recommendation=None, quantity=2)
            booking3 = create_booking(user, stock3, venue, recommendation=None, quantity=1)
            PcObject.save(booking1, booking2, booking3)

            # when
            response = TestClient(app.test_client()) \
                .with_auth(user_pro.email) \
                .get(
                '/offerers/%s/bookings?order_by_column=booking_id&order=desc' % humanize(offerer.id))

            # then
            assert response.status_code == 200
            elements = response.json
            assert dehumanize(elements[0]['id']) == booking3.id
            assert dehumanize(elements[1]['id']) == booking2.id
            assert dehumanize(elements[2]['id']) == booking1.id

        @clean_database
        def when_user_managing_offerer_and_returns_bookings_with_only_public_user_info_and_none_token(self, app):
            # given
            now = datetime.utcnow()
            user_pro = create_user(can_book_free_offers=False)
            user = create_user(first_name='Jean', last_name='Aimarx', email='jean.aimarx@disrupflux.fr')
            deposit = create_deposit(user, amount=24000)
            offerer = create_offerer()
            user_offerer = create_user_offerer(user_pro, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=20)
            booking = create_booking(user, stock, venue, recommendation=None, quantity=2)

            PcObject.save(deposit, user_offerer, booking)

            # when
            response = TestClient(app.test_client()) \
                .with_auth(user_pro.email).get(
                '/offerers/%s/bookings' % humanize(offerer.id))

            # then
            response_first_booking_json = response.json[0]
            assert response.status_code == 200
            assert response_first_booking_json['token'] == None
            assert response_first_booking_json['user'] == {
                'firstName': user.firstName,
                'email': user.email,
                'lastName': user.lastName
            }

        @clean_database
        def when_user_managing_offerer_and_returns_bookings_with_public_user_info_and_token_when_it_is_used(self, app):
            # given
            now = datetime.utcnow()
            user_pro = create_user(can_book_free_offers=False)
            user = create_user(first_name='Jean', last_name='Aimarx', email='jean.aimarx@disrupflux.fr')
            deposit = create_deposit(user, amount=24000)
            offerer = create_offerer()
            user_offerer = create_user_offerer(user_pro, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=20)
            booking = create_booking(user, stock, venue, recommendation=None, quantity=2, is_used=True)

            PcObject.save(deposit, user_offerer, booking)

            # when
            response = TestClient(app.test_client()) \
                .with_auth(user_pro.email) \
                .get('/offerers/%s/bookings' % humanize(offerer.id))

            # then
            response_first_booking_json = response.json[0]
            assert response.status_code == 200
            assert response_first_booking_json['token'] == booking.token
            assert response_first_booking_json['user'] == {
                'firstName': user.firstName,
                'email': user.email,
                'lastName': user.lastName
            }

        @clean_database
        def when_user_managing_offerer_and_returns_bookings_with_their_reimbursements_infos(self, app):
            # given
            now = datetime.utcnow()
            user_pro = create_user(can_book_free_offers=False)
            user = create_user(email='test@email.com')
            deposit = create_deposit(user, amount=500)
            PcObject.save(deposit)
            offerer = create_offerer()
            user_offerer = create_user_offerer(user_pro, offerer)
            PcObject.save(user_offerer)

            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=20)
            booking = create_booking(user, stock, venue, recommendation=None, quantity=2,
                                     date_created=now - timedelta(days=5))

            PcObject.save(booking)

            # when
            response = TestClient(app.test_client()) \
                .with_auth(user_pro.email) \
                .get('/offerers/%s/bookings' % humanize(offerer.id))

            # then
            assert response.status_code == 200
            assert response.json[0]['id'] == humanize(booking.id)
            assert response.json[0]['reimbursement_rule'] == ReimbursementRules.PHYSICAL_OFFERS.value.description
            assert response.json[0]['reimbursed_amount'] == booking.value

        @clean_database
        def when_user_managing_offerer_and_returns_bookings_with_thing_or_event_offer_type(self, app):
            # given
            now = datetime.utcnow()
            user_pro = create_user(can_book_free_offers=False)
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user_pro, offerer)
            venue = create_venue(offerer)
            thing_product = create_product_with_thing_type(thing_type=ThingType.AUDIOVISUEL)
            offer_thing = create_offer_with_thing_product(venue, thing_product)
            stock_thing = create_stock_from_offer(offer_thing, price=0)
            booking_thing = create_booking(user, stock_thing, venue, recommendation=None, quantity=2,
                                           date_created=now - timedelta(days=5))
            event_product = create_product_with_event_type(event_type=EventType.MUSEES_PATRIMOINE)
            offer_event = create_offer_with_event_product(venue, event_product)
            stock_event = create_stock_from_event_occurrence(create_event_occurrence(offer_event), price=0)
            booking_event = create_booking(user, stock_event, venue, recommendation=None, quantity=2,
                                           date_created=now - timedelta(days=5))

            PcObject.save(booking_thing, booking_event, user_offerer)

            expected_audiovisuel_offer_type = {
                'conditionalFields': [],
                'description': 'Action, science-fiction, documentaire ou comédie sentimentale ? ' \
                               'En salle, en plein air ou bien au chaud chez soi ? ' \
                               'Et si c’était plutôt cette exposition qui allait faire son cinéma ?',
                'proLabel': 'Audiovisuel — films sur supports physiques et VOD',
                'appLabel': "Films sur supports physiques et VOD",
                'offlineOnly': False,
                'onlineOnly': False,
                'sublabel': 'Regarder',
                'type': 'Thing',
                'value': 'ThingType.AUDIOVISUEL'
            }

            expected_musees_patrimoine_offer_type = {
                'conditionalFields': [],
                'description': 'Action, science-fiction, documentaire ou comédie sentimentale ? En salle, en plein air ou bien au chaud chez soi ? Et si c’était plutôt cette exposition qui allait faire son cinéma ?',
                'proLabel': 'Musées, patrimoine — expositions, visites guidées, activités spécifiques',
                'appLabel': "Expositions, visites guidées, activités spécifiques",
                'offlineOnly': True,
                'onlineOnly': False,
                'sublabel': 'Regarder',
                'type': 'Event',
                'value': 'EventType.MUSEES_PATRIMOINE'
            }

            # when
            response = TestClient(app.test_client()) \
                .with_auth(user_pro.email) \
                .get('/offerers/%s/bookings' % humanize(offerer.id))

            # then
            offer_types = list(map(_get_offer_type, response.json))
            assert expected_audiovisuel_offer_type in offer_types
            assert expected_musees_patrimoine_offer_type in offer_types

        @clean_database
        def when_ordered_by_venue_name_desc(self, app):
            # given
            now = datetime.utcnow()
            user_pro = create_user(can_book_free_offers=False)
            user = create_user(email='test@email.com')
            deposit = create_deposit(user, amount=500)
            offerer = create_offerer()
            user_offerer = create_user_offerer(user_pro, offerer)

            venue_1 = create_venue(offerer, name='La petite librairie', siret=offerer.siren + '12345')
            venue_2 = create_venue(offerer, name='Atelier expérimental', siret=offerer.siren + '54321')
            offer_1 = create_offer_with_thing_product(venue_1)
            offer_2 = create_offer_with_event_product(venue_2)
            stock1 = create_stock_from_offer(offer_1)
            stock2 = create_stock_from_offer(offer_2)
            stock3 = create_stock_from_offer(offer_2)
            booking1 = create_booking(user, stock2, venue_2, recommendation=None, quantity=2)
            booking2 = create_booking(user, stock1, venue_1, recommendation=None, quantity=2)
            booking3 = create_booking(user, stock3, venue_2, recommendation=None, quantity=1)
            PcObject.save(deposit, user_offerer, booking1, booking2, booking3)

            # when
            response = TestClient(app.test_client()) \
                .with_auth(user_pro.email) \
                .get(
                '/offerers/%s/bookings?order_by_column=venue_name&order=desc' % humanize(offerer.id)
            )

            # then
            assert response.status_code == 200
            elements = response.json
            assert elements[0]['stock']['resolvedOffer']['venueId'] == humanize(venue_1.id)
            assert elements[1]['stock']['resolvedOffer']['venueId'] == humanize(venue_2.id)
            assert elements[2]['stock']['resolvedOffer']['venueId'] == humanize(venue_2.id)

        @clean_database
        def when_ordered_by_venue_name_asc(self, app):
            # given
            now = datetime.utcnow()
            user_pro = create_user(can_book_free_offers=False)
            user = create_user(email='test@email.com')
            deposit = create_deposit(user, amount=500)
            offerer = create_offerer()
            user_offerer = create_user_offerer(user_pro, offerer)

            venue_1 = create_venue(offerer, name='La petite librairie', siret=offerer.siren + '12345')
            venue_2 = create_venue(offerer, name='Atelier expérimental', siret=offerer.siren + '54321')
            offer_1 = create_offer_with_thing_product(venue_1)
            offer_2 = create_offer_with_event_product(venue_2)
            stock1 = create_stock_from_offer(offer_1)
            stock2 = create_stock_from_offer(offer_2)
            stock3 = create_stock_from_offer(offer_2)
            booking1 = create_booking(user, stock2, venue_2, recommendation=None, quantity=2)
            booking2 = create_booking(user, stock1, venue_1, recommendation=None, quantity=2)
            booking3 = create_booking(user, stock3, venue_2, recommendation=None, quantity=1)
            PcObject.save(deposit, user_offerer, booking1, booking2, booking3)

            # when
            response = TestClient(app.test_client()) \
                .with_auth(user_pro.email) \
                .get(
                '/offerers/%s/bookings?order_by_column=venue_name&order=asc' % humanize(offerer.id))

            # then
            assert response.status_code == 200
            elements = response.json
            assert elements[0]['stock']['resolvedOffer']['venueId'] == humanize(venue_2.id)
            assert elements[1]['stock']['resolvedOffer']['venueId'] == humanize(venue_2.id)
            assert elements[2]['stock']['resolvedOffer']['venueId'] == humanize(venue_1.id)

        @clean_database
        def when_ordered_by_date_asc(self, app):
            # given
            now = datetime.utcnow()
            user_pro = create_user(can_book_free_offers=False)
            user = create_user(email='test@email.com')
            deposit = create_deposit(user, amount=500)
            offerer = create_offerer()
            user_offerer = create_user_offerer(user_pro, offerer)

            venue = create_venue(offerer, name='La petite librairie')
            offer = create_offer_with_thing_product(venue)
            stock1 = create_stock_from_offer(offer)
            stock2 = create_stock_from_offer(offer)
            stock3 = create_stock_from_offer(offer)
            booking1 = create_booking(user, stock2, venue, recommendation=None,
                                      date_created=serialize(datetime(2018, 10, 1)))
            booking2 = create_booking(user, stock1, venue, recommendation=None,
                                      date_created=serialize(datetime(2018, 10, 5)))
            booking3 = create_booking(user, stock3, venue, recommendation=None,
                                      date_created=serialize(datetime(2018, 10, 3)))
            PcObject.save(deposit, user_offerer, booking1, booking2, booking3)

            # when
            response = TestClient(app.test_client()) \
                .with_auth(user_pro.email) \
                .get(
                '/offerers/%s/bookings?order_by_column=date&order=asc' % humanize(offerer.id))

            # then
            assert response.status_code == 200
            elements = response.json
            assert elements[0]['dateCreated'].startswith('2018-10-01')
            assert elements[1]['dateCreated'].startswith('2018-10-03')
            assert elements[2]['dateCreated'].startswith('2018-10-05')

        @clean_database
        def when_ordered_by_date_desc(self, app):
            # given
            now = datetime.utcnow()
            user_pro = create_user(can_book_free_offers=False)
            user = create_user(email='test@email.com')
            deposit = create_deposit(user, amount=500)
            offerer = create_offerer()
            user_offerer = create_user_offerer(user_pro, offerer)

            venue = create_venue(offerer, name='La petite librairie')
            offer = create_offer_with_thing_product(venue)
            stock1 = create_stock_from_offer(offer)
            stock2 = create_stock_from_offer(offer)
            stock3 = create_stock_from_offer(offer)
            booking1 = create_booking(user, stock2, venue, recommendation=None,
                                      date_created=serialize(datetime(2018, 10, 1)))
            booking2 = create_booking(user, stock1, venue, recommendation=None,
                                      date_created=serialize(datetime(2018, 10, 5)))
            booking3 = create_booking(user, stock3, venue, recommendation=None,
                                      date_created=serialize(datetime(2018, 10, 3)))
            PcObject.save(deposit, user_offerer, booking1, booking2, booking3)

            # when
            response = TestClient(app.test_client()) \
                .with_auth(user_pro.email) \
                .get(
                '/offerers/%s/bookings?order_by_column=date&order=desc' % humanize(offerer.id))

            # then
            assert response.status_code == 200
            elements = response.json
            assert elements[0]['dateCreated'].startswith('2018-10-05')
            assert elements[1]['dateCreated'].startswith('2018-10-03')
            assert elements[2]['dateCreated'].startswith('2018-10-01')

        @clean_database
        def when_ordered_by_category_asc(self, app):
            # given
            now = datetime.utcnow()
            user_pro = create_user(can_book_free_offers=False)
            user = create_user(email='test@email.com')
            deposit = create_deposit(user, amount=500)
            offerer = create_offerer()
            user_offerer = create_user_offerer(user_pro, offerer)

            venue_1 = create_venue(offerer, name='La petite librairie', siret=offerer.siren + '12345')
            venue_2 = create_venue(offerer, name='Atelier expérimental', siret=offerer.siren + '54321')
            offer_1 = create_offer_with_thing_product(venue_1, thing_type=ThingType.LIVRE_EDITION)
            offer_2 = create_offer_with_event_product(venue_2, event_type=EventType.SPECTACLE_VIVANT)
            stock1 = create_stock_from_offer(offer_1)
            stock2 = create_stock_from_offer(offer_2)
            stock3 = create_stock_from_offer(offer_2)
            booking1 = create_booking(user, stock2, venue_2, recommendation=None)
            booking2 = create_booking(user, stock1, venue_1, recommendation=None)
            booking3 = create_booking(user, stock3, venue_2, recommendation=None)
            PcObject.save(deposit, user_offerer, booking1, booking2, booking3)

            # when
            response = TestClient(app.test_client()) \
                .with_auth(user_pro.email) \
                .get(
                '/offerers/%s/bookings?order_by_column=category&order=asc' % humanize(offerer.id))

            # then
            assert response.status_code == 200
            elements = response.json
            assert elements[0]['stock']['resolvedOffer']['product']['type'] == 'EventType.SPECTACLE_VIVANT'
            assert elements[1]['stock']['resolvedOffer']['product']['type'] == 'EventType.SPECTACLE_VIVANT'
            assert elements[2]['stock']['resolvedOffer']['product']['type'] == 'ThingType.LIVRE_EDITION'

        @clean_database
        def when_ordered_by_category_desc(self, app):
            # given
            now = datetime.utcnow()
            user_pro = create_user(can_book_free_offers=False)
            user = create_user(email='test@email.com')
            deposit = create_deposit(user, amount=500)
            offerer = create_offerer()
            user_offerer = create_user_offerer(user_pro, offerer)

            venue_1 = create_venue(offerer, name='La petite librairie', siret=offerer.siren + '12345')
            venue_2 = create_venue(offerer, name='Atelier expérimental', siret=offerer.siren + '54321')
            offer_1 = create_offer_with_thing_product(venue_1, thing_type=ThingType.LIVRE_EDITION)
            offer_2 = create_offer_with_event_product(venue_2, event_type=EventType.SPECTACLE_VIVANT)
            stock1 = create_stock_from_offer(offer_1)
            stock2 = create_stock_from_offer(offer_2)
            stock3 = create_stock_from_offer(offer_2)
            booking1 = create_booking(user, stock2, venue_2, recommendation=None)
            booking2 = create_booking(user, stock1, venue_1, recommendation=None)
            booking3 = create_booking(user, stock3, venue_2, recommendation=None)
            PcObject.save(deposit, user_offerer, booking1, booking2, booking3)

            # when
            response = TestClient(app.test_client()) \
                .with_auth(user_pro.email) \
                .get(
                '/offerers/%s/bookings?order_by_column=category&order=desc' % humanize(offerer.id))

            # then
            assert response.status_code == 200
            elements = response.json
            assert elements[0]['stock']['resolvedOffer']['product']['type'] == 'ThingType.LIVRE_EDITION'
            assert elements[1]['stock']['resolvedOffer']['product']['type'] == 'EventType.SPECTACLE_VIVANT'
            assert elements[2]['stock']['resolvedOffer']['product']['type'] == 'EventType.SPECTACLE_VIVANT'

        @clean_database
        def when_ordered_by_amount_desc(self, app):
            # given
            now = datetime.utcnow()
            user_pro = create_user(can_book_free_offers=False)
            user = create_user(email='test@email.com')
            deposit = create_deposit(user, amount=500)
            offerer = create_offerer()
            user_offerer = create_user_offerer(user_pro, offerer)

            venue_1 = create_venue(offerer, name='La petite librairie', is_virtual=True, siret=None)
            venue_2 = create_venue(offerer, name='Atelier expérimental')
            offer_1 = create_offer_with_thing_product(venue_1, thing_type=ThingType.JEUX_VIDEO,
                                                      url='http://game.fr/jeu')
            offer_2 = create_offer_with_event_product(venue_2, event_type=EventType.SPECTACLE_VIVANT)
            stock1 = create_stock_from_offer(offer_1, price=10)
            stock2 = create_stock_from_offer(offer_2, price=20)
            stock3 = create_stock_from_offer(offer_2, price=0)
            booking1 = create_booking(user, stock2, venue_2, recommendation=None)
            booking2 = create_booking(user, stock1, venue_1, recommendation=None)
            booking3 = create_booking(user, stock3, venue_2, recommendation=None)
            PcObject.save(deposit, user_offerer, booking1, booking2, booking3)

            # when
            response = TestClient(app.test_client()) \
                .with_auth(user_pro.email) \
                .get(
                '/offerers/%s/bookings?order_by_column=amount&order=desc' % humanize(offerer.id))

            # then
            assert response.status_code == 200
            elements = response.json
            assert elements[0]['amount'] == 20
            assert elements[1]['amount'] == 10
            assert elements[2]['amount'] == 0

        @clean_database
        def when_ordered_by_amount_asc(self, app):
            # given
            now = datetime.utcnow()
            user_pro = create_user(can_book_free_offers=False)
            user = create_user(email='test@email.com')
            deposit = create_deposit(user, amount=500)
            offerer = create_offerer()
            user_offerer = create_user_offerer(user_pro, offerer)

            venue_1 = create_venue(offerer, name='La petite librairie', is_virtual=True, siret=None)
            venue_2 = create_venue(offerer, name='Atelier expérimental')
            offer_1 = create_offer_with_thing_product(venue_1, thing_type=ThingType.JEUX_VIDEO,
                                                      url='http://game.fr/jeu')
            offer_2 = create_offer_with_event_product(venue_2, event_type=EventType.SPECTACLE_VIVANT)
            stock1 = create_stock_from_offer(offer_1, price=10)
            stock2 = create_stock_from_offer(offer_2, price=20)
            stock3 = create_stock_from_offer(offer_2, price=0)
            booking1 = create_booking(user, stock2, venue_2, recommendation=None)
            booking2 = create_booking(user, stock1, venue_1, recommendation=None)
            booking3 = create_booking(user, stock3, venue_2, recommendation=None)
            PcObject.save(deposit, user_offerer, booking1, booking2, booking3)

            # when
            response = TestClient(app.test_client()) \
                .with_auth(user_pro.email).get(
                '/offerers/%s/bookings?order_by_column=amount&order=asc' % humanize(offerer.id))

            # then
            assert response.status_code == 200
            elements = response.json
            assert elements[0]['amount'] == 0
            assert elements[1]['amount'] == 10
            assert elements[2]['amount'] == 20

    class Returns403:
        @clean_database
        def when_user_has_no_rights_on_offerer(self, app):
            # given
            now = datetime.utcnow()
            user = create_user(email='test@email.com')
            deposit = create_deposit(user, amount='500')
            PcObject.save(deposit)
            offerer = create_offerer()
            PcObject.save(offerer)

            venue = create_venue(offerer)
            stock1 = create_stock_with_event_offer(offerer, venue, price=20)
            stock2 = create_stock_with_thing_offer(offerer, venue, offer=None, price=30)
            stock3 = create_stock_with_thing_offer(offerer, venue, offer=None, price=40)
            booking1 = create_booking(user, stock1, venue, recommendation=None, quantity=2)
            booking2 = create_booking(user, stock2, venue, recommendation=None, quantity=1)
            booking3 = create_booking(user, stock3, venue, recommendation=None, quantity=2)

            PcObject.save(booking1, booking2, booking3)

            # when
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .get('/offerers/%s/bookings' % humanize(offerer.id))

            # then
            assert response.status_code == 403

    class Returns401:
        @clean_database
        def when_user_not_logged_in(self, app):
            # when
            offerer = create_offerer()
            PcObject.save(offerer)
            response = TestClient(app.test_client()).get('/offerers/%s/bookings' % humanize(offerer.id),
                                                         headers={'origin': 'http://localhost:3000'})

            # then
            assert response.status_code == 401


def _get_offer_type(response_json):
    return response_json['stock']['resolvedOffer']['product']['offerType']
