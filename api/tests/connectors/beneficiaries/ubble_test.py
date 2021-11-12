import datetime

from pcapi.connectors.beneficiaries import ubble
from pcapi.core.fraud import models as fraud_models


class StartIdentificationTest:
    def test_start_identification(self, ubble_mock):

        response = ubble.start_identification(
            user_id=123,
            phone_number="+33601232323",
            birth_date=datetime.date(2001, 2, 23),
            first_name="prenom",
            last_name="nom",
            webhook_url="http://webhook/url/",
            redirect_url="http://redirect/url",
            face_required=True,
        )

        assert isinstance(response, fraud_models.UbbleIdentificationResponse)
        assert ubble_mock.call_count == 1

        attributes = ubble_mock.last_request.json()["data"]["attributes"]
        assert attributes["identification-form"]["external-user-id"] == 123
        assert attributes["identification-form"]["phone-number"] == "+33601232323"

        assert attributes["reference-data"]["birth-date"] == "2001-02-23"
        assert attributes["reference-data"]["first-name"] == "prenom"
        assert attributes["reference-data"]["last-name"] == "nom"
        assert attributes["webhook"] == "http://webhook/url/"
        assert attributes["redirect_url"] == "http://redirect/url"
        assert attributes["face_required"] == True
