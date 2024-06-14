import logging

import pytest

import pcapi.core.geography.factories as geography_factories
import pcapi.core.geography.models as geography_models
from pcapi.core.offerers import models as offerers_models
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_settings
import pcapi.core.users.factories as users_factories

from tests.connectors.api_adresse import fixtures


class CreateOffererAddressesTest:
    @pytest.mark.usefixtures("db_session")
    def test_create_offerer_address_with_inexisting_address(self, client):
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        offerer_id = offerer.id

        expected_data = {
            "label": "Ministère de la Culture",
            "banId": "75101_9575_00003",
            "postalCode": "75001",
            "inseeCode": "75056",
            "city": "Paris",
            "street": "3 Rue de Valois",
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
            response = http_client.post(
                f"/offerers/{offerer_id}/addresses/",
                json={
                    "label": expected_data["label"],
                    "street": expected_data["street"],
                    "inseeCode": expected_data["inseeCode"],
                },
            )

        assert response.status_code == 201
        content = response.json
        address = geography_models.Address.query.one()
        assert content["label"] == expected_data["label"]
        assert content["offererId"] == offerer_id
        assert content["address"]["inseeCode"] == expected_data["inseeCode"] == address.inseeCode
        assert content["address"]["street"] == expected_data["street"] == address.street
        assert content["address"]["postalCode"] == expected_data["postalCode"] == address.postalCode
        assert content["address"]["city"] == expected_data["city"] == address.city
        assert content["address"]["latitude"] == expected_data["latitude"] == float(address.latitude)
        assert content["address"]["longitude"] == expected_data["longitude"] == float(address.longitude)

    @pytest.mark.usefixtures("db_session")
    def test_create_offerer_address_with_existing_address(self, client):
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        offerer_id = offerer.id
        expected_data = {
            "banId": "75101_9575_00003",
            "postalCode": "75001",
            "inseeCode": "75056",
            "city": "Paris",
            "street": "3 Rue de Valois",
            "latitude": 48.87171,
            "longitude": 2.30829,
        }

        address = geography_factories.AddressFactory(**expected_data)
        expected_data["label"] = "Ministère de la Culture"
        http_client = client.with_session_auth(pro_user.email)

        # Fetch the session
        # Fetch the user
        # Check permissions
        # Try to insert address & rollback
        # Select address
        # Insert OffererAddress
        # Select OffererAddress & address
        with assert_num_queries(7):
            response = http_client.post(
                f"/offerers/{offerer_id}/addresses/",
                json={
                    "label": expected_data["label"],
                    "street": expected_data["street"],
                    "inseeCode": expected_data["inseeCode"],
                },
            )
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
        assert content["address"]["latitude"] == expected_data["latitude"] == float(address.latitude)
        assert content["address"]["longitude"] == expected_data["longitude"] == float(address.longitude)

    @pytest.mark.usefixtures("db_session")
    def test_create_offerer_address_with_existing_offerer_address(self, client, caplog):
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        offerer_id = offerer.id
        expected_data = {
            "banId": "75101_9575_00003",
            "postalCode": "75001",
            "inseeCode": "75056",
            "city": "Paris",
            "street": "3 Rue de Valois",
            "latitude": 48.87171,
            "longitude": 2.30829,
        }

        address = geography_factories.AddressFactory(**expected_data)
        expected_data["label"] = "Ministère de la Culture"
        offerers_factories.OffererAddressFactory(address=address, offerer=offerer, label="Pass Culture")
        http_client = client.with_session_auth(pro_user.email)

        # Fetch the session
        # Fetch the user
        # Check permissions
        # Try to insert address & rollback
        # Select address
        # Try to insert OffererAddress & rollback
        # Select OffererAddress & address
        with assert_num_queries(7):
            with caplog.at_level(logging.ERROR):
                response = http_client.post(
                    f"/offerers/{offerer_id}/addresses/",
                    json={
                        "label": expected_data["label"],
                        "street": expected_data["street"],
                        "inseeCode": expected_data["inseeCode"],
                    },
                )

        assert not caplog.records

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
        assert content["address"]["latitude"] == expected_data["latitude"] == float(address.latitude)
        assert content["address"]["longitude"] == expected_data["longitude"] == float(address.longitude)

    @pytest.mark.usefixtures("db_session")
    def test_we_are_aware_of_mismatch_coordinates_between_our_data_and_api_addresses_ones(self, client, caplog):
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        offerer_id = offerer.id
        expected_data = {
            "banId": "75101_9575_00003",
            "postalCode": "75001",
            "inseeCode": "75056",
            "city": "Paris",
            "street": "3 Rue de Valois",
            "latitude": 48.97171,  # Mismatch at 0.1 degree
            "longitude": 2.408289,  # Mismatch at 0.1 degree
        }

        address = geography_factories.AddressFactory(**expected_data)
        expected_data["label"] = "Ministère de la Culture"
        offerers_factories.OffererAddressFactory(address=address, offerer=offerer, label="Pass Culture")
        http_client = client.with_session_auth(pro_user.email)

        # Fetch the session
        # Fetch the user
        # Check permissions
        # rollback
        # Select address
        # Select offererAddress if exists
        # Insert offererAddress
        with assert_num_queries(7):
            with caplog.at_level(logging.ERROR):
                http_client.post(
                    f"/offerers/{offerer_id}/addresses/",
                    json={
                        "label": expected_data["label"],
                        "street": expected_data["street"],
                        "inseeCode": expected_data["inseeCode"],
                    },
                )

        assert "Unique constraint over street and inseeCode matched different coordinates" == caplog.records[0].message

    @override_settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
    @pytest.mark.usefixtures("db_session")
    def test_we_dont_want_to_get_false_positive_because_of_rounding(self, client, caplog, requests_mock):
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        offerer_id = offerer.id
        fixture = {
            "type": "FeatureCollection",
            "version": "draft",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [3.106593, 50.64182]},
                    "properties": {
                        "label": "18 Rue Duhesme 75018 Paris",
                        "score": 0.9806027272727271,
                        "housenumber": "18",
                        "id": "75118_2974_00018",
                        "name": "18 Rue Duhesme",
                        "postcode": "75018",
                        "citycode": "75118",
                        "x": 651500.23,
                        "y": 6865844.9,
                        "city": "Paris",
                        "district": "Paris 18e Arrondissement",
                        "context": "75, Paris, Île-de-France",
                        "type": "housenumber",
                        "importance": 0.78663,
                        "street": "Rue Duhesme",
                    },
                }
            ],
            "attribution": "BAN",
            "licence": "ETALAB-2.0",
            "query": "18 rue Duhesme",
            "filters": {"citycode": "75118"},
            "limit": 1,
        }
        expected_data = {
            "banId": "75118_2974_00018",
            "inseeCode": "75118",
            "street": "18 Rue Duhesme",
            "postalCode": "75018",
            "city": "Paris",
            "latitude": 50.641825,
            "longitude": 3.106593,
        }
        requests_mock.get(
            f"""https://api-adresse.data.gouv.fr/search?q={expected_data["street"]}&citycode={expected_data["inseeCode"]}&autocomplete=0&limit=1""",
            json=fixture,
        )

        address = geography_factories.AddressFactory(**expected_data)
        expected_data["label"] = "Ministère de la Culture"
        offerers_factories.OffererAddressFactory(address=address, offerer=offerer, label="Pass Culture")
        http_client = client.with_session_auth(pro_user.email)

        # Fetch the session
        # Fetch the user
        # Check permissions
        # rollback
        # Select address
        # Select offererAddress if exists
        # Insert offererAddress
        with assert_num_queries(7):
            with caplog.at_level(logging.ERROR):
                http_client.post(
                    f"/offerers/{offerer_id}/addresses/",
                    json={
                        "label": expected_data["label"],
                        "street": expected_data["street"],
                        "inseeCode": expected_data["inseeCode"],
                    },
                )

        assert not caplog.records

    @pytest.mark.usefixtures("db_session")
    def test_create_offerer_address_with_existing_offerer_address_and_without_label(self, client):
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        offerer_id = offerer.id
        expected_data = {
            "banId": "75101_9575_00003",
            "postalCode": "75001",
            "inseeCode": "75056",
            "city": "Paris",
            "street": "3 Rue de Valois",
            "latitude": 48.87171,
            "longitude": 2.30829,
        }

        address = geography_factories.AddressFactory(**expected_data)
        expected_data["label"] = None
        pre_existing_oa = offerers_factories.OffererAddressFactory(address=address, offerer=offerer, label=None)
        http_client = client.with_session_auth(pro_user.email)

        # Fetch the session
        # Fetch the user
        # Check permissions
        # Try to insert address & rollback
        # Select address
        # Try to insert OffererAddress & rollback
        # Select OffererAddress & address
        with assert_num_queries(7):
            response = http_client.post(
                f"/offerers/{offerer_id}/addresses/",
                json={
                    "label": expected_data["label"],
                    "street": expected_data["street"],
                    "inseeCode": expected_data["inseeCode"],
                },
            )

        assert response.status_code == 201
        content = response.json
        address = geography_models.Address.query.one()
        offerer_address = offerers_models.OffererAddress.query.one()
        assert offerer_address.id == pre_existing_oa.id
        assert content["label"] == expected_data["label"] == None
        assert content["offererId"] == offerer_id
        assert content["address"]["id"] == address.id
        assert content["address"]["inseeCode"] == expected_data["inseeCode"] == address.inseeCode
        assert content["address"]["street"] == expected_data["street"] == address.street
        assert content["address"]["postalCode"] == expected_data["postalCode"] == address.postalCode
        assert content["address"]["city"] == expected_data["city"] == address.city
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
            "latitude": 48.87171,
            "longitude": 2.30829,
        }

        http_client = client.with_session_auth(pro_user.email)

        # Fetch the session
        # Fetch the user
        # Check permission
        with assert_num_queries(3):
            response = http_client.post(
                f"/offerers/{foreign_offerer_id}/addresses/",
                json={
                    "label": expected_data["label"],
                    "street": expected_data["street"],
                    "inseeCode": expected_data["inseeCode"],
                },
            )

        assert response.status_code == 403
        assert not geography_models.Address.query.count()
        assert not offerers_models.OffererAddress.query.count()

    @override_settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
    @pytest.mark.usefixtures("db_session")
    def test_check_consistency_between_address_and_coordinates(self, client, requests_mock):
        payload = {
            "label": "Label",
            "inseeCode": "75118",
            "street": "18 Rue Duhesme",
        }

        expected_data = {
            "label": "Label",
            "banId": "75118_2974_00018",
            "inseeCode": "75118",
            "street": "18 Rue Duhesme",
            "postalCode": "75018",
            "city": "Paris",
            "latitude": 48.89079,
            "longitude": 2.33856,
        }
        requests_mock.get(
            f"""https://api-adresse.data.gouv.fr/search?q={payload["street"]}&citycode={payload["inseeCode"]}&autocomplete=0&limit=1""",
            json=fixtures.ONE_FEATURE_RESPONSE,
        )
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerer_id = offerer.id
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

        http_client = client.with_session_auth(pro_user.email)

        # Fetch the session
        # Fetch the user
        # Check permissions
        # Insert address
        # Insert OffererAddress
        # Select OffererAddress & address
        with assert_num_queries(6):
            response = http_client.post(
                f"/offerers/{offerer_id}/addresses/",
                json={
                    "label": expected_data["label"],
                    "street": expected_data["street"],
                    "inseeCode": expected_data["inseeCode"],
                },
            )

        assert response.status_code == 201
        content = response.json
        address = geography_models.Address.query.one()
        assert content["label"] == expected_data["label"]
        assert content["offererId"] == offerer_id
        assert content["address"]["inseeCode"] == expected_data["inseeCode"] == address.inseeCode
        assert content["address"]["street"] == expected_data["street"] == address.street
        assert content["address"]["postalCode"] == expected_data["postalCode"] == address.postalCode
        assert content["address"]["city"] == expected_data["city"] == address.city
        assert content["address"]["latitude"] == expected_data["latitude"] == float(address.latitude)
        assert content["address"]["longitude"] == expected_data["longitude"] == float(address.longitude)

    @override_settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
    @pytest.mark.usefixtures("db_session")
    def test_inexisting_address_return_proper_error_message(self, client, requests_mock):
        payload = {
            "label": "Adresse qui n'existe pas",
            "inseeCode": "00000",
            "street": "51 Rue de la Poupée qui tousse",
        }

        requests_mock.get(
            f"""https://api-adresse.data.gouv.fr/search?q={payload["street"]}&citycode={payload["inseeCode"]}&autocomplete=0&limit=1""",
            json=fixtures.NO_FEATURE_RESPONSE,
        )
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerer_id = offerer.id
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

        http_client = client.with_session_auth(pro_user.email)

        # Fetch the session
        # Fetch the user
        # Check permissions
        with assert_num_queries(3):
            response = http_client.post(
                f"/offerers/{offerer_id}/addresses/",
                json={
                    "label": payload["label"],
                    "street": payload["street"],
                    "inseeCode": payload["inseeCode"],
                },
            )
            assert response.status_code == 400

        assert response.json == {"address": "Cette adresse n'existe pas"}
        assert not geography_models.Address.query.all()

    @override_settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
    @pytest.mark.usefixtures("db_session")
    def test_creating_offerer_address_when_only_municipality_centroid_is_the_default(self, client, requests_mock):
        payload = {
            "label": "Centroïde de la commune",
            "inseeCode": "75118",
            "street": "51 Rue de la Poupée qui tousse",
        }

        expected_data = {
            "label": payload["label"],
            "postalCode": "75018",
            "inseeCode": "75118",
            "city": "Paris 18e Arrondissement",
            "latitude": 48.89205,
            "longitude": 2.34868,
        }

        requests_mock.get(
            f"""https://api-adresse.data.gouv.fr/search?q={payload["street"]}&citycode={payload["inseeCode"]}&autocomplete=0&limit=1""",
            json=fixtures.MUNICIPALITY_CENTROID_RESPONSE,
        )
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerer_id = offerer.id
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

        http_client = client.with_session_auth(pro_user.email)

        # Fetch the session
        # Fetch the user
        # Check permissions
        # Insert address
        # Select OffererAddress if exists
        # Insert offererAddress
        with assert_num_queries(6):
            response = http_client.post(
                f"/offerers/{offerer_id}/addresses/",
                json={
                    "label": payload["label"],
                    "street": payload["street"],
                    "inseeCode": payload["inseeCode"],
                },
            )
            assert response.status_code == 201

        content = response.json
        address = geography_models.Address.query.one()
        assert content["label"] == expected_data["label"]
        assert content["offererId"] == offerer_id
        assert content["address"]["inseeCode"] == expected_data["inseeCode"] == address.inseeCode
        assert content["address"]["street"] == address.street == None
        assert content["address"]["postalCode"] == expected_data["postalCode"] == address.postalCode
        assert content["address"]["city"] == expected_data["city"] == address.city
        assert content["address"]["latitude"] == expected_data["latitude"] == float(address.latitude)
        assert content["address"]["longitude"] == expected_data["longitude"] == float(address.longitude)
