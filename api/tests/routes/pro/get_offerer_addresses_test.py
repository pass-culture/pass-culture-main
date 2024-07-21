import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories


class Return200Test:
    # session
    # user
    # user_offerer
    # oa retrieving request
    num_queries = 4

    @pytest.mark.usefixtures("db_session")
    def test_get_offerer_addresses_success(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        pro = user_offerer.user
        offerer = user_offerer.offerer

        offerer_address_1 = offerers_factories.OffererAddressFactory(
            offerer=offerer,
            label="1ere adresse",
            address__street="1 boulevard Poissonnière",
            address__postalCode="75002",
            address__city="Paris",
        )
        offerer_address_2 = offerers_factories.OffererAddressFactory(
            offerer=offerer,
            label="2eme adresse",
            address__street="20 Avenue de Ségur",
            address__postalCode="75007",
            address__city="Paris",
            address__banId="75107_7560_00001",
        )
        offerer_address_3 = offerers_factories.OffererAddressFactory(
            offerer=offerer,
            label="3eme adresse",
            address__street=None,
            address__postalCode="75008",
            address__city="Paris",
            address__banId="75108_7560_00000",
        )
        offerers_factories.OffererAddressFactory(
            label="1ere adresse différent offerer",
            address__street="8 Boulevard du Port",
            address__postalCode="80000",
            address__city="Amiens",
            address__banId="80000_7560_00001",
        )

        response = client.with_session_auth(email=pro.email).get(f"/offerers/{offerer.id}/addresses")

        assert response.status_code == 200
        assert response.json == [
            {
                "city": "Paris",
                "id": offerer_address_1.id,
                "isEditable": True,
                "label": "1ere adresse",
                "postalCode": "75002",
                "street": "1 boulevard Poissonnière",
            },
            {
                "city": "Paris",
                "id": offerer_address_2.id,
                "isEditable": True,
                "label": "2eme adresse",
                "postalCode": "75007",
                "street": "20 Avenue de Ségur",
            },
            {
                "city": "Paris",
                "id": offerer_address_3.id,
                "isEditable": True,
                "label": "3eme adresse",
                "postalCode": "75008",
                "street": None,
            },
        ]

    @pytest.mark.usefixtures("db_session")
    def test_get_offerer_addresses_with_offers(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        pro = user_offerer.user
        offerer = user_offerer.offerer

        offerer_address_1 = offerers_factories.OffererAddressFactory(
            offerer=offerer,
            label="1ere adresse",
            address__street="1 boulevard Poissonnière",
            address__postalCode="75002",
            address__city="Paris",
        )
        offerers_factories.OffererAddressFactory(
            offerer=offerer,
            label="2eme adresse",
            address__street="20 Avenue de Ségur",
            address__postalCode="75007",
            address__city="Paris",
            address__banId="75107_7560_00001",
        )
        offers_factories.OfferFactory(
            venue__managingOfferer=offerer, offererAddress=offerer_address_1, venue__offererAddress=offerer_address_1
        )

        client = client.with_session_auth(email=pro.email)
        offerer_id = offerer.id
        with assert_num_queries(self.num_queries):
            response = client.get(f"/offerers/{offerer_id}/addresses?onlyWithOffers=true")
            assert response.status_code == 200
            assert response.json == [
                {
                    "city": "Paris",
                    "id": offerer_address_1.id,
                    "isEditable": False,
                    "label": "1ere adresse",
                    "postalCode": "75002",
                    "street": "1 boulevard Poissonnière",
                },
            ]

        # Try with the same data without the filter. We should get both OffererAddress
        with assert_num_queries(self.num_queries):
            response = response = client.get(f"/offerers/{offerer_id}/addresses")
            assert response.status_code == 200
            assert len(response.json) == 2

    @pytest.mark.usefixtures("db_session")
    @pytest.mark.parametrize("linked_to_venue", [True, False])
    def test_get_offerer_addresses_is_editable(self, client, linked_to_venue):
        user_offerer = offerers_factories.UserOffererFactory()
        pro = user_offerer.user
        offerer = user_offerer.offerer

        offerer_address_1 = offerers_factories.OffererAddressFactory(
            offerer=offerer,
            label="1ere adresse",
            address__street="1 boulevard Poissonnière",
            address__postalCode="75002",
            address__city="Paris",
        )
        offerer_address_2 = offerers_factories.OffererAddressFactory(
            offerer=offerer,
            label="2eme adresse",
            address__street="20 Avenue de Ségur",
            address__postalCode="75007",
            address__city="Paris",
            address__banId="75107_7560_00001",
        )
        offerer_address_3 = offerers_factories.OffererAddressFactory(
            offerer=offerer,
            label="3eme adresse",
            address__street="1 rue de la Paix",
            address__postalCode="75008",
            address__city="Paris",
            address__banId="75108_7560_00000",
        )

        if linked_to_venue:
            offerers_factories.VenueFactory(managingOfferer=offerer, offererAddress=offerer_address_1)
        client = client.with_session_auth(email=pro.email)
        offerer_id = offerer.id
        with assert_num_queries(self.num_queries):
            response = client.get(f"/offerers/{offerer_id}/addresses")
            assert response.status_code == 200
            assert len(response.json) == 3
            assert response.json == [
                {
                    "city": "Paris",
                    "id": offerer_address_1.id,
                    "isEditable": (not linked_to_venue),
                    "label": "1ere adresse",
                    "postalCode": "75002",
                    "street": "1 boulevard Poissonnière",
                },
                {
                    "city": "Paris",
                    "id": offerer_address_2.id,
                    "isEditable": True,
                    "label": "2eme adresse",
                    "postalCode": "75007",
                    "street": "20 Avenue de Ségur",
                },
                {
                    "city": "Paris",
                    "id": offerer_address_3.id,
                    "isEditable": True,
                    "label": "3eme adresse",
                    "postalCode": "75008",
                    "street": "1 rue de la Paix",
                },
            ]


class Return400Test:

    @pytest.mark.usefixtures("db_session")
    def test_access_by_unauthorized_pro_user(self, client):
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        client = client.with_session_auth(email=pro.email)
        offerer_id = offerer.id
        with assert_num_queries(3):
            response = client.get(f"/offerers/{offerer_id}/addresses")
            assert response.status_code == 403
