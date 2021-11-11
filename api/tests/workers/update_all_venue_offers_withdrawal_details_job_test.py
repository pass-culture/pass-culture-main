import pytest

from pcapi.core.offers import factories
from pcapi.workers.update_all_venue_offers_withdrawal_details_job import update_all_venue_offers_withdrawal_details_job


@pytest.mark.usefixtures("db_session")
def test_update_all_venue_offers_withdrawal_details_job_test():
    venue = factories.VenueFactory()
    offer1 = factories.OfferFactory(venue=venue)
    offer2 = factories.OfferFactory(venue=venue)
    offer3 = factories.OfferFactory(venue=venue)
    withdrawal_details = "Ceci est un exemple de modalités de retrait d'un bien"

    update_all_venue_offers_withdrawal_details_job(venue, withdrawal_details)

    assert offer1.withdrawalDetails == withdrawal_details
    assert offer2.withdrawalDetails == withdrawal_details
    assert offer3.withdrawalDetails == withdrawal_details
