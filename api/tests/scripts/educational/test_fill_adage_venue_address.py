import pytest

from pcapi.core.educational.models import AdageVenueAddress
from pcapi.core.offerers.factories import CollectiveVenueFactory
from pcapi.core.offerers.factories import VenueFactory
from pcapi.models import db
from pcapi.scripts.educational.fill_adage_venue_address import fill_adage_venue_addresses


pytestmark = pytest.mark.usefixtures("db_session")


class FillAdageVenueAddressesTest:
    def test_only_unknown_collective_venues(self):
        venues = CollectiveVenueFactory.create_batch(2)

        fill_adage_venue_addresses()
        self._assert_all_venues_have_been_processed(venues)

    def test_only_unknown_venues(self):
        venues = VenueFactory.create_batch(2)
        venues.extend(CollectiveVenueFactory.create_batch(2))

        fill_adage_venue_addresses()
        self._assert_all_venues_have_been_processed(venues)

    def test_known_collective_venue(self):
        venues = CollectiveVenueFactory.create_batch(2)

        venue = venues[0]
        ava = AdageVenueAddress(
            id=venue.id, venueId=venue.id, adageId=venue.adageId, adageInscriptionDate=venue.adageInscriptionDate
        )
        db.session.add(ava)
        db.session.commit()

        fill_adage_venue_addresses()
        self._assert_all_venues_have_been_processed(venues)

    def test_with_only_known_collective_venues(self):
        venues = CollectiveVenueFactory.create_batch(2)

        for venue in venues:
            ava = AdageVenueAddress(
                id=venue.id, venueId=venue.id, adageId=venue.adageId, adageInscriptionDate=venue.adageInscriptionDate
            )
            db.session.add(ava)
        db.session.commit()

        fill_adage_venue_addresses()
        self._assert_all_venues_have_been_processed(venues)

    def test_with_only_known_venues_mix(self):
        venues = CollectiveVenueFactory.create_batch(2)
        venues.extend(CollectiveVenueFactory.create_batch(2))

        for venue in venues:
            ava = AdageVenueAddress(
                id=venue.id, venueId=venue.id, adageId=venue.adageId, adageInscriptionDate=venue.adageInscriptionDate
            )
            db.session.add(ava)
        db.session.commit()

        fill_adage_venue_addresses()
        self._assert_all_venues_have_been_processed(venues)

    def test_no_venues(self):
        fill_adage_venue_addresses()
        self._assert_all_venues_have_been_processed([])

    def _assert_all_venues_have_been_processed(self, venues):
        avas = AdageVenueAddress.query.all()
        assert len(avas) == len(venues)

        for venue in venues:
            db.session.refresh(venue)

        assert {ava.venueId for ava in avas} == {v.id for v in venues}
        assert {ava.adageId for ava in avas} == {v.adageId for v in venues}
        assert {ava.adageInscriptionDate for ava in avas} == {v.adageInscriptionDate for v in venues}
