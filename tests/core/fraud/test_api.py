from datetime import datetime
from unittest.mock import patch

from freezegun import freeze_time
import pytest

from pcapi.core.fraud.models import BeneficiaryFraudCheck
from pcapi.core.fraud.models import FraudCheckType
from pcapi.core.fraud.models import JouveContent
from pcapi.core.users.factories import UserFactory
from pcapi.core.users.models import PhoneValidationStatusType
from pcapi.flask_app import db


pytestmark = pytest.mark.usefixtures("db_session")


class JouveFraudCheckTest:
    application_id = 35
    user_email = "tour.de.passpass@example.com"

    JOUVE_CONTENT = {
        "activity": "Etudiant",
        "address": "",
        "birthDate": "06/08/2002",
        "birthDateTxt": "06/08/2002",
        "birthLocation": "STRASBOURG I67)",
        "birthLocationCtrl": "OK",
        "bodyBirthDate": "06 06 2002",
        "bodyBirthDateCtrl": "OK",
        "bodyBirthDateLevel": "100",
        "bodyFirstname": "CHRISTOPH",
        "bodyFirstnameCtrl": "",
        "bodyFirstnameLevel": "100",
        "bodyName": "DUPO",
        "bodyNameCtrl": "OK",
        "bodyNameLevel": "100",
        "bodyPieceNumber": "140767100016",
        "bodyPieceNumberCtrl": "OK",
        "bodyPieceNumberLevel": "100",
        "city": "",
        "creatorCtrl": "NOT_APPLICABLE",
        "docFileID": 535,
        "docObjectID": 535,
        "email": user_email,
        "firstName": "CHRISTOPH",
        "gender": "M",
        "id": application_id,
        "initial": "",
        "initialNumberCtrl": "",
        "initialSizeCtrl": "",
        "lastName": "DUPO",
        "phoneNumber": "",
        "postalCode": "",
        "posteCode": "678083",
        "posteCodeCtrl": "OK",
        "registrationDate": "10/06/2021 21:00",
        "serviceCode": "1",
        "serviceCodeCtrl": "",
    }

    @patch("pcapi.connectors.beneficiaries.jouve_backend._get_raw_content")
    @pytest.mark.usefixtures("client")
    @freeze_time("2018/06/06 09:00:00")
    def test_jouve_update(self, _get_raw_content, client):
        user = UserFactory(
            hasCompletedIdCheck=True,
            isBeneficiary=False,
            phoneValidationStatus=PhoneValidationStatusType.VALIDATED,
            dateOfBirth=datetime(2000, 1, 1),
            email=self.user_email,
        )
        _get_raw_content.return_value = self.JOUVE_CONTENT

        response = client.post("/beneficiaries/application_update", json={"id": self.application_id})
        assert response.status_code == 200

        fraud_check = BeneficiaryFraudCheck.query.filter_by(user=user, type=FraudCheckType.JOUVE).first()
        jouve_fraud_content = JouveContent(**fraud_check.resultContent)

        assert jouve_fraud_content.bodyPieceNumber == "140767100016"
        assert fraud_check.dateCreated

        db.session.refresh(user)
        assert user.isBeneficiary
