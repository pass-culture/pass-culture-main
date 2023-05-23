from typing import Any
from unittest.mock import patch

from freezegun import freeze_time
import pytest

from pcapi import settings
from pcapi.core.educational import factories as educational_factories
from pcapi.core.mails.transactional.educational.eac_new_request_made_by_redactor_to_pro import (
    send_new_request_made_by_redactor_to_pro,
)


pytestmark = pytest.mark.usefixtures("db_session")


class SendEacNewBookingEmailToProTest:
    @freeze_time("2019-11-26 18:29:20.891028")
    @patch("pcapi.core.mails.transactional.educational.eac_new_request_made_by_redactor_to_pro.mails")
    def test_new_request_made_by_redactor_for_pro(self, mails: Any) -> None:
        # given
        request = educational_factories.CollectiveOfferRequestFactory(
            collectiveOfferTemplate__bookingEmails=[
                "pouet@example.com",
                "plouf@example.com",
            ],
        )

        # when
        send_new_request_made_by_redactor_to_pro(request)

        # then
        mails.send.assert_called_once()
        assert mails.send.call_args.kwargs["data"].params == {
            "OFFER_NAME": request.collectiveOfferTemplate.name,
            "EVENT_DATE_REQUESTED": None,
            "TOTAL_STUDENTS": None,
            "TOTAL_TEACHERS": None,
            "COMMENT": "Un commentaire sublime",
            "REDACTOR_NAME": "Reda",
            "REDACTOR_LAST_NAME": "Khteur",
            "REDACTOR_MAIL": request.educationalRedactor.email,
            "REDACTOR_PHONE": None,
            "OFFER_CREATION_URL": f"{settings.PRO_URL}/offre/collectif/creation/{request.id}/requete",
        }
