import pytest

import pcapi.core.geography.factories as geography_factories
import pcapi.core.geography.models as geography_models
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.testing import assert_num_queries
import pcapi.core.users.factories as users_factories


class CreateOffererAddressesTest:
    @pytest.mark.usefixtures("db_session")
    def test_create_offerer_address_with_inexisting_address(self, client):
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        offerer_id = offerer.id

        expected_data = {
            "label": "Pass Culture",
            "banId": "75108_5194_00089",
            "inseeCode": "75108",
            "street": "89 Rue de la Boétie",
            "postalCode": "75008",
            "city": "Paris",
            "country": "France",
            "latitude": 48.87171,
            "longitude": 2.30829,
        }

        http_client = client.with_session_auth(pro_user.email)

        # Fetch the session
        # Fetch the user
        # Check permissions
        # Insert address
        # Insert OffererAddress
        # Select OffererAddress & address
        with assert_num_queries(6):
            response = http_client.post(f"/offerers/{offerer_id}/addresses/", json=expected_data)

        assert response.status_code == 201
        content = response.json
        address = geography_models.Address.query.one()
        assert content["label"] == expected_data["label"]
        assert content["offererId"] == offerer_id
        assert content["address"]["inseeCode"] == expected_data["inseeCode"] == address.inseeCode
        assert content["address"]["street"] == expected_data["street"] == address.street
        assert content["address"]["postalCode"] == expected_data["postalCode"] == address.postalCode
        assert content["address"]["city"] == expected_data["city"] == address.city
        assert content["address"]["country"] == expected_data["country"] == address.country
        assert content["address"]["latitude"] == expected_data["latitude"] == float(address.latitude)
        assert content["address"]["longitude"] == expected_data["longitude"] == float(address.longitude)

    @pytest.mark.usefixtures("db_session")
    def test_create_offerer_address_with_existing_address(self, client):
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        offerer_id = offerer.id
        expected_data = {
            "label": "Pass Culture",
            "banId": "75108_5194_00089",
            "inseeCode": "75108",
            "street": "89 Rue de la Boétie",
            "postalCode": "75008",
            "city": "Paris",
            "country": "France",
            "latitude": 48.87171,
            "longitude": 2.30829,
        }

        address = geography_factories.AddressFactory(
            **{
                "banId": "75108_5194_00089",
                "inseeCode": "75108",
                "street": "89 Rue de la Boétie",
                "postalCode": "75008",
                "city": "Paris",
                "country": "France",
                "latitude": 48.87171,
                "longitude": 2.308289,
            }
        )
        http_client = client.with_session_auth(pro_user.email)

        # Fetch the session
        # Fetch the user
        # Check permissions
        # Try to insert address & rollback
        # Select address
        # Insert OffererAddress
        # Select OffererAddress & address
        with assert_num_queries(7):
            response = http_client.post(f"/offerers/{offerer_id}/addresses/", json=expected_data)

        assert response.status_code == 201
        content = response.json
        address = geography_models.Address.query.one()
        assert content["label"] == expected_data["label"]
        assert content["offererId"] == offerer_id
        assert content["address"]["id"] == address.id
        assert content["address"]["inseeCode"] == expected_data["inseeCode"] == address.inseeCode
        assert content["address"]["street"] == expected_data["street"] == address.street
        assert content["address"]["postalCode"] == expected_data["postalCode"] == address.postalCode
        assert content["address"]["city"] == expected_data["city"] == address.city
        assert content["address"]["country"] == expected_data["country"] == address.country
        assert content["address"]["latitude"] == expected_data["latitude"] == float(address.latitude)
        assert content["address"]["longitude"] == expected_data["longitude"] == float(address.longitude)

    @pytest.mark.usefixtures("db_session")
    def test_create_offerer_address_with_existing_existing_offerer_address(self, client):
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        offerer_id = offerer.id
        expected_data = {
            "label": "Pass Culture",
            "banId": "75108_5194_00089",
            "inseeCode": "75108",
            "street": "89 Rue de la Boétie",
            "postalCode": "75008",
            "city": "Paris",
            "country": "France",
            "latitude": 48.87171,
            "longitude": 2.30829,
        }

        address = geography_factories.AddressFactory(
            **{
                "banId": "75108_5194_00089",
                "inseeCode": "75108",
                "street": "89 Rue de la Boétie",
                "postalCode": "75008",
                "city": "Paris",
                "country": "France",
                "latitude": 48.87171,
                "longitude": 2.308289,
            }
        )
        geography_factories.OffererAddressFactory(addressId=address.id, offererId=offerer_id, label="Pass Culture")
        http_client = client.with_session_auth(pro_user.email)

        # Fetch the session
        # Fetch the user
        # Check permissions
        # Try to insert address & rollback
        # Select address
        # Try to insert OffererAddress & rollback
        # Select OffererAddress & address
        with assert_num_queries(7):
            response = http_client.post(f"/offerers/{offerer_id}/addresses/", json=expected_data)

        assert response.status_code == 201
        content = response.json
        address = geography_models.Address.query.one()
        assert content["label"] == expected_data["label"]
        assert content["offererId"] == offerer_id
        assert content["address"]["id"] == address.id
        assert content["address"]["inseeCode"] == expected_data["inseeCode"] == address.inseeCode
        assert content["address"]["street"] == expected_data["street"] == address.street
        assert content["address"]["postalCode"] == expected_data["postalCode"] == address.postalCode
        assert content["address"]["city"] == expected_data["city"] == address.city
        assert content["address"]["country"] == expected_data["country"] == address.country
        assert content["address"]["latitude"] == expected_data["latitude"] == float(address.latitude)
        assert content["address"]["longitude"] == expected_data["longitude"] == float(address.longitude)

    @pytest.mark.usefixtures("db_session")
    def test_user_cant_create_offerer_address_on_foreign_offerer(self, client):
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        foreign_offerer = offerers_factories.OffererFactory()
        foreign_offerer_id = foreign_offerer.id

        expected_data = {
            "label": "Label",
            "banId": "75108_5194_00089",
            "inseeCode": "75108",
            "street": "89 Rue de la Boétie",
            "postalCode": "75008",
            "city": "Paris",
            "country": "France",
            "latitude": 48.87171,
            "longitude": 2.308289,
        }

        http_client = client.with_session_auth(pro_user.email)

        with assert_num_queries(4):
            response = http_client.post(f"/offerers/{foreign_offerer_id}/addresses/", json=expected_data)

        assert response.status_code == 403
        assert not geography_models.Address.query.count()
        assert not geography_models.OffererAddress.query.count()
