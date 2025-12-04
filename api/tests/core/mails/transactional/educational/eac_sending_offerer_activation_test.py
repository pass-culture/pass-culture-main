from unittest.mock import patch

import pytest

from pcapi.core.mails.transactional import send_eac_offerer_activation_email
from pcapi.core.offerers import factories as offerers_factory


pytestmark = pytest.mark.usefixtures("db_session")


class SendEacBlueTemplateIdTest:
    @patch("pcapi.core.mails.transactional.educational.eac_sending_offerer_activation.mails")
    def test_with_one_email(self, mails):
        venue = offerers_factory.VenueFactory()

        send_eac_offerer_activation_email(venue, emails=["example@example.fr"])

        mails.send.assert_called_once()

        assert mails.send.call_args.kwargs["recipients"] == ["example@example.fr"]
        assert mails.send.call_args.kwargs["bcc_recipients"] == []
        assert mails.send.call_args.kwargs["data"].params == {"VENUE_NAME": venue.name}

    @patch("pcapi.core.mails.transactional.educational.eac_sending_offerer_activation.mails")
    def test_with_multiple_emails(self, mails):
        venue = offerers_factory.VenueFactory()

        send_eac_offerer_activation_email(
            venue, emails=["example@example.fr", "example2@example.fr", "example3@example.fr"]
        )

        mails.send.assert_called_once()

        assert mails.send.call_args.kwargs["recipients"] == ["example@example.fr"]
        assert mails.send.call_args.kwargs["bcc_recipients"] == ["example2@example.fr", "example3@example.fr"]
        assert mails.send.call_args.kwargs["data"].params == {"VENUE_NAME": venue.name}

    @patch("pcapi.core.mails.transactional.educational.eac_sending_offerer_activation.mails")
    def test_with_no_email(self, mails):
        venue = offerers_factory.VenueFactory()

        send_eac_offerer_activation_email(venue, emails=[])

        mails.send.assert_not_called()
