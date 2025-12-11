import pytest
import sqlalchemy as sa

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
from pcapi.core.offers import factories
from pcapi.core.testing import assert_num_queries
from pcapi.models import db
from pcapi.utils.date import timespan_str_to_numrange


def setup_auth_client_and_offer(client, ignore_offer=False):
    venue = offerers_factories.VenueFactory()
    offer = None if ignore_offer else factories.ThingOfferFactory(venue=venue)
    user = offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com").user
    auth_client = client.with_session_auth(user.email)
    return auth_client, offer


@pytest.mark.usefixtures("db_session")
class Returns401Test:
    def test_unauthenticated_user_gets_an_error(self, client):
        offer = factories.ThingOfferFactory()
        url = f"/offers/{offer.id}/opening-hours"
        response = client.get(url)
        assert response.status_code == 401


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def test_authenticated_user_but_with_no_rights_on_offer_gets_an_error(self, client):
        auth_client, _ = setup_auth_client_and_offer(client)
        offer = factories.ThingOfferFactory()

        url = f"/offers/{offer.id}/opening-hours"
        response = auth_client.get(url)
        assert response.status_code == 403


@pytest.mark.usefixtures("db_session")
class Returns404Test:
    def test_unknown_offer_returns_an_error(self, client):
        auth_client, _ = setup_auth_client_and_offer(client, ignore_offer=True)
        max_offer_id = db.session.query(sa.func.max(offers_models.Offer.id)).scalar()
        unknown_offer_id = max_offer_id + 1 if max_offer_id is not None else 1

        url = f"/offers/{unknown_offer_id}/opening-hours"
        response = auth_client.get(url)
        assert response.status_code == 404


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_opening_hours_no_existing_hours_returns_empty_week(self, client):
        auth_client, offer = setup_auth_client_and_offer(client)

        url = f"/offers/{offer.id}/opening-hours"
        response = auth_client.get(url)

        assert response.status_code == 200
        assert response.json == {"openingHours": {weekday.value: None for weekday in offerers_models.Weekday}}

    def test_opening_hours_existings_are_returned_with_all_week_days(self, client):
        auth_client, offer = setup_auth_client_and_offer(client)

        opening_hours = timespan_str_to_numrange([("10:00", "12:00"), ("14:00", "18:00")])

        offerers_factories.OpeningHoursFactory(
            venue=None, offer=offer, weekday=offerers_models.Weekday.TUESDAY, timespan=opening_hours
        )

        offerers_factories.OpeningHoursFactory(
            venue=None, offer=offer, weekday=offerers_models.Weekday.WEDNESDAY, timespan=opening_hours
        )

        url = f"/offers/{offer.id}/opening-hours"

        # fetch user_session + user
        # fetch offer with its venue
        # check user has access to offer
        with assert_num_queries(3):
            response = auth_client.get(url)

        assert response.status_code == 200
        assert response.json == {
            "openingHours": {
                **{weekday.value: None for weekday in offerers_models.Weekday},
                "TUESDAY": [["10:00", "12:00"], ["14:00", "18:00"]],
                "WEDNESDAY": [["10:00", "12:00"], ["14:00", "18:00"]],
            }
        }

    def test_opening_hours_every_weekday_has_opening_hours_set_and_all_are_returned(self, client):
        auth_client, offer = setup_auth_client_and_offer(client)
        opening_hours = timespan_str_to_numrange([("10:00", "12:00"), ("14:00", "18:00")])

        for weekday in offerers_models.Weekday:
            offerers_factories.OpeningHoursFactory(venue=None, offer=offer, weekday=weekday, timespan=opening_hours)

        url = f"/offers/{offer.id}/opening-hours"

        # fetch user_session + user
        # fetch offer with its venue
        # check user has access to offer
        with assert_num_queries(3):
            response = auth_client.get(url)

        assert response.status_code == 200
        assert response.json == {
            "openingHours": {
                "MONDAY": [["10:00", "12:00"], ["14:00", "18:00"]],
                "TUESDAY": [["10:00", "12:00"], ["14:00", "18:00"]],
                "WEDNESDAY": [["10:00", "12:00"], ["14:00", "18:00"]],
                "THURSDAY": [["10:00", "12:00"], ["14:00", "18:00"]],
                "FRIDAY": [["10:00", "12:00"], ["14:00", "18:00"]],
                "SATURDAY": [["10:00", "12:00"], ["14:00", "18:00"]],
                "SUNDAY": [["10:00", "12:00"], ["14:00", "18:00"]],
            }
        }
