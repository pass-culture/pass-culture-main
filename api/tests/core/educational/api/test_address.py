import pytest

from pcapi.core.educational import models
from pcapi.core.educational.api import address as api
from pcapi.core.offerers import factories as offerers_factories
from pcapi.repository.session_management import atomic


pytestmark = pytest.mark.usefixtures("db_session")


class UnlinkUnknownVenueAddressesTest:
    def test_unlink_many(self):
        venues = offerers_factories.CollectiveVenueFactory.create_batch(2)

        with atomic():
            api.unlink_deactivated_venue_addresses({venue.adageId: venue.id for venue in venues})

        venue_addresses = get_venue_addresses([venue.id for venue in venues])
        assert len(venue_addresses) == len(venues)
        assert {ava.adageId for ava in venue_addresses} == {None}
        assert found_inscription_dates(venue_addresses) == {None}

    def test_unlink_many_keep_many(self):
        to_unlink = offerers_factories.CollectiveVenueFactory.create_batch(2)
        to_keep = offerers_factories.CollectiveVenueFactory.create_batch(2)

        with atomic():
            api.unlink_deactivated_venue_addresses({venue.adageId: venue.id for venue in to_unlink})

        venue_addresses = get_venue_addresses([venue.id for venue in to_unlink + to_keep])
        assert {ava.adageId for ava in venue_addresses} == {venue.adageId for venue in to_keep} | {None}

        expected_dates = {format_date(venue.adageInscriptionDate) for venue in to_keep} | {None}
        assert found_inscription_dates(venue_addresses) == expected_dates


class UpsertVenuesAddressesTest:
    def test_insert_many(self):
        venues = offerers_factories.VenueFactory.create_batch(2)
        adage_ids_venues = {venue.adageId: venue.id for venue in venues}

        api.upsert_venues_addresses(adage_ids_venues)

        venue_addresses = get_venue_addresses()
        assert {addr.adageId: addr.venueId for addr in venue_addresses} == adage_ids_venues

    def test_update_many(self):
        venues = offerers_factories.CollectiveVenueFactory.create_batch(2)  # has adage_addresses
        other_venues = offerers_factories.VenueFactory.create_batch(2)  # does not have adage_addresses
        adage_ids_venues = {venue.adageId: other_venue.id for venue, other_venue in zip(venues, other_venues)}

        api.upsert_venues_addresses(adage_ids_venues)

        venue_addresses = get_venue_addresses()
        assert {addr.adageId: addr.venueId for addr in venue_addresses} == adage_ids_venues

    def test_upsert(self):
        # note: venue does not create any AdageVenueAddress
        # whilst collective_venue and other_collective_venue will
        # both create one.
        venue = offerers_factories.VenueFactory()
        collective_venue = offerers_factories.CollectiveVenueFactory()
        other_collective_venue = offerers_factories.CollectiveVenueFactory()

        adage_ids_venues = {
            # adage id unknown -> create
            collective_venue.adageId + collective_venue.adageId: venue.id,
            # adage id known -> update
            collective_venue.adageId: other_collective_venue.id,
        }

        api.upsert_venues_addresses(adage_ids_venues)

        found_addresses = {addr.adageId: addr.venueId for addr in get_venue_addresses()}
        assert found_addresses == {
            collective_venue.adageId + collective_venue.adageId: venue.id,
            collective_venue.adageId: other_collective_venue.id,
            other_collective_venue.adageId: other_collective_venue.id,
        }


def get_venue_addresses(venue_ids=None):
    if venue_ids is None:
        return models.AdageVenueAddress.query.all()
    return models.AdageVenueAddress.query.filter(models.AdageVenueAddress.venueId.in_(venue_ids)).all()


def format_date(inscription_date):
    if inscription_date:
        return inscription_date.date()
    return inscription_date


def found_inscription_dates(venue_addresses):
    return {format_date(ava.adageInscriptionDate) for ava in venue_addresses}
