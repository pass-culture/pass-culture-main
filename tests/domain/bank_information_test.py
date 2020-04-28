import pytest
from tests.model_creators.generic_creators import (create_offerer,
                                                   create_venue)
from domain.bank_information import check_offerer_presence, check_venue_presence, check_venue_queried_by_name, VenueMatchingError


class CheckOffererPresenceTest:
    def test_raises_an_error_if_no_offerer_found(self):
        # given
        offerer = None

        # when
        with pytest.raises(VenueMatchingError) as error:
            check_offerer_presence(offerer)

        # then
        assert error.value.args == ("Offerer not found",)


class CheckVenuePresenceTest:
    def test_raises_an_error_if_no_venue_found(self):
        # given
        venue = None

        # when
        with pytest.raises(VenueMatchingError) as error:
            check_venue_presence(venue)

        # then
        assert error.value.args == ("Venue not found",)


class CheckVenueQueriedByNameTest:
    def test_raises_an_error_if_no_venue_found(self):
        # given
        venues = []

        # when
        with pytest.raises(VenueMatchingError) as error:
            check_venue_queried_by_name(venues)

        # then
        assert error.value.args == ("Venue name for found",)

    def test_raise_an_error_if_more_than_one_venue_found(self):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        venue1 = create_venue(offerer=offerer)
        venues = [venue, venue1]

        # when
        with pytest.raises(VenueMatchingError) as error:
            check_venue_queried_by_name(venues)

        # then
        assert error.value.args == ("Multiple venues found",)
