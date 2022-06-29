import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.models.bank_information import BankInformationStatus


pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:
    def test_available_reimbursement_points(self, client):
        user_offerer = offerers_factories.UserOffererFactory(
            user__email="user.pro@example.com",
        )
        offerer = user_offerer.offerer
        offerers_factories.VirtualVenueFactory(managingOfferer=offerer)
        venue_1 = offerers_factories.VenueFactory(managingOfferer=offerer, name="Chez Toto")
        offers_factories.BankInformationFactory(venue=venue_1, status=BankInformationStatus.ACCEPTED)
        venue_2 = offerers_factories.VenueFactory(
            managingOfferer=offerer, name="Dans l'antre de la folie", publicName="Association des démons"
        )
        offers_factories.BankInformationFactory(venue=venue_2, status=BankInformationStatus.ACCEPTED)
        _venue_without_bank_info_nor_siret = offerers_factories.VenueFactory(
            siret=None, comment="Pas de SIRET", managingOfferer=offerer
        )

        client = client.with_session_auth("user.pro@example.com")
        response = client.get(f"/offerers/{offerer.id}/reimbursement-points")

        assert response.status_code == 200
        assert response.json == [
            {
                "venueId": venue_2.id,
                "venueName": "Association des démons",
                "siret": venue_2.siret,
                "iban": venue_2.iban,
                "bic": venue_2.bic,
            },
            {
                "venueId": venue_1.id,
                "venueName": "Chez Toto",
                "siret": venue_1.siret,
                "iban": venue_1.iban,
                "bic": venue_1.bic,
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
        offers_factories.BankInformationFactory(venue=venue_with_pending_bank_info, status=BankInformationStatus.DRAFT)

        client = client.with_session_auth("user.pro@example.com")
        response = client.get(f"/offerers/{offerer.id}/reimbursement-points")

        assert response.status_code == 200
        assert response.json == []
