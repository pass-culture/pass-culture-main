from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

from flask import url_for
import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.permissions.models as perm_models
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_features
from pcapi.models import db
from pcapi.routes.backoffice_v3 import venues

from .helpers import html_parser
from .helpers import unauthorized as unauthorized_helpers


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.fixture(scope="function", name="venue")
def venue_fixture(offerer):  # type: ignore
    venue = offerers_factories.VenueReimbursementPointLinkFactory().venue
    finance_factories.BankInformationFactory(
        venue=venue,
        status=finance_models.BankInformationStatus.ACCEPTED,
    )
    return venue


class GetVenueTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
        endpoint = "backoffice_v3_web.venue.get"
        endpoint_kwargs = {"venue_id": 1}
        needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.get_bank_info_status")
    def test_get_venue(self, bank_info_mock, authenticated_client, venue):  # type: ignore
        bank_info_mock.return_value = {
            "dossier": {
                "state": "en_construction",
                "dateDepot": "2022-09-21T16:30:22+02:00",
            }
        }

        url = url_for("backoffice_v3_web.venue.get", venue_id=venue.id)

        # if venue is not removed from the current session, any get
        # query won't be executed because of this specific testing
        # environment. this would tamper the real database queries
        # count.
        db.session.expire(venue)

        # get session (1 query)
        # get user with profile and permissions (1 query)
        # get FF (1 query)
        # get venue (1 query)
        with assert_num_queries(4):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        assert venue.name in response.data.decode("utf-8")
        response_text = html_parser.content_as_text(response.data)
        assert "Éligible EAC : Non" in response_text
        assert "ID Adage" not in response_text
        assert f"Site web : {venue.contact.website}" in response_text

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_get_venue_with_adage_id(self, authenticated_client):
        venue = offerers_factories.VenueFactory(adageId="7122022", contact=None)

        with assert_no_duplicated_queries():
            response = authenticated_client.get(url_for("backoffice_v3_web.venue.get", venue_id=venue.id))
            assert response.status_code == 200

        response_text = html_parser.content_as_text(response.data)
        assert "Éligible EAC : Oui" in response_text
        assert "ID Adage : 7122022" in response_text


class GetVenueStatsDataTest:
    def test_get_stats_data(
        self,
        venue_with_accepted_bank_info,
        offerer_active_individual_offers,
        offerer_inactive_individual_offers,
        offerer_active_collective_offers,
        offerer_inactive_collective_offers,
    ):
        venue_id = venue_with_accepted_bank_info.id

        with assert_num_queries(2):
            data = venues.get_stats_data(venue_id)

        stats = data.stats

        assert stats.active.individual == 2
        assert stats.active.collective == 4
        assert stats.inactive.individual == 3
        assert stats.inactive.collective == 5
        assert not stats.lastSync.date
        assert not stats.lastSync.provider

    def test_no_offers(self, venue):
        venue_id = venue.id

        with assert_num_queries(2):
            data = venues.get_stats_data(venue_id)

        stats = data.stats

        assert stats.active.individual == 0
        assert stats.active.collective == 0
        assert stats.inactive.individual == 0
        assert stats.inactive.collective == 0
        assert not stats.lastSync.date
        assert not stats.lastSync.provider


class GetVenueStatsTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
        endpoint = "backoffice_v3_web.venue.get_stats"
        endpoint_kwargs = {"venue_id": 1}
        needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_get_stats(self, authenticated_client, venue):
        booking = bookings_factories.BookingFactory(stock__offer__venue=venue)
        url = url_for("backoffice_v3_web.venue.get_stats", venue_id=venue.id)

        # get session (1 query)
        # get user with profile and permissions (1 query)
        # get FF (1 query)
        # get total revenue (1 query)
        # get venue stats (1 query)
        with assert_num_queries(5):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        # cast to integer to avoid errors due to amount formatting
        assert str(int(booking.amount)) in response.data.decode("utf-8")


class HasReimbursementPointTest:
    def test_venue_with_reimbursement_point_links(self, venue):
        assert venues.has_reimbursement_point(venue)

    def test_venue_with_no_current_reimbursement_point_links(self):
        venue = offerers_factories.VenueFactory()

        # starts in 10 days, ends in 100
        offerers_factories.VenueReimbursementPointLinkFactory(
            venue=venue,
            reimbursementPoint=venue,
            timespan=[datetime.utcnow() + timedelta(days=10), datetime.utcnow() + timedelta(days=100)],
        )

        # starts in 100 days and has no end
        offerers_factories.VenueReimbursementPointLinkFactory(
            venue=venue,
            reimbursementPoint=venue,
            timespan=[datetime.utcnow() + timedelta(days=100), None],
        )

        # started 100 days ago, ended 10 days ago
        offerers_factories.VenueReimbursementPointLinkFactory(
            venue=venue,
            reimbursementPoint=venue,
            timespan=[datetime.utcnow() - timedelta(days=100), datetime.utcnow() - timedelta(days=10)],
        )

        assert not venues.has_reimbursement_point(venue)

    def test_venue_with_no_reimbursement_point_links(self):
        venue = offerers_factories.VenueFactory()
        assert not venues.has_reimbursement_point(venue)
