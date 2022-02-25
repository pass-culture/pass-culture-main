import datetime

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time
import pytest

import pcapi.core.fraud.api as fraud_api
import pcapi.core.fraud.factories as fraud_factories
import pcapi.core.fraud.models as fraud_models
from pcapi.core.fraud.ubble import api as ubble_fraud_api
import pcapi.core.fraud.ubble.models as ubble_fraud_models
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


def filter_invalid_fraud_items_to_reason_code(
    fraud_items: list[fraud_models.FraudItem],
) -> list[fraud_models.FraudItem]:
    return [item.reason_code for item in fraud_items if item.status != fraud_models.FraudStatus.OK]


@pytest.mark.usefixtures("db_session")
class CommonFraudCheckTest:
    def filter_invalid_fraud_items_to_reason_code(
        self, fraud_items: list[fraud_models.FraudItem]
    ) -> list[fraud_models.FraudItem]:
        return [item.reason_code for item in fraud_items if item.status != fraud_models.FraudStatus.OK]

    def test_duplicate_id_piece_number_ok(self):
        user = users_factories.UserFactory()
        fraud_item = fraud_api.duplicate_id_piece_number_fraud_item(user, "random_id")
        assert fraud_item.status == fraud_models.FraudStatus.OK

    def test_duplicate_id_piece_number_suspicious(self):
        user = users_factories.BeneficiaryGrant18Factory()
        applicant = users_factories.UserFactory()

        fraud_item = fraud_api.duplicate_id_piece_number_fraud_item(applicant, user.idPieceNumber)
        assert fraud_item.status == fraud_models.FraudStatus.SUSPICIOUS

    def test_duplicate_id_piece_number_suspicious_not_self(self):
        applicant = users_factories.UserFactory(idPieceNumber="random_id")

        fraud_item = fraud_api.duplicate_id_piece_number_fraud_item(applicant, applicant.idPieceNumber)
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

    def test_underage_user_validation_is_beneficiary(self):
        user = users_factories.UnderageBeneficiaryFactory()
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.EDUCONNECT,
            user=user,
            resultContent=fraud_factories.EduconnectContentFactory(),
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        fraud_items = fraud_api.on_identity_fraud_check_result(user, fraud_check)
        invalid_codes = filter_invalid_fraud_items_to_reason_code(fraud_items)
        assert fraud_models.FraudReasonCode.ALREADY_HAS_ACTIVE_DEPOSIT in invalid_codes
        assert fraud_models.FraudReasonCode.ALREADY_BENEFICIARY in invalid_codes

    @pytest.mark.parametrize(
        "fraud_check_type",
        [fraud_models.FraudCheckType.DMS],
    )
    def test_user_validation_has_email_validated(self, fraud_check_type):
        user = users_factories.UserFactory(isEmailValidated=False)
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(type=fraud_check_type, user=user)
        fraud_items = fraud_api.on_identity_fraud_check_result(user, fraud_check)

        invalid_codes = filter_invalid_fraud_items_to_reason_code(fraud_items)
        assert len(invalid_codes) == 1
        assert fraud_models.FraudReasonCode.EMAIL_NOT_VALIDATED in invalid_codes

    @pytest.mark.parametrize("age", [15, 16, 17])
    def test_underage_user_validation_has_email_validated(self, age):
        user = users_factories.UserFactory(isEmailValidated=False)
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.EDUCONNECT,
            user=user,
            resultContent=fraud_factories.EduconnectContentFactory(age=age),
        )
        fraud_items = fraud_api.on_identity_fraud_check_result(user, fraud_check)

        invalid_codes = filter_invalid_fraud_items_to_reason_code(fraud_items)
        assert fraud_models.FraudReasonCode.EMAIL_NOT_VALIDATED in invalid_codes

    @pytest.mark.parametrize("fraud_check_type", [fraud_models.FraudCheckType.DMS])
    def test_previously_validated_user_with_retry(self, fraud_check_type):
        # The user is already beneficiary, and has already done all the checks but
        # for any circumstances, someone is trying to redo the validation
        # an error should be raised
        user = users_factories.BeneficiaryGrant18Factory()
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(type=fraud_check_type, user=user)
        fraud_items = fraud_api.on_identity_fraud_check_result(user, fraud_check)
        invalid_codes = filter_invalid_fraud_items_to_reason_code(fraud_items)
        assert fraud_models.FraudReasonCode.ALREADY_HAS_ACTIVE_DEPOSIT in invalid_codes
        assert fraud_models.FraudReasonCode.ALREADY_BENEFICIARY in invalid_codes


@pytest.mark.usefixtures("db_session")
class DMSFraudCheckTest:
    def test_dms_fraud_check(self):
        user = users_factories.UserFactory()
        content = fraud_factories.DMSContentFactory()
        fraud_check = fraud_api.on_dms_fraud_result(user, content)
        assert fraud_check.eligibilityType == users_models.EligibilityType.AGE18

        expected_content = fraud_check.source_data()
        assert content == expected_content

    def test_dms_update_eligibility(self):
        birth_date = datetime.datetime.utcnow() - relativedelta(years=17, months=1)
        user = users_factories.UserFactory(dateOfBirth=birth_date)
        assert user.eligibility == users_models.EligibilityType.UNDERAGE
        content = fraud_factories.DMSContentFactory(
            birth_date=datetime.datetime.utcnow() - relativedelta(years=18, months=1)
        )

        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.DMS,
            eligibilityType=user.eligibility,
            thirdPartyId=str(content.application_id),
        )
        fraud_api.on_dms_fraud_result(user, content)

        assert fraud_check.eligibilityType == users_models.EligibilityType.AGE18


@pytest.mark.usefixtures("db_session")
class EduconnectFraudTest:
    def test_on_educonnect_result(self):
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
        assert fraud_check.status == fraud_models.FraudCheckStatus.OK
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

        # If the user logs in again with another educonnect account, create another fraud check
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

        fraud_check = (
            fraud_models.BeneficiaryFraudCheck.query.filter_by(
                user=user,
                type=fraud_models.FraudCheckType.EDUCONNECT,
            )
            .filter(fraud_models.BeneficiaryFraudCheck.id != fraud_check.id)
            .first()
        )
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
            age_check.detail == f"L'âge de l'utilisateur est invalide ({age} ans). Il devrait être parmi [15, 16, 17]"
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

        # Do not call educonnect_fraud_checks directly because duplicate check is common
        fraud_items = fraud_api.on_identity_fraud_check_result(user, fraud_check)

        invalid_item = [
            item for item in fraud_items if item.reason_code == fraud_models.FraudReasonCode.DUPLICATE_USER
        ][0]
        assert f"Duplicat de l'utilisateur {already_existing_user.id}" in invalid_item.detail
        assert invalid_item.status == fraud_models.FraudStatus.SUSPICIOUS

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

    def test_ine_duplicates_fraud_checks(self):
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

    def test_ine_duplicates_fraud_checks_self_ine(self):
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


@pytest.mark.usefixtures("db_session")
class HasUserPerformedIdentityCheckTest:
    def test_has_not_performed(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime.now() - relativedelta(years=18, months=1))
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.JOUVE, eligibilityType=users_models.EligibilityType.UNDERAGE
        )

        assert not fraud_api.has_user_performed_identity_check(user)

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
    @pytest.mark.parametrize("status", [fraud_models.FraudCheckStatus.PENDING, fraud_models.FraudCheckStatus.OK])
    def test_has_user_performed_identity_check(self, age, eligibility_type, check_type, status):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime.now() - relativedelta(years=age, months=1))
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=check_type, user=user, status=status, eligibilityType=eligibility_type
        )

        assert fraud_api.has_user_performed_identity_check(user)
        assert ubble_fraud_api.is_user_allowed_to_perform_ubble_check(user, user.eligibility) == (
            check_type != fraud_models.FraudCheckType.UBBLE
        )

    def test_has_user_performed_identity_check_turned_18(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime.now() - relativedelta(years=18, months=1))
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE, user=user, eligibilityType=users_models.EligibilityType.UNDERAGE
        )

        assert not fraud_api.has_user_performed_identity_check(user)
        assert ubble_fraud_api.is_user_allowed_to_perform_ubble_check(user, user.eligibility)

    def test_has_user_performed_identity_check_without_identity_fraud_check(self):
        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudCheckFactory(type=fraud_models.FraudCheckType.USER_PROFILING, user=user)

        assert not fraud_api.has_user_performed_identity_check(user)

    def test_has_user_performed_identity_check_status_initiated(self):
        user = users_factories.UserFactory()
        ubble_content = fraud_factories.UbbleContentFactory(
            status=ubble_fraud_models.UbbleIdentificationStatus.INITIATED
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            user=user,
            resultContent=ubble_content,
            status=fraud_models.FraudCheckStatus.PENDING,
        )

    def test_has_user_performed_identity_check_ubble_suspicious(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime.now() - relativedelta(years=18, months=1))
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            user=user,
            status=fraud_models.FraudCheckStatus.SUSPICIOUS,
            reasonCodes=[fraud_models.FraudReasonCode.ID_CHECK_EXPIRED],
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        # Suspicous => Retry allowed
        assert not fraud_api.has_user_performed_identity_check(user)
        assert ubble_fraud_api.is_user_allowed_to_perform_ubble_check(user, user.eligibility)

    def test_has_user_performed_identity_check_ubble_suspicious_x3(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime.now() - relativedelta(years=18, months=1))
        for _ in range(3):
            fraud_factories.BeneficiaryFraudCheckFactory(
                type=fraud_models.FraudCheckType.UBBLE,
                user=user,
                status=fraud_models.FraudCheckStatus.SUSPICIOUS,
                reasonCodes=[fraud_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE],
                eligibilityType=users_models.EligibilityType.AGE18,
            )

        # Suspicous but all retries already performed
        assert fraud_api.has_user_performed_identity_check(user)
        assert not ubble_fraud_api.is_user_allowed_to_perform_ubble_check(user, user.eligibility)

    def test_has_user_performed_identity_check_ubble_ko(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime.now() - relativedelta(years=18, months=1))
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            user=user,
            status=fraud_models.FraudCheckStatus.KO,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        # Retry not allowed
        assert fraud_api.has_user_performed_identity_check(user)
        assert not ubble_fraud_api.is_user_allowed_to_perform_ubble_check(user, user.eligibility)

    def test_user_beneficiary(self):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.now() - relativedelta(years=20, months=1),
            roles=[users_models.UserRole.BENEFICIARY],
        )
        assert fraud_api.has_user_performed_identity_check(user)

    def test_user_not_eligible_anymore_but_has_performed(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime.now() - relativedelta(years=20, months=1))
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.JOUVE, eligibilityType=users_models.EligibilityType.AGE18
        )

        assert fraud_api.has_user_performed_identity_check(user)


@pytest.mark.usefixtures("db_session")
class DecideEligibilityTest:
    @freeze_time("2020-01-02")
    def test_19yo_is_eligible_if_application_at_18_yo(self):
        birth_date = datetime.date(year=2001, month=1, day=1)
        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            eligibilityType=users_models.EligibilityType.AGE18,
            dateCreated=datetime.datetime(year=2019, month=1, day=2),
        )

        dms_content = fraud_factories.DMSContentFactory(
            registration_datetime=datetime.datetime(year=2020, month=1, day=2), birth_date=birth_date
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.DMS, resultContent=dms_content
        )

        result = fraud_api.decide_eligibility(user, dms_content)
        assert result == users_models.EligibilityType.AGE18

    @freeze_time("2020-01-02")
    def test_19yo_not_eligible(self):
        birth_date = datetime.date(year=2001, month=1, day=1)
        user = users_factories.UserFactory()

        dms_content = fraud_factories.DMSContentFactory(
            registration_datetime=datetime.datetime(year=2020, month=1, day=2), birth_date=birth_date
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.DMS, resultContent=dms_content
        )

        result = fraud_api.decide_eligibility(user, dms_content)
        assert result == None

    @freeze_time("2020-01-02")
    def test_19yo_ex_underage_not_eligible(self):
        birth_date = datetime.date(year=2001, month=1, day=1)
        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            dateCreated=datetime.date(year=2017, month=1, day=1),
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        dms_content = fraud_factories.DMSContentFactory(
            registration_datetime=datetime.datetime(year=2020, month=1, day=2), birth_date=birth_date
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.DMS, resultContent=dms_content
        )

        result = fraud_api.decide_eligibility(user, dms_content)
        assert result == None

    @freeze_time("2020-01-02")
    def test_18yo_eligible(self):
        birth_date = datetime.date(year=2001, month=1, day=1)
        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            eligibilityType=users_models.EligibilityType.AGE18,
            dateCreated=datetime.datetime(year=2019, month=1, day=2),
        )
        dms_content = fraud_factories.DMSContentFactory(
            registration_datetime=datetime.datetime(year=2019, month=1, day=3), birth_date=birth_date
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.DMS, resultContent=dms_content
        )

        result = fraud_api.decide_eligibility(user, dms_content)
        assert result == users_models.EligibilityType.AGE18

    @freeze_time("2020-01-02")
    def test_18yo_underage_eligible(self):
        birth_date = datetime.date(year=2002, month=1, day=1)
        user = users_factories.UserFactory()
        dms_content = fraud_factories.DMSContentFactory(
            registration_datetime=datetime.datetime(year=2019, month=1, day=3), birth_date=birth_date
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.DMS, resultContent=dms_content
        )

        result = fraud_api.decide_eligibility(user, dms_content)
        assert result == users_models.EligibilityType.AGE18
