import pytest

from pcapi.core.offers.factories import OfferFactory
from pcapi.scripts.batch_update_offer_withdrawal_details_for_offerer import (
    batch_update_offer_withdrawal_details_for_offerer,
)


@pytest.mark.usefixtures("db_session")
class BatchUpdateOfferWithdrawalDetailsForOffererTest:
    def should_update_offer_withdrawal_details(self):
        # Given
        new_withdrawals_details = "Some withdrawal informations"
        active_offer_1 = OfferFactory(isActive=True)
        active_offer_2 = OfferFactory(isActive=True, venue=active_offer_1.venue)
        inactive_offer = OfferFactory(isActive=False, venue=active_offer_1.venue)
        different_offerer_offer = OfferFactory()

        # When
        batch_update_offer_withdrawal_details_for_offerer(
            active_offer_1.venue.managingOffererId, new_withdrawals_details, 1
        )

        # Then
        assert active_offer_1.withdrawalDetails == new_withdrawals_details
        assert active_offer_2.withdrawalDetails == new_withdrawals_details
        assert inactive_offer.withdrawalDetails is None
        assert different_offerer_offer.withdrawalDetails is None
