from pcapi.domain.bank_information import check_offerer_presence
from pcapi.models.api_errors import ApiErrors


class CheckOffererPresenceTest:
    def test_raises_an_error_if_no_offerer_found(self):
        # given
        offerer = None
        api_errors = ApiErrors()

        # when
        check_offerer_presence(offerer, api_errors)
        # then
        assert api_errors.errors == {"Offerer": ["Offerer not found"]}
