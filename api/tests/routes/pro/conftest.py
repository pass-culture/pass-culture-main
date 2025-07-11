import flask
import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories


@pytest.fixture(name="client_email", scope="module")
def client_email_fixture():
    return "user@example.com"


@pytest.fixture(name="venue")
def venue_fixture():
    return offerers_factories.VenueFactory()


@pytest.fixture(name="offer")
def offer_fixture(venue):
    return factories.ThingOfferFactory(venue=venue)


@pytest.fixture(name="user")
def user_fixture(venue, client_email):
    offerer = venue.managingOfferer
    return offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com").user


@pytest.fixture(name="auth_client")
def auth_client_fixture(client, user):
    return client.with_session_auth(user.email)


class SharedOfferOpeningHoursErrors:
    endpoint = ""

    def test_unknown_offer_returns_an_error(self, auth_client):
        data = {"openingHours": {"MONDAY": [["10:00", "18:00"]]}}
        url = flask.url_for(self.endpoint, offer_id=-1)
        assert auth_client.post(url, json=data).status_code == 404

    def test_unauthenticated_user_gets_an_error(self, client, offer):
        data = {"openingHours": {"MONDAY": [["10:00", "18:00"]]}}
        url = flask.url_for(self.endpoint, offer_id=offer.id)
        assert client.post(url, json=data).status_code == 401

    def test_authenticated_user_but_with_no_rights_on_offer_gets_an_error(self, auth_client):
        offer = factories.ThingOfferFactory()

        data = {"openingHours": {"MONDAY": [["10:00", "18:00"]]}}
        url = flask.url_for(self.endpoint, offer_id=offer.id)

        response = auth_client.post(url, json=data)
        assert response.status_code == 403
