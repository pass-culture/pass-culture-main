from flask import url_for
import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.history import models as history_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import factories as users_factories

from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


class GetMoveSiretTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.move_siret.move_siret"
    needed_permission = perm_models.Permissions.MOVE_SIRET

    def test_get_move_siret(self, authenticated_client):
        response = authenticated_client.get(url_for(self.endpoint))
        assert response.status_code == 200


class MoveSiretTestHelper(PostEndpointHelper):
    def _assert_move_siret_ok_response(self, response):
        raise NotImplementedError()

    @pytest.mark.parametrize("override_revenue_check", ["", "on"])
    def test_move_siret_ok(self, authenticated_client, override_revenue_check):
        self.offerer = offerers_factories.OffererFactory(siren="123456789")
        self.venue1 = offerers_factories.VenueFactory(managingOfferer=self.offerer, siret="12345678900001")
        self.venue2 = offerers_factories.VenueWithoutSiretFactory(managingOfferer=self.offerer)

        if override_revenue_check:
            rich_beneficiary = users_factories.BeneficiaryGrant18Factory(deposit__amount=100_000)
            bookings_factories.ReimbursedBookingFactory(
                user=rich_beneficiary, stock__price=10800, stock__offer__venue=self.venue2
            )

        self.form_data = {
            "source_venue": str(self.venue1.id),
            "target_venue": str(self.venue2.id),
            "siret": self.venue1.siret,
            "comment": 'lieu public, le SIRET est porté par le "Lieu administratif"',
            "override_revenue_check": override_revenue_check,
        }
        response = self.post_to_endpoint(authenticated_client, form=self.form_data)
        self._assert_move_siret_ok_response(response)

    def _assert_error_400(
        self,
        authenticated_client,
        source_venue: offerers_models.Venue,
        target_venue: offerers_models.Venue,
        siret: str | None = None,
        expected_alert: str | None = None,
    ):
        form = {
            "source_venue": str(source_venue.id),
            "target_venue": str(target_venue.id),
            "siret": siret or source_venue.siret,
            "comment": 'lieu public, le SIRET est porté par le "Lieu administratif"',
            "override_revenue_check": "",
        }
        response = self.post_to_endpoint(authenticated_client, form=form)
        assert response.status_code == 400
        assert expected_alert in html_parser.extract_alert(response.data)

        assert source_venue.siret == "12345678900001"
        assert history_models.ActionHistory.query.count() == 0

    def test_move_siret_same_venue(self, authenticated_client):
        # given
        offerer = offerers_factories.OffererFactory(siren="123456789")
        venue = offerers_factories.VenueFactory(managingOfferer=offerer, siret="12345678900001")

        self._assert_error_400(
            authenticated_client, venue, venue, expected_alert="Les lieux source et destination doivent être différents"
        )

    def test_move_siret_not_matching_venue(self, authenticated_client):
        # given
        offerer = offerers_factories.OffererFactory(siren="123456789")
        venue1 = offerers_factories.VenueFactory(managingOfferer=offerer, siret="12345678900001")
        venue2 = offerers_factories.VirtualVenueFactory(managingOfferer=offerer)

        self._assert_error_400(
            authenticated_client,
            venue1,
            venue2,
            siret="12345678900002",
            expected_alert=f"Le SIRET 12345678900002 ne correspond pas au lieu {venue1.id}",
        )

    def test_move_siret_virtual_venue(self, authenticated_client):
        offerer = offerers_factories.OffererFactory(siren="123456789")
        venue1 = offerers_factories.VenueFactory(managingOfferer=offerer, siret="12345678900001")
        venue2 = offerers_factories.VirtualVenueFactory(managingOfferer=offerer)

        self._assert_error_400(
            authenticated_client,
            venue1,
            venue2,
            expected_alert=f"Le lieu cible {venue2.name} (ID {venue2.id}) est un lieu virtuel",
        )

    def test_move_siret_different_offerer(self, authenticated_client):
        venue1 = offerers_factories.VenueFactory(siret="12345678900001")
        venue2 = offerers_factories.VenueWithoutSiretFactory()

        self._assert_error_400(
            authenticated_client,
            venue1,
            venue2,
            expected_alert=f"Source {venue1.id} and target {venue2.id} do not have the same offerer",
        )

    def test_move_siret_target_with_siret(self, authenticated_client):
        offerer = offerers_factories.OffererFactory(siren="123456789")
        venue1 = offerers_factories.VenueFactory(managingOfferer=offerer, siret="12345678900001")
        venue2 = offerers_factories.VenueFactory(managingOfferer=offerer, siret="12345678900003")

        self._assert_error_400(
            authenticated_client,
            venue1,
            venue2,
            expected_alert=f"Target venue {venue2.id} already has a siret: {venue2.siret}",
        )

    def test_move_siret_high_revenue(self, authenticated_client):
        offerer = offerers_factories.OffererFactory(siren="123456789")
        venue1 = offerers_factories.VenueFactory(managingOfferer=offerer, siret="12345678900001")
        venue2 = offerers_factories.VenueWithoutSiretFactory(managingOfferer=offerer)
        rich_beneficiary = users_factories.BeneficiaryGrant18Factory(deposit__amount=100_000)
        bookings_factories.ReimbursedBookingFactory(
            user=rich_beneficiary, stock__price=10200, stock__offer__venue=venue2
        )

        self._assert_error_400(
            authenticated_client,
            venue1,
            venue2,
            expected_alert=f"Target venue has an unexpectedly high yearly revenue: {10200.00}",
        )


class PostMoveSiretTest(MoveSiretTestHelper):
    endpoint = "backoffice_v3_web.move_siret.post_move_siret"
    needed_permission = perm_models.Permissions.MOVE_SIRET

    def _assert_move_siret_ok_response(self, response):
        assert response.status_code == 200
        assert self.venue1.siret == self.form_data["siret"]
        assert not self.venue2.siret
        assert history_models.ActionHistory.query.count() == 0


class ApplyMoveSiretTest(MoveSiretTestHelper):
    endpoint = "backoffice_v3_web.move_siret.apply_move_siret"
    needed_permission = perm_models.Permissions.MOVE_SIRET

    def _assert_move_siret_ok_response(self, response):
        assert response.status_code == 303
        assert not self.venue1.siret
        assert self.venue1.comment == self.form_data["comment"]
        assert self.venue2.siret == self.form_data["siret"]
        assert not self.venue2.comment

        actions = history_models.ActionHistory.query.all()
        assert len(actions) == 2
        for action in actions:
            assert action.actionType == history_models.ActionType.INFO_MODIFIED
            assert action.offererId == self.offerer.id
            assert action.venueId in (self.venue1.id, self.venue2.id)
            assert action.extraData.get("modified_info")

    @pytest.mark.skip("TODO: fix issue with test 'A transaction is already begun on this Session.'")
    def test_move_siret_ok(self, authenticated_client, override_revenue_check):
        pass
