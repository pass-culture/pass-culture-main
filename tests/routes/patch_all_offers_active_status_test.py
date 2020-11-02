import pytest

from pcapi.models import OfferSQLEntity
from pcapi.repository import repository
from pcapi.utils.human_ids import humanize
from pcapi.model_creators.generic_creators import create_user, create_offerer, create_user_offerer, create_venue, API_URL
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from tests.conftest import TestClient


class Patch:
    class Returns204:
        @pytest.mark.usefixtures("db_session")
        def when_activating_all_existing_offers(self, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer1 = create_offer_with_thing_product(venue, idx=1, is_active=False)
            offer2 = create_offer_with_thing_product(venue, idx=2, is_active=False)

            repository.save(offer1, offer2, user, user_offerer)

            json = {
                'isActive': True,
                'offererId': 'all',
                'venueId': 'all',
                'active': 'true',
                'inactive': 'true',
            }

            # When
            response = TestClient(app.test_client()).with_auth(user.email).patch(
                f'{API_URL}/offers/all-active-status',
                json=json)

            # Then
            assert response.status_code == 204
            assert OfferSQLEntity.query.get(offer1.id).isActive == True
            assert OfferSQLEntity.query.get(offer2.id).isActive == True

        @pytest.mark.usefixtures("db_session")
        def when_deactivating_all_existing_offers(self, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer1 = create_offer_with_thing_product(venue, idx=1, is_active=True)
            offer2 = create_offer_with_thing_product(venue, idx=2, is_active=True)

            repository.save(offer1, offer2, user, user_offerer)

            json = {
                'isActive': False,
                'offererId': 'all',
                'venueId': 'all',
                'active': 'true',
                'inactive': 'true',
            }

            # When
            response = TestClient(app.test_client()).with_auth(user.email).patch(
                f'{API_URL}/offers/all-active-status',
                json=json)

            # Then
            assert response.status_code == 204
            assert OfferSQLEntity.query.get(offer1.id).isActive == False
            assert OfferSQLEntity.query.get(offer2.id).isActive == False

        @pytest.mark.usefixtures("db_session")
        def should_update_offers_by_given_filters(self, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            offerer2 = create_offerer(siren='516399122')
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            venue2 = create_venue(offerer, siret='12355678912354')
            venue3 = create_venue(offerer2, siret='12355691912354')
            offer_corresponding_to_filters = create_offer_with_thing_product(venue, idx=1, is_active=True, thing_name='OK 1')
            offer_corresponding_to_filters_2 = create_offer_with_thing_product(venue, idx=2, is_active=True, thing_name='OK 2')
            offer_not_corresponding_to_filters = create_offer_with_thing_product(venue2, idx=3, is_active=True, thing_name='OK 3')
            offer_not_corresponding_to_filters_2 = create_offer_with_thing_product(venue3, idx=4, is_active=True, thing_name='OK 4')
            offer_not_corresponding_to_filters_3 = create_offer_with_thing_product(venue, idx=5, is_active=True, thing_name='Pas celle ci')

            repository.save(offer_corresponding_to_filters, offer_corresponding_to_filters_2, offer_not_corresponding_to_filters, offer_not_corresponding_to_filters_2, offer_not_corresponding_to_filters_3, user, user_offerer)

            json = {
                'isActive': False,
                'offererId': humanize(offerer.id),
                'venueId': humanize(venue.id),
                'active': 'true',
                'inactive': 'true',
                'name': 'OK',
            }

            # When
            response = TestClient(app.test_client()).with_auth(user.email).patch(
                f'{API_URL}/offers/all-active-status',
                json=json)

            # Then
            assert response.status_code == 204
            assert OfferSQLEntity.query.get(offer_corresponding_to_filters.id).isActive == False
            assert OfferSQLEntity.query.get(offer_corresponding_to_filters_2.id).isActive == False
            assert OfferSQLEntity.query.get(offer_not_corresponding_to_filters.id).isActive == True
            assert OfferSQLEntity.query.get(offer_not_corresponding_to_filters_2.id).isActive == True
            assert OfferSQLEntity.query.get(offer_not_corresponding_to_filters_3.id).isActive == True
