import pytest

from pcapi.domain.bank_information import CannotRegisterBankInformation
from pcapi.domain.bank_information import check_offerer_presence
from pcapi.domain.bank_information import check_venue_presence
from pcapi.domain.bank_information import check_venue_queried_by_name
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_venue


class CheckOffererPresenceTest:
    def test_raises_an_error_if_no_offerer_found(self):
        # given
        offerer = None

        # when
        with pytest.raises(CannotRegisterBankInformation) as error:
            check_offerer_presence(offerer)

        # then
        assert error.value.args == ("Offerer not found",)


class CheckVenuePresenceTest:
    def test_raises_an_error_if_no_venue_found(self):
        # given
        venue = None

        # when
        with pytest.raises(CannotRegisterBankInformation) as error:
            check_venue_presence(venue)

        # then
        assert error.value.args == ("Venue not found",)


class CheckVenueQueriedByNameTest:
    def test_raises_an_error_if_no_venue_found(self):
        # given
        venues = []

        # when
        with pytest.raises(CannotRegisterBankInformation) as error:
            check_venue_queried_by_name(venues)

        # then
        assert error.value.args == ("Venue name not found",)

    def test_raise_an_error_if_more_than_one_venue_found(self):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        venue1 = create_venue(offerer=offerer)
        venues = [venue, venue1]

        # when
        with pytest.raises(CannotRegisterBankInformation) as error:
            check_venue_queried_by_name(venues)

        # then
        assert error.value.args == ("Multiple venues found",)
