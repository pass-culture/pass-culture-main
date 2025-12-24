"""Check that one client can create an offer's opening hours

This should only test some relatively basic behaviour:
    * all more complex opening hours creation tests should be done
    by the opening hours api test module
    * all the complex input validation tests should be done by the model
    test module

-> Check that every part seems to work together, there is no need to
go any further.
"""

import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
from pcapi.core.offers import factories
from pcapi.core.testing import assert_num_queries
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


def setup_auth_client_and_offer(client):
    venue = offerers_factories.VenueFactory()
    offer = factories.ThingOfferFactory(venue=venue)
    user = offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com").user
    auth_client = client.with_session_auth(user.email)
    return auth_client, offer


class Returns200Test:
    def test_create_simple_opening_hours_works(self, client):
        auth_client, offer = setup_auth_client_and_offer(client)

        data = {"openingHours": {"MONDAY": [["10:00", "18:00"]]}}
        url = f"/offers/{offer.id}/opening-hours"

        # fetch user_session + user
        # fetch offer with its venue
        # check user has access to offer
        # delete offer's opening hours
        # insert opening hours
        # reload offer (with its opening hours)
        with assert_num_queries(6):
            response = auth_client.patch(url, json=data)

        assert response.status_code == 200
        assert response.json == {
            "openingHours": {
                **{weekday.value: None for weekday in offerers_models.Weekday},
                **data["openingHours"],
            }
        }

        db.session.refresh(offer)

        assert offer.openingHours
        assert len(offer.openingHours) == 1
        assert offer.openingHours[0].weekday == offerers_models.Weekday.MONDAY

        assert len(offer.openingHours[0].timespan) == 1
        timespan = offer.openingHours[0].timespan[0]

        assert timespan.lower == 10 * 60
        assert timespan.upper == 18 * 60

    @pytest.mark.parametrize("opening_hours", [{}, {"MONDAY": None, "TUESDAY": None}])
    def test_empty_opening_hours_is_ok_and_creates_nothing(self, client, opening_hours):
        auth_client, offer = setup_auth_client_and_offer(client)

        data = {"openingHours": opening_hours}
        url = f"/offers/{offer.id}/opening-hours"

        # fetch user_session + user
        # fetch offer with its venue
        # check user has access to offer
        # delete offer's existing opening hours
        # reload offer (with its opening hours)
        with assert_num_queries(5):
            response = auth_client.patch(url, json=data)

        assert response.status_code == 200
        assert response.json == {"openingHours": {weekday.value: None for weekday in offerers_models.Weekday}}


class Returns400Test:
    def test_missing_opening_hours_returns_an_error(self, client):
        auth_client, offer = setup_auth_client_and_offer(client)

        url = f"/offers/{offer.id}/opening-hours"
        response = auth_client.patch(url, json=None)

        assert response.status_code == 400
        assert response.json == {"openingHours": ["Ce champ est obligatoire"]}

    def test_too_many_opening_hours_for_one_day_returns_an_error(self, client):
        auth_client, offer = setup_auth_client_and_offer(client)

        data = {"openingHours": {"MONDAY": [["10:00", "18:00", "21:00"]]}}
        url = f"/offers/{offer.id}/opening-hours"

        response = auth_client.patch(url, json=data)
        assert response.status_code == 400
        assert response.json == {"openingHours.MONDAY.0": ["ensure this value has at most 2 items"]}

    def test_starting_opening_hour_without_an_end_returns_an_error(self, client):
        auth_client, offer = setup_auth_client_and_offer(client)

        data = {"openingHours": {"MONDAY": [["10:00"]]}}
        url = f"/offers/{offer.id}/opening-hours"

        response = auth_client.patch(url, json=data)
        assert response.status_code == 400
        assert response.json == {"openingHours.MONDAY.0": ["ensure this value has at least 2 items"]}

    def test_overlapping_timespans_returns_an_error(self, client):
        auth_client, offer = setup_auth_client_and_offer(client)

        data = {"openingHours": {"MONDAY": [["10:00", "18:00"], ["12:00", "19:00"]]}}
        url = f"/offers/{offer.id}/opening-hours"

        response = auth_client.patch(url, json=data)
        assert response.status_code == 400
        assert response.json == {"openingHours.MONDAY": ["overlapping opening hours: 12:00:00 <> 18:00:00"]}

    def test_unknown_weekday_returns_an_error(self, client):
        auth_client, offer = setup_auth_client_and_offer(client)

        data = {"openingHours": {"OOPS": [["10:00", "18:00"]]}}
        url = f"/offers/{offer.id}/opening-hours"

        response = auth_client.patch(url, json=data)
        assert response.status_code == 400
        assert "openingHours.OOPS" in response.json


class Returns401Test:
    def test_unauthenticated_user_gets_an_error(self, client):
        offer = factories.ThingOfferFactory()

        url = f"/offers/{offer.id}/opening-hours"
        response = client.patch(url, json={"openingHours": {"MONDAY": [["10:00", "18:00"]]}})
        assert response.status_code == 401


class Returns403Test:
    def test_authenticated_user_but_with_no_rights_on_offer_gets_an_error(self, client):
        auth_client, _ = setup_auth_client_and_offer(client)
        offer = factories.ThingOfferFactory()

        url = f"/offers/{offer.id}/opening-hours"
        response = auth_client.patch(url, json={"openingHours": {"MONDAY": [["10:00", "18:00"]]}})
        assert response.status_code == 403


class Returns404Test:
    def test_unknown_offer_returns_an_error(self, client):
        auth_client, _ = setup_auth_client_and_offer(client)

        url = "/offers/-1/opening-hours"
        response = auth_client.patch(url, json={"openingHours": {"MONDAY": [["10:00", "18:00"]]}})
        assert response.status_code == 404
