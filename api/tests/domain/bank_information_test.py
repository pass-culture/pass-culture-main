import pytest

from pcapi.domain.bank_information import CannotRegisterBankInformation
from pcapi.domain.bank_information import check_offerer_presence


class CheckOffererPresenceTest:
    def test_raises_an_error_if_no_offerer_found(self):
        # given
        offerer = None

        # when
        with pytest.raises(CannotRegisterBankInformation) as error:
            check_offerer_presence(offerer)

        # then
        assert error.value.args == ("Offerer not found",)
