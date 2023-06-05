import datetime
import itertools

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time
import pytest

import pcapi.core.fraud.api as fraud_api
import pcapi.core.fraud.factories as fraud_factories
import pcapi.core.fraud.models as fraud_models
import pcapi.core.fraud.ubble.models as ubble_fraud_models
import pcapi.core.history.factories as history_factories
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_settings
import pcapi.core.users.constants as users_constants
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models


@pytest.mark.usefixtures("db_session")
class CommonTest:
    @pytest.mark.parametrize(
        "id_piece_number",
        ["I III1", "I I 1JII 11IB I E", "", "Passeport n: XXXXX", "15347402 5 ZX9 "],
    )
    def test_id_piece_number_wrong_format(self, id_piece_number):
        item = fraud_api.validate_id_piece_number_format_fraud_item(id_piece_number)
        assert item.status == fraud_models.FraudStatus.SUSPICIOUS

    @pytest.mark.parametrize(
        "id_piece_number",
        [
            # Some edge cases examples come from here:
            # https://www.notion.so/passcultureapp/79afb2e511544bfcb2da83826cde0043?v=48070c75add24820ac1cae498199d469
            # https://www.notion.so/passcultureapp/Tableau-des-ID-trang-res-sur-FA-440ab8cbb31d4ae9a16debe3eb5aab24
            "210238320",
            "12121L000454",
            "593-0169535-39",
            "CKKPZ0YH",
            "B0715645",
            "EB5853834",
            "H394589",
            "114454304",
            "N1795170",
            "PA1356204",
            "YE227383",
            "040211-5703",
            "1774519",
            "53 1278779",
            "AU0443438",
            "11658590",
            "EK 1122107",
            "037316896",
            "M62082473",
            "RL 4052317",
            "AQ543939",
            "2 99 20030915 00001 3",
            "1 808 2011 01857",
            "00825128061",
            "A02621372",
            "NND5PF684",
            "FC5729729",
            "25359693",
            "MZ785199",
            "1314109248",
            "AQ1510973",
            "20AA63328",
            "32363144 4 ZZ7",
            "1112338",
            "339546T",
            "AZ 3099856",
            "CES 177869",
            "FGRGJJTEF",
            "0A0445529",
            "CCF620343",
            "121-21-L000454",
            "PA 0473778",
            "EB509436",
            "C975773",
            "X6372552",
            "EJ0618532",
            "1026070",
            "S0010042",
            "N 013057163",
            "A02L8Z01",
        ],
    )
    def test_id_piece_number_valid_format(self, id_piece_number):
        item = fraud_api.validate_id_piece_number_format_fraud_item(id_piece_number)
        assert item.status == fraud_models.FraudStatus.OK

    @override_settings(ENABLE_PERMISSIVE_NAME_VALIDATION=False)
    @pytest.mark.parametrize(
        "name,is_valid",
        [
            ("Ellingson", True),
            ("Ellingson2", False),
            ("/", False),
            (" ", False),
            ("Charles-Apollon", True),
            ("John O'Wick", True),
            ("John O’Wick", True),
            ("Martin king, Jr.", True),
            ("მარიამ", False),
            ("aé", True),
            ("&", False),
            ("a&", False),
            ("1", False),
        ],
    )
    def test_is_subscription_name_valid(self, name, is_valid):
        assert fraud_api.is_subscription_name_valid(name) is is_valid
        with override_settings(ENABLE_PERMISSIVE_NAME_VALIDATION=True):
            assert fraud_api.is_subscription_name_valid(name) is True

    def test_create_profile_completion_fraud_check(self, caplog):
        user = users_factories.EligibleGrant18Factory()
        content = fraud_factories.ProfileCompletionContentFactory(origin="Origine orignale")
        fraud_api.create_profile_completion_fraud_check(user, user.eligibility, content)
        profile_completion_fraud_check = user.beneficiaryFraudChecks[0]

        assert profile_completion_fraud_check.type == fraud_models.FraudCheckType.PROFILE_COMPLETION
        assert profile_completion_fraud_check.status == fraud_models.FraudCheckStatus.OK
        assert profile_completion_fraud_check.eligibilityType == users_models.EligibilityType.AGE18

        # try to create duplicate
        fraud_api.create_profile_completion_fraud_check(user, user.eligibility, content)
        assert caplog.records[0].message == "Profile completion fraud check for user already exists."
        assert caplog.records[0].extra == {
            "user_id": user.id,
        }


def filter_invalid_fraud_items_to_reason_codes(
    fraud_items: list[fraud_models.FraudItem],
) -> set[fraud_models.FraudReasonCode]:
    return set(
        itertools.chain.from_iterable(
            item.reason_codes for item in fraud_items if item.status != fraud_models.FraudStatus.OK
        )
    )


@pytest.mark.usefixtures("db_session")
class CommonFraudCheckTest:
    def test_duplicate_id_piece_number_ok(self):
        user = users_factories.UserFactory()
        fraud_item = fraud_api.duplicate_id_piece_number_fraud_item(user, "random_id")
        assert fraud_item.status == fraud_models.FraudStatus.OK

    def test_duplicate_id_piece_number_suspicious(self):
        user = users_factories.BeneficiaryGrant18Factory(idPieceNumber="random_id")
        applicant = users_factories.UserFactory()

        fraud_item = fraud_api.duplicate_id_piece_number_fraud_item(applicant, user.idPieceNumber)
        assert fraud_item.status == fraud_models.FraudStatus.SUSPICIOUS

    def test_duplicate_id_piece_number_suspicious_not_self(self):
        applicant = users_factories.UserFactory(idPieceNumber="random_id")

        fraud_item = fraud_api.duplicate_id_piece_number_fraud_item(applicant, applicant.idPieceNumber)
        assert fraud_item.status == fraud_models.FraudStatus.OK

    def test_duplicate_user_fraud_ok(self):
        fraud_item = fraud_api._duplicate_user_fraud_item(
            first_name="Jean",
            last_name="Michel",
            married_name=None,
            birth_date=datetime.date.today(),
            excluded_user_id=1,
        )

        assert fraud_item.status == fraud_models.FraudStatus.OK

    def test_duplicate_user_fraud_suspicious(self):
        user = users_factories.BeneficiaryGrant18Factory()
        fraud_item = fraud_api._duplicate_user_fraud_item(
            first_name=user.firstName,
            last_name=user.lastName,
            married_name=None,
            birth_date=user.dateOfBirth.date(),
            excluded_user_id=1,
        )

        assert fraud_item.status == fraud_models.FraudStatus.SUSPICIOUS

    def test_duplicate_user_ok_if_self_found(self):
        user = users_factories.BeneficiaryGrant18Factory()
        fraud_item = fraud_api._duplicate_user_fraud_item(
            first_name=user.firstName,
            last_name=user.lastName,
            married_name=None,
            birth_date=user.dateOfBirth.date(),
            excluded_user_id=user.id,
        )

        assert fraud_item.status == fraud_models.FraudStatus.OK

    @pytest.mark.parametrize(
        "fraud_check_type",
        [fraud_models.FraudCheckType.DMS],
    )
    def test_user_validation_has_email_validated(self, fraud_check_type):
        user = users_factories.UserFactory(isEmailValidated=False)
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(type=fraud_check_type, user=user)
        fraud_items = fraud_api.on_identity_fraud_check_result(user, fraud_check)

        invalid_codes = filter_invalid_fraud_items_to_reason_codes(fraud_items)
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

        invalid_codes = filter_invalid_fraud_items_to_reason_codes(fraud_items)
        assert fraud_models.FraudReasonCode.EMAIL_NOT_VALIDATED in invalid_codes


@pytest.mark.usefixtures("db_session")
class FindDuplicateUserTest:
    first_name = "Alice"
    last_name = "Ravineau"
    birth_date = datetime.datetime(2000, 1, 1)

    def test_duplicate_user_found(self):
        existing_user = users_factories.BeneficiaryGrant18Factory(
            firstName=self.first_name,
            lastName=self.last_name,
            dateOfBirth=self.birth_date,
        )

        assert (
            fraud_api.find_duplicate_beneficiary(
                "Alice", "RAVINEAU ", None, self.birth_date.date(), existing_user.id + 1
            )
            == existing_user
        )

    def test_same_user_id(self):
        existing_user = users_factories.UserFactory(
            firstName=self.first_name,
            lastName=self.last_name,
            validatedBirthDate=self.birth_date,
            roles=[users_models.UserRole.BENEFICIARY],
        )

        assert (
            fraud_api.find_duplicate_beneficiary(
                self.first_name, self.last_name, None, self.birth_date, existing_user.id
            )
            is None
        )

    def test_duplicate_not_beneficiary(self):
        existing_user = users_factories.UserFactory(
            firstName=self.first_name,
            lastName=self.last_name,
            validatedBirthDate=self.birth_date,
        )

        assert (
            fraud_api.find_duplicate_beneficiary(
                self.first_name, self.last_name, None, self.birth_date, existing_user.id + 1
            )
            is None
        )

    def test_duplicate_user_with_married_name(self):
        existing_user = users_factories.UserFactory(
            firstName=self.first_name,
            lastName=self.last_name,
            married_name=None,
            validatedBirthDate=self.birth_date,
            roles=[users_models.UserRole.BENEFICIARY],
        )

        assert (
            fraud_api.find_duplicate_beneficiary(
                "Alice", "Nom de jeune fille ", "RAVINEAU", self.birth_date.date(), existing_user.id + 1
            )
            == existing_user
        )

    def test_duplicate_user_with_last_name_matching_married_name(self):
        existing_user = users_factories.UserFactory(
            firstName=self.first_name,
            lastName="Nom de jeune fille",
            married_name="RAVINEAU",
            validatedBirthDate=self.birth_date,
            roles=[users_models.UserRole.BENEFICIARY],
        )

        assert (
            fraud_api.find_duplicate_beneficiary(
                "Alice", "Ravineau", None, self.birth_date.date(), existing_user.id + 1
            )
            == existing_user
        )

    @pytest.mark.parametrize(
        "existing_id_piece_number,new_id_piece_number",
        [
            ("123456789", "123456789"),
            ("123456789", "123 456 789"),
        ],
    )
    def test_find_duplicate_id_piece_number_user(self, existing_id_piece_number, new_id_piece_number):
        existing_user = users_factories.UserFactory(idPieceNumber=existing_id_piece_number)
        new_user = users_factories.UserFactory()

        assert fraud_api.find_duplicate_id_piece_number_user(new_id_piece_number, new_user.id) == existing_user


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
                civility=users_models.GenderEnum.F,
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
            "civility": users_models.GenderEnum.F,
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
                civility=users_models.GenderEnum.M,
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
            "civility": users_models.GenderEnum.M,
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
        result = fraud_api.educonnect_fraud_checks(user, fraud_check.source_data())

        age_check = next(
            fraud_item for fraud_item in result if fraud_models.FraudReasonCode.AGE_NOT_VALID in fraud_item.reason_codes
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
        result = fraud_api.educonnect_fraud_checks(user, fraud_check.source_data())

        age_check = next(
            (
                fraud_item
                for fraud_item in result
                if fraud_models.FraudReasonCode.AGE_NOT_VALID in fraud_item.reason_codes
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
            item for item in fraud_items if fraud_models.FraudReasonCode.DUPLICATE_USER in item.reason_codes
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
        result = fraud_api.educonnect_fraud_checks(underage_user, fraud_check.source_data())

        assert not any(fraud_models.FraudReasonCode.DUPLICATE_USER in fraud_item.reason_codes for fraud_item in result)

    def test_ine_duplicates_fraud_checks(self):
        same_ine_user = users_factories.UnderageBeneficiaryFactory(ineHash="ylwavk71o3jiwyla83fxk5pcmmu0ws01")
        user_in_validation = users_factories.UserFactory()
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.EDUCONNECT,
            resultContent=fraud_factories.EduconnectContentFactory(ine_hash=same_ine_user.ineHash),
            user=user_in_validation,
        )
        result = fraud_api.educonnect_fraud_checks(user_in_validation, fraud_check.source_data())

        duplicate_ine_check = next(
            fraud_item for fraud_item in result if fraud_models.FraudReasonCode.DUPLICATE_INE in fraud_item.reason_codes
        )
        assert duplicate_ine_check.status == fraud_models.FraudStatus.SUSPICIOUS
        assert (
            duplicate_ine_check.detail
            == f"L'INE ylwavk71o3jiwyla83fxk5pcmmu0ws01 est déjà pris par l'utilisateur {same_ine_user.id}"
        )


def build_user_at_id_check(age, eligibility_type=users_models.EligibilityType.AGE18):
    user = users_factories.UserFactory(
        dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=age, days=5),
        phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
    )
    fraud_factories.ProfileCompletionFraudCheckFactory(
        user=user,
        eligibilityType=eligibility_type,
        resultContent=fraud_factories.ProfileCompletionContentFactory(first_name="Sally", last_name="Mara"),
    )
    return user


@pytest.mark.usefixtures("db_session")
class HasUserPerformedIdentityCheckTest:
    def test_has_not_performed(self):
        user = build_user_at_id_check(18)
        fraud_factories.BeneficiaryFraudCheckFactory(user=user, eligibilityType=users_models.EligibilityType.UNDERAGE)

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
    @pytest.mark.parametrize("check_type", [fraud_models.FraudCheckType.DMS, fraud_models.FraudCheckType.UBBLE])
    @pytest.mark.parametrize("status", [fraud_models.FraudCheckStatus.PENDING, fraud_models.FraudCheckStatus.OK])
    def test_has_user_performed_identity_check(self, age, eligibility_type, check_type, status):
        user = build_user_at_id_check(age, eligibility_type=eligibility_type)
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=check_type, user=user, status=status, eligibilityType=eligibility_type
        )

        assert fraud_api.has_user_performed_identity_check(user)

    def test_has_user_performed_identity_check_turned_18(self):
        user = build_user_at_id_check(18)
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE, user=user, eligibilityType=users_models.EligibilityType.UNDERAGE
        )

        assert not fraud_api.has_user_performed_identity_check(user)

    def test_has_user_performed_identity_check_without_identity_fraud_check(self):
        user = user = build_user_at_id_check(18)

        assert not fraud_api.has_user_performed_identity_check(user)

    def test_has_user_performed_identity_check_status_initiated(self):
        user = user = build_user_at_id_check(18)
        ubble_content = fraud_factories.UbbleContentFactory(
            status=ubble_fraud_models.UbbleIdentificationStatus.INITIATED
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            user=user,
            resultContent=ubble_content,
            status=fraud_models.FraudCheckStatus.PENDING,
        )

        assert fraud_api.has_user_performed_identity_check(user)

    def test_has_user_performed_identity_check_ubble_suspicious(self):
        user = build_user_at_id_check(18)
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            user=user,
            status=fraud_models.FraudCheckStatus.SUSPICIOUS,
            reasonCodes=[fraud_models.FraudReasonCode.ID_CHECK_EXPIRED],
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        # Suspicous => Retry allowed
        assert not fraud_api.has_user_performed_identity_check(user)

    def test_has_user_performed_identity_check_ubble_suspicious_x3(self):
        user = build_user_at_id_check(18)
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

    def test_has_user_performed_identity_check_ubble_ko(self):
        user = build_user_at_id_check(18)
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            user=user,
            status=fraud_models.FraudCheckStatus.KO,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        # Retry not allowed
        assert fraud_api.has_user_performed_identity_check(user)

    def test_user_beneficiary(self):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=20, months=1),
            roles=[users_models.UserRole.BENEFICIARY],
        )
        assert fraud_api.has_user_performed_identity_check(user)

    def test_user_not_eligible_anymore_but_has_performed(self):
        user = build_user_at_id_check(20)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=fraud_models.FraudCheckStatus.OK,
            type=fraud_models.FraudCheckType.UBBLE,
        )
        user.roles = [users_models.UserRole.BENEFICIARY]

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

        result = fraud_api.decide_eligibility(
            user, dms_content.get_birth_date(), dms_content.get_registration_datetime()
        )
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

        result = fraud_api.decide_eligibility(
            user, dms_content.get_birth_date(), dms_content.get_registration_datetime()
        )
        assert result is None

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

        result = fraud_api.decide_eligibility(
            user, dms_content.get_birth_date(), dms_content.get_registration_datetime()
        )
        assert result is None

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

        result = fraud_api.decide_eligibility(
            user, dms_content.get_birth_date(), dms_content.get_registration_datetime()
        )
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

        result = fraud_api.decide_eligibility(
            user, dms_content.get_birth_date(), dms_content.get_registration_datetime()
        )
        assert result == users_models.EligibilityType.AGE18

    @freeze_time("2022-03-01")
    def test_decide_eligibility_for_underage_users(self):
        # All 15-17 users are eligible after 2022-01-01
        for age in range(15, 18):
            user = users_factories.UserFactory(dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=age))
            birth_date = user.dateOfBirth
            registration_datetime = datetime.datetime.today()

            assert (
                fraud_api.decide_eligibility(user, birth_date, registration_datetime)
                == users_models.EligibilityType.UNDERAGE
            )

    @freeze_time("2022-01-01")
    def test_decide_eligibility_for_18_yo_users_is_always_age_18(self):
        # 18 users are always eligible
        age = 18
        birth_date = datetime.datetime.utcnow() - relativedelta(years=age)
        user = users_factories.UserFactory()

        assert (
            fraud_api.decide_eligibility(user, birth_date, datetime.datetime.today())
            == users_models.EligibilityType.AGE18
        )
        assert fraud_api.decide_eligibility(user, birth_date, None) == users_models.EligibilityType.AGE18
        assert (
            fraud_api.decide_eligibility(user, birth_date, datetime.datetime.utcnow() - relativedelta(years=1))
            == users_models.EligibilityType.AGE18
        )

    @freeze_time("2022-07-01")
    @pytest.mark.parametrize(
        "first_registration_datetime,expected_eligibility",
        [
            (None, None),
            (datetime.datetime(year=2022, month=1, day=15), None),
            (
                datetime.datetime(year=2021, month=12, day=1),
                users_models.EligibilityType.AGE18,
            ),
        ],
    )
    # 19yo users are eligible if they have started registration before turning 19
    def test_decide_eligibility_for_19_yo_users(self, first_registration_datetime, expected_eligibility):
        birth_date = datetime.datetime(year=2003, month=1, day=1)
        user = users_factories.UserFactory()

        if first_registration_datetime:
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=user,
                type=fraud_models.FraudCheckType.DMS,
                resultContent=fraud_factories.DMSContentFactory(
                    registration_datetime=first_registration_datetime, birth_date=birth_date
                ),
            )

        assert fraud_api.decide_eligibility(user, birth_date, datetime.datetime.today()) == expected_eligibility

    def test_decide_eligibility_for_19_yo_users_with_no_registration_datetime(self):
        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.DMS,
            resultContent=fraud_factories.DMSContentFactory(
                registration_datetime=None,
                birth_date=datetime.datetime(year=2003, month=1, day=1),
            ),
            dateCreated=datetime.datetime(year=2021, month=12, day=1),
        )

        with freeze_time("2022-07-01"):
            assert (
                fraud_api.decide_eligibility(user, datetime.datetime(year=2003, month=1, day=1), None)
                == users_models.EligibilityType.AGE18
            )


@pytest.mark.usefixtures("db_session")
class GetSuspendedAccountsUponUserRequestSinceTest:
    def test_get_suspended_upon_user_request_accounts_since(self) -> None:
        one_week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        something = history_factories.SuspendedUserActionHistoryFactory(
            actionDate=one_week_ago, reason=users_constants.SuspensionReason.UPON_USER_REQUEST
        )

        # not suspended upon user request: should be ignored
        history_factories.SuspendedUserActionHistoryFactory(
            actionDate=one_week_ago, reason=users_constants.SuspensionReason.FRAUD_SUSPICION
        )

        # suspended less than 5 days ago (see below): should be ignored
        yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        history_factories.SuspendedUserActionHistoryFactory(
            actionDate=yesterday, reason=users_constants.SuspensionReason.UPON_USER_REQUEST
        )

        expected_user_ids = {something.userId}

        with assert_num_queries(1):
            query = fraud_api.get_suspended_upon_user_request_accounts_since(5)
            user_ids = {user.id for user in query}
            assert user_ids == expected_user_ids

    def test_unsuspended_account(self) -> None:
        """
        Test that an unsuspended account is ignored, even if the
        suspension event occurred more than N days ago.
        """
        one_week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        user = users_factories.UserFactory(isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(
            user=user, actionDate=one_week_ago, reason=users_constants.SuspensionReason.FRAUD_SUSPICION
        )

        yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        history_factories.UnsuspendedUserActionHistoryFactory(user=user, actionDate=yesterday)

        with assert_num_queries(1):
            assert not list(fraud_api.get_suspended_upon_user_request_accounts_since(5))


@pytest.mark.usefixtures("db_session")
class DuplicateBeneficiaryEmailTest:
    @pytest.mark.parametrize(
        "input_email, anonymized_email",
        [
            ("anne-onime@me.com", "ann***@me.com"),
            ("wrong_address.com", "***"),
            ("yo@lo.com", "y***@lo.com"),
            ("y@o.com", "***@o.com"),
        ],
    )
    def test_anonymize(self, input_email, anonymized_email) -> None:
        assert fraud_api._anonymize_email(input_email) == anonymized_email

    def test_duplicate_user(self):
        rejected_user = users_factories.UserFactory()
        duplicater_user = users_factories.BeneficiaryGrant18Factory(email="shotgun@example.com")
        identity_content = fraud_factories.UbbleContentFactory(
            first_name=duplicater_user.firstName,
            last_name=duplicater_user.lastName,
            birth_date=duplicater_user.dateOfBirth.date().isoformat(),
        )
        assert (
            fraud_api.get_duplicate_beneficiary_anonymized_email(
                rejected_user, identity_content, fraud_models.FraudReasonCode.DUPLICATE_USER
            )
            == "sho***@example.com"
        )
        assert (
            fraud_api.get_duplicate_beneficiary_anonymized_email(
                rejected_user, identity_content, fraud_models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER
            )
            is None
        )

    def test_duplicate_id_piece_number(self):
        rejected_user = users_factories.UserFactory()
        users_factories.BeneficiaryGrant18Factory(email="shotgun@example.com", idPieceNumber="123")
        identity_content = fraud_factories.UbbleContentFactory(id_document_number="123")
        assert (
            fraud_api.get_duplicate_beneficiary_anonymized_email(
                rejected_user, identity_content, fraud_models.FraudReasonCode.DUPLICATE_USER
            )
            is None
        )
        assert (
            fraud_api.get_duplicate_beneficiary_anonymized_email(
                rejected_user, identity_content, fraud_models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER
            )
            == "sho***@example.com"
        )
