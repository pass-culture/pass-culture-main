from datetime import datetime, timedelta

from models import PcObject, Offer, Recommendation, Product, Provider
from routes.serialization import serialize
from tests.conftest import clean_database, TestClient
from tests.test_utils import create_user, create_offerer, create_user_offerer, create_venue, \
    create_offer_with_thing_product, API_URL, create_product_with_event_type, create_offer_with_event_product, \
    create_product_with_thing_type, create_recommendation, activate_provider
from utils.human_ids import humanize


class Patch:
    class Returns200:
        @clean_database
        def when_updating_offer_booking_email(self, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue, booking_email='old@email.com')

            PcObject.save(offer, user, user_offerer)

            json = {
                'bookingEmail': 'offer@email.com',
            }

            # When
            response = TestClient(app.test_client()).with_auth(user.email).patch(
                f'{API_URL}/offers/{humanize(offer.id)}',
                json=json)

            # Then
            assert response.status_code == 200
            assert Offer.query.get(offer.id).bookingEmail == 'offer@email.com'

        @clean_database
        def when_deactivating_offer_and_makes_recommendations_outdated(self, app):
            # Given
            seven_days_from_now = datetime.utcnow() + timedelta(days=7)
            user = create_user()
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue, booking_email='old@email.com')
            recommendation = create_recommendation(offer, user, valid_until_date=seven_days_from_now)
            PcObject.save(offer, user, user_offerer, recommendation)
            recommendation_id = recommendation.id

            json = {
                'isActive': False,
            }

            # When
            response = TestClient(app.test_client()).with_auth(user.email).patch(
                f'{API_URL}/offers/{humanize(offer.id)}',
                json=json)

            # Then
            assert response.status_code == 200
            assert Recommendation.query.get(recommendation_id).validUntilDate < datetime.utcnow()

        @clean_database
        def when_user_updating_thing_offer_is_linked_to_same_owning_offerer(self, app):
            # Given
            user = create_user(email='editor@email.com')
            owning_offerer = create_offerer()
            user_offerer = create_user_offerer(user, owning_offerer)
            venue = create_venue(owning_offerer)
            product = create_product_with_thing_type(thing_name='Old Name', owning_offerer=owning_offerer)
            offer = create_offer_with_thing_product(venue, product)
            PcObject.save(offer, user_offerer)
            offer_id = offer.id
            product_id = product.id

            json = {
                'name': 'New Name'
            }

            # When
            response = TestClient(app.test_client()).with_auth(user.email).patch(
                f'{API_URL}/offers/{humanize(offer_id)}',
                json=json)

            # Then
            assert response.status_code == 200
            assert Offer.query.get(offer_id).name == 'New Name'
            assert Product.query.get(product_id).name == 'New Name'

        @clean_database
        def when_user_updating_thing_offer_is_not_linked_to_owning_offerer(self, app):
            # Given
            user = create_user(email='editor@email.com')
            owning_offerer = create_offerer(siren='123456789')
            editor_offerer = create_offerer(siren='123456780')
            editor_user_offerer = create_user_offerer(user, editor_offerer)
            venue = create_venue(editor_offerer)
            product = create_product_with_thing_type(thing_name='Old Name', owning_offerer=owning_offerer)
            offer = create_offer_with_thing_product(venue, product)
            PcObject.save(offer, editor_user_offerer, owning_offerer)
            offer_id = offer.id
            product_id = product.id

            json = {
                'name': 'New Name'
            }

            # When
            response = TestClient(app.test_client()).with_auth(user.email).patch(
                f'{API_URL}/offers/{humanize(offer.id)}',
                json=json)

            # Then
            assert response.status_code == 200
            assert Offer.query.get(offer_id).name == 'New Name'
            assert Product.query.get(product_id).name == 'Old Name'

        @clean_database
        def when_user_updating_thing_offer_has_rights_on_offer_but_no_owningOfferer_for_thing(self, app):
            # Given
            user = create_user(email='editor@email.com')
            offerer = create_offerer(siren='123456780')
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            product = create_product_with_thing_type(thing_name='Old Name', owning_offerer=None)
            offer = create_offer_with_thing_product(venue, product)
            PcObject.save(offer, user_offerer)

            json = {
                'name': 'New Name'
            }

            # When
            response = TestClient(app.test_client()).with_auth(user.email).patch(
                f'{API_URL}/offers/{humanize(offer.id)}',
                json=json)

            # Then
            assert response.status_code == 200
            assert Offer.query.one().name == 'New Name'
            assert Product.query.one().name == 'Old Name'

        @clean_database
        def when_deactivate_offer_from_provider(self, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            provider = activate_provider('TiteLiveStocks')
            offer = create_offer_with_thing_product(venue, id_at_providers='id_provider', last_provider_id=provider.id)
            PcObject.save(offer, user_offerer)
            offer_id = offer.id

            json = {
                'isActive': False
            }

            # When
            response = TestClient(app.test_client()).with_auth(user.email).patch(
                f'{API_URL}/offers/{humanize(offer.id)}',
                json=json)

            # Then
            assert response.status_code == 200
            assert not Offer.query.get(offer_id).isActive

        @clean_database
        def when_activate_offer_from_provider(self, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            provider = activate_provider('TiteLiveStocks')
            offer = create_offer_with_thing_product(venue,
                                                    is_active=False,
                                                    id_at_providers='id_provider',
                                                    last_provider_id=provider.id)
            PcObject.save(offer, user_offerer)
            offer_id = offer.id

            json = {
                'isActive': True
            }

            # When
            response = TestClient(app.test_client()).with_auth(user.email).patch(
                f'{API_URL}/offers/{humanize(offer.id)}',
                json=json)

            # Then
            assert response.status_code == 200
            assert Offer.query.get(offer_id).isActive

        @clean_database
        def when_patch_an_offer_that_is_imported_with_local_provider(self, app):
            # given
            tite_live_provider = Provider \
                .query \
                .filter(Provider.localClass == 'TiteLiveThings') \
                .first()

            user = create_user()
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue,
                                                    booking_email='old@email.com',
                                                    last_provider_id=tite_live_provider.id)

            PcObject.save(offer, user, user_offerer)
            json = {
                'bookingEmail': 'offer@email.com',
            }

            # When
            response = TestClient(app.test_client()).with_auth(user.email).patch(
                f'{API_URL}/offers/{humanize(offer.id)}',
                json=json)

            # then
            assert response.status_code == 200

    class Returns400:
        @clean_database
        def when_trying_to_patch_forbidden_attributes(self, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            thing_product = create_product_with_thing_type(thing_name='Old Name', owning_offerer=None)
            offer = create_offer_with_thing_product(venue, thing_product)

            PcObject.save(offer, user, user_offerer)

            forbidden_keys = ['idAtProviders', 'dateModifiedAtLastProvider', 'thumbCount',
                              'owningOffererId', 'id', 'lastProviderId', 'dateCreated']

            json = {
                'id': 1,
                'dateCreated': serialize(datetime(2019, 1, 1)),
                'lastProviderId': 1,
                'owningOffererId': 'AA',
                'idAtProviders': 1,
                'dateModifiedAtLastProvider': serialize(datetime(2019, 1, 1)),
                'thumbCount': 2
            }

            # When
            response = TestClient(app.test_client()).with_auth(user.email).patch(
                f'{API_URL}/offers/{humanize(offer.id)}',
                json=json)

            # Then
            assert response.status_code == 400
            assert response.json['owningOffererId'] == ['Vous ne pouvez pas modifier cette information']
            for key in forbidden_keys:
                assert key in response.json

    class Returns403:
        @clean_database
        def when_user_is_not_attached_to_offerer(self, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            event_product = create_product_with_event_type(event_name='Old name')
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_product)

            PcObject.save(event_product, offer, user, venue)

            json = {
                'name': 'New name',
                'venueId': humanize(venue.id)
            }

            # When
            response = TestClient(app.test_client()).with_auth(user.email).patch(
                f'{API_URL}/offers/{humanize(offer.id)}',
                json=json)

            # Then
            assert response.status_code == 403
            assert response.json['global'] == [
                "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."]

    class Returns404:
        @clean_database
        def test_returns_404_if_offer_does_not_exist(self, app):
            # given
            user = create_user()
            PcObject.save(user)
            auth_request = TestClient(app.test_client()).with_auth(email=user.email)

            # when
            response = auth_request.patch('/offers/ADFGA', json={})

            # then
            assert response.status_code == 404
