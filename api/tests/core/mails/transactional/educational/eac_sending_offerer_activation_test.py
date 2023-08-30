from typing import Any
from unittest.mock import patch

from freezegun import freeze_time
import pytest

from pcapi.core.mails.transactional import send_eac_offerer_activation_email
from pcapi.core.offerers import factories as offerers_factory


class SendEacBlueTemplateIdTest:
    @freeze_time("2019-11-26 18:29:20.891028")
    @patch("pcapi.core.mails.transactional.educational.eac_sending_offerer_activation.mails")
    def test_with_collective_booking(
        self,
        mails: Any,
    ) -> None:
        # given
        venue = offerers_factory.VenueFactory(
            bookingEmail=["pouet@example.com", "plouf@example.com"],
        )

        # when
        send_eac_offerer_activation_email(venue, emails=["exemple"])

        # then
        mails.send.assert_called_once()

        assert mails.send.call_args.kwargs["data"].params == {
            "VENUE_NAME": venue.name,
        }
