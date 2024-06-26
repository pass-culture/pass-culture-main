import pytest

import pcapi.utils.email as email_utils


@pytest.mark.parametrize(
    "content, expected_result",
    (
        ("Beneficiary.User@GMAIL.COM", "beneficiary.user@gmail.com"),
        ("venue@offerer.fr ", "venue@offerer.fr"),
    ),
)
def test_sanitize_email(content, expected_result):
    assert email_utils.sanitize_email(content) == expected_result


@pytest.mark.parametrize(
    "content, expected_result",
    (
        ("venue@offerer.net", True),
        ("beneficiary.user@gmail.com", True),
        ("venue.offerer.com", False),
        ("user@gmail", False),
        ("user@.fr", False),
    ),
)
def test_is_valid_email(content, expected_result):
    assert email_utils.is_valid_email(content) is expected_result


@pytest.mark.parametrize(
    "content, expected_result",
    (
        ("@passculture.app", True),
        ("@domain.fr", True),
        ("offerer.net", False),
        ("user@gmail", False),
    ),
)
def test_is_valid_email_domain(content, expected_result):
    assert email_utils.is_valid_email_domain(content) is expected_result


@pytest.mark.usefixtures("db_session")
@pytest.mark.parametrize(
    "input_email, anonymized_email",
    [
        ("anne-onime@me.com", "ann***@me.com"),
        ("wrong_address.com", "***"),
        ("yo@lo.com", "y***@lo.com"),
        ("y@o.com", "***@o.com"),
    ],
)
def test_anonymize(input_email, anonymized_email) -> None:
    assert email_utils.anonymize_email(input_email) == anonymized_email
