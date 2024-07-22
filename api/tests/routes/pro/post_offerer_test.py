from datetime import datetime

import pytest

import pcapi.core.history.models as history_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
from pcapi.core.testing import override_settings
import pcapi.core.users.factories as users_factories
import pcapi.core.users.testing as users_testing
from pcapi.models.validation_status_mixin import ValidationStatus

from tests.connectors import sirene_test_data


pytestmark = pytest.mark.usefixtures("db_session")


DEFAULT_DIGITAL_VENUE_LABEL = "Offre numérique"


def test_create_virtual_venue(client):
    # given
    pro = users_factories.ProFactory(
        lastConnectionDate=datetime.utcnow(),
    )

    body = {
        "name": "MINISTERE DE LA CULTURE",
        "siren": "418166096",
        "address": "123 rue de Paris",
        "postalCode": "93100",
        "city": "Montreuil",
    }

    # when
    client = client.with_session_auth(pro.email)
    response = client.post("/offerers", json=body)

    # then
    assert response.status_code == 201
    assert response.json["siren"] == "418166096"
    assert response.json["name"] == "MINISTERE DE LA CULTURE"
    virtual_venues = offerers_models.Venue.query.filter(offerers_models.Venue.isVirtual == True).all()
    assert len(virtual_venues) == 1
    assert len(users_testing.sendinblue_requests) == 1


def test_returned_data(client):
    pro = users_factories.ProFactory()

    body = {
        "name": "MINISTERE DE LA CULTURE",
        "siren": "418166096",
        "address": "123 rue de Paris",
        "postalCode": "93100",
        "city": "Montreuil",
    }

    client = client.with_session_auth(pro.email)
    response = client.post("/offerers", json=body)

    created_offerer = offerers_models.Offerer.query.one()
    assert response.json == {
        "id": created_offerer.id,
        "siren": "418166096",
        "name": "MINISTERE DE LA CULTURE",
    }


def test_user_cant_create_same_offerer_twice(client):
    pro = users_factories.ProFactory()

    body = {
        "name": "MINISTERE DE LA CULTURE",
        "siren": "418166096",
        "address": "123 rue de Paris",
        "postalCode": "93100",
        "city": "Montreuil",
    }

    client = client.with_session_auth(pro.email)
    first_response = client.post("/offerers", json=body)

    created_offerer = offerers_models.Offerer.query.one()
    assert first_response.json == {
        "id": created_offerer.id,
        "siren": "418166096",
        "name": "MINISTERE DE LA CULTURE",
    }

    second_response = client.post("/offerers", json=body)

    assert second_response.status_code == 400
    assert "This user already belongs to this offerer" in str(second_response.data)


def test_when_no_address_is_provided(client):
    # given
    pro = users_factories.ProFactory(
        lastConnectionDate=datetime.utcnow(),
    )
    body = {"name": "Test Offerer", "siren": "418166096", "postalCode": "93100", "city": "Montreuil"}

    # when
    client = client.with_session_auth(pro.email)
    response = client.post("/offerers", json=body)

    # then
    assert response.status_code == 201
    assert response.json["siren"] == "418166096"
    assert response.json["name"] == "MINISTERE DE LA CULTURE"
    assert len(users_testing.sendinblue_requests) == 1


def test_use_offerer_name_retrieved_from_sirene_api(client):
    pro = users_factories.ProFactory()
    body = {
        "name": "Manually edited name",
        "siren": "418166096",
        "address": "123 rue de Paris",
        "postalCode": "93100",
        "city": "Montreuil",
    }
    client = client.with_session_auth(pro.email)
    response = client.post("/offerers", json=body)

    offerers_models.Offerer.query.one()
    assert response.status_code == 201
    assert response.json["siren"] == "418166096"
    assert response.json["name"] == "MINISTERE DE LA CULTURE"


def test_when_current_user_is_admin(client):
    # Given
    admin = users_factories.AdminFactory()
    body = {
        "name": "Test Offerer",
        "siren": "418166096",
        "address": "123 rue de Paris",
        "postalCode": "93100",
        "city": "Montreuil",
    }

    # When
    client = client.with_session_auth(admin.email)
    response = client.post("/offerers", json=body)

    # then
    assert response.status_code == 201


def test_current_user_has_access_to_created_offerer(client):
    # Given
    pro = users_factories.ProFactory()
    body = {
        "name": "Test Offerer",
        "siren": "418166096",
        "address": "123 rue de Paris",
        "postalCode": "93100",
        "city": "Montreuil",
    }

    # when
    client = client.with_session_auth(pro.email)
    response = client.post("/offerers", json=body)

    # then
    assert response.status_code == 201
    offerer = offerers_models.Offerer.query.one()
    assert offerer.UserOfferers[0].user == pro


def test_new_user_offerer_has_validation_status_new(client):
    # Given
    pro = users_factories.ProFactory()
    offerer = offerers_factories.OffererFactory()
    offerers_factories.UserOffererFactory(offerer=offerer)
    body = {
        "name": offerer.name,
        "siren": offerer.siren,
        "street": offerer.street,
        "postalCode": offerer.postalCode,
        "city": offerer.city,
    }

    # when
    client = client.with_session_auth(pro.email)
    response = client.post("/offerers", json=body)

    # then
    assert response.status_code == 201
    offerer = offerers_models.Offerer.query.one()
    created_user_offerer = offerers_models.UserOfferer.query.filter_by(offerer=offerer, user=pro).one()
    assert created_user_offerer.validationStatus == ValidationStatus.NEW


def test_create_offerer_action_is_logged(client):
    # given
    user = users_factories.UserFactory()

    body = {
        "name": "Test Offerer",
        "siren": "418166096",
        "address": "123 rue de Paris",
        "postalCode": "93100",
        "city": "Montreuil",
    }

    # when
    client = client.with_session_auth(user.email)
    response = client.post("/offerers", json=body)

    # then
    assert response.status_code == 201
    action = history_models.ActionHistory.query.one()
    assert action.actionType == history_models.ActionType.OFFERER_NEW
    assert action.authorUser == user
    assert action.user == user
    assert action.offererId == response.json["id"]


@override_settings(SIRENE_BACKEND="pcapi.connectors.entreprise.backends.insee.InseeBackend")
def test_with_inactive_siren(requests_mock, client):
    siren = "123456789"
    requests_mock.get(
        f"https://api.insee.fr/entreprises/sirene/V3.11/siren/{siren}",
        json=sirene_test_data.RESPONSE_SIREN_INACTIVE_COMPANY,
    )
    requests_mock.get(
        f"https://api.insee.fr/entreprises/sirene/V3.11/siret/{siren}00018",
        json=sirene_test_data.RESPONSE_SIRET_INACTIVE_COMPANY,
    )
    user = users_factories.UserFactory()

    body = {
        "name": "Test Offerer",
        "siren": siren,
        "address": "123 rue de Paris",
        "postalCode": "93100",
        "city": "Montreuil",
    }

    client = client.with_session_auth(user.email)
    response = client.post("/offerers", json=body)

    assert response.status_code == 400
    assert response.json["siren"] == ["SIREN is no longer active"]


@pytest.mark.usefixtures("db_session")
@override_settings(SIRENE_BACKEND="pcapi.connectors.entreprise.backends.insee.InseeBackend")
def test_saint_martin_offerer_creation_without_postal_code_is_successfull(requests_mock, client):
    siren = "123456789"
    requests_mock.get(
        f"https://api.insee.fr/entreprises/sirene/V3.11/siren/{siren}",
        json=sirene_test_data.RESPONSE_SIREN_SAINT_MARTIN_COMPANY_WITHOUT_POSTAL_CODE,
    )
    requests_mock.get(
        f"https://api.insee.fr/entreprises/sirene/V3.11/siret/{siren}00011",
        json=sirene_test_data.RESPONSE_SIRET_SAINT_MARTIN_COMPANY_WITHOUT_POSTAL_CODE,
    )
    user = users_factories.ProFactory()

    body = {
        "address": "RUE DE SAINT MARTIN",
        "city": "SAINT-MARTIN",
        "name": "ENTREPRISE SANS CODE POSTAL",
        "postalCode": "",
        "siren": siren,
        "apeCode": "94.99Z",
    }

    client = client.with_session_auth(user.email)
    response = client.post("/offerers", json=body)

    assert response.status_code == 201

    offerer = offerers_models.Offerer.query.one()
    assert offerer.postalCode == "97150"
