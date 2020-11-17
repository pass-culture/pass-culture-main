from datetime import datetime

import pytest

from pcapi.model_creators.generic_creators import API_URL
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_provider
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.model_creators.specific_creators import create_stock_from_offer
from pcapi.models import Offer
from pcapi.repository import repository
from pcapi.utils.human_ids import humanize

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
                "isActive": True,
                "active": "true",
                "inactive": "true",
            }

            # When
            response = (
                TestClient(app.test_client())
                .with_auth(user.email)
                .patch(f"{API_URL}/offers/all-active-status", json=json)
            )

            # Then
            assert response.status_code == 204
            assert Offer.query.get(offer1.id).isActive == True
            assert Offer.query.get(offer2.id).isActive == True

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
                "isActive": False,
                "active": "true",
                "inactive": "true",
            }

            # When
            response = (
                TestClient(app.test_client())
                .with_auth(user.email)
                .patch(f"{API_URL}/offers/all-active-status", json=json)
            )

            # Then
            assert response.status_code == 204
            assert Offer.query.get(offer1.id).isActive == False
            assert Offer.query.get(offer2.id).isActive == False

        @pytest.mark.usefixtures("db_session")
        def should_update_offers_by_given_filters(self, app):
            # Given
            user = create_user()
            offerer_1 = create_offerer()
            offerer_2 = create_offerer(siren="516399122")
            user_offerer = create_user_offerer(user, offerer_1)
            venue_1 = create_venue(offerer_1)
            venue_2 = create_venue(offerer_1, siret="12355678912354")
            venue_3 = create_venue(offerer_2, siret="12355691912354")
            provider = create_provider()
            offer_corresponding_to_filters_1 = create_offer_with_thing_product(
                venue_1, idx=1, is_active=True, thing_name="OK 1", last_provider_id=provider.id, last_provider=provider
            )
            offer_corresponding_to_filters_2 = create_offer_with_thing_product(
                venue_1, idx=2, is_active=True, thing_name="OK 2", last_provider_id=provider.id, last_provider=provider
            )
            offer_not_corresponding_to_filters_1 = create_offer_with_thing_product(
                venue_2, idx=3, is_active=True, thing_name="OK 3"
            )
            offer_not_corresponding_to_filters_2 = create_offer_with_thing_product(
                venue_3, idx=4, is_active=True, thing_name="OK 4"
            )
            offer_not_corresponding_to_filters_3 = create_offer_with_thing_product(
                venue_1, idx=5, is_active=True, thing_name="Pas celle ci"
            )
            stock_corresponding_to_filters = create_stock_from_offer(offer=offer_corresponding_to_filters_1, beginning_datetime=datetime(2020, 10, 10, 10, 00, 00, 0))
            stock_not_corresponding_to_filters = create_stock_from_offer(offer=offer_corresponding_to_filters_2, beginning_datetime=datetime(2020, 11, 11, 10, 00, 00, 0))

            repository.save(
                offer_corresponding_to_filters_1,
                offer_corresponding_to_filters_2,
                offer_not_corresponding_to_filters_1,
                offer_not_corresponding_to_filters_2,
                offer_not_corresponding_to_filters_3,
                user,
                user_offerer,
                stock_corresponding_to_filters,
                stock_not_corresponding_to_filters,
            )

            json = {
                "isActive": False,
                "offererId": humanize(offerer_1.id),
                "venueId": humanize(venue_1.id),
                "name": "OK",
                "creationMode": "imported",
                'periodBeginningDate': '2020-10-09T00:00:00Z',
                'periodEndingDate': '2020-10-11T23:59:59Z',
            }

            # When
            response = (
                TestClient(app.test_client())
                .with_auth(user.email)
                .patch(f"{API_URL}/offers/all-active-status", json=json)
            )

            # Then
            assert response.status_code == 204
            assert Offer.query.get(offer_corresponding_to_filters_1.id).isActive == False
            assert Offer.query.get(offer_corresponding_to_filters_2.id).isActive == True
            assert Offer.query.get(offer_not_corresponding_to_filters_1.id).isActive == True
            assert Offer.query.get(offer_not_corresponding_to_filters_2.id).isActive == True
            assert Offer.query.get(offer_not_corresponding_to_filters_3.id).isActive == True
