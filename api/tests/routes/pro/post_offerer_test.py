import json
from datetime import datetime

import pytest

import pcapi.core.history.models as history_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
import pcapi.core.users.factories as users_factories
import pcapi.core.users.testing as users_testing
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.models.validation_status_mixin import ValidationStatus

from tests.connectors import sirene_test_data


pytestmark = pytest.mark.usefixtures("db_session")


DEFAULT_DIGITAL_VENUE_LABEL = "Offre numérique"


def test_returned_data(client):
    pro = users_factories.ProFactory()

    body = {
        "name": "MINISTERE DE LA CULTURE",
        "siren": "418166096",
        "address": "123 rue de Paris",
        "postalCode": "93100",
        "city": "Montreuil",
        "latitude": 48,
        "longitude": 2,
    }

    client = client.with_session_auth(pro.email)
    response = client.post("/offerers", json=body)

    created_offerer = db.session.query(offerers_models.Offerer).one()
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
        "latitude": 48,
        "longitude": 2,
    }

    client = client.with_session_auth(pro.email)
    first_response = client.post("/offerers", json=body)

    created_offerer = db.session.query(offerers_models.Offerer).one()
    assert first_response.json == {
        "id": created_offerer.id,
        "siren": "418166096",
        "name": "MINISTERE DE LA CULTURE",
    }

    second_response = client.post("/offerers", json=body)

    assert second_response.status_code == 400
    response_json = json.loads(second_response.data.decode())
    assert "Votre compte est déjà rattaché à cette structure." in response_json["user_offerer"][0]


def test_user_can_create_rejected_offerer_again(client):
    pro = users_factories.ProFactory()
    rejected_offerer = offerers_factories.RejectedOffererFactory(siren="418166096")
    user_offerer = offerers_factories.RejectedUserOffererFactory(user=pro, offerer=rejected_offerer)

    body = {
        "name": "MINISTERE DE LA CULTURE",
        "siren": "418166096",
        "address": "123 rue de Paris",
        "postalCode": "93100",
        "city": "Montreuil",
        "latitude": 48,
        "longitude": 2,
    }

    client = client.with_session_auth(pro.email)
    response = client.post("/offerers", json=body)

    assert response.status_code == 201
    assert rejected_offerer.isNew
    assert user_offerer.isValidated


@pytest.mark.features(WIP_2025_SIGN_UP=True)
def test_user_can_create_offerer_with_phone_number(client):
    pro = users_factories.ProFactory(phoneNumber=None)

    body = {
        "name": "MINISTERE DE LA CULTURE",
        "siren": "418166096",
        "address": "123 rue de Paris",
        "postalCode": "93100",
        "city": "Montreuil",
        "latitude": 48,
        "longitude": 2,
        "phoneNumber": "0123456789",
    }

    assert not pro.phoneNumber

    client = client.with_session_auth(pro.email)
    response = client.post("/offerers", json=body)

    created_offerer = db.session.query(offerers_models.Offerer).one()
    assert response.json == {
        "id": created_offerer.id,
        "siren": "418166096",
        "name": "MINISTERE DE LA CULTURE",
    }

    pro = db.session.query(users_models.User).filter_by(id=pro.id).one()
    assert pro.phoneNumber == "+33123456789"


def test_when_no_address_is_provided(client):
    # given
    pro = users_factories.ProFactory(
        lastConnectionDate=datetime.utcnow(),
    )
    body = {
        "name": "Test Offerer",
        "siren": "418166096",
        "postalCode": "93100",
        "city": "Montreuil",
        "latitude": 48,
        "longitude": 2,
    }

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
        "latitude": 48,
        "longitude": 2,
    }
    client = client.with_session_auth(pro.email)
    response = client.post("/offerers", json=body)

    db.session.query(offerers_models.Offerer).one()
    assert response.status_code == 201
    assert response.json["siren"] == "418166096"
    assert response.json["name"] == "MINISTERE DE LA CULTURE"


def test_current_user_has_access_to_created_offerer(client):
    # Given
    pro = users_factories.ProFactory()
    body = {
        "name": "Test Offerer",
        "siren": "418166096",
        "address": "123 rue de Paris",
        "postalCode": "93100",
        "city": "Montreuil",
        "latitude": 48,
        "longitude": 2,
    }

    # when
    client = client.with_session_auth(pro.email)
    response = client.post("/offerers", json=body)

    # then
    assert response.status_code == 201
    offerer = db.session.query(offerers_models.Offerer).one()
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
        "latitude": 48,
        "longitude": 2,
    }

    # when
    client = client.with_session_auth(pro.email)
    response = client.post("/offerers", json=body)

    # then
    assert response.status_code == 201
    offerer = db.session.query(offerers_models.Offerer).one()
    created_user_offerer = db.session.query(offerers_models.UserOfferer).filter_by(offerer=offerer, user=pro).one()
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
        "latitude": 48,
        "longitude": 2,
    }

    # when
    client = client.with_session_auth(user.email)
    response = client.post("/offerers", json=body)

    # then
    assert response.status_code == 201
    action = db.session.query(history_models.ActionHistory).one()
    assert action.actionType == history_models.ActionType.OFFERER_NEW
    assert action.authorUser == user
    assert action.user == user
    assert action.offererId == response.json["id"]


@pytest.mark.settings(SIRENE_BACKEND="pcapi.connectors.entreprise.backends.insee.InseeBackend")
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
        "latitude": 48,
        "longitude": 2,
    }

    client = client.with_session_auth(user.email)
    response = client.post("/offerers", json=body)

    assert response.status_code == 400
    assert response.json["siren"] == ["SIREN is no longer active"]


@pytest.mark.usefixtures("db_session")
@pytest.mark.settings(SIRENE_BACKEND="pcapi.connectors.entreprise.backends.insee.InseeBackend")
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
        "latitude": 48,
        "longitude": 2,
    }

    client = client.with_session_auth(user.email)
    response = client.post("/offerers", json=body)

    assert response.status_code == 201

    offerer = db.session.query(offerers_models.Offerer).one()
    assert offerer.postalCode == "97150"
