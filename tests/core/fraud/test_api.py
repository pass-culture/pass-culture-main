import datetime
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
import pytest

import pcapi.core.fraud.api as fraud_api
import pcapi.core.fraud.factories as fraud_factories
import pcapi.core.fraud.models as fraud_models
from pcapi.core.testing import override_features
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models
from pcapi.flask_app import db


@pytest.mark.usefixtures("db_session")
class JouveFraudCheckTest:
    application_id = 35
    user_email = "tour.de.passpass@example.com"
    eighteen_years_in_the_past = datetime.datetime.now() - relativedelta(years=18, months=4)

    JOUVE_CONTENT = {
        "activity": "Etudiant",
        "address": "",
        "birthDateTxt": f"{eighteen_years_in_the_past:%d/%m/%Y}",
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
    def test_jouve_update(self, _get_raw_content, client):
        user = users_factories.UserFactory(
            hasCompletedIdCheck=True,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            dateOfBirth=self.eighteen_years_in_the_past,
            email=self.user_email,
        )
        _get_raw_content.return_value = self.JOUVE_CONTENT

        response = client.post("/beneficiaries/application_update", json={"id": self.application_id})
        assert response.status_code == 200

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(
            user=user, type=fraud_models.FraudCheckType.JOUVE
        ).first()
        fraud_result = fraud_models.BeneficiaryFraudResult.query.filter_by(user=user).first()
        jouve_fraud_content = fraud_models.JouveContent(**fraud_check.resultContent)

        assert jouve_fraud_content.bodyPieceNumber == "140767100016"
        assert fraud_check.dateCreated
        assert fraud_check.thirdPartyId == "35"
        assert fraud_result.status == fraud_models.FraudStatus.OK

        db.session.refresh(user)
        assert user.isBeneficiary

    @patch("pcapi.connectors.beneficiaries.jouve_backend._get_raw_content")
    def test_jouve_update_duplicate_user(self, _get_raw_content, client):
        existing_user = users_factories.BeneficiaryGrant18Factory(
            firstName="Christophe",
            lastName="Dupo",
            dateOfBirth=self.eighteen_years_in_the_past,
            idPieceNumber="140767100016",
        )
        user = users_factories.UserFactory(
            hasCompletedIdCheck=True,
            isBeneficiary=False,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            dateOfBirth=self.eighteen_years_in_the_past,
            email=self.user_email,
        )
        _get_raw_content.return_value = self.JOUVE_CONTENT

        response = client.post("/beneficiaries/application_update", json={"id": self.application_id})
        assert response.status_code == 200

        fraud_result = fraud_models.BeneficiaryFraudResult.query.filter_by(user=user).first()

        assert fraud_result.status == fraud_models.FraudStatus.SUSPICIOUS
        assert (
            fraud_result.reason
            == f"Duplicat de l'utilisateur {existing_user.id} ; Le n° de cni 140767100016 est déjà pris par l'utilisateur {existing_user.id}"
        )

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
            "Passeport n: XXXXX",
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
        user = users_factories.UserFactory(isBeneficiary=False)
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
        user = users_factories.UserFactory(isBeneficiary=False)

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

    #     user = users_factories.users_factories.UserFactory(
    #         hasCompletedIdCheck=True,
    #         isBeneficiary=False,
    #         phoneValidationStatus=PhoneValidationStatusType.VALIDATED,
    #         dateOfBirth=datetime(2002, 6, 8),
    #         email=self.user_email,
    #     )
    #     _get_raw_content.return_value = self.JOUVE_CONTENT | {"serviceCodeCtrl": "KO", "bodyFirstnameLevel": "30"}

    #     response = client.post("/beneficiaries/application_update", json={"id": self.application_id})
    #     assert response.status_code == 200

    #     fraud_result = fraud_models.BeneficiaryFraudResult.query.filter_by(user=user).first()

    #     assert fraud_result.status == fraud_models.FraudStatus.KO
    #     assert (
    #         fraud_result.reason
    #         == "Le champ serviceCodeCtrl est KO ; Le champ bodyFirstnameLevel a le score 30 (minimum 50)"
    #     )

    #     db.session.refresh(user)
    #     assert not user.isBeneficiary


@pytest.mark.usefixtures("db_session")
class CommonTest:
    def test_validator_data(self):
        user = users_factories.UserFactory()
        fraud_data = fraud_factories.BeneficiaryFraudCheckFactory(user=user, type=fraud_models.FraudCheckType.JOUVE)
        fraud_factories.BeneficiaryFraudCheckFactory(user=user, type=fraud_models.FraudCheckType.DMS)

        expected = fraud_api.get_source_data(user)

        assert isinstance(expected, fraud_models.JouveContent)
        assert expected == fraud_models.JouveContent(**fraud_data.resultContent)


@pytest.mark.usefixtures("db_session")
class UpsertSuspiciousFraudResultTest:
    def test_do_not_repeat_previous_reason_and_keep_history(self):
        """
        Test that the upsert function does updated the reason when consecutive
        calls do not use the same reason.
        """
        user = users_factories.UserFactory()
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


@pytest.mark.usefixtures("db_session")
class CommonFraudCheckTest:
    def test_duplicate_id_piece_number_ok(self):
        fraud_item = fraud_api._duplicate_id_piece_number_fraud_item("random_id")
        assert fraud_item.status == fraud_models.FraudStatus.OK

    def test_duplicate_id_piece_number_suspicious(self):
        user = users_factories.BeneficiaryGrant18Factory()

        fraud_item = fraud_api._duplicate_id_piece_number_fraud_item(user.idPieceNumber)
        assert fraud_item.status == fraud_models.FraudStatus.SUSPICIOUS

    def test_duplicate_user_fraud_ok(self):
        fraud_item = fraud_api._duplicate_user_fraud_item(
            first_name="Jean", last_name="Michel", birth_date=datetime.date.today()
        )

        assert fraud_item.status == fraud_models.FraudStatus.OK

    def test_duplicate_user_fraud_suspicious(self):
        user = users_factories.BeneficiaryGrant18Factory()
        fraud_item = fraud_api._duplicate_user_fraud_item(
            first_name=user.firstName, last_name=user.lastName, birth_date=user.dateOfBirth.date()
        )

        assert fraud_item.status == fraud_models.FraudStatus.SUSPICIOUS

    @pytest.mark.parametrize("fraud_check_type", [fraud_models.FraudCheckType.DMS, fraud_models.FraudCheckType.JOUVE])
    def test_user_validation_is_beneficiary(self, fraud_check_type):
        user = users_factories.BeneficiaryGrant18Factory()
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(type=fraud_check_type, user=user)
        fraud_result = fraud_api.on_identity_fraud_check_result(user, fraud_check)

        assert "L'utilisateur est déjà bénéficiaire" in fraud_result.reason
        assert fraud_result.status == fraud_models.FraudStatus.KO

    @pytest.mark.parametrize("fraud_check_type", [fraud_models.FraudCheckType.DMS, fraud_models.FraudCheckType.JOUVE])
    def test_user_validation_has_email_validated(self, fraud_check_type):
        user = users_factories.UserFactory(isBeneficiary=False, isEmailValidated=False)
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(type=fraud_check_type, user=user)
        fraud_result = fraud_api.on_identity_fraud_check_result(user, fraud_check)

        assert "L'email de l'utilisateur n'est pas validé" in fraud_result.reason
        assert fraud_result.status == fraud_models.FraudStatus.KO

    @override_features(FORCE_PHONE_VALIDATION=True)
    @pytest.mark.parametrize(
        "phone_status",
        [
            users_models.PhoneValidationStatusType.BLOCKED_TOO_MANY_CODE_SENDINGS,
            users_models.PhoneValidationStatusType.BLOCKED_TOO_MANY_CODE_VERIFICATION_TRIES,
        ],
    )
    @pytest.mark.parametrize("fraud_check_type", [fraud_models.FraudCheckType.DMS, fraud_models.FraudCheckType.JOUVE])
    def test_user_validation_has_phone_validated(self, phone_status, fraud_check_type):
        user = users_factories.UserFactory(
            isBeneficiary=False,
            isEmailValidated=True,
            phoneValidationStatus=phone_status,
        )
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(type=fraud_check_type, user=user)
        fraud_result = fraud_api.on_identity_fraud_check_result(user, fraud_check)

        assert "Le n° de téléphone de l'utilisateur n'est pas validé" in fraud_result.reason
        assert fraud_result.status == fraud_models.FraudStatus.KO

    @pytest.mark.parametrize("fraud_check_type", [fraud_models.FraudCheckType.DMS, fraud_models.FraudCheckType.JOUVE])
    def test_previously_validated_user_with_retry(self, fraud_check_type):
        # The user is already beneficiary, and has already done all the checks but
        # for any circumstances, someone is trying to redo the validation
        user = users_factories.BeneficiaryGrant18Factory()
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(type=fraud_check_type, user=user)
        fraud_result = fraud_factories.BeneficiaryFraudResultFactory(user=user, status=fraud_models.FraudStatus.OK)

        fraud_api.on_identity_fraud_check_result(user, fraud_check)

        assert fraud_result.status == fraud_models.FraudStatus.OK


@pytest.mark.usefixtures("db_session")
class DMSFraudCheckTest:
    def test_dms_fraud_check(self):
        user = users_factories.UserFactory(isBeneficiary=False)
        content = fraud_factories.DMSContentFactory()
        fraud_api.on_dms_fraud_check(user, content)

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(
            user=user, type=fraud_models.FraudCheckType.DMS
        ).one_or_none()

        expected_content = fraud_models.DMSContent(**fraud_check.resultContent)
        assert content == expected_content

        fraud_result = fraud_models.BeneficiaryFraudResult.query.filter_by(user=user).one_or_none()
        assert fraud_result.status == fraud_models.FraudStatus.OK
