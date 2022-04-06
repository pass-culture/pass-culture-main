import pytest

from pcapi.core.mails.transactional.users import duplicate_beneficiary


pytestmark = pytest.mark.usefixtures("db_session")


class AnonymizeEmailTest:
    @pytest.mark.parametrize(
        "input_email, anonymized_email",
        [
            ("anne-onime@me.com", "ann***@me.com"),
            ("wrong_address.com", "***"),
            ("yo@lo.com", "y***@lo.com"),
            ("y@o.com", "***@o.com"),
        ],
    )
    def test_anonymize(self, input_email, anonymized_email) -> None:
        assert duplicate_beneficiary._anonymize_email(input_email) == anonymized_email
