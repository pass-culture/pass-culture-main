import pytest

from pcapi.core import testing
import pcapi.core.finance.factories as finance_factories
from pcapi.core.finance.models import BankInformationStatus
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.testing import override_features


pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:
    @pytest.mark.skip("Keep single function WIP_ENABLE_NEW_ONBOARDING FF is removed")
    def test_available_reimbursement_points_sorted_by_common_name(self, client):
        user_offerer = offerers_factories.UserOffererFactory(
            user__email="user.pro@example.com",
        )
        offerer = user_offerer.offerer
        offerers_factories.VirtualVenueFactory(managingOfferer=offerer)
        first_venue = offerers_factories.VenueFactory(
            managingOfferer=offerer,
            name="Raison sociale A",
            publicName="Nom public F",
        )
        finance_factories.BankInformationFactory(venue=first_venue, status=BankInformationStatus.ACCEPTED)
        second_venue = offerers_factories.VenueFactory(
            managingOfferer=offerer,
            name="Raison sociale B",
            publicName="Nom public D",
        )
        finance_factories.BankInformationFactory(venue=second_venue, status=BankInformationStatus.ACCEPTED)
        offerers_factories.VenueWithoutSiretFactory(managingOfferer=offerer)

        client = client.with_session_auth("user.pro@example.com")

        with testing.assert_no_duplicated_queries():
            response = client.get(f"/offerers/{offerer.id}/reimbursement-points")

        assert response.status_code == 200
        assert response.json == [
            {
                "venueId": second_venue.id,
                "venueName": "Nom public D",
                "iban": second_venue.iban,
            },
            {
                "venueId": first_venue.id,
                "venueName": "Nom public F",
                "iban": first_venue.iban,
            },
        ]

    @override_features(WIP_ENABLE_NEW_ONBOARDING=False)
    def test_available_reimbursement_points_sorted_by_common_name_legacy(self, client):
        self.test_available_reimbursement_points_sorted_by_common_name(client)

    @override_features(WIP_ENABLE_NEW_ONBOARDING=True)
    def test_available_reimbursement_points_sorted_by_common_name_new_onboarding(self, client):
        self.test_available_reimbursement_points_sorted_by_common_name(client)

    @pytest.mark.skip("Keep single function when WIP_ENABLE_NEW_ONBOARDING FF is removed")
    def test_no_available_reimbursement_point(self, client):
        user_offerer = offerers_factories.UserOffererFactory(
            user__email="user.pro@example.com",
        )
        offerer = user_offerer.offerer
        offerers_factories.VirtualVenueFactory(managingOfferer=offerer)
        _venue_without_siret_nor_bank_info = offerers_factories.VenueWithoutSiretFactory(managingOfferer=offerer)
        venue_with_pending_bank_info = offerers_factories.VenueFactory(managingOfferer=offerer)
        finance_factories.BankInformationFactory(venue=venue_with_pending_bank_info, status=BankInformationStatus.DRAFT)

        client = client.with_session_auth("user.pro@example.com")
        response = client.get(f"/offerers/{offerer.id}/reimbursement-points")

        assert response.status_code == 200
        assert response.json == []

    @override_features(WIP_ENABLE_NEW_ONBOARDING=False)
    def test_no_available_reimbursement_point_legacy(self, client):
        self.test_no_available_reimbursement_point(client)

    @override_features(WIP_ENABLE_NEW_ONBOARDING=True)
    def test_no_available_reimbursement_point_new_onboarding(self, client):
        self.test_no_available_reimbursement_point(client)
