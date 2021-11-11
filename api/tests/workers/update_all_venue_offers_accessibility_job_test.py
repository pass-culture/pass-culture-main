import pytest

from pcapi.core.offers import factories
from pcapi.workers.update_all_venue_offers_accessibility_job import update_all_venue_offers_accessibility_job


@pytest.mark.usefixtures("db_session")
def test_update_all_venue_offers_accessibility_job():
    venue = factories.VenueFactory(bookingEmail="old.venue@email.com")
    offer1 = factories.OfferFactory(venue=venue)
    offer2 = factories.OfferFactory(venue=venue)
    offer3 = factories.OfferFactory(venue=venue)
    new_accessibility = {
        "audioDisabilityCompliant": True,
        "mentalDisabilityCompliant": False,
        "motorDisabilityCompliant": True,
        "visualDisabilityCompliant": False,
    }

    update_all_venue_offers_accessibility_job(venue, new_accessibility)

    assert offer1.audioDisabilityCompliant == new_accessibility["audioDisabilityCompliant"]
    assert offer1.mentalDisabilityCompliant == new_accessibility["mentalDisabilityCompliant"]
    assert offer1.motorDisabilityCompliant == new_accessibility["motorDisabilityCompliant"]
    assert offer1.visualDisabilityCompliant == new_accessibility["visualDisabilityCompliant"]

    assert offer2.audioDisabilityCompliant == new_accessibility["audioDisabilityCompliant"]
    assert offer2.mentalDisabilityCompliant == new_accessibility["mentalDisabilityCompliant"]
    assert offer2.motorDisabilityCompliant == new_accessibility["motorDisabilityCompliant"]
    assert offer2.visualDisabilityCompliant == new_accessibility["visualDisabilityCompliant"]

    assert offer3.audioDisabilityCompliant == new_accessibility["audioDisabilityCompliant"]
    assert offer3.mentalDisabilityCompliant == new_accessibility["mentalDisabilityCompliant"]
    assert offer3.motorDisabilityCompliant == new_accessibility["motorDisabilityCompliant"]
    assert offer3.visualDisabilityCompliant == new_accessibility["visualDisabilityCompliant"]
