from datetime import datetime
from unittest.mock import patch

import pytest

import pcapi.core.fraud.api as fraud_api
import pcapi.core.fraud.factories as fraud_factories
import pcapi.core.fraud.models as fraud_models
from pcapi.core.fraud.models import BeneficiaryFraudCheck
from pcapi.core.fraud.models import BeneficiaryFraudResult
from pcapi.core.fraud.models import FraudCheckType
from pcapi.core.fraud.models import FraudStatus
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
        "bodyFirstnameCtrl": "OK",
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
        "firstName": "CHRISTOPHE",
        "gender": "M",
        "id": application_id,
        "initial": "",
        "initialNumberCtrl": "OK",
        "initialSizeCtrl": "OK",
        "lastName": "DUPO",
        "phoneNumber": "",
        "postalCode": "",
        "posteCode": "678083",
        "posteCodeCtrl": "OK",
        "registrationDate": "10/06/2021 21:00",
        "serviceCode": "1",
        "serviceCodeCtrl": "OK",
    }

    @patch("pcapi.connectors.beneficiaries.jouve_backend._get_raw_content")
    @pytest.mark.parametrize("body_name_level", [None, "", "100"])
    def test_jouve_update(self, _get_raw_content, client, body_name_level):
        user = UserFactory(
            hasCompletedIdCheck=True,
            isBeneficiary=False,
            phoneValidationStatus=PhoneValidationStatusType.VALIDATED,
            dateOfBirth=datetime(2002, 6, 8),
            email=self.user_email,
        )
        _get_raw_content.return_value = self.JOUVE_CONTENT | {"bodyNameLevel": body_name_level}

        response = client.post("/beneficiaries/application_update", json={"id": self.application_id})
        assert response.status_code == 200

        fraud_check = BeneficiaryFraudCheck.query.filter_by(user=user, type=FraudCheckType.JOUVE).first()
        fraud_result = BeneficiaryFraudResult.query.filter_by(user=user).first()
        jouve_fraud_content = JouveContent(**fraud_check.resultContent)

        assert jouve_fraud_content.bodyPieceNumber == "140767100016"
        assert fraud_check.dateCreated
        assert fraud_check.thirdPartyId == "35"
        assert fraud_result.status == FraudStatus.OK

        db.session.refresh(user)
        assert user.isBeneficiary

    @patch("pcapi.connectors.beneficiaries.jouve_backend._get_raw_content")
    def test_jouve_update_duplicate_user(self, _get_raw_content, client):
        existing_user = UserFactory(
            firstName="Christophe",
            lastName="Dupo",
            isBeneficiary=True,
            dateOfBirth=datetime(2002, 6, 8),
            idPieceNumber="140767100016",
        )
        user = UserFactory(
            hasCompletedIdCheck=True,
            isBeneficiary=False,
            phoneValidationStatus=PhoneValidationStatusType.VALIDATED,
            dateOfBirth=datetime(2002, 6, 8),
            email=self.user_email,
        )
        _get_raw_content.return_value = self.JOUVE_CONTENT

        response = client.post("/beneficiaries/application_update", json={"id": self.application_id})
        assert response.status_code == 200

        fraud_result = BeneficiaryFraudResult.query.filter_by(user=user).first()

        assert fraud_result.status == FraudStatus.SUSPICIOUS
        assert fraud_result.reason == f"Le n° de cni 140767100016 est déjà pris par l'utilisateur {existing_user.id}"

        db.session.refresh(user)
        assert not user.isBeneficiary

    @pytest.mark.parametrize("jouve_field", ["birthLocationCtrl", "bodyBirthDateCtrl", "bodyNameCtrl"])
    @pytest.mark.parametrize("wrong_possible_value", ["NOT_APPLICABLE", "KO"])
    def test_id_check_fraud_items_wrong_values_are_supiscious(self, jouve_field, wrong_possible_value):
        jouve_content = fraud_factories.JouveContentFactory(**{jouve_field: wrong_possible_value})
        item_found = False
        for item in fraud_api._id_check_fraud_items(jouve_content):
            if item.detail == f"Le champ {jouve_field} est {wrong_possible_value}":
                assert item.status == fraud_models.FraudStatus.SUSPICIOUS
                item_found = True

        assert item_found

    @pytest.mark.parametrize(
        "id_piece_number",
        [
            "I III1",
            "I I 1JII 11IB I E",
            "",
        ],
    )
    def test_jouve_id_piece_number_wrong_format(self, id_piece_number):
        item = fraud_api._validate_id_piece_number_format_fraud_item(id_piece_number)
        assert item.status == fraud_models.FraudStatus.SUSPICIOUS

    @pytest.mark.parametrize(
        "id_piece_number",
        [
            "321070751234",
            "090435303687",
        ],
    )
    def test_jouve_id_piece_number_valid_format(self, id_piece_number):
        item = fraud_api._validate_id_piece_number_format_fraud_item(id_piece_number)
        assert item.status == fraud_models.FraudStatus.OK

    def test_on_identity_fraud_check_result_retry(self):
        user = UserFactory(isBeneficiary=False)
        content = fraud_factories.JouveContentFactory(
            birthLocationCtrl="OK",
            bodyBirthDateCtrl="OK",
            bodyBirthDateLevel=100,
            bodyFirstnameCtrl="OK",
            bodyFirstnameLevel=100,
            bodyNameLevel=100,
            bodyNameCtrl="OK",
            bodyPieceNumber="wrong-id-piece-number",
            bodyPieceNumberCtrl="KO",  # ensure we correctly update this field later in the test
            bodyPieceNumberLevel=100,
            creatorCtrl="OK",
            initialSizeCtrl="OK",
        )
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.JOUVE, user=user, resultContent=content
        )
        fraud_check = fraud_api.admin_update_identity_fraud_check_result(user, "123123123123")
        fraud_result = fraud_factories.BeneficiaryFraudResultFactory(
            user=user, status=fraud_models.FraudStatus.SUSPICIOUS, reason="Suspiscious case"
        )
        fraud_api.on_identity_fraud_check_result(user, fraud_check)
        fraud_result = fraud_models.BeneficiaryFraudResult.query.get(fraud_result.id)
        assert fraud_result.status == fraud_models.FraudStatus.OK

    def test_admin_update_identity_fraud_check_result(self):
        user = UserFactory(isBeneficiary=False)

        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.JOUVE,
            user=user,
        )

        fraud_check = fraud_api.admin_update_identity_fraud_check_result(user, "id-piece-number")
        content = fraud_models.JouveContent(**fraud_check.resultContent)
        assert content.bodyPieceNumberLevel == 100
        assert content.bodyPieceNumber == "id-piece-number"
        assert content.bodyPieceNumberCtrl == "OK"

    # TODO(xordoquy): make fraud fields configurable and reactivate this test
    # @patch("pcapi.connectors.beneficiaries.jouve_backend._get_raw_content")
    # def test_jouve_update_id_fraud(self, _get_raw_content, client):

    #     user = UserFactory(
    #         hasCompletedIdCheck=True,
    #         isBeneficiary=False,
    #         phoneValidationStatus=PhoneValidationStatusType.VALIDATED,
    #         dateOfBirth=datetime(2002, 6, 8),
    #         email=self.user_email,
    #     )
    #     _get_raw_content.return_value = self.JOUVE_CONTENT | {"serviceCodeCtrl": "KO", "bodyFirstnameLevel": "30"}

    #     response = client.post("/beneficiaries/application_update", json={"id": self.application_id})
    #     assert response.status_code == 200

    #     fraud_result = BeneficiaryFraudResult.query.filter_by(user=user).first()

    #     assert fraud_result.status == FraudStatus.KO
    #     assert (
    #         fraud_result.reason
    #         == "Le champ serviceCodeCtrl est KO ; Le champ bodyFirstnameLevel a le score 30 (minimum 50)"
    #     )

    #     db.session.refresh(user)
    #     assert not user.isBeneficiary


class CommonTest:
    def test_validator_data(self):
        user = UserFactory()
        fraud_data = fraud_factories.BeneficiaryFraudCheckFactory(user=user, type=FraudCheckType.JOUVE)
        fraud_factories.BeneficiaryFraudCheckFactory(user=user, type=FraudCheckType.DMS)

        expected = fraud_api.get_source_data(user)

        assert isinstance(expected, JouveContent)
        assert expected == JouveContent(**fraud_data.resultContent)


class UpsertSuspiciousFraudResultTest:
    def test_do_not_repeat_previous_reason_and_keep_history(self):
        """
        Test that the upsert function does updated the reason when consecutive
        calls do not use the same reason.
        """
        user = UserFactory()
        first_reason = "first reason"
        second_reason = "second reason"

        fraud_api.upsert_suspicious_fraud_result(user, first_reason)
        fraud_api.upsert_suspicious_fraud_result(user, first_reason)
        fraud_api.upsert_suspicious_fraud_result(user, first_reason)
        fraud_api.upsert_suspicious_fraud_result(user, second_reason)
        fraud_api.upsert_suspicious_fraud_result(user, second_reason)
        fraud_api.upsert_suspicious_fraud_result(user, first_reason)
        result = fraud_api.upsert_suspicious_fraud_result(user, first_reason)

        assert fraud_models.BeneficiaryFraudResult.query.count() == 1
        assert result.user == user
        assert result.reason == f"{first_reason} ; {second_reason} ; {first_reason}"
