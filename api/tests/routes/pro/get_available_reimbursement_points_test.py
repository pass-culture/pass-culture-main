import pytest

from pcapi.core import testing
import pcapi.core.finance.factories as finance_factories
from pcapi.core.finance.models import BankInformationStatus
import pcapi.core.offerers.factories as offerers_factories


pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:
    def test_available_reimbursement_points(self, client):
        user_offerer = offerers_factories.UserOffererFactory(
            user__email="user.pro@example.com",
        )
        offerer = user_offerer.offerer
        offerers_factories.VirtualVenueFactory(managingOfferer=offerer)
        venue_with_siret = offerers_factories.VenueFactory(managingOfferer=offerer, name="Chez Toto")
        finance_factories.BankInformationFactory(venue=venue_with_siret, status=BankInformationStatus.ACCEPTED)
        venue_without_siret = offerers_factories.VenueFactory(
            siret=None,
            comment="Ceci est une collectivité locale",
            managingOfferer=offerer,
            name="Dans l'antre de la folie",
            publicName="Association des démons",
        )
        finance_factories.BankInformationFactory(venue=venue_without_siret, status=BankInformationStatus.ACCEPTED)
        _venue_without_bank_info_nor_siret = offerers_factories.VenueFactory(
            siret=None, comment="Pas de SIRET", managingOfferer=offerer
        )

        client = client.with_session_auth("user.pro@example.com")
        n_queries = (
            testing.AUTHENTICATION_QUERIES
            + 1  # check_user_has_access_to_offerer
            + 1  # eligible Venues with their eagerly loaded BankInformation
        )
        with testing.assert_num_queries(n_queries):
            response = client.get(f"/offerers/{offerer.id}/reimbursement-points")

        assert response.status_code == 200
        assert response.json == [
            {
                "venueId": venue_without_siret.id,
                "venueName": "Association des démons",
                "iban": venue_without_siret.iban,
            },
            {
                "venueId": venue_with_siret.id,
                "venueName": "Chez Toto",
                "iban": venue_with_siret.iban,
            },
        ]

    def test_no_available_reimbursement_point(self, client):
        user_offerer = offerers_factories.UserOffererFactory(
            user__email="user.pro@example.com",
        )
        offerer = user_offerer.offerer
        offerers_factories.VirtualVenueFactory(managingOfferer=offerer)
        _venue_without_siret_nor_bank_info = offerers_factories.VenueFactory(
            siret=None, comment="Pas de SIRET", managingOfferer=offerer
        )
        venue_with_pending_bank_info = offerers_factories.VenueFactory(managingOfferer=offerer)
        finance_factories.BankInformationFactory(venue=venue_with_pending_bank_info, status=BankInformationStatus.DRAFT)

        client = client.with_session_auth("user.pro@example.com")
        response = client.get(f"/offerers/{offerer.id}/reimbursement-points")

        assert response.status_code == 200
        assert response.json == []
