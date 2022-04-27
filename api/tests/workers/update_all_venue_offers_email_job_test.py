import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.workers.update_all_venue_offers_email_job import update_all_venue_offers_email_job


@pytest.mark.usefixtures("db_session")
def test_update_all_venue_offers_email_job():
    venue = offerers_factories.VenueFactory(bookingEmail="old.venue@email.com")
    offer1 = offers_factories.OfferFactory(bookingEmail="old.offer@email.com", venue=venue)
    offer2 = offers_factories.OfferFactory(bookingEmail="old.offer@email.com", venue=venue)
    offer3 = offers_factories.OfferFactory(bookingEmail="old.offer@email.com", venue=venue)
    new_email = "new.venue@email.com"

    update_all_venue_offers_email_job(venue, new_email)

    assert offer1.bookingEmail == new_email
    assert offer2.bookingEmail == new_email
    assert offer3.bookingEmail == new_email
