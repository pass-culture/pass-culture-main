import pytest

from pcapi.core.educational.factories import CollectiveOfferFactory
from pcapi.core.educational.factories import CollectiveOfferTemplateFactory
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.workers.update_all_venue_offers_accessibility_job import update_all_venue_offers_accessibility_job


@pytest.mark.usefixtures("db_session")
def test_update_all_venue_offers_accessibility_job() -> None:
    venue = offerers_factories.VenueFactory(bookingEmail="old.venue@email.com")
    offer1 = offers_factories.OfferFactory(venue=venue)
    offer2 = offers_factories.OfferFactory(venue=venue)
    offer3 = offers_factories.OfferFactory(venue=venue)
    collective_offer = CollectiveOfferFactory(venue=venue, audioDisabilityCompliant=False)
    collective_offer_template = CollectiveOfferTemplateFactory(venue=venue, audioDisabilityCompliant=False)
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

    assert collective_offer.audioDisabilityCompliant == new_accessibility["audioDisabilityCompliant"]
    assert collective_offer.mentalDisabilityCompliant == new_accessibility["mentalDisabilityCompliant"]
    assert collective_offer.motorDisabilityCompliant == new_accessibility["motorDisabilityCompliant"]
    assert collective_offer.visualDisabilityCompliant == new_accessibility["visualDisabilityCompliant"]

    assert collective_offer_template.audioDisabilityCompliant == new_accessibility["audioDisabilityCompliant"]
    assert collective_offer_template.mentalDisabilityCompliant == new_accessibility["mentalDisabilityCompliant"]
    assert collective_offer_template.motorDisabilityCompliant == new_accessibility["motorDisabilityCompliant"]
    assert collective_offer_template.visualDisabilityCompliant == new_accessibility["visualDisabilityCompliant"]
