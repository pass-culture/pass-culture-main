from flask import g
from flask import url_for
import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.history import models as history_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import factories as users_factories

from tests.conftest import clean_database

from .helpers import html_parser
from .helpers import unauthorized as unauthorized_helpers


pytestmark = [
    pytest.mark.backoffice_v3,
]


class MoveSiretUnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
    endpoint = "backoffice_v3_web.pro_support.move_siret"
    needed_permission = perm_models.Permissions.ADVANCED_PRO_SUPPORT


class PostMoveSiretUnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
    endpoint = "backoffice_v3_web.pro_support.post_move_siret"
    needed_permission = perm_models.Permissions.ADVANCED_PRO_SUPPORT


class ApplyMoveSiretUnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
    endpoint = "backoffice_v3_web.pro_support.apply_move_siret"
    needed_permission = perm_models.Permissions.ADVANCED_PRO_SUPPORT


class MoveSiretTest:
    def _post_request(self, authenticated_client, form: dict, apply: bool):
        form_response = authenticated_client.get(url_for("backoffice_v3_web.pro_support.move_siret"))
        assert form_response.status_code == 200

        if apply:
            endpoint = "backoffice_v3_web.pro_support.apply_move_siret"
        else:
            endpoint = "backoffice_v3_web.pro_support.post_move_siret"

        form["csrf_token"] = g.get("csrf_token", "")
        return authenticated_client.post(url_for(endpoint), form=form)

    @clean_database
    @pytest.mark.parametrize("override_revenue_check", ["", "on"])
    def test_move_siret_ok(self, authenticated_client, override_revenue_check):
        offerer = offerers_factories.OffererFactory(siren="123456789")
        venue1 = offerers_factories.VenueFactory(managingOfferer=offerer, siret="12345678900001")
        venue2 = offerers_factories.VenueFactory(managingOfferer=offerer, siret=None, comment="No SIRET")

        if override_revenue_check:
            rich_beneficiary = users_factories.BeneficiaryGrant18Factory(deposit__amount=100_000)
            bookings_factories.ReimbursedBookingFactory(
                user=rich_beneficiary, stock__price=10800, stock__offer__venue=venue2
            )

        form = {
            "source_venue": str(venue1.id),
            "target_venue": str(venue2.id),
            "siret": venue1.siret,
            "comment": 'lieu public, le SIRET est porté par le "Lieu administratif"',
            "override_revenue_check": override_revenue_check,
        }
        response = self._post_request(authenticated_client, form, False)

        assert response.status_code == 200
        assert venue1.siret == form["siret"]
        assert not venue2.siret
        assert history_models.ActionHistory.query.count() == 0

        response = self._post_request(authenticated_client, form, True)

        assert response.status_code == 303
        assert not venue1.siret
        assert venue1.comment == form["comment"]
        assert venue2.siret == form["siret"]
        assert not venue2.comment

        actions = history_models.ActionHistory.query.all()
        assert len(actions) == 2
        for action in actions:
            assert action.actionType == history_models.ActionType.INFO_MODIFIED
            assert action.offererId == offerer.id
            assert action.venueId in (venue1.id, venue2.id)
            assert action.extraData.get("modified_info")

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
        response = self._post_request(authenticated_client, form, False)
        assert response.status_code == 400
        assert expected_alert in html_parser.extract_alert(response.data)

        response = self._post_request(authenticated_client, form, True)
        assert response.status_code == 400
        assert expected_alert in html_parser.extract_alert(response.data)

        assert source_venue.siret == "12345678900001"
        assert history_models.ActionHistory.query.count() == 0

    @clean_database
    def test_move_siret_same_venue(self, authenticated_client):
        # given
        offerer = offerers_factories.OffererFactory(siren="123456789")
        venue = offerers_factories.VenueFactory(managingOfferer=offerer, siret="12345678900001")

        self._assert_error_400(
            authenticated_client, venue, venue, expected_alert="Les lieux source et destination doivent être différents"
        )

    @clean_database
    def test_move_siret_not_matching_venue(self, authenticated_client):
        # given
        offerer = offerers_factories.OffererFactory(siren="123456789")
        venue1 = offerers_factories.VenueFactory(managingOfferer=offerer, siret="12345678900001")
        venue2 = offerers_factories.VirtualVenueFactory(managingOfferer=offerer, siret=None)

        self._assert_error_400(
            authenticated_client,
            venue1,
            venue2,
            siret="12345678900002",
            expected_alert=f"Le SIRET 12345678900002 ne correspond pas au lieu {venue1.id}",
        )

    @clean_database
    def test_move_siret_virtual_venue(self, authenticated_client):
        offerer = offerers_factories.OffererFactory(siren="123456789")
        venue1 = offerers_factories.VenueFactory(managingOfferer=offerer, siret="12345678900001")
        venue2 = offerers_factories.VirtualVenueFactory(managingOfferer=offerer, siret=None)

        self._assert_error_400(
            authenticated_client,
            venue1,
            venue2,
            expected_alert=f"Le lieu cible {venue2.name} (ID {venue2.id}) est un lieu virtuel",
        )

    @clean_database
    def test_move_siret_different_offerer(self, authenticated_client):
        venue1 = offerers_factories.VenueFactory(siret="12345678900001")
        venue2 = offerers_factories.VenueFactory(siret=None, comment="No SIRET")

        self._assert_error_400(
            authenticated_client,
            venue1,
            venue2,
            expected_alert=f"Source {venue1.id} and target {venue2.id} do not have the same offerer",
        )

    @clean_database
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

    @clean_database
    def test_move_siret_high_revenue(self, authenticated_client):
        offerer = offerers_factories.OffererFactory(siren="123456789")
        venue1 = offerers_factories.VenueFactory(managingOfferer=offerer, siret="12345678900001")
        venue2 = offerers_factories.VenueFactory(managingOfferer=offerer, siret=None, comment="No SIRET")
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
