import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.geography import factories as geography_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import schemas
from pcapi.core.offers import factories as offers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class Return200Test:
    # session + user
    # user_offerer
    # oa retrieving request
    num_queries = 3

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
            address__street="3 rue des moutons",
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

        response = client.with_session_auth(email=pro.email).get(f"/offerers/{offerer.id}/offerer_addresses")

        assert response.status_code == 200
        assert response.json == [
            {
                "city": "Paris",
                "departmentCode": "75",
                "id": offerer_address_1.id,
                "label": "1ere adresse",
                "postalCode": "75002",
                "street": "1 boulevard Poissonnière",
            },
            {
                "city": "Paris",
                "departmentCode": "75",
                "id": offerer_address_2.id,
                "label": "2eme adresse",
                "postalCode": "75007",
                "street": "20 Avenue de Ségur",
            },
            {
                "city": "Paris",
                "departmentCode": "75",
                "id": offerer_address_3.id,
                "label": "3eme adresse",
                "postalCode": "75008",
                "street": "3 rue des moutons",
            },
        ]

    @pytest.mark.parametrize(
        "offer_factory,with_offers_option",
        (
            (offers_factories.OfferFactory, schemas.GetOffererAddressesWithOffersOption.INDIVIDUAL_OFFERS_ONLY),
            (
                educational_factories.CollectiveOfferOnOtherAddressLocationFactory,
                schemas.GetOffererAddressesWithOffersOption.COLLECTIVE_OFFERS_ONLY,
            ),
            (
                educational_factories.CollectiveOfferTemplateOnOtherAddressLocationFactory,
                schemas.GetOffererAddressesWithOffersOption.COLLECTIVE_OFFER_TEMPLATES_ONLY,
            ),
        ),
    )
    def test_get_offerer_addresses_with_offers(self, client, offer_factory, with_offers_option):
        user_offerer = offerers_factories.UserOffererFactory()
        pro = user_offerer.user
        offerer = user_offerer.offerer

        address = geography_factories.AddressFactory(
            street="1 boulevard Poissonnière",
            postalCode="75002",
            city="Paris",
        )
        venue = offerers_factories.VenueFactory(
            managingOfferer=offerer,
            publicName="Venue public name",
            offererAddress__address=address,
        )
        offer_location = offerers_factories.OfferLocationFactory(
            label="1ere adresse", offerer=offerer, venue=venue, address=address
        )
        offerers_factories.OfferLocationFactory(
            offerer=offerer,
            venue=venue,
            label="2eme adresse",
            address__street="20 Avenue de Ségur",
            address__postalCode="75007",
            address__city="Paris",
            address__banId="75107_7560_00001",
        )
        offer_factory(
            venue=venue,
            offererAddress=offer_location,
        )

        client = client.with_session_auth(email=pro.email)
        offerer_id = offerer.id
        offerer_address_id = offer_location.id

        with assert_num_queries(self.num_queries):
            response = client.get(
                f"/offerers/{offerer_id}/offerer_addresses?withOffersOption={with_offers_option.value}"
            )
            assert response.status_code == 200
            assert response.json == [
                {
                    "city": "Paris",
                    "departmentCode": "75",
                    "id": offerer_address_id,
                    "label": "Venue public name",
                    "postalCode": "75002",
                    "street": "1 boulevard Poissonnière",
                },
            ]

        # Try with the same data without the filter. We should get both OffererAddress
        with assert_num_queries(self.num_queries):
            response = client.get(f"/offerers/{offerer_id}/offerer_addresses")
            assert response.status_code == 200
            assert len(response.json) == 2

    def test_get_offerer_addresses_is_editable(self, client):
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

        client = client.with_session_auth(email=pro.email)
        offerer_id = offerer.id
        offerer_address_1_id = offerer_address_1.id
        offerer_address_2_id = offerer_address_2.id
        offerer_address_3_id = offerer_address_3.id
        with assert_num_queries(self.num_queries):
            response = client.get(f"/offerers/{offerer_id}/offerer_addresses")
            assert response.status_code == 200
            assert len(response.json) == 3
            assert response.json == [
                {
                    "city": "Paris",
                    "departmentCode": "75",
                    "id": offerer_address_1_id,
                    "label": "1ere adresse",
                    "postalCode": "75002",
                    "street": "1 boulevard Poissonnière",
                },
                {
                    "city": "Paris",
                    "departmentCode": "75",
                    "id": offerer_address_2_id,
                    "label": "2eme adresse",
                    "postalCode": "75007",
                    "street": "20 Avenue de Ségur",
                },
                {
                    "city": "Paris",
                    "departmentCode": "75",
                    "id": offerer_address_3_id,
                    "label": "3eme adresse",
                    "postalCode": "75008",
                    "street": "1 rue de la Paix",
                },
            ]


class Return400Test:
    def test_access_by_unauthorized_pro_user(self, client):
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        client = client.with_session_auth(email=pro.email)
        offerer_id = offerer.id
        with assert_num_queries(2):
            response = client.get(f"/offerers/{offerer_id}/offerer_addresses")
            assert response.status_code == 403
