import pytest

from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.offers.factories import OfferFactory
from pcapi.scripts.clean_duplicated_offers import count_duplicate_offers
from pcapi.scripts.clean_duplicated_offers import get_venue_ids_with_duplicates
from pcapi.scripts.clean_duplicated_offers import handle_offer_duplicates


class VenueOffersWrapper:
    def __init__(self, nb_duplicates, nb_regulars):
        self.venue = VenueFactory()

        self.duplicates = [
            (
                OfferFactory(idAtProviders=f"duplicate-id-{count}@siret-venue-{self.venue.id}", venue=self.venue),
                OfferFactory(idAtProviders=f"duplicate-id-{count}@other-siret-venue-{self.venue.id}", venue=self.venue),
            )
            for count in range(nb_duplicates)
        ]

        self.others = [
            OfferFactory(idAtProviders=f"regular-id-{count}@siret-venue-{self.venue.id}", venue=self.venue)
            for count in range(nb_regulars)
        ]


@pytest.mark.usefixtures("db_session")
def test_get_venue_ids_with_duplicates(app):
    venues_with_duplicates = [
        VenueOffersWrapper(nb_duplicates=1, nb_regulars=0),
        VenueOffersWrapper(nb_duplicates=2, nb_regulars=1),
    ]

    VenueOffersWrapper(nb_duplicates=0, nb_regulars=1)

    venue_ids = get_venue_ids_with_duplicates()
    assert venue_ids == {wrapper.venue.id for wrapper in venues_with_duplicates}


@pytest.mark.usefixtures("db_session")
def test_count_duplicates(app):
    VenueOffersWrapper(nb_duplicates=3, nb_regulars=1)
    VenueOffersWrapper(nb_duplicates=0, nb_regulars=2)

    assert count_duplicate_offers() == 3


@pytest.mark.usefixtures("db_session")
def test_handle_offer_duplicates(app, tmp_path):
    """
    Test that the expected duplicated rows have been updated (and no more)
    The most recent ones remain unchanged, same for offers that have no
    duplicates.
    """
    venues_with_duplicates = [
        VenueOffersWrapper(nb_duplicates=1, nb_regulars=0),
        VenueOffersWrapper(nb_duplicates=1, nb_regulars=6),
        VenueOffersWrapper(nb_duplicates=2, nb_regulars=1),
        VenueOffersWrapper(nb_duplicates=3, nb_regulars=5),
    ]

    VenueOffersWrapper(nb_duplicates=0, nb_regulars=2)
    VenueOffersWrapper(nb_duplicates=0, nb_regulars=3)

    updated_ids = handle_offer_duplicates(tmp_path / "updated_offer_ids")

    assert count_duplicate_offers() == 0

    expected_ids = set()
    for venue_wrapper in venues_with_duplicates:
        for duplicates in venue_wrapper.duplicates:
            # first duplicate row: oldest one -> should have been updated
            assert not duplicates[0].lastProviderId
            assert not duplicates[0].idAtProviders
            assert not duplicates[0].idAtProvider

            expected_ids.add(duplicates[0].id)

            # second duplicate row: most recent one -> should not have been updated
            assert duplicates[1].idAtProviders

    assert updated_ids == expected_ids
