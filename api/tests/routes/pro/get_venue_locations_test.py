import pytest

import pcapi.core.offers.factories as offers_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.models.api_errors import OBJECT_NOT_FOUND_ERROR_MESSAGE


pytestmark = pytest.mark.usefixtures("db_session")


class Return200Test:
    def test_get_offerer_addresses_success(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        pro = user_offerer.user
        offerer = user_offerer.offerer
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)

        offerer_address_1 = offerers_factories.OfferLocationFactory(
            offerer=offerer,
            label="1ere adresse",
            address__street="1 boulevard Poissonnière",
            address__postalCode="75002",
            address__city="Paris",
            venue=venue,
        )
        offers_factories.OfferFactory(venue=offerer_address_1.venue, offererAddress=offerer_address_1)
        offerer_address_2 = offerers_factories.OfferLocationFactory(
            offerer=offerer,
            venue=venue,
            label="2eme adresse",
            address__street="20 Avenue de Ségur",
            address__postalCode="75007",
            address__city="Paris",
            address__banId="75107_7560_00001",
        )
        offers_factories.OfferFactory(venue=offerer_address_2.venue, offererAddress=offerer_address_2)
        offerer_address_3 = offerers_factories.OfferLocationFactory(
            offerer=offerer,
            venue=venue,
            label="3eme adresse",
            address__street="3 rue des moutons",
            address__postalCode="75008",
            address__city="Paris",
            address__banId="75108_7560_00000",
        )
        offers_factories.OfferFactory(venue=offerer_address_3.venue, offererAddress=offerer_address_3)
        offerers_factories.OfferLocationFactory(
            label="1ere adresse différent offerer",
            address__street="8 Boulevard du Port",
            address__postalCode="80000",
            address__city="Amiens",
            address__banId="80000_7560_00001",
        )

        response = client.with_session_auth(email=pro.email).get(
            f"/venues/{venue.id}/locations", params={"withOffersOption": "INDIVIDUAL_OFFERS_ONLY"}
        )

        assert response.status_code == 200
        assert response.json == [
            {
                "addressId": offerer_address_1.addressId,
                "city": "Paris",
                "departmentCode": "75",
                "id": offerer_address_1.id,
                "label": "1ere adresse",
                "postalCode": "75002",
                "street": "1 boulevard Poissonnière",
                "venueId": venue.id,
                "venueName": venue.name,
            },
            {
                "addressId": offerer_address_2.addressId,
                "city": "Paris",
                "departmentCode": "75",
                "id": offerer_address_2.id,
                "label": "2eme adresse",
                "postalCode": "75007",
                "street": "20 Avenue de Ségur",
                "venueId": venue.id,
                "venueName": venue.name,
            },
            {
                "addressId": offerer_address_3.addressId,
                "city": "Paris",
                "departmentCode": "75",
                "id": offerer_address_3.id,
                "label": "3eme adresse",
                "postalCode": "75008",
                "street": "3 rue des moutons",
                "venueId": venue.id,
                "venueName": venue.name,
            },
        ]


class Return404Test:
    def test_access_by_unauthorized_pro_user(self, client):
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        client = client.with_session_auth(email=pro.email)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        with assert_num_queries(2):
            response = client.get(
                f"/venues/{venue.id}/locations", params={"withOffersOption": "INDIVIDUAL_OFFERS_ONLY"}
            )
            assert response.status_code == 404
            assert response.json == {"global": [OBJECT_NOT_FOUND_ERROR_MESSAGE]}

    def test_get_offerer_addresses_unexistent_venue(self, client):
        pro = users_factories.ProFactory()
        client = client.with_session_auth(email=pro.email)
        response = client.get("/venues/1/locations", params={"withOffersOption": "INDIVIDUAL_OFFERS_ONLY"})
        assert response.status_code == 404
        assert response.json == {"global": [OBJECT_NOT_FOUND_ERROR_MESSAGE]}
