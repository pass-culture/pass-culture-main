import dataclasses
from datetime import date
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
import freezegun
import pytest

from pcapi.connectors.dms import api as dms_connector_api
from pcapi.connectors.dms import models as dms_models
import pcapi.core.fraud.factories as fraud_factories
import pcapi.core.fraud.models as fraud_models
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.payments.models import Deposit
from pcapi.core.payments.models import DepositType
import pcapi.core.subscription.api as subscription_api
from pcapi.core.subscription.dms import api as dms_api
import pcapi.core.subscription.models as subscription_models
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.core.users.constants import ELIGIBILITY_AGE_18
import pcapi.notifications.push.testing as push_testing
from pcapi.scripts.beneficiary.import_dms_accepted_applications import import_dms_accepted_applications

from tests.scripts.beneficiary import fixture


NOW = datetime.utcnow()

AGE18_ELIGIBLE_BIRTH_DATE = datetime.utcnow() - relativedelta(years=ELIGIBILITY_AGE_18)


@pytest.mark.usefixtures("db_session")
class RunTest:
    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    @patch("pcapi.core.subscription.api.on_successful_application")
    def test_should_retrieve_applications_from_new_procedure_id(
        self,
        on_sucessful_application,
        get_applications_with_details,
    ):
        get_applications_with_details.return_value = [
            fixture.make_parsed_graphql_application(
                123, "accepte", email="email1@example.com", id_piece_number="123123121"
            ),
            fixture.make_parsed_graphql_application(
                456, "accepte", email="email2@example.com", id_piece_number="123123122"
            ),
            fixture.make_parsed_graphql_application(
                789, "accepte", email="email3@example.com", id_piece_number="123123123"
            ),
        ]

        import_dms_accepted_applications(procedure_id=6712558)
        assert get_applications_with_details.call_count == 1
        get_applications_with_details.assert_called_with(6712558, dms_models.GraphQLApplicationStates.accepted)

    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    @patch("pcapi.core.subscription.api.on_successful_application")
    def test_all_applications_are_processed_once(
        self,
        on_sucessful_application,
        get_applications_with_details,
    ):
        users_factories.UserFactory(email="email1@example.com")
        users_factories.UserFactory(email="email2@example.com")
        users_factories.UserFactory(email="email3@example.com")
        get_applications_with_details.return_value = [
            fixture.make_parsed_graphql_application(
                123,
                "accepte",
                email="email1@example.com",
                id_piece_number="123123121",
                birth_date=AGE18_ELIGIBLE_BIRTH_DATE,
            ),
            fixture.make_parsed_graphql_application(
                456,
                "accepte",
                email="email2@example.com",
                id_piece_number="123123122",
                birth_date=AGE18_ELIGIBLE_BIRTH_DATE,
            ),
            fixture.make_parsed_graphql_application(
                789,
                "accepte",
                email="email3@example.com",
                id_piece_number="123123123",
                birth_date=AGE18_ELIGIBLE_BIRTH_DATE,
            ),
        ]

        import_dms_accepted_applications(procedure_id=6712558)
        assert on_sucessful_application.call_count == 3

    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    @patch("pcapi.core.subscription.api.on_successful_application")
    def test_application_with_known_email_and_already_beneficiary_are_saved_as_rejected(
        self, on_sucessful_application, get_applications_with_details
    ):
        # same user, but different
        user = users_factories.BeneficiaryGrant18Factory(email="john.doe@example.com")
        get_applications_with_details.return_value = [
            fixture.make_parsed_graphql_application(123, "accepte", email="john.doe@example.com")
        ]

        import_dms_accepted_applications(procedure_id=6712558)

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter(
            fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.DMS
        ).one()
        assert fraud_check.userId == user.id
        assert fraud_check.thirdPartyId == "123"
        assert fraud_check.status == fraud_models.FraudCheckStatus.KO
        assert fraud_check.reason == (
            "L’utilisateur est déjà bénéfiaire du pass AGE18 ; "
            "L’utilisateur est déjà bénéfiaire, avec un portefeuille non expiré. "
            "Il ne peut pas prétendre au pass culture 18 ans"
        )

        on_sucessful_application.assert_not_called()

    @override_features(FORCE_PHONE_VALIDATION=False)
    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    @patch("pcapi.core.subscription.api.on_successful_application")
    def test_beneficiary_is_created_with_procedure_id(self, on_sucessful_application, get_applications_with_details):
        # given
        applicant = users_factories.UserFactory(firstName="Doe", lastName="John", email="john.doe@test.com")
        get_applications_with_details.return_value = [
            fixture.make_parsed_graphql_application(
                123, "accepte", id_piece_number="123123121", email=applicant.email, birth_date=AGE18_ELIGIBLE_BIRTH_DATE
            )
        ]

        import_dms_accepted_applications(procedure_id=6712558)

        on_sucessful_application.assert_called_with(
            user=applicant,
            source_data=fraud_models.DMSContent(
                last_name="Doe",
                first_name="John",
                civility=dms_models.Civility.MME,
                email="john.doe@test.com",
                application_id=123,
                procedure_id=6712558,
                department="67",
                phone="0123456789",
                birth_date=AGE18_ELIGIBLE_BIRTH_DATE.date(),
                activity="Étudiant",
                address="3 La Bigotais 22800 Saint-Donan",
                postal_code="67200",
                processed_datetime=datetime(2020, 5, 13, 10, 41, 21, tzinfo=timezone(timedelta(seconds=7200))),
                registration_datetime=datetime(2020, 5, 13, 9, 9, 46, tzinfo=timezone(timedelta(seconds=7200))),
                id_piece_number="123123121",
            ),
        )


class ParseBeneficiaryInformationTest:
    @pytest.mark.parametrize(
        "department_code,expected_code",
        [("67 - Bas-Rhin", "67"), ("973 - Guyane", "973"), ("2B - Haute-Corse", "2B"), ("2a - Corse-du-Sud", "2a")],
    )
    def test_handles_department_code(self, department_code, expected_code):
        application_detail = fixture.make_parsed_graphql_application(1, "accepte", department_code=department_code)
        information = dms_connector_api.parse_beneficiary_information_graphql(application_detail, procedure_id=201201)
        assert information.department == expected_code

    @pytest.mark.parametrize(
        "postal_code,expected_code",
        [
            ("  93130  ", "93130"),
            ("67 200", "67200"),
            ("67 200 Strasbourg ", "67200"),
        ],
    )
    def test_handles_postal_codes(self, postal_code, expected_code):
        application_detail = fixture.make_parsed_graphql_application(1, "accepte", postal_code=postal_code)
        information = dms_connector_api.parse_beneficiary_information_graphql(application_detail, procedure_id=201201)
        assert information.postal_code == expected_code

    def test_handles_civility_parsing(self):
        # given
        application_detail = fixture.make_parsed_graphql_application(1, "accepte", civility="M")

        # when
        information = dms_connector_api.parse_beneficiary_information_graphql(application_detail, procedure_id=201201)

        # then
        assert information.civility == users_models.GenderEnum.M

    @pytest.mark.parametrize("activity", ["Étudiant", None])
    def test_handles_activity(self, activity):
        application_detail = fixture.make_parsed_graphql_application(1, "accepte", activity=activity)
        information = dms_connector_api.parse_beneficiary_information_graphql(application_detail, procedure_id=201201)
        assert information.activity == activity

    @pytest.mark.parametrize("possible_value", ["0123456789", " 0123456789", "0123456789 ", " 0123456789 "])
    def test_beneficiary_information_id_piece_number_with_spaces_graphql(self, possible_value):
        application_detail = fixture.make_parsed_graphql_application(1, "accepte", id_piece_number=possible_value)
        information = dms_connector_api.parse_beneficiary_information_graphql(application_detail, procedure_id=123123)

        assert information.id_piece_number == "0123456789"

    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    def test_new_procedure(self, get_applications_with_details):
        raw_data = fixture.make_new_application()
        content = dms_connector_api.parse_beneficiary_information_graphql(
            dms_models.DmsApplicationResponse(**raw_data), 32
        )
        assert content.last_name == "VALGEAN"
        assert content.first_name == "Jean"
        assert content.civility == users_models.GenderEnum.M
        assert content.email == "jean.valgean@example.com"
        assert content.application_id == 5718303
        assert content.procedure_id == 32
        assert content.department == None
        assert content.birth_date == date(2004, 12, 19)
        assert content.phone == "0601010101"
        assert content.postal_code == "92700"
        assert content.activity == "Employé"
        assert content.address == "32 rue des sapins gris 21350 l'îsle à dent"
        assert content.id_piece_number == "F9GFAL123"

    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    def test_new_procedure_for_stranger_residents(self, get_applications_with_details):
        raw_data = fixture.make_new_stranger_application()
        content = dms_connector_api.parse_beneficiary_information_graphql(
            dms_models.DmsApplicationResponse(**raw_data), 32
        )
        assert content.last_name == "VALGEAN"
        assert content.first_name == "Jean"
        assert content.civility == users_models.GenderEnum.M
        assert content.email == "jean.valgean@example.com"
        assert content.application_id == 5742994
        assert content.procedure_id == 32
        assert content.department == None
        assert content.birth_date == date(2006, 5, 12)
        assert content.phone == "0601010101"
        assert content.postal_code == "92700"
        assert content.activity == "Employé"
        assert content.address == "32 rue des sapins gris 21350 l'îsle à dent"
        assert content.id_piece_number == "K682T8YLO"

    def test_processed_datetime_none(self):
        raw_data = fixture.make_graphql_application(1, "en_construction", processed_datetime=None)
        content = dms_connector_api.parse_beneficiary_information_graphql(
            dms_models.DmsApplicationResponse(**raw_data), 32
        )
        assert content.processed_datetime is None

    def test_processed_datetime_not_none(self):
        raw_data = fixture.make_graphql_application(1, "accepte")
        content = dms_connector_api.parse_beneficiary_information_graphql(
            dms_models.DmsApplicationResponse(**raw_data), 32
        )
        assert content.processed_datetime == datetime(2020, 5, 13, 10, 41, 21, tzinfo=timezone(timedelta(seconds=7200)))


class ParsingErrorsTest:
    def test_beneficiary_information_postalcode_error(self):
        application_detail = fixture.make_parsed_graphql_application(1, "accepte", postal_code="Strasbourg")
        with pytest.raises(ValueError) as exc_info:
            dms_connector_api.parse_beneficiary_information_graphql(application_detail, procedure_id=123123)

        assert exc_info.value.errors["postal_code"] == "Strasbourg"

    @pytest.mark.parametrize("possible_value", ["Passeport n: XXXXX", "sans numéro"])
    def test_beneficiary_information_id_piece_number_error(self, possible_value):
        application_detail = fixture.make_parsed_graphql_application(1, "accepte", id_piece_number=possible_value)

        with pytest.raises(ValueError) as exc_info:
            dms_connector_api.parse_beneficiary_information_graphql(application_detail, procedure_id=123123)

        assert exc_info.value.errors["id_piece_number"] == possible_value


@pytest.mark.usefixtures("db_session")
class RunIntegrationTest:
    EMAIL = "john.doe@example.com"
    BENEFICIARY_BIRTH_DATE = date.today() - timedelta(days=6752)  # ~18.5 years

    @override_features(FORCE_PHONE_VALIDATION=False)
    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    def test_import_user(self, get_applications_with_details):
        user = users_factories.UserFactory(
            firstName="john",
            lastName="doe",
            email="john.doe@example.com",
            dateOfBirth=AGE18_ELIGIBLE_BIRTH_DATE,
        )

        get_applications_with_details.return_value = [
            fixture.make_parsed_graphql_application(application_id=123, state="accepte", email=user.email)
        ]
        import_dms_accepted_applications(procedure_id=6712558)

        assert users_models.User.query.count() == 1
        user = users_models.User.query.first()
        assert user.firstName == "John"
        assert user.postalCode == "67200"
        assert user.address == "3 La Bigotais 22800 Saint-Donan"
        assert user.phoneNumber == "0123456789"

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter(
            fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.DMS
        ).one()
        assert fraud_check.userId == user.id
        assert fraud_check.thirdPartyId == "123"
        assert fraud_check.status == fraud_models.FraudCheckStatus.OK
        assert len(push_testing.requests) == 2

    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    def test_import_exunderage_beneficiary(self, get_applications_with_details):
        with freezegun.freeze_time(datetime.utcnow() - relativedelta(years=2, month=1)):
            user = users_factories.UnderageBeneficiaryFactory(
                email="john.doe@example.com",
                firstName="john",
                lastName="doe",
                dateOfBirth=AGE18_ELIGIBLE_BIRTH_DATE,
                subscription_age=15,
                phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.USER_PROFILING,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        details = fixture.make_parsed_graphql_application(application_id=123, state="accepte", email=user.email)
        details.draft_date = datetime.utcnow().isoformat()
        get_applications_with_details.return_value = [details]
        import_dms_accepted_applications(procedure_id=6712558)

        assert users_models.User.query.count() == 1
        user = users_models.User.query.first()
        assert user.has_beneficiary_role
        deposits = Deposit.query.filter_by(user=user).all()
        age_18_deposit = next(deposit for deposit in deposits if deposit.type == DepositType.GRANT_18)
        assert len(deposits) == 2
        assert age_18_deposit.amount == 300

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter(
            fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.DMS
        ).one()
        assert fraud_check.userId == user.id
        assert fraud_check.thirdPartyId == "123"
        assert fraud_check.status == fraud_models.FraudCheckStatus.OK

    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    def test_import_with_no_user_found(self, get_applications_with_details):
        # when
        get_applications_with_details.return_value = [
            fixture.make_parsed_graphql_application(
                application_id=123, state="accepte", email="nonexistant@example.com"
            )
        ]

        import_dms_accepted_applications(procedure_id=6712558)
        dms_application = fraud_models.OrphanDmsApplication.query.filter(
            fraud_models.OrphanDmsApplication.application_id == 123
        ).one()
        assert dms_application.application_id == 123
        assert dms_application.process_id == 6712558
        assert dms_application.email == "nonexistant@example.com"

    @override_features(FORCE_PHONE_VALIDATION=True)
    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    def test_phone_not_validated_create_beneficiary_with_phone_to_validate(self, get_applications_with_details):
        """
        Test that an imported user without a validated phone number, and the
        FORCE_PHONE_VALIDATION feature flag activated, requires a future validation
        """
        date_of_birth = self.BENEFICIARY_BIRTH_DATE.strftime("%Y-%m-%dT%H:%M:%S")

        # Create a user that has validated its email and phone number, meaning it
        # should become beneficiary.
        user = users_factories.UserFactory(
            email=self.EMAIL,
            isEmailValidated=True,
            dateOfBirth=date_of_birth,
            phoneValidationStatus=None,
        )
        get_applications_with_details.return_value = [
            fixture.make_parsed_graphql_application(application_id=123, state="accepte", email=user.email)
        ]
        # when
        import_dms_accepted_applications(procedure_id=6712558)

        # then
        assert users_models.User.query.count() == 1
        user = users_models.User.query.first()

        assert len(user.beneficiaryFraudChecks) == 2

        honor_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(
            user=user, type=fraud_models.FraudCheckType.HONOR_STATEMENT
        ).one_or_none()
        assert honor_check
        dms_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(
            user=user, type=fraud_models.FraudCheckType.DMS, status=fraud_models.FraudCheckStatus.OK
        ).one_or_none()
        assert dms_check
        assert len(push_testing.requests) == 2

        assert not user.is_beneficiary
        assert not user.deposit
        assert (
            subscription_api.get_next_subscription_step(user) == subscription_models.SubscriptionStep.PHONE_VALIDATION
        )

    @override_features(FORCE_PHONE_VALIDATION=True)
    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    def test_import_user_requires_userprofiling(self, get_applications_with_details):
        user = users_factories.UserFactory(
            email=self.EMAIL,
            dateOfBirth=self.BENEFICIARY_BIRTH_DATE,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            city="Quito",
        )
        get_applications_with_details.return_value = [
            fixture.make_parsed_graphql_application(application_id=123, state="accepte", email=user.email)
        ]
        # when
        import_dms_accepted_applications(procedure_id=6712558)

        # then
        assert users_models.User.query.count() == 1
        user = users_models.User.query.first()

        assert len(user.beneficiaryFraudChecks) == 2

        honor_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(
            user=user, type=fraud_models.FraudCheckType.HONOR_STATEMENT
        ).one_or_none()
        assert honor_check
        dms_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(
            user=user, type=fraud_models.FraudCheckType.DMS, status=fraud_models.FraudCheckStatus.OK
        ).one_or_none()
        assert dms_check

        assert len(push_testing.requests) == 2

        assert not user.is_beneficiary
        assert not user.deposit
        assert subscription_api.get_next_subscription_step(user) == subscription_models.SubscriptionStep.USER_PROFILING

    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    def test_import_makes_user_beneficiary(self, get_applications_with_details):
        """
        Test that an existing user with its phone number validated can become
        beneficiary.
        """
        date_of_birth = self.BENEFICIARY_BIRTH_DATE.strftime("%Y-%m-%dT%H:%M:%S")

        # Create a user that has validated its email and phone number, meaning it
        # should become beneficiary.
        user = users_factories.UserFactory(
            email=self.EMAIL,
            isEmailValidated=True,
            dateOfBirth=date_of_birth,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.USER_PROFILING,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        get_applications_with_details.return_value = [
            fixture.make_parsed_graphql_application(application_id=123, state="accepte", email=user.email)
        ]

        import_dms_accepted_applications(procedure_id=6712558)

        assert users_models.User.query.count() == 1
        user = users_models.User.query.first()

        assert user.firstName == "John"
        assert user.postalCode == "67200"
        assert user.address == "3 La Bigotais 22800 Saint-Donan"
        assert user.has_beneficiary_role
        assert user.phoneNumber == "0123456789"
        assert user.idPieceNumber == "123123123"

        assert len(user.beneficiaryFraudChecks) == 3

        dms_fraud_check = next(
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type == fraud_models.FraudCheckType.DMS
        )
        assert dms_fraud_check.type == fraud_models.FraudCheckType.DMS
        fraud_content = fraud_models.DMSContent(**dms_fraud_check.resultContent)
        assert fraud_content.birth_date == user.dateOfBirth.date()
        assert fraud_content.address == "3 La Bigotais 22800 Saint-Donan"

        assert next(
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type == fraud_models.FraudCheckType.HONOR_STATEMENT
        )

        assert len(push_testing.requests) == 2

    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    def test_import_makes_user_beneficiary_after_19_birthday(self, get_applications_with_details):
        date_of_birth = (datetime.utcnow() - relativedelta(years=19)).strftime("%Y-%m-%dT%H:%M:%S")

        # Create a user that has validated its email and phone number, meaning it
        # should become beneficiary.
        user = users_factories.UserFactory(
            email=self.EMAIL,
            isEmailValidated=True,
            dateOfBirth=date_of_birth,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.USER_PROFILING,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        get_applications_with_details.return_value = [
            fixture.make_parsed_graphql_application(application_id=123, state="accepte", email=user.email)
        ]
        import_dms_accepted_applications(procedure_id=6712558)

        user = users_models.User.query.one()

        assert user.roles == [users_models.UserRole.BENEFICIARY]

    @override_features(FORCE_PHONE_VALIDATION=False)
    @freezegun.freeze_time("2021-10-30 09:00:00")
    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    def test_import_duplicated_user(self, get_applications_with_details):
        existing_user = users_factories.BeneficiaryGrant18Factory(
            firstName="John",
            lastName="Doe",
            email="john.doe.beneficiary@example.com",
            dateOfBirth=self.BENEFICIARY_BIRTH_DATE,
            idPieceNumber="1234123432",
            isEmailValidated=True,
            isActive=True,
        )

        user = users_factories.UserFactory(
            firstName="john",
            lastName="doe",
            email="john.doe@example.com",
            dateOfBirth=existing_user.dateOfBirth,
            isEmailValidated=True,
            isActive=True,
        )

        get_applications_with_details.return_value = [
            fixture.make_parsed_graphql_application(
                application_id=123, state="accepte", email=user.email, birth_date=self.BENEFICIARY_BIRTH_DATE
            )
        ]
        import_dms_accepted_applications(procedure_id=6712558)

        assert users_models.User.query.count() == 2

        user = users_models.User.query.get(user.id)
        assert len(user.beneficiaryFraudChecks) == 1
        fraud_check = user.beneficiaryFraudChecks[0]
        assert fraud_check.type == fraud_models.FraudCheckType.DMS
        assert fraud_models.FraudReasonCode.DUPLICATE_USER in fraud_check.reasonCodes
        assert fraud_check.status == fraud_models.FraudCheckStatus.SUSPICIOUS

        sub_msg = user.subscriptionMessages[0]
        assert (
            sub_msg.userMessage
            == "Ton dossier a été bloqué : Il y a déjà un compte à ton nom sur le pass Culture. Tu peux contacter le support pour plus d'informations."
        )
        assert sub_msg.callToActionIcon == subscription_models.CallToActionIcon.EMAIL

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["params"] == {"DUPLICATE_BENEFICIARY_EMAIL": "joh***@example.com"}

    @override_features(FORCE_PHONE_VALIDATION=False)
    @freezegun.freeze_time("2021-10-30 09:00:00")
    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    def test_import_with_existing_user_with_the_same_id_number(self, get_applications_with_details, mocker):
        beneficiary = users_factories.BeneficiaryGrant18Factory(idPieceNumber="1234123412")
        applicant = users_factories.UserFactory(
            email=self.EMAIL,
            isEmailValidated=True,
            dateOfBirth=self.BENEFICIARY_BIRTH_DATE,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        get_applications_with_details.return_value = [
            fixture.make_parsed_graphql_application(
                application_id=123,
                state="accepte",
                email=applicant.email,
                id_piece_number="1234123412",
                birth_date=self.BENEFICIARY_BIRTH_DATE,
            )
        ]

        process_mock = mocker.patch("pcapi.core.subscription.api.on_successful_application")
        import_dms_accepted_applications(procedure_id=6712558)

        assert process_mock.call_count == 0
        assert users_models.User.query.count() == 2

        fraud_check = applicant.beneficiaryFraudChecks[0]
        assert fraud_check.type == fraud_models.FraudCheckType.DMS

        assert fraud_check.status == fraud_models.FraudCheckStatus.SUSPICIOUS
        assert (
            fraud_check.reason == f"La pièce d'identité n°1234123412 est déjà prise par l'utilisateur {beneficiary.id}"
        )

        fraud_content = fraud_models.DMSContent(**fraud_check.resultContent)
        assert fraud_content.birth_date == applicant.dateOfBirth.date()
        assert fraud_content.address == "3 La Bigotais 22800 Saint-Donan"

        sub_msg = applicant.subscriptionMessages[0]
        assert (
            sub_msg.userMessage
            == "Ton dossier a été bloqué : Il y a déjà un compte à ton nom sur le pass Culture. Tu peux contacter le support pour plus d'informations."
        )
        assert sub_msg.callToActionIcon == subscription_models.CallToActionIcon.EMAIL

    @override_features(FORCE_PHONE_VALIDATION=False)
    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    def test_import_native_app_user(self, get_applications_with_details):
        user = users_factories.UserFactory(email=self.EMAIL, dateOfBirth=self.BENEFICIARY_BIRTH_DATE, city="Quito")
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.USER_PROFILING,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        push_testing.reset_requests()
        get_applications_with_details.return_value = [
            fixture.make_parsed_graphql_application(
                application_id=123,
                state="accepte",
                email=user.email,
            )
        ]
        import_dms_accepted_applications(procedure_id=6712558)

        # then
        assert users_models.User.query.count() == 1

        user = users_models.User.query.first()
        assert user.firstName == "John"
        assert user.postalCode == "67200"

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["template"] == dataclasses.asdict(
            TransactionalEmail.ACCEPTED_AS_BENEFICIARY.value
        )

        assert len(push_testing.requests) == 2
        assert push_testing.requests[0]["attribute_values"]["u.is_beneficiary"]

    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    def test_dms_application_value_error(self, get_applications_with_details):
        user = users_factories.UserFactory()
        get_applications_with_details.return_value = [
            fixture.make_parsed_graphql_application(
                application_id=123,
                state="accepte",
                email=user.email,
                postal_code="Strasbourg",
                id_piece_number="121314",
            )
        ]
        import_dms_accepted_applications(procedure_id=6712558)

        fraud_check = user.beneficiaryFraudChecks[0]
        assert fraud_check.status == fraud_models.FraudCheckStatus.ERROR
        assert fraud_check.thirdPartyId == "123"
        assert (
            fraud_check.reason
            == "Erreur dans les données soumises dans le dossier DMS : 'id_piece_number' (121314),'postal_code' (Strasbourg)"
        )
        assert fraud_check.reasonCodes == [fraud_models.FraudReasonCode.ERROR_IN_DATA]

        assert len(mails_testing.outbox) == 1
        assert (
            mails_testing.outbox[0].sent_data["template"]
            == TransactionalEmail.PRE_SUBSCRIPTION_DMS_ERROR_TO_BENEFICIARY.value.__dict__
        )

        # A second import should ignore the already processed application
        user_fraud_check_number = len(user.beneficiaryFraudChecks)
        import_dms_accepted_applications(procedure_id=6712558)
        assert len(user.beneficiaryFraudChecks) == user_fraud_check_number

    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    def test_dms_application_value_error_known_user(self, get_applications_with_details):
        user = users_factories.UserFactory()
        get_applications_with_details.return_value = [
            fixture.make_parsed_graphql_application(
                application_id=1, state="accepte", postal_code="Strasbourg", id_piece_number="121314", email=user.email
            )
        ]
        import_dms_accepted_applications(procedure_id=6712558)

        fraud_check = user.beneficiaryFraudChecks[0]
        assert fraud_check.status == fraud_models.FraudCheckStatus.ERROR
        assert fraud_check.thirdPartyId == "1"
        assert (
            fraud_check.reason
            == "Erreur dans les données soumises dans le dossier DMS : 'id_piece_number' (121314),'postal_code' (Strasbourg)"
        )
        assert fraud_check.reasonCodes == [fraud_models.FraudReasonCode.ERROR_IN_DATA]

        assert len(mails_testing.outbox) == 1
        assert (
            mails_testing.outbox[0].sent_data["template"]
            == TransactionalEmail.PRE_SUBSCRIPTION_DMS_ERROR_TO_BENEFICIARY.value.__dict__
        )

    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    def test_dms_application_without_city_does_not_validate_profile(self, get_applications_with_details):
        # instanciate user with validated phone number
        user = users_factories.UserFactory(
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            dateOfBirth=self.BENEFICIARY_BIRTH_DATE,
            city=None,
        )
        # Perform user profiling
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.USER_PROFILING,
            resultContent=fraud_factories.UserProfilingFraudDataFactory(
                risk_rating=fraud_models.UserProfilingRiskRating.TRUSTED
            ),
            eligibilityType=users_models.EligibilityType.AGE18,
            status=fraud_models.FraudCheckStatus.OK,
        )
        get_applications_with_details.return_value = [
            fixture.make_parsed_graphql_application(
                email=user.email,
                application_id=123,
                state="accepte",
            )
        ]
        import_dms_accepted_applications(procedure_id=6712558)

        assert (
            subscription_api.get_next_subscription_step(user) == subscription_models.SubscriptionStep.PROFILE_COMPLETION
        )

    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    def test_complete_dms_application_also_validates_profile(self, get_applications_with_details, client):
        # instanciate user with validated phone number
        user = users_factories.UserFactory(
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            dateOfBirth=self.BENEFICIARY_BIRTH_DATE,
            city=None,
        )
        # Perform user profiling
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.USER_PROFILING,
            resultContent=fraud_factories.UserProfilingFraudDataFactory(
                risk_rating=fraud_models.UserProfilingRiskRating.TRUSTED
            ),
            eligibilityType=users_models.EligibilityType.AGE18,
            status=fraud_models.FraudCheckStatus.OK,
        )
        get_applications_with_details.return_value = [
            fixture.make_parsed_graphql_application(
                email=user.email,
                application_id=123,
                state="accepte",
                city="Strasbourg",
            )
        ]
        import_dms_accepted_applications(procedure_id=6712558)

        client.with_token(user.email)
        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] == None
        assert users_models.UserRole.BENEFICIARY in user.roles


@pytest.mark.usefixtures("db_session")
class GraphQLSourceProcessApplicationTest:
    def test_process_accepted_application_user_already_created(self):
        user = users_factories.UserFactory(dateOfBirth=AGE18_ELIGIBLE_BIRTH_DATE)
        application_id = 123123
        application_details = fixture.make_parsed_graphql_application(application_id, "accepte", email=user.email)
        information = dms_connector_api.parse_beneficiary_information_graphql(application_details, 123123)
        # fixture
        dms_api._process_accepted_application(user, information)

        assert len(user.beneficiaryFraudChecks) == 2
        dms_fraud_check = next(
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type == fraud_models.FraudCheckType.DMS
        )
        assert not dms_fraud_check.reasonCodes
        assert dms_fraud_check.status == fraud_models.FraudCheckStatus.OK
        statement_fraud_check = next(
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type == fraud_models.FraudCheckType.HONOR_STATEMENT
        )
        assert statement_fraud_check.status == fraud_models.FraudCheckStatus.OK
        assert statement_fraud_check.reason == "honor statement contained in DMS application"

    def test_process_accepted_application_user_registered_at_18(self):
        user = users_factories.UserFactory(
            dateOfBirth=AGE18_ELIGIBLE_BIRTH_DATE,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.USER_PROFILING, status=fraud_models.FraudCheckStatus.OK
        )

        application_id = 123123
        application_details = fixture.make_parsed_graphql_application(application_id, "accepte", email=user.email)
        information = dms_connector_api.parse_beneficiary_information_graphql(application_details, 123123)
        # fixture
        dms_api._process_accepted_application(user, information)
        assert len(user.beneficiaryFraudChecks) == 3  # user profiling, DMS, honor statement
        assert user.roles == [users_models.UserRole.BENEFICIARY]

    def test_process_accepted_application_user_registered_at_18_dms_at_19(self):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.utcnow() - relativedelta(years=19, months=4),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.USER_PROFILING,
            status=fraud_models.FraudCheckStatus.OK,
            dateCreated=datetime.utcnow() - relativedelta(years=1, months=2),
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        application_id = 123123
        application_details = fixture.make_parsed_graphql_application(
            application_id,
            "accepte",
            email=user.email,
            birth_date=user.dateOfBirth,
            construction_datetime=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+02:00"),
        )
        information = dms_connector_api.parse_beneficiary_information_graphql(application_details, 123123)
        # fixture
        dms_api._process_accepted_application(user, information)
        assert len(user.beneficiaryFraudChecks) == 3  # user profiling, DMS, honor statement
        assert user.roles == [users_models.UserRole.BENEFICIARY]

    def test_process_accepted_application_user_not_eligible(self):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.utcnow() - relativedelta(years=19, months=4),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )

        application_id = 123123
        application_details = fixture.make_parsed_graphql_application(
            application_id,
            "accepte",
            email=user.email,
            birth_date=user.dateOfBirth,
            construction_datetime=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+02:00"),
        )
        information = dms_connector_api.parse_beneficiary_information_graphql(application_details, 123123)
        # fixture
        dms_api._process_accepted_application(user, information)
        assert len(user.beneficiaryFraudChecks) == 1
        dms_fraud_check = user.beneficiaryFraudChecks[0]
        assert dms_fraud_check.status == fraud_models.FraudCheckStatus.KO
        assert fraud_models.FraudReasonCode.NOT_ELIGIBLE in dms_fraud_check.reasonCodes
        assert user.roles == []

    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    def test_dms_application_value_error(self, get_applications_with_details):
        user = users_factories.UserFactory()
        get_applications_with_details.return_value = [
            fixture.make_parsed_graphql_application(
                application_id=1, state="accepte", postal_code="Strasbourg", id_piece_number="121314", email=user.email
            )
        ]

        import_dms_accepted_applications(procedure_id=6712558)

        dms_fraud_check = fraud_models.BeneficiaryFraudCheck.query.first()
        assert dms_fraud_check.userId == user.id
        assert dms_fraud_check.status == fraud_models.FraudCheckStatus.ERROR
        assert dms_fraud_check.thirdPartyId == "1"
        assert (
            dms_fraud_check.reason
            == "Erreur dans les données soumises dans le dossier DMS : 'id_piece_number' (121314),'postal_code' (Strasbourg)"
        )
        assert dms_fraud_check.reasonCodes == [fraud_models.FraudReasonCode.ERROR_IN_DATA]

        assert len(mails_testing.outbox) == 1
        assert (
            mails_testing.outbox[0].sent_data["template"]
            == TransactionalEmail.PRE_SUBSCRIPTION_DMS_ERROR_TO_BENEFICIARY.value.__dict__
        )
        assert len(user.subscriptionMessages) == 1
        assert user.subscriptionMessages[0]
        assert (
            user.subscriptionMessages[0].userMessage
            == "Ton dossier déposé sur le site Démarches-Simplifiées a été refusé car les champs ‘ta pièce d'identité, ton code postal’ ne sont pas valides."
        )
        assert user.subscriptionMessages[0].popOverIcon == subscription_models.PopOverIcon.WARNING

    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    def test_avoid_reimporting_already_imported_user(self, get_applications_with_details):
        procedure_id = 42
        already_imported_user = users_factories.BeneficiaryGrant18Factory()

        get_applications_with_details.return_value = [
            fixture.make_parsed_graphql_application(
                application_id=2,
                state="accepte",
                email=already_imported_user.email,
            ),
        ]

        import_dms_accepted_applications(procedure_id=procedure_id)

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter(
            fraud_models.BeneficiaryFraudCheck.userId == already_imported_user.id,
            fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.DMS,
        ).first()
        assert fraud_check.status == fraud_models.FraudCheckStatus.KO
        assert (
            "L’utilisateur est déjà bénéfiaire du pass AGE18 ; "
            "L’utilisateur est déjà bénéfiaire, avec un portefeuille non expiré. Il ne peut pas prétendre au pass culture 18 ans"
        ) in fraud_check.reason
