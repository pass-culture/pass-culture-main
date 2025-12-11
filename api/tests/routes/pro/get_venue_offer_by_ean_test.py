import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core import testing


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    num_queries = 1  # get user_session + user
    num_queries += 1  # get venue
    num_queries += 1  # check user_offerer exists
    num_queries += 1  # rollback
    num_queries += 1  # rollback

    def test_access_by_beneficiary(self, client):
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        offer = offers_factories.ThingOfferFactory(ean="0123456789123")

        auth_client = client.with_session_auth(email=beneficiary.email)
        venue_id = offer.venueId
        ean = offer.ean
        with testing.assert_num_queries(self.num_queries):
            response = auth_client.get(f"/offers/{venue_id}/ean/{ean}")
            assert response.status_code == 403

    def test_access_by_unauthorized_pro_user(self, client):
        pro_user = users_factories.ProFactory()
        offer = offers_factories.ThingOfferFactory(ean="0123456789123")

        auth_client = client.with_session_auth(email=pro_user.email)
        venue_id = offer.venueId
        ean = offer.ean
        with testing.assert_num_queries(self.num_queries):
            response = auth_client.get(f"/offers/{venue_id}/ean/{ean}")
            assert response.status_code == 403


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    num_queries = 1  # session + user
    num_queries += 1  # venue
    num_queries += 1  # user offerer
    num_queries += 1  # payload (joined query)
    num_queries += 1  # stocks of offer (a backref)

    def test_access_by_pro_user(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.ThingOfferFactory(
            venue__managingOfferer=user_offerer.offerer,
            ean="0123456789123",
        )

        auth_client = client.with_session_auth(email=user_offerer.user.email)
        venue_id = offer.venueId
        ean = offer.ean
        with testing.assert_num_queries(self.num_queries):
            response = auth_client.get(f"/offers/{venue_id}/ean/{ean}")
            assert response.status_code == 200

        response_json = response.json
        assert response_json["id"] == offer.id
        assert response_json["isActive"] == True


@pytest.mark.usefixtures("db_session")
class Returns404Test:
    num_queries = 1  # session + user
    num_queries += 1  # venue
    num_queries += 1  # user offerer
    num_queries += 1  # payload (joined query)
    num_queries += 1  # rollback
    num_queries += 1  # rollback

    def test_access_to_not_existing_ean(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.ThingOfferFactory(
            venue__managingOfferer=user_offerer.offerer,
            ean="0123456789123",
        )

        auth_client = client.with_session_auth(email=user_offerer.user.email)
        venue_id = offer.venueId
        with testing.assert_num_queries(self.num_queries):
            response = auth_client.get(f"/offers/{venue_id}/ean/2323456789123")
            assert response.status_code == 404

        response_json = response.json
        assert response_json == {"global": ["Aucun objet ne correspond à cet identifiant dans notre base de données"]}

    def test_access_to_not_active_offer(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.ThingOfferFactory(
            venue__managingOfferer=user_offerer.offerer,
            ean="0123456789123",
            isActive=False,
        )

        auth_client = client.with_session_auth(email=user_offerer.user.email)
        venue_id = offer.venueId
        ean = offer.ean
        with testing.assert_num_queries(self.num_queries):
            response = auth_client.get(f"/offers/{venue_id}/ean/{ean}")
            assert response.status_code == 404

        response_json = response.json
        assert response_json == {"global": ["Aucun objet ne correspond à cet identifiant dans notre base de données"]}
