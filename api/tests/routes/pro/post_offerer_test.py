import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
import pcapi.core.users.factories as users_factories
import pcapi.core.users.testing as users_testing


pytestmark = pytest.mark.usefixtures("db_session")


DEFAULT_DIGITAL_VENUE_LABEL = "Offre numérique"


def test_create_virtual_venue(client):
    # given
    pro = users_factories.ProFactory()
    offerers_factories.VirtualVenueTypeFactory()

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
    assert response.json["siren"] == "418166096"
    assert response.json["name"] == "Test Offerer"
    virtual_venues = list(filter(lambda v: v["isVirtual"], response.json["managedVenues"]))
    assert len(virtual_venues) == 1
    assert len(users_testing.sendinblue_requests) == 1


def test_when_no_address_is_provided(client):
    # given
    pro = users_factories.ProFactory()
    offerers_factories.VirtualVenueTypeFactory()
    body = {"name": "Test Offerer", "siren": "418166096", "postalCode": "93100", "city": "Montreuil"}

    # when
    client = client.with_session_auth(pro.email)
    response = client.post("/offerers", json=body)

    # then
    assert response.status_code == 201
    assert response.json["siren"] == "418166096"
    assert response.json["name"] == "Test Offerer"
    assert len(users_testing.sendinblue_requests) == 1


def test_when_current_user_is_admin(client):
    # Given
    admin = users_factories.AdminFactory()
    offerers_factories.VirtualVenueTypeFactory()
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
    offerers_factories.VirtualVenueTypeFactory()
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


def test_new_user_offerer_has_validation_token(client):
    # Given
    pro = users_factories.ProFactory()
    offerer = offerers_factories.OffererFactory()
    offerers_factories.UserOffererFactory(offerer=offerer, validationToken=None)
    offerers_factories.VirtualVenueTypeFactory()
    body = {
        "name": offerer.name,
        "siren": offerer.siren,
        "address": offerer.address,
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
    assert created_user_offerer.validationToken is not None
