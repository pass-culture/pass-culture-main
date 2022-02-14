import copy
from unittest.mock import patch

import pytest
import requests.exceptions
import requests_mock

from pcapi.core import mails
import pcapi.core.mails.backends.mailjet
from pcapi.core.mails.models.models import Email
from pcapi.core.mails.models.models import EmailStatus
from pcapi.core.testing import override_settings


@pytest.mark.usefixtures("db_session")
class SendTest:

    recipients = ["recipient1@example.com", "recipient2@example.com"]
    data = {"key": "value", "Vars": {"other-key": "other-value"}}
    expected_sent_data = {
        "FromEmail": "support@example.com",
        "To": ", ".join(recipients),
        "key": "value",
        "Vars": {
            "other-key": "other-value",
            "env": "-development",
        },
    }

    def test_send(self):
        successful = mails.send(recipients=self.recipients, data=self.data)
        assert successful
        email = Email.query.one()
        assert email.status == EmailStatus.SENT
        assert email.content == self.expected_sent_data

    @override_settings(MAILJET_EMAIL_BACKEND="pcapi.core.mails.backends.testing.FailingBackend")
    def test_send_failure(self):
        successful = mails.send(recipients=self.recipients, data=self.data)
        assert not successful
        email = Email.query.one()
        assert email.status == EmailStatus.ERROR
        assert email.content == self.expected_sent_data

    @override_settings(MAILJET_EMAIL_BACKEND="pcapi.core.mails.backends.mailjet.MailjetBackend")
    def test_send_with_mailjet(self):
        expected = copy.deepcopy(self.expected_sent_data)
        expected["MJ-TemplateErrorReporting"] = "dev@example.com"
        with requests_mock.Mocker() as mock:
            posted = mock.post("https://api.mailjet.com/v3/send")
            successful = mails.send(recipients=self.recipients, data=self.data)
            assert posted.last_request.json() == expected
        assert successful


class MailjetBackendTest:

    recipients = ["recipient1@example.com", "recipient2@example.com"]
    data = {"key": "value", "Vars": {"other-key": "other-value"}}
    expected_sent_data = {
        "FromEmail": "support@example.com",
        "To": ", ".join(recipients),
        "key": "value",
        "Vars": {
            "other-key": "other-value",
            "env": "-development",
        },
        "MJ-TemplateErrorReporting": "dev@example.com",
    }

    def _get_backend(self):
        return pcapi.core.mails.backends.mailjet.MailjetBackend()

    def test_send_mail(self):
        backend = self._get_backend()
        with requests_mock.Mocker() as mock:
            posted = mock.post("https://api.mailjet.com/v3/send")
            result = backend.send_mail(recipients=self.recipients, data=self.data)

        assert posted.last_request.json() == self.expected_sent_data
        assert result.successful

    def test_send_mail_with_error_response(self):
        backend = self._get_backend()
        with requests_mock.Mocker() as mock:
            posted = mock.post("https://api.mailjet.com/v3/send", status_code=400)
            result = backend.send_mail(recipients=self.recipients, data=self.data)

        assert posted.last_request.json() == self.expected_sent_data
        assert not result.successful

    def test_send_mail_with_timeout(self):
        backend = self._get_backend()
        with requests_mock.Mocker() as mock:
            mock.post("https://api.mailjet.com/v3/send", exc=requests.exceptions.ConnectTimeout)
            result = backend.send_mail(recipients=self.recipients, data=self.data)
        assert not result.successful

    @patch("pcapi.utils.requests.logger.info")
    def test_use_our_requests_wrapper_that_logs(self, mocked_logger):
        backend = self._get_backend()
        with requests_mock.Mocker() as mock:
            posted = mock.post("https://api.mailjet.com/v3/send")
            backend.send_mail(recipients=self.recipients, data=self.data)

        assert posted.last_request.json() == self.expected_sent_data
        mocked_logger.assert_called_once()


class ToDevMailjetBackendTest:
    recipients = ["real1@example.com", "real2@example.com"]
    data = {"key": "value"}
    expected_sent_data = {
        "FromEmail": "support@example.com",
        "To": ", ".join(recipients),
        "key": "value",
        "MJ-TemplateErrorReporting": "dev@example.com",
    }

    def _get_backend(self):
        return pcapi.core.mails.backends.mailjet.ToDevMailjetBackend()

    def test_send_mail_overrides_recipients(self):
        backend = self._get_backend()
        with requests_mock.Mocker() as mock:
            posted = mock.post("https://api.mailjet.com/v3/send")
            result = backend.send_mail(recipients=self.recipients, data=self.data)

        expected = copy.deepcopy(self.expected_sent_data)
        expected["To"] = "dev@example.com"
        assert posted.last_request.json() == expected
        assert result.successful

    @override_settings(WHITELISTED_EMAIL_RECIPIENTS=["false1@example.com", "real2@example.com"])
    def test_send_mail_if_any_recipient_is_whitelisted(self):
        backend = self._get_backend()
        with requests_mock.Mocker() as mock:
            posted = mock.post("https://api.mailjet.com/v3/send")
            result = backend.send_mail(recipients=self.recipients, data=self.data)

        assert posted.last_request.json() == self.expected_sent_data
        assert result.successful

    def test_send_mail_inject_preamble_in_html(self):
        backend = self._get_backend()
        data = copy.deepcopy(self.data)
        data["Html-part"] = "<div>some HTML...<div>"

        with requests_mock.Mocker() as mock:
            posted = mock.post("https://api.mailjet.com/v3/send")
            result = backend.send_mail(recipients=self.recipients, data=data)

        expected = copy.deepcopy(self.expected_sent_data)
        expected["To"] = "dev@example.com"
        posted_json = posted.last_request.json()
        assert posted_json["Html-part"].endswith("<div>some HTML...<div>")
        assert "would have been sent to real1@example.com, real2@example.com" in posted_json["Html-part"]
        assert result.successful
