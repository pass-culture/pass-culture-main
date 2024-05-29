import dataclasses
from datetime import date
from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
import pytest
import time_machine

from pcapi.connectors.dms import api as dms_connector_api
import pcapi.core.finance.models as finance_models
import pcapi.core.fraud.factories as fraud_factories
import pcapi.core.fraud.models as fraud_models
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
import pcapi.core.subscription.api as subscription_api
from pcapi.core.subscription.dms import api as dms_subscription_api
import pcapi.core.subscription.models as subscription_models
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.core.users.constants import ELIGIBILITY_AGE_18
import pcapi.notifications.push.testing as push_testing
from pcapi.scripts.subscription.dms.import_dms_applications import import_all_updated_dms_applications

from tests.scripts.beneficiary import fixture


NOW = datetime.utcnow()

AGE18_ELIGIBLE_BIRTH_DATE = datetime.utcnow() - relativedelta(years=ELIGIBILITY_AGE_18)


@pytest.mark.usefixtures("db_session")
class RunTest:
    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    def test_should_retrieve_applications_from_new_procedure_number(
        self,
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

        import_all_updated_dms_applications(6712558)
        assert get_applications_with_details.call_count == 1
        get_applications_with_details.assert_called_with(6712558)

    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    @patch("pcapi.core.subscription.api.activate_beneficiary_if_no_missing_step")
    def test_all_applications_are_processed_once(
        self,
        activate_beneficiary_if_no_missing_step,
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

        import_all_updated_dms_applications(6712558)
        assert activate_beneficiary_if_no_missing_step.call_count == 3

    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    @patch("pcapi.core.subscription.api.activate_beneficiary_if_no_missing_step")
    def test_application_for_already_beneficiary_is_not_downgraded(
        self, activate_beneficiary_if_no_missing_step, get_applications_with_details
    ):
        # same user, but different
        user = users_factories.BeneficiaryGrant18Factory(email="john.doe@example.com")
        get_applications_with_details.return_value = [
            fixture.make_parsed_graphql_application(123, "accepte", email="john.doe@example.com")
        ]

        import_all_updated_dms_applications(6712558)

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter(
            fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.DMS
        ).one()
        assert fraud_check.userId == user.id
        assert fraud_check.thirdPartyId == "123"
        assert fraud_check.status == fraud_models.FraudCheckStatus.OK

        activate_beneficiary_if_no_missing_step.assert_called_once()

    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    @patch("pcapi.core.subscription.api.activate_beneficiary_if_no_missing_step")
    def test_beneficiary_is_created_with_procedure_number(
        self, activate_beneficiary_if_no_missing_step, get_applications_with_details
    ):
        applicant = users_factories.UserFactory(firstName="Doe", lastName="John", email="john.doe@test.com")
        get_applications_with_details.return_value = [
            fixture.make_parsed_graphql_application(
                123,
                "accepte",
                id_piece_number="123123121",
                email=applicant.email,
                birth_date=AGE18_ELIGIBLE_BIRTH_DATE,
                procedure_number=6712558,
            )
        ]

        import_all_updated_dms_applications(6712558)

        activate_beneficiary_if_no_missing_step.assert_called_with(user=applicant)


@pytest.mark.usefixtures("db_session")
class RunIntegrationTest:
    EMAIL = "john.doe@example.com"
    BENEFICIARY_BIRTH_DATE = date.today() - timedelta(days=6752)  # ~18.5 years

    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    def test_import_user(self, get_applications_with_details):
        user = users_factories.UserFactory(
            firstName="profile-firstname",
            lastName="doe",
            email="john.doe@example.com",
            dateOfBirth=AGE18_ELIGIBLE_BIRTH_DATE,
            postalCode="12400",
            address="Route de Gozon",
        )

        get_applications_with_details.return_value = [
            fixture.make_parsed_graphql_application(
                application_number=123, state="accepte", email=user.email, city="Strasbourg"
            )
        ]
        import_all_updated_dms_applications(6712558)

        assert users_models.User.query.count() == 1
        user = users_models.User.query.first()
        assert user.firstName == "profile-firstname"
        assert user.postalCode == "12400"
        assert user.address == "Route de Gozon"
        assert user.phoneNumber is None

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter(
            fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.DMS
        ).one()
        assert fraud_check.userId == user.id
        assert fraud_check.thirdPartyId == "123"
        assert fraud_check.status == fraud_models.FraudCheckStatus.OK
        assert len(push_testing.requests) == 3

        # Check that a PROFILE_COMPLETION fraud check is created
        profile_completion_fraud_checks = [
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type == fraud_models.FraudCheckType.PROFILE_COMPLETION
        ]
        assert len(profile_completion_fraud_checks) == 1
        profile_completion_fraud_check = profile_completion_fraud_checks[0]
        assert profile_completion_fraud_check.status == fraud_models.FraudCheckStatus.OK
        assert profile_completion_fraud_check.reason == "Completed in DMS application 123"

    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    def test_import_ex_underage_beneficiary(self, get_applications_with_details):
        with time_machine.travel(datetime.utcnow() - relativedelta(years=2, month=1)):
            user = users_factories.UnderageBeneficiaryFactory(
                email="john.doe@example.com",
                firstName="john",
                lastName="doe",
                dateOfBirth=AGE18_ELIGIBLE_BIRTH_DATE,
                subscription_age=15,
                phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            )
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)
        details = fixture.make_parsed_graphql_application(application_number=123, state="accepte", email=user.email)
        details.draft_date = datetime.utcnow().isoformat()
        get_applications_with_details.return_value = [details]
        import_all_updated_dms_applications(6712558)

        assert users_models.User.query.count() == 1
        user = users_models.User.query.first()
        assert user.has_beneficiary_role
        deposits = finance_models.Deposit.query.filter_by(user=user).all()
        age_18_deposit = next(deposit for deposit in deposits if deposit.type == finance_models.DepositType.GRANT_18)
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
                application_number=123, state="accepte", email="nonexistant@example.com", procedure_number=6712558
            )
        ]

        import_all_updated_dms_applications(6712558)
        dms_application = fraud_models.OrphanDmsApplication.query.filter(
            fraud_models.OrphanDmsApplication.application_id == 123
        ).one()
        assert dms_application.application_id == 123
        assert dms_application.process_id == 6712558
        assert dms_application.email == "nonexistant@example.com"
        assert dms_application.dateCreated is not None

    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    def test_phone_not_validated_create_beneficiary_with_phone_to_validate(self, get_applications_with_details):
        """
        Test that an imported user without a validated phone number, and the
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
            fixture.make_parsed_graphql_application(
                application_number=123,
                state="accepte",
                email=user.email,
                construction_datetime=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+02:00"),
            )
        ]
        # when
        import_all_updated_dms_applications(6712558)

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
        assert len(push_testing.requests) == 3

        assert not user.is_beneficiary
        assert not user.deposit
        assert (
            subscription_api.get_user_subscription_state(user).next_step
            == subscription_models.SubscriptionStep.PHONE_VALIDATION
        )

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"]["id_prod"] == 679  # complete subscription

    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    def test_import_makes_user_beneficiary(self, get_applications_with_details):
        """
        Test that an existing user with its phone number validated can become
        beneficiary.
        """
        date_of_birth = self.BENEFICIARY_BIRTH_DATE.strftime("%Y-%m-%dT%H:%M:%S")
        dms_validated_birth_date = date.today() - relativedelta(years=18)

        # Create a user that has validated its email and phone number, meaning it
        # should become beneficiary.
        user = users_factories.UserFactory(
            email=self.EMAIL,
            isEmailValidated=True,
            dateOfBirth=date_of_birth,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)

        get_applications_with_details.return_value = [
            fixture.make_parsed_graphql_application(
                application_number=123,
                state="accepte",
                email=user.email,
                birth_date=dms_validated_birth_date,
                construction_datetime=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+02:00"),
            ),
        ]

        import_all_updated_dms_applications(6712558)

        assert users_models.User.query.count() == 1
        user = users_models.User.query.first()

        assert user.firstName == "John"
        assert user.postalCode == "67200"
        assert user.departementCode == "67"
        assert user.address == "3 La Bigotais 22800 Saint-Donan"
        assert user.has_beneficiary_role
        assert user.phoneNumber is None
        assert user.idPieceNumber == "123123123"
        assert user.dateOfBirth.date() == self.BENEFICIARY_BIRTH_DATE
        assert user.validatedBirthDate == dms_validated_birth_date

        assert len(user.beneficiaryFraudChecks) == 3  # DMS, HONOR_STATEMENT, PROFILE_COMPLETION

        dms_fraud_check = next(
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type == fraud_models.FraudCheckType.DMS
        )
        assert dms_fraud_check.type == fraud_models.FraudCheckType.DMS
        fraud_content = dms_fraud_check.source_data()
        assert fraud_content.birth_date == dms_validated_birth_date
        assert fraud_content.address == "3 La Bigotais 22800 Saint-Donan"

        assert next(
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type == fraud_models.FraudCheckType.HONOR_STATEMENT
        )

        assert len(push_testing.requests) == 4

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"]["id_prod"] == 96  # accepted as beneficiary email

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
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)
        get_applications_with_details.return_value = [
            fixture.make_parsed_graphql_application(
                application_number=123,
                state="accepte",
                email=user.email,
                # For the user to be automatically credited, the DMS application must be created before user's 19th birthday
                construction_datetime=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+02:00"),
            )
        ]
        import_all_updated_dms_applications(6712558)

        user = users_models.User.query.one()

        assert user.roles == [users_models.UserRole.BENEFICIARY]

    @time_machine.travel("2021-10-30 09:00:00")
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
                application_number=123, state="accepte", email=user.email, birth_date=self.BENEFICIARY_BIRTH_DATE
            )
        ]
        import_all_updated_dms_applications(6712558)

        assert users_models.User.query.count() == 2

        user = users_models.User.query.filter_by(user.id).one()
        assert len(user.beneficiaryFraudChecks) == 1
        fraud_check = user.beneficiaryFraudChecks[0]
        assert fraud_check.type == fraud_models.FraudCheckType.DMS
        assert fraud_models.FraudReasonCode.DUPLICATE_USER in fraud_check.reasonCodes
        assert fraud_check.status == fraud_models.FraudCheckStatus.SUSPICIOUS

        message = dms_subscription_api.get_dms_subscription_message(fraud_check)
        assert message.user_message == (
            "Ton dossier a été refusé car il y a déjà un compte bénéficiaire à ton nom. "
            "Connecte-toi avec l’adresse mail joh***@example.com ou contacte le support si tu penses qu’il s’agit d’une erreur. "
            "Si tu n’as plus ton mot de passe, tu peux effectuer une demande de réinitialisation."
        )
        assert message.call_to_action.icon == subscription_models.CallToActionIcon.EMAIL

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["params"] == {"DUPLICATE_BENEFICIARY_EMAIL": "joh***@example.com"}

    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    @patch("pcapi.core.subscription.api.activate_beneficiary_if_no_missing_step")
    def test_import_with_existing_user_with_the_same_id_number(
        self,
        mocked_activate_beneficiary_if_no_missing_step,
        get_applications_with_details,
    ):
        beneficiary = users_factories.BeneficiaryGrant18Factory(idPieceNumber="123412341234")
        applicant = users_factories.UserFactory(
            email=self.EMAIL,
            isEmailValidated=True,
            dateOfBirth=self.BENEFICIARY_BIRTH_DATE,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        get_applications_with_details.return_value = [
            fixture.make_parsed_graphql_application(
                application_number=123,
                state="accepte",
                email=applicant.email,
                id_piece_number="123412341234",
                birth_date=self.BENEFICIARY_BIRTH_DATE,
            )
        ]

        import_all_updated_dms_applications(6712558)

        mocked_activate_beneficiary_if_no_missing_step.assert_not_called()
        assert users_models.User.query.count() == 2

        fraud_check = applicant.beneficiaryFraudChecks[0]
        assert fraud_check.type == fraud_models.FraudCheckType.DMS

        assert fraud_check.status == fraud_models.FraudCheckStatus.SUSPICIOUS
        assert (
            fraud_check.reason
            == f"La pièce d'identité n°123412341234 est déjà prise par l'utilisateur {beneficiary.id}"
        )

        fraud_content = fraud_models.DMSContent(**fraud_check.resultContent)
        assert fraud_content.birth_date == applicant.dateOfBirth.date()
        assert fraud_content.address == "3 La Bigotais 22800 Saint-Donan"

    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    def test_import_native_app_user(self, get_applications_with_details):
        user = users_factories.UserFactory(
            email=self.EMAIL,
            dateOfBirth=self.BENEFICIARY_BIRTH_DATE,
            city="Quito",
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)
        push_testing.reset_requests()
        get_applications_with_details.return_value = [
            fixture.make_parsed_graphql_application(
                application_number=123,
                state="accepte",
                email=user.email,
                construction_datetime=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+02:00"),
            )
        ]
        import_all_updated_dms_applications(6712558)

        # then
        assert users_models.User.query.count() == 1

        user = users_models.User.query.first()
        assert user.firstName == "John"
        assert user.postalCode == "67200"

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(
            TransactionalEmail.ACCEPTED_AS_BENEFICIARY.value
        )

        assert len(push_testing.requests) == 4
        assert push_testing.requests[1]["attribute_values"]["u.is_beneficiary"]

    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    def test_dms_application_value_error(self, get_applications_with_details):
        user = users_factories.UserFactory()
        get_applications_with_details.return_value = [
            fixture.make_parsed_graphql_application(
                application_number=123,
                state="accepte",
                email=user.email,
                postal_code="Strasbourg",
                id_piece_number="121314",
            )
        ]
        import_all_updated_dms_applications(6712558)

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
            mails_testing.outbox[0]["template"]
            == TransactionalEmail.PRE_SUBSCRIPTION_DMS_ERROR_TO_BENEFICIARY.value.__dict__
        )

        # A second import should ignore the already processed application
        user_fraud_check_number = len(user.beneficiaryFraudChecks)
        import_all_updated_dms_applications(6712558)
        assert len(user.beneficiaryFraudChecks) == user_fraud_check_number

    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    def test_dms_application_value_error_known_user(self, get_applications_with_details):
        user = users_factories.UserFactory()
        get_applications_with_details.return_value = [
            fixture.make_parsed_graphql_application(
                application_number=1,
                state="accepte",
                postal_code="Strasbourg",
                id_piece_number="121314",
                email=user.email,
            )
        ]
        import_all_updated_dms_applications(6712558)

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
            mails_testing.outbox[0]["template"]
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
        get_applications_with_details.return_value = [
            fixture.make_parsed_graphql_application(
                email=user.email,
                application_number=123,
                state="accepte",
            )
        ]
        import_all_updated_dms_applications(6712558)

        assert (
            subscription_api.get_user_subscription_state(user).next_step
            == subscription_models.SubscriptionStep.PROFILE_COMPLETION
        )

    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    def test_complete_dms_application_also_validates_profile(self, get_applications_with_details, client):
        # instanciate user with validated phone number
        user = users_factories.UserFactory(
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            dateOfBirth=self.BENEFICIARY_BIRTH_DATE,
            city=None,
        )
        get_applications_with_details.return_value = [
            fixture.make_parsed_graphql_application(
                email=user.email,
                application_number=123,
                state="accepte",
                city="Strasbourg",
                construction_datetime=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+02:00"),
            )
        ]
        import_all_updated_dms_applications(6712558)

        client.with_token(user.email)
        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] is None
        assert users_models.UserRole.BENEFICIARY in user.roles


@pytest.mark.usefixtures("db_session")
class GraphQLSourceProcessApplicationTest:
    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    def test_process_accepted_application_user_already_created(self, get_applications_with_details):
        user = users_factories.UserFactory(dateOfBirth=AGE18_ELIGIBLE_BIRTH_DATE)

        get_applications_with_details.return_value = [
            fixture.make_parsed_graphql_application(123, "accepte", email=user.email),
        ]

        import_all_updated_dms_applications(6712558)

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

    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    def test_process_accepted_application_user_registered_at_18(self, get_applications_with_details):
        user = users_factories.UserFactory(
            dateOfBirth=AGE18_ELIGIBLE_BIRTH_DATE,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)

        get_applications_with_details.return_value = [
            fixture.make_parsed_graphql_application(
                123,
                "accepte",
                email=user.email,
                construction_datetime=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+02:00"),
            ),
        ]

        import_all_updated_dms_applications(6712558)

        assert len(user.beneficiaryFraudChecks) == 3  # profile, DMS, honor statement
        assert user.roles == [users_models.UserRole.BENEFICIARY]

    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    def test_process_accepted_application_user_registered_at_18_dms_at_19(self, get_applications_with_details):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.utcnow() - relativedelta(years=19, months=4),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(
            user=user,
            dateCreated=datetime.utcnow() - relativedelta(years=1, months=2),
        )

        get_applications_with_details.return_value = [
            fixture.make_parsed_graphql_application(
                123123,
                "accepte",
                email=user.email,
                birth_date=user.dateOfBirth,
                # For the user to be automatically credited, the DMS application must be created before user's 19th birthday
                construction_datetime=(datetime.utcnow() - relativedelta(months=5)).strftime("%Y-%m-%dT%H:%M:%S+02:00"),
            ),
        ]

        import_all_updated_dms_applications(6712558)

        assert len(user.beneficiaryFraudChecks) == 3  # profile, DMS, honor statement
        assert user.roles == [users_models.UserRole.BENEFICIARY]

    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    def test_process_accepted_application_user_registered_at_18_dms_started_at_19(self, get_applications_with_details):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.utcnow() - relativedelta(years=19, days=1),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(
            user=user,
            dateCreated=datetime.utcnow() - relativedelta(years=1),
        )

        get_applications_with_details.return_value = [
            fixture.make_parsed_graphql_application(
                123123,
                "accepte",
                email=user.email,
                birth_date=user.dateOfBirth,
                # For the user to be automatically credited, the DMS application must be created before user's 19th birthday
                # Here it's created after 19yo, so requires a manual review
                construction_datetime=(datetime.utcnow()).strftime("%Y-%m-%dT%H:%M:%S+02:00"),
            ),
        ]

        import_all_updated_dms_applications(6712558)

        assert len(user.beneficiaryFraudChecks) == 3  # profile, DMS, honor statement
        assert mails_testing.outbox[0]["subject"] == "Revue manuelle nécessaire"

    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    def test_process_accepted_application_user_not_eligible(self, get_applications_with_details):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.utcnow() - relativedelta(years=19, months=4),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )

        get_applications_with_details.return_value = [
            fixture.make_parsed_graphql_application(
                123123,
                "accepte",
                email=user.email,
                birth_date=user.dateOfBirth,
                construction_datetime=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+02:00"),
            ),
        ]

        import_all_updated_dms_applications(6712558)

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
                application_number=1,
                state="accepte",
                postal_code="Strasbourg",
                id_piece_number="121314",
                email=user.email,
            )
        ]

        import_all_updated_dms_applications(6712558)

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
            mails_testing.outbox[0]["template"]
            == TransactionalEmail.PRE_SUBSCRIPTION_DMS_ERROR_TO_BENEFICIARY.value.__dict__
        )

    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    def test_reimport_same_user(self, get_applications_with_details):
        procedure_number = 42
        already_imported_user = users_factories.BeneficiaryGrant18Factory()

        get_applications_with_details.return_value = [
            fixture.make_parsed_graphql_application(
                application_number=2,
                state="accepte",
                email=already_imported_user.email,
            ),
        ]

        import_all_updated_dms_applications(procedure_number)

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter(
            fraud_models.BeneficiaryFraudCheck.userId == already_imported_user.id,
            fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.DMS,
        ).one()
        assert fraud_check.status == fraud_models.FraudCheckStatus.OK
