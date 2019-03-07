import pytest

from models import PcObject
from repository.email_queries import find_all_in_error
from tests.conftest import clean_database
from tests.test_utils import create_email


@pytest.mark.standalone
class FindAllInErrorTest:
    @clean_database
    def test_returns_emails_failed_with_status_ERROR_only(self, app):
        # given
        email = {}
        email_failed_in_error = create_email(email, status='ERROR')
        email_failed_sent= create_email(email, status='SENT')

        PcObject.check_and_save(email_failed_in_error, email_failed_sent)

        # when
        email_failed_in_error = find_all_in_error()

        # then
        assert len(email_failed_in_error)
        assert email_failed_in_error[0].status == 'ERROR'
