import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.workers.update_all_venue_offers_withdrawal_details_job import update_all_venue_offers_withdrawal_details_job


@pytest.mark.usefixtures("db_session")
def test_update_all_venue_offers_withdrawal_details_job_test():
    venue = offerers_factories.VenueFactory()
    offer1 = offers_factories.OfferFactory(venue=venue)
    offer2 = offers_factories.OfferFactory(venue=venue)
    offer3 = offers_factories.OfferFactory(venue=venue)
    withdrawal_details = "Ceci est un exemple de modalités de retrait d'un bien"

    update_all_venue_offers_withdrawal_details_job(venue, withdrawal_details)

    assert offer1.withdrawalDetails == withdrawal_details
    assert offer2.withdrawalDetails == withdrawal_details
    assert offer3.withdrawalDetails == withdrawal_details
