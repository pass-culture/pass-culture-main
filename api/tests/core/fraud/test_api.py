import datetime
import uuid

from dateutil.relativedelta import relativedelta
import freezegun
import pytest

import pcapi.core.fraud.api as fraud_api
import pcapi.core.fraud.exceptions as fraud_exceptions
import pcapi.core.fraud.factories as fraud_factories
import pcapi.core.fraud.models as fraud_models
from pcapi.core.testing import override_features
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models


@pytest.mark.usefixtures("db_session")
class CommonTest:
    def test_validator_data(self):
        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudCheckFactory(user=user, type=fraud_models.FraudCheckType.DMS)
        fraud_data = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.JOUVE,
            dateCreated=datetime.datetime.utcnow() + datetime.timedelta(seconds=2),
        )

        expected = fraud_api.get_source_data(user)

        assert isinstance(expected, fraud_models.JouveContent)
        assert expected == fraud_models.JouveContent(**fraud_data.resultContent)

    @freezegun.freeze_time("2018-01-01")
    @pytest.mark.parametrize(
        "registration_datetime, user_birth_date, expected_eligibility_type",
        [
            (
                datetime.datetime(year=2017, month=12, day=25),  # User registered at 17
                datetime.date(year=2000, month=1, day=12),  # User is 17 today (nominal case)
                users_models.EligibilityType.UNDERAGE,
            ),
            (
                datetime.datetime(year=2017, month=12, day=25),  # User registered at 17
                datetime.date(year=2000, month=1, day=1),  # User is 18 today
                users_models.EligibilityType.AGE18,
            ),
            (
                datetime.datetime(year=2017, month=12, day=12),  # User registered at 18
                datetime.date(year=1999, month=1, day=1),  # User is 19 today
                users_models.EligibilityType.AGE18,
            ),
            (
                datetime.datetime(year=2018, month=1, day=1),  # User registered at 19
                datetime.date(year=1998, month=12, day=20),  # User is 19 today
                None,
            ),
        ],
    )
    def test_get_eligibility_type_dms(self, registration_datetime, user_birth_date, expected_eligibility_type):
        data = fraud_factories.DMSContentFactory(
            birth_date=user_birth_date,
            registration_datetime=registration_datetime,
        )
        assert fraud_api.get_eligibility_type(data) == expected_eligibility_type

    @pytest.mark.parametrize(
        "id_piece_number",
        [
            "I III1",
            "I I 1JII 11IB I E",
            "",
            "Passeport n: XXXXX",
        ],
    )
    def test_id_piece_number_wrong_format(self, id_piece_number):
        item = fraud_api.validate_id_piece_number_format_fraud_item(id_piece_number)
        assert item.status == fraud_models.FraudStatus.SUSPICIOUS

    @pytest.mark.parametrize(
        "id_piece_number",
        [
            "321070751234",
            "090435303687",
            "Y808952",  # Tunisie
            "U 13884935",  # Turquie
            "AZ 1461290",  # Ancienne id italienne
            "595-0103264-74",  # ID Belge
            "1277367",  # ID Congolaise, Camerounaise, Mauricienne
            "100030595009080004",  # ID Algerienne
            "00000000 0 ZU4",  # portugal format
            "03146310",  # andora CNI format
        ],
    )
    def test_id_piece_number_valid_format(self, id_piece_number):
        item = fraud_api.validate_id_piece_number_format_fraud_item(id_piece_number)
        assert item.status == fraud_models.FraudStatus.OK


@pytest.mark.usefixtures("db_session")
class UpsertFraudResultTest:
    def test_create_on_first_fraud_result(self):
        user = users_factories.UserFactory()
        assert fraud_models.BeneficiaryFraudResult.query.count() == 0

        result = fraud_api.upsert_fraud_result(
            user, fraud_models.FraudStatus.SUSPICIOUS, users_models.EligibilityType.AGE18, "no reason at all"
        )

        assert fraud_models.BeneficiaryFraudResult.query.count() == 1
        assert result.user == user
        assert result.reason == "no reason at all"

    def test_update_on_following_fraud_results(self):
        user = users_factories.UserFactory()
        fraud_api.upsert_fraud_result(user, fraud_models.FraudStatus.OK, users_models.EligibilityType.AGE18)
        assert fraud_models.BeneficiaryFraudResult.query.count() == 1

        fraud_api.upsert_fraud_result(
            user, fraud_models.FraudStatus.SUSPICIOUS, users_models.EligibilityType.AGE18, "no reason at all"
        )
        fraud_api.upsert_fraud_result(
            user, fraud_models.FraudStatus.KO, users_models.EligibilityType.AGE18, "no reason at all"
        )

        assert fraud_models.BeneficiaryFraudResult.query.count() == 1

    @pytest.mark.parametrize("fraud_status", (fraud_models.FraudStatus.SUSPICIOUS, fraud_models.FraudStatus.KO))
    def test_reason_is_mandatory_when_not_ok(self, fraud_status):
        user = users_factories.UserFactory()

        with pytest.raises(ValueError) as excinfo:
            fraud_api.upsert_fraud_result(user, fraud_status, users_models.EligibilityType.AGE18)

        assert str(excinfo.value) == f"a reason should be provided when setting fraud result to {fraud_status.value}"

    def test_do_not_repeat_previous_reason_and_keep_history(self):
        """
        Test that the upsert function does updated the reason when consecutive
        calls do not use the same reason.
        """
        user = users_factories.UserFactory()
        first_reason = "first reason"
        second_reason = "second reason"

        fraud_api.upsert_fraud_result(
            user, fraud_models.FraudStatus.SUSPICIOUS, users_models.EligibilityType.AGE18, first_reason
        )
        fraud_api.upsert_fraud_result(
            user, fraud_models.FraudStatus.SUSPICIOUS, users_models.EligibilityType.AGE18, first_reason
        )
        fraud_api.upsert_fraud_result(
            user, fraud_models.FraudStatus.SUSPICIOUS, users_models.EligibilityType.AGE18, first_reason
        )
        fraud_api.upsert_fraud_result(
            user, fraud_models.FraudStatus.SUSPICIOUS, users_models.EligibilityType.AGE18, second_reason
        )
        fraud_api.upsert_fraud_result(
            user, fraud_models.FraudStatus.SUSPICIOUS, users_models.EligibilityType.AGE18, second_reason
        )
        fraud_api.upsert_fraud_result(
            user, fraud_models.FraudStatus.SUSPICIOUS, users_models.EligibilityType.AGE18, first_reason
        )
        result = fraud_api.upsert_fraud_result(
            user, fraud_models.FraudStatus.SUSPICIOUS, users_models.EligibilityType.AGE18, first_reason
        )

        assert fraud_models.BeneficiaryFraudResult.query.count() == 1
        assert result.user == user
        assert result.reason == f"{first_reason} ; {second_reason} ; {first_reason}"


@pytest.mark.usefixtures("db_session")
class CommonFraudCheckTest:
    def test_duplicate_id_piece_number_ok(self):
        user = users_factories.UserFactory()
        fraud_item = fraud_api._duplicate_id_piece_number_fraud_item(user, "random_id")
        assert fraud_item.status == fraud_models.FraudStatus.OK

    def test_duplicate_id_piece_number_suspicious(self):
        user = users_factories.BeneficiaryGrant18Factory()
        applicant = users_factories.UserFactory()

        fraud_item = fraud_api._duplicate_id_piece_number_fraud_item(applicant, user.idPieceNumber)
        assert fraud_item.status == fraud_models.FraudStatus.SUSPICIOUS

    def test_duplicate_id_piece_number_suspicious_not_self(self):
        applicant = users_factories.UserFactory(idPieceNumber="random_id")

        fraud_item = fraud_api._duplicate_id_piece_number_fraud_item(applicant, applicant.idPieceNumber)
        assert fraud_item.status == fraud_models.FraudStatus.OK

    def test_duplicate_user_fraud_ok(self):
        fraud_item = fraud_api._duplicate_user_fraud_item(
            first_name="Jean", last_name="Michel", birth_date=datetime.date.today(), excluded_user_id=1
        )

        assert fraud_item.status == fraud_models.FraudStatus.OK

    def test_duplicate_user_fraud_suspicious(self):
        user = users_factories.BeneficiaryGrant18Factory()
        fraud_item = fraud_api._duplicate_user_fraud_item(
            first_name=user.firstName,
            last_name=user.lastName,
            birth_date=user.dateOfBirth.date(),
            excluded_user_id=1,
        )

        assert fraud_item.status == fraud_models.FraudStatus.SUSPICIOUS

    def test_duplicate_user_ok_if_self_found(self):
        user = users_factories.BeneficiaryGrant18Factory()
        fraud_item = fraud_api._duplicate_user_fraud_item(
            first_name=user.firstName,
            last_name=user.lastName,
            birth_date=user.dateOfBirth.date(),
            excluded_user_id=user.id,
        )

        assert fraud_item.status == fraud_models.FraudStatus.OK

    @pytest.mark.parametrize(
        "fraud_check_type",
        [fraud_models.FraudCheckType.DMS],
    )
    def test_user_validation_is_beneficiary(self, fraud_check_type):
        user = users_factories.BeneficiaryGrant18Factory()
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(type=fraud_check_type, user=user)

        with pytest.raises(fraud_exceptions.BeneficiaryFraudResultCannotBeDowngraded):
            fraud_api.on_identity_fraud_check_result(user, fraud_check)

    def test_underage_user_validation_is_beneficiary(self):
        user = users_factories.UnderageBeneficiaryFactory()
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.EDUCONNECT,
            user=user,
            resultContent=fraud_factories.EduconnectContentFactory(),
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        with pytest.raises(fraud_exceptions.BeneficiaryFraudResultCannotBeDowngraded):
            fraud_api.on_identity_fraud_check_result(user, fraud_check)

    @pytest.mark.parametrize(
        "fraud_check_type",
        [fraud_models.FraudCheckType.DMS],
    )
    def test_user_validation_has_email_validated(self, fraud_check_type):
        user = users_factories.UserFactory(isEmailValidated=False)
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(type=fraud_check_type, user=user)
        fraud_result = fraud_api.on_identity_fraud_check_result(user, fraud_check)

        assert "L'email de l'utilisateur n'est pas validé" in fraud_result.reason
        assert fraud_result.status == fraud_models.FraudStatus.KO

    @pytest.mark.parametrize("age", [15, 16, 17])
    def test_underage_user_validation_has_email_validated(self, age):
        user = users_factories.UserFactory(isEmailValidated=False)
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.EDUCONNECT,
            user=user,
            resultContent=fraud_factories.EduconnectContentFactory(age=age),
        )
        fraud_result = fraud_api.on_identity_fraud_check_result(user, fraud_check)

        assert "L'email de l'utilisateur n'est pas validé" in fraud_result.reason
        assert fraud_result.status == fraud_models.FraudStatus.KO

    @pytest.mark.parametrize("fraud_check_type", [fraud_models.FraudCheckType.DMS])
    def test_previously_validated_user_with_retry(self, fraud_check_type):
        # The user is already beneficiary, and has already done all the checks but
        # for any circumstances, someone is trying to redo the validation
        # an error should be raised
        user = users_factories.BeneficiaryGrant18Factory()
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(type=fraud_check_type, user=user)

        with pytest.raises(fraud_exceptions.BeneficiaryFraudResultCannotBeDowngraded):
            fraud_api.on_identity_fraud_check_result(user, fraud_check)


@pytest.mark.usefixtures("db_session")
class DMSFraudCheckTest:
    def test_dms_fraud_check(self):
        user = users_factories.UserFactory()
        content = fraud_factories.DMSContentFactory()
        fraud_api.on_dms_fraud_result(user, content)

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(
            user=user, type=fraud_models.FraudCheckType.DMS
        ).one_or_none()

        assert fraud_check.eligibilityType == users_models.EligibilityType.AGE18

        expected_content = fraud_models.DMSContent(**fraud_check.resultContent)
        assert content == expected_content

        fraud_result = fraud_models.BeneficiaryFraudResult.query.filter_by(user=user).one_or_none()
        assert fraud_result.status == fraud_models.FraudStatus.OK

    def test_admin_update_identity_fraud_check_result(self):
        user = users_factories.UserFactory()

        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.DMS,
            user=user,
        )

        fraud_check = fraud_api.admin_update_identity_fraud_check_result(user, "id-piece-number")
        content = fraud_models.DMSContent(**fraud_check.resultContent)
        assert content.id_piece_number == "id-piece-number"


@pytest.mark.usefixtures("db_session")
class UserFraudsterTest:
    @pytest.mark.parametrize(
        "fraud_status,is_fraudster",
        (
            (fraud_models.FraudStatus.OK, False),
            (fraud_models.FraudStatus.KO, True),
            (fraud_models.FraudStatus.SUSPICIOUS, True),
        ),
    )
    def test_is_user_fraudster(self, fraud_status, is_fraudster):
        fraud_result = fraud_factories.BeneficiaryFraudResultFactory(status=fraud_status)
        assert is_fraudster == fraud_api.is_user_fraudster(fraud_result.user)


@pytest.mark.usefixtures("db_session")
class EduconnectFraudTest:
    def test_on_educonnect_result(self):
        fraud_factories.IneHashWhitelistFactory(ine_hash="5ba682c0fc6a05edf07cd8ed0219258f")
        birth_date = (datetime.datetime.today() - relativedelta(years=15, days=5)).date()
        registration_date = datetime.datetime.utcnow() - relativedelta(days=3)  # eligible 15-17
        user = users_factories.UserFactory(dateOfBirth=birth_date)
        fraud_api.on_educonnect_result(
            user,
            fraud_models.EduconnectContent(
                birth_date=birth_date,
                educonnect_id="id-1",
                first_name="Lucy",
                ine_hash="5ba682c0fc6a05edf07cd8ed0219258f",
                last_name="Ellingson",
                registration_datetime=registration_date,
                school_uai="shchool-uai",
                student_level="2212",
            ),
        )

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(
            user=user,
            type=fraud_models.FraudCheckType.EDUCONNECT,
        ).one_or_none()
        assert fraud_check is not None
        assert fraud_check.userId == user.id
        assert fraud_check.type == fraud_models.FraudCheckType.EDUCONNECT
        assert fraud_check.eligibilityType == users_models.EligibilityType.UNDERAGE
        assert fraud_check.source_data().__dict__ == {
            "educonnect_id": "id-1",
            "first_name": "Lucy",
            "ine_hash": "5ba682c0fc6a05edf07cd8ed0219258f",
            "last_name": "Ellingson",
            "birth_date": birth_date,
            "registration_datetime": registration_date,
            "school_uai": "shchool-uai",
            "student_level": "2212",
        }
        assert len(user.beneficiaryFraudResults) == 1
        assert user.beneficiaryFraudResults[0].status == fraud_models.FraudStatus.OK

        # If the user logs in again with another educonnect account, update the fraud check
        fraud_factories.IneHashWhitelistFactory(ine_hash="0000")
        fraud_api.on_educonnect_result(
            user,
            fraud_models.EduconnectContent(
                birth_date=birth_date,
                educonnect_id="id-1",
                first_name="Lucille",
                ine_hash="0000",
                last_name="Ellingson",
                registration_datetime=registration_date,
                school_uai="shchool-uai",
                student_level="2212",
            ),
        )

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(
            user=user,
            type=fraud_models.FraudCheckType.EDUCONNECT,
        ).one_or_none()
        assert fraud_check.userId == user.id
        assert fraud_check.type == fraud_models.FraudCheckType.EDUCONNECT
        assert fraud_check.eligibilityType == users_models.EligibilityType.UNDERAGE
        assert fraud_check.source_data().__dict__ == {
            "educonnect_id": "id-1",
            "first_name": "Lucille",
            "ine_hash": "0000",
            "last_name": "Ellingson",
            "birth_date": birth_date,
            "registration_datetime": registration_date,
            "school_uai": "shchool-uai",
            "student_level": "2212",
        }
        assert user.beneficiaryFraudResults[0].status == fraud_models.FraudStatus.OK

    @pytest.mark.parametrize("age", [14, 18])
    def test_age_fraud_check_ko(self, age):
        user = users_factories.UserFactory()
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.EDUCONNECT,
            resultContent=fraud_factories.EduconnectContentFactory(age=age),
            user=user,
        )
        result = fraud_api.educonnect_fraud_checks(user, beneficiary_fraud_check=fraud_check)

        age_check = next(
            fraud_check
            for fraud_check in result
            if fraud_check.reason_code == fraud_models.FraudReasonCode.AGE_NOT_VALID
        )
        assert age_check.status == fraud_models.FraudStatus.KO
        assert (
            age_check.detail == f"L'age de l'utilisateur est invalide ({age} ans). Il devrait être parmi [15, 16, 17]"
        )

    @pytest.mark.parametrize("age", [15, 16, 17])
    def test_age_fraud_check_ok(self, age):
        user = users_factories.UserFactory()
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.EDUCONNECT,
            resultContent=fraud_factories.EduconnectContentFactory(age=age),
        )
        result = fraud_api.educonnect_fraud_checks(user, beneficiary_fraud_check=fraud_check)

        age_check = next(
            (
                fraud_item
                for fraud_item in result
                if fraud_item.reason_code == fraud_models.FraudReasonCode.AGE_NOT_VALID
            ),
            None,
        )
        assert not age_check

    @override_features(ENABLE_NATIVE_EAC_INDIVIDUAL=True)
    def test_duplicates_fraud_checks(self):
        already_existing_user = users_factories.UnderageBeneficiaryFactory(subscription_age=15)
        user = users_factories.UserFactory()
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.EDUCONNECT,
            resultContent=fraud_factories.EduconnectContentFactory(
                first_name=already_existing_user.firstName,
                last_name=already_existing_user.lastName,
                birth_date=already_existing_user.dateOfBirth,
            ),
            user=user,
        )
        result = fraud_api.educonnect_fraud_checks(user, fraud_check)

        duplicate_check = next(
            fraud_item for fraud_item in result if fraud_item.reason_code == fraud_models.FraudReasonCode.DUPLICATE_USER
        )

        assert duplicate_check.status == fraud_models.FraudStatus.SUSPICIOUS
        assert duplicate_check.detail == f"Duplicat de l'utilisateur {already_existing_user.id}"

    @override_features(ENABLE_NATIVE_EAC_INDIVIDUAL=True)
    def test_same_user_is_not_duplicate(self):
        underage_user = users_factories.UnderageBeneficiaryFactory(subscription_age=15)

        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.EDUCONNECT,
            resultContent=fraud_factories.EduconnectContentFactory(
                first_name=underage_user.firstName,
                last_name=underage_user.lastName,
                birth_date=underage_user.dateOfBirth,
            ),
            user=underage_user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        result = fraud_api.educonnect_fraud_checks(underage_user, fraud_check)

        assert not any(fraud_item.reason_code == fraud_models.FraudReasonCode.DUPLICATE_USER for fraud_item in result)

    @override_features(ENABLE_NATIVE_EAC_INDIVIDUAL=True)
    def test_ine_duplicates_fraud_checks(self):
        fraud_factories.IneHashWhitelistFactory(ine_hash="ylwavk71o3jiwyla83fxk5pcmmu0ws01")
        same_ine_user = users_factories.UnderageBeneficiaryFactory(ineHash="ylwavk71o3jiwyla83fxk5pcmmu0ws01")
        user_in_validation = users_factories.UserFactory()
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.EDUCONNECT,
            resultContent=fraud_factories.EduconnectContentFactory(ine_hash=same_ine_user.ineHash),
            user=user_in_validation,
        )
        result = fraud_api.educonnect_fraud_checks(user_in_validation, fraud_check)

        duplicate_ine_check = next(
            fraud_check
            for fraud_check in result
            if fraud_check.reason_code == fraud_models.FraudReasonCode.DUPLICATE_INE
        )
        assert duplicate_ine_check.status == fraud_models.FraudStatus.SUSPICIOUS
        assert (
            duplicate_ine_check.detail
            == f"L'INE ylwavk71o3jiwyla83fxk5pcmmu0ws01 est déjà pris par l'utilisateur {same_ine_user.id}"
        )

    @override_features(ENABLE_NATIVE_EAC_INDIVIDUAL=True)
    def test_ine_duplicates_fraud_checks_self_ine(self):
        fraud_factories.IneHashWhitelistFactory(ine_hash="ylwavk71o3jiwyla83fxk5pcmmu0ws01")
        user_in_validation = users_factories.UserFactory(ineHash="ylwavk71o3jiwyla83fxk5pcmmu0ws01")
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.EDUCONNECT,
            resultContent=fraud_factories.EduconnectContentFactory(ine_hash=user_in_validation.ineHash),
            user=user_in_validation,
        )
        result = fraud_api.educonnect_fraud_checks(user_in_validation, fraud_check)

        duplicate_ine_check = next(
            (
                fraud_check
                for fraud_check in result
                if fraud_check.reason_code == fraud_models.FraudReasonCode.INE_NOT_WHITELISTED
            ),
            None,
        )
        assert duplicate_ine_check is None

    @override_features(ENABLE_NATIVE_EAC_INDIVIDUAL=True)
    def test_ine_whitelisted_fraud_checks_pass(self):
        user = users_factories.UserFactory()
        fraud_factories.IneHashWhitelistFactory(ine_hash="identifiantWhitelisté1")
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.EDUCONNECT,
            resultContent=fraud_factories.EduconnectContentFactory(ine_hash="identifiantWhitelisté1"),
            user=user,
        )
        result = fraud_api.educonnect_fraud_checks(user, fraud_check)

        duplicate_ine_check = next(
            (
                fraud_check
                for fraud_check in result
                if fraud_check.reason_code == fraud_models.FraudReasonCode.INE_NOT_WHITELISTED
            ),
            None,
        )
        assert duplicate_ine_check is None

    @override_features(ENABLE_NATIVE_EAC_INDIVIDUAL=True)
    def test_ine_whitelisted_fraud_checks_fail(self):
        user = users_factories.UserFactory()
        fraud_factories.IneHashWhitelistFactory(ine_hash="identifiantWhitelisté1")
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.EDUCONNECT,
            resultContent=fraud_factories.EduconnectContentFactory(ine_hash="identifiantWhitelisté2"),
        )
        result = fraud_api.educonnect_fraud_checks(user, fraud_check)

        duplicate_ine_check = next(
            fraud_check
            for fraud_check in result
            if fraud_check.reason_code == fraud_models.FraudReasonCode.INE_NOT_WHITELISTED
        )
        assert duplicate_ine_check.status == fraud_models.FraudStatus.SUSPICIOUS


@pytest.mark.usefixtures("db_session")
class HasUserPerformedIdentityCheckTest:
    @pytest.mark.parametrize(
        "age, eligibility_type",
        [
            (15, users_models.EligibilityType.UNDERAGE),
            (16, users_models.EligibilityType.UNDERAGE),
            (17, users_models.EligibilityType.UNDERAGE),
            (18, users_models.EligibilityType.AGE18),
        ],
    )
    @pytest.mark.parametrize("check_type", [fraud_models.FraudCheckType.JOUVE, fraud_models.FraudCheckType.UBBLE])
    def test_has_user_performed_identity_check(self, age, eligibility_type, check_type):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime.now() - relativedelta(years=age, months=1))
        fraud_factories.BeneficiaryFraudCheckFactory(type=check_type, user=user, eligibilityType=eligibility_type)

        assert fraud_api.has_user_performed_identity_check(user)
        assert fraud_api.has_user_performed_ubble_check(user) == (check_type == fraud_models.FraudCheckType.UBBLE)

    def test_has_user_performed_identity_check_turned_18(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime.now() - relativedelta(years=18, months=1))
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE, user=user, eligibilityType=users_models.EligibilityType.UNDERAGE
        )

        assert fraud_api.has_user_performed_identity_check(user)
        assert not fraud_api.has_user_performed_ubble_check(user)

    def test_has_user_performed_identity_check_without_identity_fraud_check(self):
        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudCheckFactory(type=fraud_models.FraudCheckType.USER_PROFILING, user=user)

        assert not fraud_api.has_user_performed_identity_check(user)

    def test_has_user_performed_identity_check_status_initiated(self):
        user = users_factories.UserFactory()
        ubble_content = fraud_factories.UbbleContentFactory(
            status=fraud_models.ubble_models.UbbleIdentificationStatus.INITIATED
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            user=user,
            resultContent=ubble_content,
            status=fraud_models.FraudCheckStatus.PENDING,
        )


@pytest.mark.usefixtures("db_session")
class FraudCheckLifeCycleTest:
    @pytest.mark.parametrize(
        "check_type",
        [
            fraud_models.FraudCheckType.DMS,
            fraud_models.FraudCheckType.EDUCONNECT,
            fraud_models.FraudCheckType.JOUVE,
            fraud_models.FraudCheckType.UBBLE,
        ],
    )
    def test_start_fraud_check(self, check_type):
        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudCheckFactory(type=check_type)
        factory_class = fraud_factories.FRAUD_CHECK_TYPE_MODEL_ASSOCIATION[check_type]

        source_data = factory_class()

        fraud_check = fraud_api.start_fraud_check(user, str(uuid.uuid4()), source_data)

        assert fraud_check.status == fraud_models.FraudCheckStatus.PENDING
        assert fraud_models.BeneficiaryFraudCheck.query.filter_by(user=user).count() == 1

    @pytest.mark.parametrize(
        "check_type",
        [
            fraud_models.FraudCheckType.DMS,
            fraud_models.FraudCheckType.EDUCONNECT,
            fraud_models.FraudCheckType.JOUVE,
            fraud_models.FraudCheckType.UBBLE,
        ],
    )
    def test_start_fraud_check_already_pending(self, check_type):
        user = users_factories.UserFactory()
        application_id = str(uuid.uuid4())
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=check_type, thirdPartyId=application_id, status=fraud_models.FraudCheckStatus.PENDING
        )
        factory_class = fraud_factories.FRAUD_CHECK_TYPE_MODEL_ASSOCIATION[check_type]

        source_data = factory_class()

        with pytest.raises(fraud_exceptions.ApplicationValidationAlreadyStarted):
            fraud_api.start_fraud_check(user, application_id, source_data)

        assert (
            fraud_models.BeneficiaryFraudCheck.query.filter_by(
                user=user,
                type=check_type,
            ).count()
            == 1
        )

    @pytest.mark.parametrize(
        "check_type",
        [
            fraud_models.FraudCheckType.DMS,
            fraud_models.FraudCheckType.EDUCONNECT,
            fraud_models.FraudCheckType.JOUVE,
            fraud_models.FraudCheckType.UBBLE,
        ],
    )
    @pytest.mark.parametrize(
        "closed_state",
        [
            fraud_models.FraudCheckStatus.OK,
            fraud_models.FraudCheckStatus.KO,
            fraud_models.FraudCheckStatus.SUSPICIOUS,
        ],
    )
    def test_start_fraud_check_with_other_check_finished(self, check_type, closed_state):
        user = users_factories.UserFactory()
        application_id = str(uuid.uuid4())
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=check_type, thirdPartyId=application_id, status=closed_state
        )
        factory_class = fraud_factories.FRAUD_CHECK_TYPE_MODEL_ASSOCIATION[check_type]

        source_data = factory_class()
        fraud_api.start_fraud_check(user, str(uuid.uuid4()), source_data)
        assert (
            fraud_models.BeneficiaryFraudCheck.query.filter_by(
                user=user,
                type=check_type,
            ).count()
            == 2
        )

    @pytest.mark.parametrize(
        "check_type",
        [
            fraud_models.FraudCheckType.DMS,
            fraud_models.FraudCheckType.EDUCONNECT,
            fraud_models.FraudCheckType.JOUVE,
            fraud_models.FraudCheckType.UBBLE,
        ],
    )
    def test_mark_fraud_check_failed(self, check_type):
        user = users_factories.UserFactory()
        application_id = str(uuid.uuid4())

        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=check_type,
            status=fraud_models.FraudCheckStatus.PENDING,
            thirdPartyId=application_id,
        )
        fraud_api.mark_fraud_check_failed(
            user,
            application_id,
            fraud_check.source_data(),
            reasons=[fraud_models.FraudReasonCode.DUPLICATE_USER],
        )

        assert fraud_check.status == fraud_models.FraudCheckStatus.KO
        assert (
            fraud_models.BeneficiaryFraudCheck.query.filter_by(
                user=user,
                type=check_type,
            ).count()
            == 1
        )

    @pytest.mark.parametrize(
        "check_type,eligibility_type",
        [
            (fraud_models.FraudCheckType.DMS, users_models.EligibilityType.AGE18),
            (fraud_models.FraudCheckType.EDUCONNECT, users_models.EligibilityType.UNDERAGE),  # age = 15 in factory
            (fraud_models.FraudCheckType.JOUVE, users_models.EligibilityType.AGE18),
            (fraud_models.FraudCheckType.UBBLE, users_models.EligibilityType.AGE18),
        ],
    )
    def test_mark_fraud_check_failed_unexistant_previous_check(self, check_type, eligibility_type):
        user = users_factories.UserFactory()
        application_id = str(uuid.uuid4())

        factory_class = fraud_factories.FRAUD_CHECK_TYPE_MODEL_ASSOCIATION[check_type]
        source_data = factory_class()

        fraud_api.mark_fraud_check_failed(
            user,
            application_id,
            source_data,
            reasons=[fraud_models.FraudReasonCode.DUPLICATE_USER],
        )

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.first()
        assert fraud_check.status == fraud_models.FraudCheckStatus.KO
        assert fraud_check.eligibilityType == eligibility_type
