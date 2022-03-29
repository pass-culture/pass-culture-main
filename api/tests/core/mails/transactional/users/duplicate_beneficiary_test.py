import pytest

from pcapi.core.mails.transactional.users import duplicate_beneficiary


pytestmark = pytest.mark.usefixtures("db_session")


class AnonimyzeEmailTest:
    @pytest.mark.parametrize(
        "input_email, anonimyzed_email",
        [("anne-onime@me.com", "ann***@me.com"), ("wrong_address.com", "***"), ("yo@lo.com", "yo***@lo.com")],
    )
    def test_anonymize(self, input_email, anonimyzed_email) -> None:
        assert duplicate_beneficiary._anonimyze_email(input_email) == anonimyzed_email
