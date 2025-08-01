from typing import Any
from unittest.mock import patch

import pytest
import time_machine

from pcapi import settings
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational.models import CollectiveLocationType
from pcapi.core.mails.transactional.educational.eac_new_request_made_by_redactor_to_pro import (
    send_new_request_made_by_redactor_to_pro,
)
from pcapi.core.offerers import factories as offerers_factories


pytestmark = pytest.mark.usefixtures("db_session")


class SendEacNewBookingEmailToProTest:
    @time_machine.travel("2019-11-26")
    @patch("pcapi.core.mails.transactional.educational.eac_new_request_made_by_redactor_to_pro.mails")
    def test_new_request_made_by_redactor_for_pro(self, mails: Any) -> None:
        oa = offerers_factories.OffererAddressFactory(label="Nice location")
        request = educational_factories.CollectiveOfferRequestFactory(
            collectiveOfferTemplate__bookingEmails=["pouet@example.com", "plouf@example.com"],
            collectiveOfferTemplate__locationType=CollectiveLocationType.ADDRESS,
            collectiveOfferTemplate__offererAddress=oa,
            requestedDate="2019-11-26",
        )

        send_new_request_made_by_redactor_to_pro(request)

        mails.send.assert_called_once()
        assert mails.send.call_args.kwargs["data"].params == {
            "OFFER_NAME": request.collectiveOfferTemplate.name,
            "VENUE_NAME": request.collectiveOfferTemplate.venue.name,
            "EVENT_DATE": "mardi 26 novembre 2019",
            "NB_STUDENTS": None,
            "NB_TEACHERS": None,
            "REQUEST_COMMENT": "Un commentaire sublime",
            "EDUCATIONAL_INSTITUTION_NAME": request.educationalInstitution.name,
            "CITY_NAME": "PARIS",
            "INSTITUTION_ZIP_CODE": "75000",
            "REDACTOR_FIRSTNAME": "Reda",
            "REDACTOR_LASTNAME": "Khteur",
            "REDACTOR_EMAIL": request.educationalRedactor.email,
            "REDACTOR_PHONE_NUMBER": None,
            "OFFER_CREATION_URL": f"{settings.PRO_URL}/offre/collectif/creation/{request.collectiveOfferTemplateId}/requete/{request.id}",
            "OFFERER_ID": request.collectiveOfferTemplate.venue.managingOffererId,
            "VENUE_ID": request.collectiveOfferTemplate.venue.id,
            "COLLECTIVE_OFFER_ADDRESS": f"Nice location - {oa.address.fullAddress}",
        }
