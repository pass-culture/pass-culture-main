import dataclasses
import datetime
from unittest import mock
from unittest.mock import patch

import pytest
import time_machine
from dateutil.relativedelta import relativedelta

import pcapi.core.mails.testing as mails_testing
import pcapi.notifications.push.testing as push_testing
from pcapi import settings
from pcapi.connectors.dms import api as api_dms
from pcapi.connectors.dms import factories as dms_factories
from pcapi.connectors.dms import models as dms_models
from pcapi.connectors.dms import serializer as dms_serializer
from pcapi.core.finance import models as finance_models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.subscription import factories as subscription_factories
from pcapi.core.subscription import messages as subscription_messages
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription import schemas as subscription_schemas
from pcapi.core.subscription.api import get_user_subscription_state
from pcapi.core.subscription.dms import api as dms_subscription_api
from pcapi.core.subscription.dms import dms_internal_mailing
from pcapi.core.subscription.dms import schemas as dms_schemas
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.core.users.constants import ELIGIBILITY_AGE_18
from pcapi.core.users.constants import ELIGIBILITY_END_AGE
from pcapi.models import db
from pcapi.utils import date as date_utils
from pcapi.utils.transaction_manager import atomic

from tests.connectors import fixtures


AGE18_ELIGIBLE_BIRTH_DATE = datetime.date.today() - relativedelta(years=ELIGIBILITY_AGE_18)


@pytest.mark.usefixtures("db_session")
class DMSOrphanSubsriptionTest:
    @patch.object(api_dms.DMSGraphQLClient, "execute_query")
    def test_dms_orphan_corresponding_user(self, execute_query):
        application_number = 1234
        procedure_number = 4321
        email = "dms_orphan@example.com"

        user = users_factories.UserFactory(email=email)
        subscription_factories.OrphanDmsApplicationFactory(
            email=email, application_id=application_number, process_id=procedure_number
        )

        execute_query.return_value = fixtures.make_single_application(
            application_number, dms_models.GraphQLApplicationStates.draft, email=email
        )

        dms_subscription_api.try_dms_orphan_adoption(user)

        fraud_check = db.session.query(subscription_models.BeneficiaryFraudCheck).filter_by(userId=user.id).first()
        assert fraud_check is not None

        dms_orphan = db.session.query(subscription_models.OrphanDmsApplication).filter_by(email=user.email).first()
        assert dms_orphan is None

    @patch.object(api_dms.DMSGraphQLClient, "execute_query")
    def test_dms_orphan_corresponding_user_with_field_error(self, execute_query):
        application_number = 1234
        procedure_number = 4321
        email = "dms_orphan@example.com"

        user = users_factories.UserFactory(email=email)
        subscription_factories.OrphanDmsApplicationFactory(
            email=email, application_id=application_number, process_id=procedure_number
        )

        execute_query.return_value = fixtures.make_single_application(
            application_number, dms_models.GraphQLApplicationStates.draft, email=email, postal_code="1234"
        )

        dms_subscription_api.try_dms_orphan_adoption(user)

        fraud_check = db.session.query(subscription_models.BeneficiaryFraudCheck).filter_by(userId=user.id).first()
        assert fraud_check is not None

        dms_orphan = db.session.query(subscription_models.OrphanDmsApplication).filter_by(email=user.email).first()
        assert dms_orphan is None


@pytest.mark.usefixtures("db_session")
class HandleDmsApplicationTest:
    id_piece_number_not_accepted_message = (
        "Bonjour,\n"
        "\n"
        "Nous avons bien reçu ton dossier, mais il y a une erreur dans le champ contenant ton numéro de pièce d'identité, inscrit sur le formulaire en ligne :\n"
        "Ton numéro de pièce d’identité doit être renseigné sous format alphanumérique sans espace et sans caractères spéciaux\n"
        '<a href="https://aide.passculture.app/hc/fr/articles/4411999008657--Jeunes-Où-puis-je-trouver-le-numéro-de-ma-pièce-d-identité">Où puis-je trouver le numéro de ma pièce d’identité ?</a>\n'
        "\n"
        "Merci de corriger ton dossier.\n"
        "\n"
        'Tu trouveras de l’aide dans cet article : <a href="https://aide.passculture.app/hc/fr/articles/4411999116433--Jeunes-Où-puis-je-trouver-de-l-aide-concernant-mon-dossier-d-inscription-sur-Démarches-Simplifiées-">Où puis-je trouver de l’aide concernant mon dossier d’inscription sur Démarche Numérique ?</a>\n'
        "\n"
        "Nous te souhaitons une belle journée.\n"
        "\n"
        "L’équipe du pass Culture"
    )

    def test_handle_dms_application_sends_user_identity_check_started_event(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime(2000, 1, 1))
        dms_response = fixtures.make_parsed_graphql_application(
            application_number=1234,
            state=dms_models.GraphQLApplicationStates.accepted,
            email=user.email,
            birth_date=datetime.datetime(2016, 1, 1),
        )

        dms_subscription_api.handle_dms_application(dms_response)

        assert push_testing.requests[0] == {
            "can_be_asynchronously_retried": True,
            "event_name": "user_identity_check_started",
            "event_payload": {"type": "dms"},
            "user_id": user.id,
        }

    def test_handle_dms_application_made_for_beneficiary_by_representative(self):
        representative = users_factories.UserFactory(dateOfBirth=datetime.datetime(1980, 1, 1))
        applicant = users_factories.UserFactory(dateOfBirth=datetime.datetime(2000, 1, 1))
        dms_response = fixtures.make_parsed_graphql_application(
            application_number=1234,
            state=dms_models.GraphQLApplicationStates.accepted,
            email=representative.email,
            applicant_email=applicant.email,
            birth_date=datetime.datetime(2016, 1, 1),
        )

        dms_subscription_api.handle_dms_application(dms_response)

        assert push_testing.requests[0] == {
            "can_be_asynchronously_retried": True,
            "event_name": "user_identity_check_started",
            "event_payload": {"type": "dms"},
            "user_id": applicant.id,
        }

    def test_handle_dms_application_serializes_dms_response(self):
        user = users_factories.ProfileCompletedUserFactory(age=18)
        dms_response = fixtures.make_parsed_graphql_application(
            application_number=1234,
            state=dms_models.GraphQLApplicationStates.accepted,
            email=user.email,
            birth_date=user.dateOfBirth,
            construction_datetime=date_utils.get_naive_utc_now().isoformat(),
        )

        dms_subscription_api.handle_dms_application(dms_response)

        fraud_check = (
            db.session.query(subscription_models.BeneficiaryFraudCheck)
            .filter_by(userId=user.id, type=subscription_models.FraudCheckType.DMS)
            .one()
        )
        dms_content = fraud_check.resultContent
        assert dms_content["application_number"] == 1234
        assert dms_content["birth_date"] == user.birth_date.isoformat()
        assert dms_content["birth_place"] == "Paris"
        assert dms_content["civility"] == "Mme"
        assert dms_content["email"] == user.email
        assert dms_content["id_piece_number"] == "123123123"
        assert dms_content["state"] == dms_models.GraphQLApplicationStates.accepted.value

    def test_handle_dms_application_updates_birth_info(self):
        user = users_factories.ProfileCompletedUserFactory(age=17)
        seventeen_years_ago = date_utils.get_naive_utc_now() - relativedelta(years=17, months=1)
        dms_response = fixtures.make_parsed_graphql_application(
            application_number=1234,
            state=dms_models.GraphQLApplicationStates.accepted,
            email=user.email,
            birth_date=seventeen_years_ago,
            birth_place="Casablanca",
            construction_datetime=date_utils.get_naive_utc_now().isoformat(),
        )

        dms_subscription_api.handle_dms_application(dms_response)

        assert user.is_beneficiary
        assert user.validatedBirthDate == seventeen_years_ago.date()
        assert user.birthPlace == "Casablanca"

    def test_concurrent_accepted_calls(self):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime(2000, 1, 1), roles=[users_models.UserRole.UNDERAGE_BENEFICIARY]
        )
        application_number = 1234
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            thirdPartyId=str(application_number),
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.DMS,
        )
        dms_response = fixtures.make_parsed_graphql_application(
            application_number=application_number,
            state=dms_models.GraphQLApplicationStates.accepted,
            email=user.email,
            birth_date=datetime.datetime(2016, 1, 1),
        )

        dms_subscription_api.handle_dms_application(dms_response)

        assert (
            db.session.query(subscription_models.BeneficiaryFraudCheck).first().status
            == subscription_models.FraudCheckStatus.OK
        )

    @patch("pcapi.core.subscription.dms.api._process_in_progress_application")
    def test_multiple_call_for_same_application(self, mock_process_in_progress, db_session):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime(2000, 1, 1), roles=[users_models.UserRole.UNDERAGE_BENEFICIARY]
        )
        application_number = 1234
        dms_response = fixtures.make_parsed_graphql_application(
            application_number=application_number,
            state=dms_models.GraphQLApplicationStates.on_going,
            email=user.email,
            birth_date=datetime.datetime(2000, 1, 1),
        )

        dms_subscription_api.handle_dms_application(dms_response)

        mock_process_in_progress.assert_called_once()
        dms_fraud_check = next(
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type == subscription_models.FraudCheckType.DMS
        )
        assert (
            dms_fraud_check.source_data().get_latest_modification_datetime()
            == dms_response.latest_modification_datetime
        )

        mock_process_in_progress.reset_mock()
        dms_subscription_api.handle_dms_application(dms_response)

        mock_process_in_progress.assert_not_called()
        db.session.refresh(dms_fraud_check)
        assert (
            dms_fraud_check.source_data().get_latest_modification_datetime()
            == dms_response.latest_modification_datetime
        )

    @patch("pcapi.connectors.dms.serializer.parse_beneficiary_information_graphql")
    def test_field_error(self, mocked_parse_beneficiary_information):
        user = users_factories.UserFactory()
        dms_response = fixtures.make_parsed_graphql_application(
            application_number=1, state=dms_models.GraphQLApplicationStates.draft, email=user.email
        )
        mocked_parse_beneficiary_information.side_effect = [Exception()]

        with pytest.raises(Exception):
            dms_subscription_api.handle_dms_application(dms_response)

        assert db.session.query(subscription_models.BeneficiaryFraudCheck).first() is None

    @patch.object(api_dms.DMSGraphQLClient, "send_user_message")
    def test_field_error_when_draft(self, send_dms_message_mock):
        user = users_factories.UserFactory()
        dms_response = fixtures.make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.draft,
            email=user.email,
            id_piece_number="(wrong_number)",
            application_techid="XYZQVM",
        )

        dms_subscription_api.handle_dms_application(dms_response)

        fraud_check = db.session.query(subscription_models.BeneficiaryFraudCheck).filter_by(user=user).one()
        message = dms_subscription_api.get_dms_subscription_message(fraud_check)
        assert message == subscription_schemas.SubscriptionMessage(
            user_message="Il semblerait que ton numéro de pièce d'identité soit erroné. Tu peux te rendre sur le site demarche.numerique.gouv.fr pour le rectifier.",
            call_to_action=subscription_messages.REDIRECT_TO_DMS_CALL_TO_ACTION,
            pop_over_icon=None,
            updated_at=fraud_check.updatedAt,
        )

        send_dms_message_mock.assert_called_once()
        assert send_dms_message_mock.call_args[0][0] == "XYZQVM"
        assert send_dms_message_mock.call_args[0][2] == self.id_piece_number_not_accepted_message
        assert len(mails_testing.outbox) == 0

        fraud_check = db.session.query(subscription_models.BeneficiaryFraudCheck).filter_by(userId=user.id).one()
        assert fraud_check.status == subscription_models.FraudCheckStatus.STARTED
        assert fraud_check.reasonCodes == [subscription_models.FraudReasonCode.ERROR_IN_DATA]
        assert fraud_check.source_data().field_errors == [
            dms_schemas.DmsFieldErrorDetails(
                key=dms_schemas.DmsFieldErrorKeyEnum.id_piece_number, value="(wrong_number)"
            )
        ]

    @patch.object(api_dms.DMSGraphQLClient, "send_user_message")
    def test_field_error_when_on_going(self, send_dms_message_mock):
        application_number = 1
        user = users_factories.UserFactory()
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            thirdPartyId=str(application_number),
            status=subscription_models.FraudCheckStatus.STARTED,
            type=subscription_models.FraudCheckType.DMS,
        )
        dms_response = fixtures.make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.on_going,
            email=user.email,
            id_piece_number="(wrong_number)",
            application_techid="XYZQVM",
        )

        dms_subscription_api.handle_dms_application(dms_response)

        fraud_check = db.session.query(subscription_models.BeneficiaryFraudCheck).filter_by(user=user).one()
        message = dms_subscription_api.get_dms_subscription_message(fraud_check)
        assert message == subscription_schemas.SubscriptionMessage(
            user_message="Il semblerait que ton numéro de pièce d'identité soit erroné. Tu peux contacter le support pour plus d’informations.",
            call_to_action=subscription_schemas.CallToActionMessage(
                title="Contacter le support",
                link=subscription_messages.SUBSCRIPTION_SUPPORT_FORM_URL,
                icon=subscription_schemas.CallToActionIcon.EXTERNAL,
            ),
            pop_over_icon=None,
            updated_at=fraud_check.updatedAt,
        )

        send_dms_message_mock.assert_not_called()
        assert len(mails_testing.outbox) == 0

        fraud_check = db.session.query(subscription_models.BeneficiaryFraudCheck).filter_by(userId=user.id).one()
        assert fraud_check.status == subscription_models.FraudCheckStatus.PENDING

    @patch.object(api_dms.DMSGraphQLClient, "send_user_message")
    def test_field_error_when_accepted(self, send_dms_message_mock):
        application_number = 1
        user = users_factories.UserFactory()
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            thirdPartyId=str(application_number),
            status=subscription_models.FraudCheckStatus.STARTED,
            type=subscription_models.FraudCheckType.DMS,
        )
        dms_response = fixtures.make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.accepted,
            email=user.email,
            id_piece_number="(wrong_number)",
            application_techid="XYZQVM",
        )

        dms_subscription_api.handle_dms_application(dms_response)

        fraud_check = db.session.query(subscription_models.BeneficiaryFraudCheck).filter_by(user=user).one()
        message = dms_subscription_api.get_dms_subscription_message(fraud_check)
        assert message == subscription_schemas.SubscriptionMessage(
            user_message="Ton dossier déposé sur le site demarche.numerique.gouv.fr a été refusé : le format du numéro de pièce d'identité renseigné est invalide. Tu peux contacter le support pour mettre à jour ton dossier.",
            call_to_action=subscription_schemas.CallToActionMessage(
                title="Contacter le support",
                link=subscription_messages.SUBSCRIPTION_SUPPORT_FORM_URL,
                icon=subscription_schemas.CallToActionIcon.EXTERNAL,
            ),
            pop_over_icon=None,
            updated_at=fraud_check.updatedAt,
        )

        send_dms_message_mock.assert_not_called()
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"]["id_prod"] == 510

        fraud_check = db.session.query(subscription_models.BeneficiaryFraudCheck).filter_by(userId=user.id).one()
        assert fraud_check.status == subscription_models.FraudCheckStatus.ERROR

    @patch.object(api_dms.DMSGraphQLClient, "send_user_message")
    def test_field_error_when_refused(self, send_dms_message_mock):
        application_number = 1
        user = users_factories.UserFactory()
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            thirdPartyId=str(application_number),
            status=subscription_models.FraudCheckStatus.STARTED,
            type=subscription_models.FraudCheckType.DMS,
        )
        dms_response = fixtures.make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.refused,
            email=user.email,
            id_piece_number="(wrong_number)",
            application_techid="XYZQVM",
        )

        dms_subscription_api.handle_dms_application(dms_response)

        send_dms_message_mock.assert_not_called()
        assert len(mails_testing.outbox) == 0

        fraud_check = db.session.query(subscription_models.BeneficiaryFraudCheck).filter_by(userId=user.id).one()
        assert fraud_check.status == subscription_models.FraudCheckStatus.KO

        message = dms_subscription_api.get_dms_subscription_message(fraud_check)
        assert message == subscription_schemas.SubscriptionMessage(
            user_message="Ton dossier déposé sur le site demarche.numerique.gouv.fr a été refusé : le format du numéro de pièce d'identité renseigné est invalide. Tu peux contacter le support pour mettre à jour ton dossier.",
            call_to_action=subscription_schemas.CallToActionMessage(
                title="Contacter le support",
                link=subscription_messages.SUBSCRIPTION_SUPPORT_FORM_URL,
                icon=subscription_schemas.CallToActionIcon.EXTERNAL,
            ),
            pop_over_icon=None,
            updated_at=fraud_check.updatedAt,
        )

    @pytest.mark.settings(ENABLE_PERMISSIVE_NAME_VALIDATION=False)
    def test_field_error_allows_fraud_check_content(self):
        user = users_factories.UserFactory()
        dms_response = fixtures.make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.refused,
            email=user.email,
            id_piece_number="(wrong_number)",
            first_name="",
            application_techid="XYZQVM",
        )
        dms_subscription_api.handle_dms_application(dms_response)

        fraud_check = (
            db.session.query(subscription_models.BeneficiaryFraudCheck)
            .filter_by(userId=user.id, type=subscription_models.FraudCheckType.DMS)
            .first()
        )
        assert fraud_check.status == subscription_models.FraudCheckStatus.KO

        result_content = fraud_check.source_data()
        assert result_content.application_number == 1
        assert result_content.birth_date == AGE18_ELIGIBLE_BIRTH_DATE
        assert result_content.registration_datetime == datetime.datetime(2020, 5, 13, 7, 9, 46)
        assert result_content.first_name == ""
        assert result_content.field_errors == [
            dms_schemas.DmsFieldErrorDetails(key=dms_schemas.DmsFieldErrorKeyEnum.first_name, value=""),
            dms_schemas.DmsFieldErrorDetails(
                key=dms_schemas.DmsFieldErrorKeyEnum.id_piece_number, value="(wrong_number)"
            ),
        ]

    @patch("pcapi.core.mails.transactional.send_create_account_after_dms_email")
    def test_processing_accepted_orphan_application_is_idempotent(self, mock_send_create_account_after_dms_email):
        dms_response = fixtures.make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.accepted,
            email="orphan@example.com",
            last_modification_date="2020-05-13T09:09:46.000+02:00",
        )

        dms_subscription_api.handle_dms_application(dms_response)
        dms_subscription_api.handle_dms_application(dms_response)
        orphan = db.session.query(subscription_models.OrphanDmsApplication).filter_by(application_id=1).one()

        mock_send_create_account_after_dms_email.assert_called_once_with("orphan@example.com")
        assert orphan.latest_modification_datetime == datetime.datetime(2020, 5, 13, 7, 9, 46)

    @patch("pcapi.core.subscription.dms.api.dms_connector_api.DMSGraphQLClient.send_user_message")
    def test_processing_draft_orphan_application_is_idempotent(self, mock_send_user_message):
        dms_response = fixtures.make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.draft,
            email="orphan@example.com",
            last_modification_date="2020-05-13T09:09:46.000+02:00",
        )

        dms_subscription_api.handle_dms_application(dms_response)
        dms_subscription_api.handle_dms_application(dms_response)
        orphan = db.session.query(subscription_models.OrphanDmsApplication).filter_by(application_id=1).one()

        mock_send_user_message.assert_called_once()
        assert orphan.latest_modification_datetime == datetime.datetime(2020, 5, 13, 7, 9, 46)

    @patch("pcapi.core.subscription.dms.api.dms_connector_api.DMSGraphQLClient.send_user_message")
    def test_correcting_application_resets_errors(self, mock_send_user_message, db_session):
        user = users_factories.UserFactory(email="john.stiles@example.com")
        dms_response = fixtures.make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.draft,
            email="john.stiles@example.com",
            last_modification_date="2022-05-13T09:09:46.000+02:00",
            birth_date=datetime.datetime(2000, 1, 1),
        )

        dms_subscription_api.handle_dms_application(dms_response)

        fraud_check = (
            db.session.query(subscription_models.BeneficiaryFraudCheck)
            .filter_by(userId=user.id, type=subscription_models.FraudCheckType.DMS)
            .first()
        )

        assert fraud_check.reasonCodes == [subscription_models.FraudReasonCode.AGE_NOT_VALID]
        assert fraud_check.reason == "Erreur dans les données soumises dans le dossier DMS : 'birth_date' (2000-01-01)"

        # User then fixes date error
        dms_response = fixtures.make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.draft,
            email="john.stiles@example.com",
            last_modification_date="2022-05-15T09:09:46.000+02:00",
            birth_date=date_utils.get_naive_utc_now() - relativedelta(years=ELIGIBILITY_AGE_18),
        )

        dms_subscription_api.handle_dms_application(dms_response)

        db.session.refresh(fraud_check)

        assert fraud_check.reasonCodes == []
        assert fraud_check.reason is None

    @patch("pcapi.core.subscription.dms.api.dms_connector_api.DMSGraphQLClient.add_label_to_application")
    def test_add_label_when_almost_19_years_old(self, mock_add_label_to_application, db_session):
        user = users_factories.UserFactory()
        dms_response = fixtures.make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.on_going,
            email=user.email,
            birth_date=date_utils.get_naive_utc_now() - relativedelta(years=ELIGIBILITY_END_AGE, days=-6),
            procedure_number=settings.DMS_ENROLLMENT_PROCEDURE_ID_FR,
        )

        dms_subscription_api.handle_dms_application(dms_response)

        mock_add_label_to_application.assert_called_once_with(
            dms_response.id, settings.DMS_ENROLLMENT_FR_LABEL_ID_URGENT
        )
        assert db.session.query(subscription_models.BeneficiaryFraudCheck).filter_by(userId=user.id).count() == 1

    @patch("pcapi.core.subscription.dms.api.dms_connector_api.DMSGraphQLClient.add_label_to_application")
    def test_keep_label_when_almost_19_years_old(self, mock_add_label_to_application, db_session):
        user = users_factories.UserFactory()
        dms_response = fixtures.make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.on_going,
            email=user.email,
            birth_date=date_utils.get_naive_utc_now() - relativedelta(years=ELIGIBILITY_END_AGE, days=-6),
            procedure_number=settings.DMS_ENROLLMENT_PROCEDURE_ID_FR,
            application_labels=[{"id": settings.DMS_ENROLLMENT_FR_LABEL_ID_URGENT, "name": "Urgent"}],
        )

        dms_subscription_api.handle_dms_application(dms_response)

        mock_add_label_to_application.assert_not_called()
        assert db.session.query(subscription_models.BeneficiaryFraudCheck).filter_by(userId=user.id).count() == 1

    @pytest.mark.features(ENABLE_DS_APPLICATION_REFUSED_FROM_ANNOTATION=False)
    @patch("pcapi.core.subscription.dms.api.dms_connector_api.DMSGraphQLClient.make_refused")
    def test_do_not_process_instructor_annotation_without_feature_flag(self, mock_make_refused):
        user = users_factories.UserFactory()
        dms_response = fixtures.make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.draft,
            email=user.email,
            annotations=[
                {
                    "id": "Q2hhbXAtNTAxNTA2Mw==",
                    "label": f"{dms_serializer.DMS_INSTRUCTOR_ANNOTATION_SLUG}: Code de l'annotation instructeur",
                    "stringValue": dms_schemas.DmsInstructorAnnotationEnum.NEL.value,
                    "updatedAt": "2025-03-04T15:30:03+01:00",
                }
            ],
        )

        dms_subscription_api.handle_dms_application(dms_response)

        mock_make_refused.assert_not_called()

        fraud_check = db.session.query(subscription_models.BeneficiaryFraudCheck).filter_by(userId=user.id).one()
        assert fraud_check.status == subscription_models.FraudCheckStatus.STARTED

    @pytest.mark.features(ENABLE_DS_APPLICATION_REFUSED_FROM_ANNOTATION=True)
    @pytest.mark.parametrize("annotation", ["NEL", "IDP, NEL", "NEL, IDM"])
    @patch("pcapi.core.subscription.dms.api.dms_connector_api.DMSGraphQLClient.make_refused")
    def test_process_instructor_annotation_NEL(self, mock_make_refused, annotation):
        user = users_factories.UserFactory()
        dms_response = fixtures.make_parsed_graphql_application(
            procedure_number=settings.DMS_ENROLLMENT_PROCEDURE_ID_FR,
            application_number=1,
            state=dms_models.GraphQLApplicationStates.draft,
            email=user.email,
            annotations=[
                {
                    "id": "Q2hhbXAtNTAxNTA2Mw==",
                    "label": f"{dms_serializer.DMS_INSTRUCTOR_ANNOTATION_SLUG}: Code de l'annotation instructeur",
                    "stringValue": annotation,
                    "updatedAt": "2025-03-04T15:30:03+01:00",
                },
                {
                    "id": "Q2hhbXAtNDk2MTgyNg==",
                    "label": "Nouvelle annotation ID",
                    "stringValue": "",
                    "updatedAt": "2025-03-04T15:28:00+01:00",
                },
                {
                    "id": "Q2hhbXAtMjY4NDQ3Nw==",
                    "label": f"{dms_serializer.DMS_BACKEND_ANNOTATION_SLUG}: Statut du dossier côté passCulture",
                    "stringValue": "Aucune erreur détectée. Le dossier peut être passé en instruction.",
                    "updatedAt": "2025-03-04T15:28:00+01:00",
                },
            ],
        )

        dms_subscription_api.handle_dms_application(dms_response)

        mock_make_refused.assert_called_once_with(
            dms_response.id,
            settings.DMS_ENROLLMENT_INSTRUCTOR,
            dms_internal_mailing.DMS_MESSAGE_REFUSED_USER_NOT_ELIGIBLE,
            from_draft=True,
        )

        fraud_check = db.session.query(subscription_models.BeneficiaryFraudCheck).filter_by(userId=user.id).one()
        assert fraud_check.status == subscription_models.FraudCheckStatus.KO

    @pytest.mark.features(ENABLE_DS_APPLICATION_REFUSED_FROM_ANNOTATION=True)
    @pytest.mark.parametrize("annotation", ["IDP", "IDP, S"])
    @patch("pcapi.core.subscription.dms.api.dms_connector_api.DMSGraphQLClient.make_refused")
    def test_process_instructor_annotation_IDP(self, mock_make_refused, annotation):
        user = users_factories.UserFactory()
        dms_response = fixtures.make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.on_going,
            email=user.email,
            annotations=[
                {
                    "id": "Q2hhbXAtNTAxNTA2Mw==",
                    "label": f"{dms_serializer.DMS_INSTRUCTOR_ANNOTATION_SLUG}: Code de l'annotation instructeur",
                    "stringValue": annotation,
                    "updatedAt": "2025-03-04T15:30:03+01:00",
                }
            ],
        )

        dms_subscription_api.handle_dms_application(dms_response)

        mock_make_refused.assert_called_once_with(
            dms_response.id,
            settings.DMS_ENROLLMENT_INSTRUCTOR,
            dms_internal_mailing.DMS_MESSAGE_REFUSED_ID_EXPIRED,
            from_draft=False,
        )

        fraud_check = db.session.query(subscription_models.BeneficiaryFraudCheck).filter_by(userId=user.id).one()
        assert fraud_check.status == subscription_models.FraudCheckStatus.KO

    @pytest.mark.features(ENABLE_DS_APPLICATION_REFUSED_FROM_ANNOTATION=True)
    @patch("pcapi.core.subscription.dms.api.dms_connector_api.DMSGraphQLClient.make_refused")
    def test_process_instructor_annotation_IDP_when_fields_updated_later(self, mock_make_refused):
        user = users_factories.UserFactory()
        dms_response = fixtures.make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.on_going,
            email=user.email,
            last_user_fields_modification_date="2025-03-05T12:34:56+01:00",
            annotations=[
                {
                    "id": "Q2hhbXAtNTAxNTA2Mw==",
                    "label": f"{dms_serializer.DMS_INSTRUCTOR_ANNOTATION_SLUG}: Code de l'annotation instructeur",
                    "stringValue": dms_schemas.DmsInstructorAnnotationEnum.IDP.value,
                    "updatedAt": "2025-03-04T15:30:03+01:00",
                }
            ],
        )

        dms_subscription_api.handle_dms_application(dms_response)

        mock_make_refused.assert_not_called()

    @pytest.mark.features(ENABLE_DS_APPLICATION_REFUSED_FROM_ANNOTATION=True)
    @pytest.mark.parametrize("annotation", ["NEL", "IDM, NEL"])
    @patch("pcapi.core.subscription.dms.api.dms_connector_api.DMSGraphQLClient.make_refused")
    def test_process_instructor_annotation_without_user_account(self, mock_make_refused, annotation):
        dms_response = fixtures.make_parsed_graphql_application(
            procedure_number=settings.DMS_ENROLLMENT_PROCEDURE_ID_FR,
            application_number=1,
            state=dms_models.GraphQLApplicationStates.on_going,
            email="user@example.com",
            annotations=[
                {
                    "id": "Q2hhbXAtNTAxNTA2Mw==",
                    "label": f"{dms_serializer.DMS_INSTRUCTOR_ANNOTATION_SLUG}: Code de l'annotation instructeur",
                    "stringValue": annotation,
                    "updatedAt": "2025-03-13T16:00:03+01:00",
                },
            ],
        )

        dms_subscription_api.handle_dms_application(dms_response)

        mock_make_refused.assert_called_once_with(
            dms_response.id,
            settings.DMS_ENROLLMENT_INSTRUCTOR,
            dms_internal_mailing.DMS_MESSAGE_REFUSED_USER_NOT_ELIGIBLE,
            from_draft=False,
        )

        assert db.session.query(subscription_models.BeneficiaryFraudCheck).count() == 0

    @pytest.mark.features(ENABLE_DS_APPLICATION_REFUSED_FROM_ANNOTATION=True)
    @patch("pcapi.core.subscription.dms.api.dms_connector_api.DMSGraphQLClient.make_refused")
    def test_process_instructor_annotation_IDM(self, mock_make_refused):
        user = users_factories.UserFactory()
        dms_response = fixtures.make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.draft,
            email=user.email,
            annotations=[
                {
                    "id": "Q2hhbXAtNTAxNTA2Mw==",
                    "label": f"{dms_serializer.DMS_INSTRUCTOR_ANNOTATION_SLUG}: Code de l'annotation instructeur",
                    "stringValue": dms_schemas.DmsInstructorAnnotationEnum.IDM.value,
                    "updatedAt": "2025-03-04T15:30:03+01:00",
                }
            ],
        )

        dms_subscription_api.handle_dms_application(dms_response)

        mock_make_refused.assert_not_called()

        fraud_check = db.session.query(subscription_models.BeneficiaryFraudCheck).filter_by(userId=user.id).one()
        assert fraud_check.status == subscription_models.FraudCheckStatus.STARTED


@pytest.mark.usefixtures("db_session")
class HandleDmsAnnotationsTest:
    @pytest.mark.parametrize(
        "field_errors,birth_date_error,expected_annotation",
        [
            ([], None, "Aucune erreur détectée. Le dossier peut être passé en instruction."),
            (
                [],
                dms_schemas.DmsFieldErrorDetails(key=dms_schemas.DmsFieldErrorKeyEnum.birth_date, value="2000-01-01"),
                "La date de naissance (2000-01-01) indique que le demandeur n'est pas éligible au pass Culture (doit avoir entre 17 et 18 ans). ",
            ),
            (
                [dms_schemas.DmsFieldErrorDetails(key=dms_schemas.DmsFieldErrorKeyEnum.first_name, value="/taylor")],
                dms_schemas.DmsFieldErrorDetails(key=dms_schemas.DmsFieldErrorKeyEnum.birth_date, value="2000-01-01"),
                (
                    "La date de naissance (2000-01-01) indique que le demandeur n'est pas éligible au pass Culture (doit avoir entre 17 et 18 ans). "
                    "Champs invalides: Le prénom (/taylor)"
                ),
            ),
            (
                [
                    dms_schemas.DmsFieldErrorDetails(key=dms_schemas.DmsFieldErrorKeyEnum.first_name, value="/taylor"),
                    dms_schemas.DmsFieldErrorDetails(
                        key=dms_schemas.DmsFieldErrorKeyEnum.birth_date,
                        value="trente juillet deux mille quatre",
                    ),
                ],
                None,
                ("Champs invalides: Le prénom (/taylor), La date de naissance (trente juillet deux mille quatre)"),
            ),
        ],
    )
    def test_compute_new_annotation(self, field_errors, birth_date_error, expected_annotation):
        assert dms_subscription_api._compute_new_annotation(field_errors, birth_date_error) == expected_annotation

    @mock.patch("pcapi.connectors.dms.api.update_demarches_simplifiees_text_annotations")
    def test_update_application_annotations(self, mock_update_annotations):
        fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(type=subscription_models.FraudCheckType.DMS)
        dms_subscription_api._update_application_annotations(
            "St1l3s",
            subscription_factories.DMSContentFactory(
                annotation=dms_schemas.DmsAnnotation(
                    id="AnnotationId",
                    label="AN_001: Some label",
                    text="This is a test annotation",
                )
            ),
            birth_date_error=None,
            fraud_check=fraud_check,
        )
        db.session.add(fraud_check)
        db.session.commit()

        mock_update_annotations.assert_called_once_with(
            "St1l3s", "AnnotationId", "Aucune erreur détectée. Le dossier peut être passé en instruction."
        )
        assert fraud_check.resultContent["annotation"]["label"] == "AN_001: Some label"
        assert (
            fraud_check.resultContent["annotation"]["text"]
            == "Aucune erreur détectée. Le dossier peut être passé en instruction."
        )

    @mock.patch("pcapi.connectors.dms.api.update_demarches_simplifiees_text_annotations")
    def test_update_application_annotations_dont_update_if_no_modification(self, mock_update_annotations):
        dms_subscription_api._update_application_annotations(
            "St1l3s",
            subscription_factories.DMSContentFactory(
                annotation=dms_schemas.DmsAnnotation(
                    id="AnnotationId",
                    label="AN_001: Some label",
                    text="Aucune erreur détectée. Le dossier peut être passé en instruction.",
                )
            ),
            birth_date_error=None,
            fraud_check=subscription_factories.BeneficiaryFraudCheckFactory(),
        )

        mock_update_annotations.assert_not_called()

    @mock.patch("pcapi.connectors.dms.api.update_demarches_simplifiees_text_annotations")
    def test_update_application_annotations_with_no_annotation_logs_error(self, mock_update_annotations, caplog):
        dms_content = subscription_factories.DMSContentFactory()
        dms_subscription_api._update_application_annotations(
            "St1l3s",
            dms_content,
            birth_date_error=None,
            fraud_check=subscription_factories.BeneficiaryFraudCheckFactory(),
        )

        mock_update_annotations.assert_not_called()
        assert f"[DMS] No annotation defined for procedure {dms_content.procedure_number}" in caplog.text


@pytest.mark.usefixtures("db_session")
class DmsSubscriptionMessageTest:
    user_email = "déesse@dms.com"

    @patch("pcapi.core.subscription.dms.api.dms_connector_api.DMSGraphQLClient.send_user_message")
    def test_started_no_error(self, mock_send_user_message):
        users_factories.UserFactory(email=self.user_email)
        dms_response = fixtures.make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.draft,
            email=self.user_email,
            birth_date=date_utils.get_naive_utc_now() - relativedelta(years=18),
        )
        fraud_check = dms_subscription_api.handle_dms_application(dms_response)

        message = dms_subscription_api.get_dms_subscription_message(fraud_check)

        assert message == subscription_schemas.SubscriptionMessage(
            user_message=f"Nous avons bien reçu ton dossier le {fraud_check.dateCreated.date():%d/%m/%Y}. Rends-toi sur la messagerie du site Démarche Numérique pour être informé en temps réel.",
            call_to_action=None,
            pop_over_icon=subscription_schemas.PopOverIcon.FILE,
            updated_at=fraud_check.updatedAt,
        )

    @patch("pcapi.core.subscription.dms.api.dms_connector_api.DMSGraphQLClient.send_user_message")
    def test_started_error_wrong_birth_date(self, mock_send_user_message):
        users_factories.UserFactory(email=self.user_email)
        wrong_birth_date_application = fixtures.make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.draft,
            email=self.user_email,
            birth_date=date_utils.get_naive_utc_now(),
        )
        fraud_check = dms_subscription_api.handle_dms_application(wrong_birth_date_application)

        message = dms_subscription_api.get_dms_subscription_message(fraud_check)

        assert message == subscription_schemas.SubscriptionMessage(
            user_message="Il semblerait que ta date de naissance soit erronée. Tu peux te rendre sur le site demarche.numerique.gouv.fr pour la rectifier.",
            call_to_action=subscription_messages.REDIRECT_TO_DMS_CALL_TO_ACTION,
            pop_over_icon=None,
            updated_at=fraud_check.updatedAt,
        )

    @patch("pcapi.core.subscription.dms.api.dms_connector_api.DMSGraphQLClient.send_user_message")
    def test_started_error_wrong_birth_date_and_id_piece_number(self, mock_send_user_message):
        users_factories.UserFactory(email=self.user_email)
        wrong_birth_date_application = fixtures.make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.draft,
            email=self.user_email,
            birth_date=date_utils.get_naive_utc_now(),
            id_piece_number="r2d2",
        )
        fraud_check = dms_subscription_api.handle_dms_application(wrong_birth_date_application)

        message = dms_subscription_api.get_dms_subscription_message(fraud_check)

        assert message == subscription_schemas.SubscriptionMessage(
            user_message="Il semblerait que tes numéro de pièce d'identité et date de naissance soient erronés. Tu peux te rendre sur le site demarche.numerique.gouv.fr pour les rectifier.",
            call_to_action=subscription_messages.REDIRECT_TO_DMS_CALL_TO_ACTION,
            pop_over_icon=None,
            updated_at=fraud_check.updatedAt,
        )

    @patch("pcapi.core.subscription.dms.api.dms_connector_api.DMSGraphQLClient.send_user_message")
    def test_pending_error_not_eligible_date(self, mock_send_user_message):
        users_factories.UserFactory(email=self.user_email)
        not_eligible_application = fixtures.make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.on_going,
            email=self.user_email,
            birth_date=date_utils.get_naive_utc_now() - relativedelta(years=20),
            construction_datetime=date_utils.get_naive_utc_now(),
        )
        fraud_check = dms_subscription_api.handle_dms_application(not_eligible_application)

        message = dms_subscription_api.get_dms_subscription_message(fraud_check)

        assert message == subscription_schemas.SubscriptionMessage(
            user_message="Ta date de naissance indique que tu n'es pas éligible. Tu dois avoir entre 17 et 18 ans. Tu peux contacter le support pour plus d’informations.",
            call_to_action=subscription_schemas.CallToActionMessage(
                title="Contacter le support",
                link=subscription_messages.SUBSCRIPTION_SUPPORT_FORM_URL,
                icon=subscription_schemas.CallToActionIcon.EXTERNAL,
            ),
            updated_at=fraud_check.updatedAt,
        )

    @patch("pcapi.core.subscription.dms.api.dms_connector_api.DMSGraphQLClient.send_user_message")
    def test_ko_not_eligible(self, mock_send_user_message):
        users_factories.UserFactory(email=self.user_email)
        not_eligible_application = fixtures.make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.accepted,
            email=self.user_email,
            birth_date=date_utils.get_naive_utc_now() - relativedelta(years=20),
            construction_datetime=date_utils.get_naive_utc_now(),
        )
        fraud_check = dms_subscription_api.handle_dms_application(not_eligible_application)

        message = dms_subscription_api.get_dms_subscription_message(fraud_check)

        assert message == subscription_schemas.SubscriptionMessage(
            user_message="Ton dossier déposé sur le site demarche.numerique.gouv.fr a été refusé : la date de naissance indique que tu n'es pas éligible. Tu dois avoir entre 17 et 18 ans.",
            call_to_action=None,
            pop_over_icon=subscription_schemas.PopOverIcon.ERROR,
            updated_at=fraud_check.updatedAt,
        )

    @patch("pcapi.core.subscription.dms.api.dms_connector_api.DMSGraphQLClient.send_user_message")
    def test_accepted(self, mock_send_user_message):
        users_factories.UserFactory(email=self.user_email)
        application_ok = fixtures.make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.accepted,
            email=self.user_email,
            birth_date=date_utils.get_naive_utc_now() - relativedelta(years=18),
        )
        fraud_check = dms_subscription_api.handle_dms_application(application_ok)

        assert dms_subscription_api.get_dms_subscription_message(fraud_check) is None

    @patch("pcapi.core.subscription.dms.api.dms_connector_api.DMSGraphQLClient.send_user_message")
    def test_refused_by_operator(self, mock_send_user_message):
        users_factories.UserFactory(email=self.user_email)
        refused_application = fixtures.make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.refused,
            email=self.user_email,
            birth_date=date_utils.get_naive_utc_now() - relativedelta(years=18),
        )
        fraud_check = dms_subscription_api.handle_dms_application(refused_application)

        message = dms_subscription_api.get_dms_subscription_message(fraud_check)

        assert message == subscription_schemas.SubscriptionMessage(
            user_message="Ton dossier déposé sur le site demarche.numerique.gouv.fr a été refusé. Tu peux contacter le support pour plus d’informations.",
            call_to_action=subscription_schemas.CallToActionMessage(
                title="Contacter le support",
                link=subscription_messages.SUBSCRIPTION_SUPPORT_FORM_URL,
                icon=subscription_schemas.CallToActionIcon.EXTERNAL,
            ),
            pop_over_icon=subscription_schemas.PopOverIcon.ERROR,
            updated_at=fraud_check.updatedAt,
        )

    @patch("pcapi.core.subscription.dms.api.dms_connector_api.DMSGraphQLClient.send_user_message")
    def test_duplicate(self, mock_send_user_message):
        first_name = "Jean-Michel"
        last_name = "Doublon"
        birth_date = date_utils.get_naive_utc_now() - relativedelta(years=18, days=1)
        users_factories.BeneficiaryGrant18Factory(
            firstName=first_name, lastName=last_name, dateOfBirth=birth_date, email="jean-michel@doublon.com"
        )

        users_factories.UserFactory(email=self.user_email)
        duplicate_application = fixtures.make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.accepted,
            email=self.user_email,
            birth_date=birth_date,
            first_name=first_name,
            last_name=last_name,
        )
        fraud_check = dms_subscription_api.handle_dms_application(duplicate_application)

        message = dms_subscription_api.get_dms_subscription_message(fraud_check)

        assert message == subscription_schemas.SubscriptionMessage(
            user_message=(
                "Ton dossier a été refusé car il y a déjà un compte bénéficiaire à ton nom. "
                "Connecte-toi avec l’adresse mail jea***@doublon.com ou contacte le support si tu penses qu’il s’agit d’une erreur. "
                "Si tu n’as plus ton mot de passe, tu peux effectuer une demande de réinitialisation."
            ),
            call_to_action=subscription_schemas.CallToActionMessage(
                title="Contacter le support",
                link=subscription_messages.SUBSCRIPTION_SUPPORT_FORM_URL,
                icon=subscription_schemas.CallToActionIcon.EXTERNAL,
            ),
            pop_over_icon=None,
            updated_at=fraud_check.updatedAt,
        )

    def test_ko_no_info(self):
        fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.DMS,
            resultContent=None,
            status=subscription_models.FraudCheckStatus.KO,
            reasonCodes=None,
        )

        message = dms_subscription_api.get_dms_subscription_message(fraud_check)

        assert message == subscription_schemas.SubscriptionMessage(
            user_message="Ton dossier déposé sur le site demarche.numerique.gouv.fr a été refusé.",
            call_to_action=None,
            pop_over_icon=subscription_schemas.PopOverIcon.ERROR,
            updated_at=fraud_check.updatedAt,
        )


@pytest.mark.usefixtures("db_session")
class IsFraudCheckUpToDateUnitTest:
    def test_is_fraud_check_up_to_date_empty(self):
        fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.DMS,
            resultContent=None,
            status=subscription_models.FraudCheckStatus.KO,
            reasonCodes=None,
        )
        assert not dms_subscription_api._is_fraud_check_up_to_date(
            fraud_check, new_content=subscription_factories.DMSContentFactory()
        )

    def test_is_fraud_check_up_to_date_same_content(self):
        fields = {
            "activity": "Étudiant",
            "address": "21B Baker Street",
            "birth_date": (datetime.datetime.today() - relativedelta(years=18)).date(),
            "birth_place": "Edinborough",
            "city": "Londres",
            "civility": users_models.GenderEnum.F,
            "department": "92",
            "email": "cher.locked@example.com",
            "first_name": "Cher",
            "id_piece_number": "ABC123",
            "last_name": "Homie",
            "phone": "+33665432198",
            "postal_code": "92200",
            "state": "accepte",
        }
        fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.DMS,
            resultContent=subscription_factories.DMSContentFactory(**fields),
            status=subscription_models.FraudCheckStatus.OK,
            reasonCodes=None,
        )
        assert dms_subscription_api._is_fraud_check_up_to_date(
            fraud_check,
            new_content=subscription_factories.DMSContentFactory(**fields),
        )

    def test_is_fraud_check_up_to_date_different_content(self):
        content = subscription_factories.DMSContentFactory(first_name="Jean-Michel")
        fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.DMS,
            resultContent=content,
            status=subscription_models.FraudCheckStatus.OK,
            reasonCodes=None,
        )
        assert not dms_subscription_api._is_fraud_check_up_to_date(
            fraud_check, new_content=subscription_factories.DMSContentFactory(first_name="John-Michael")
        )


@pytest.mark.usefixtures("db_session")
class ShouldImportDmsApplicationTest:
    def setup_method(self):
        self.user_email = "john.stiles@example.com"

    def start_id_check(self, fields):
        user = users_factories.UserFactory(email=self.user_email)
        application = fixtures.make_parsed_graphql_application(
            application_number=1, state=dms_models.GraphQLApplicationStates.draft, email=self.user_email, **fields
        )

        dms_subscription_api.handle_dms_application(application)
        fraud_check = (
            db.session.query(subscription_models.BeneficiaryFraudCheck)
            .filter_by(userId=user.id, type=subscription_models.FraudCheckType.DMS)
            .first()
        )
        assert fraud_check.status == subscription_models.FraudCheckStatus.STARTED

        return user, fraud_check

    @patch("pcapi.core.subscription.dms.api._process_dms_application")
    def test_should_import_dms_application_when_status_changed(self, _process_dms_application_mock):
        user, fraud_check = self.start_id_check(fields={})
        updated_application = fixtures.make_parsed_graphql_application(
            application_number=1,
            application_techid="TECH_ID",
            state=dms_models.GraphQLApplicationStates.refused,
            email=self.user_email,
        )
        _process_dms_application_mock.reset_mock()

        dms_subscription_api.handle_dms_application(updated_application)

        _process_dms_application_mock.assert_called_once_with(
            mock.ANY, "TECH_ID", fraud_check, dms_models.GraphQLApplicationStates.refused, user
        )

    @patch("pcapi.core.subscription.dms.api._process_dms_application")
    def test_should_import_dms_application_when_user_field_updated(self, _process_dms_application_mock):
        user, fraud_check = self.start_id_check(fields={"first_name": "Lucy"})
        updated_application = fixtures.make_parsed_graphql_application(
            application_number=1,
            application_techid="TECH_ID",
            state=dms_models.GraphQLApplicationStates.draft,
            email=self.user_email,
            first_name="Lucille",
        )
        _process_dms_application_mock.reset_mock()

        dms_subscription_api.handle_dms_application(updated_application)

        _process_dms_application_mock.assert_called_once_with(
            mock.ANY, "TECH_ID", fraud_check, dms_models.GraphQLApplicationStates.draft, user
        )

    @patch("pcapi.core.subscription.dms.api._process_dms_application")
    def should_not_update_on_last_modification_date_update(self, _process_dms_application_mock):
        self.start_id_check(fields={})
        updated_application = fixtures.make_parsed_graphql_application(
            application_number=1,
            application_techid="TECH_ID",
            state=dms_models.GraphQLApplicationStates.draft,
            email=self.user_email,
            last_modification_date=date_utils.get_naive_utc_now(),
        )
        _process_dms_application_mock.reset_mock()

        dms_subscription_api.handle_dms_application(updated_application)

        _process_dms_application_mock.assert_not_called()


@pytest.mark.usefixtures("db_session")
class RunTest:
    @patch.object(api_dms.DMSGraphQLClient, "get_applications_with_details")
    def test_should_retrieve_applications_from_new_procedure_number(
        self,
        get_applications_with_details,
    ):
        get_applications_with_details.return_value = [
            fixtures.make_parsed_graphql_application(
                123, "accepte", email="email1@example.com", id_piece_number="123123121"
            ),
            fixtures.make_parsed_graphql_application(
                456, "accepte", email="email2@example.com", id_piece_number="123123122"
            ),
            fixtures.make_parsed_graphql_application(
                789, "accepte", email="email3@example.com", id_piece_number="123123123"
            ),
        ]

        dms_subscription_api.import_all_updated_dms_applications(6712558)
        assert get_applications_with_details.call_count == 1
        get_applications_with_details.assert_called_with(6712558)

    @patch.object(api_dms.DMSGraphQLClient, "get_applications_with_details")
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
            fixtures.make_parsed_graphql_application(
                123,
                "accepte",
                email="email1@example.com",
                id_piece_number="123123121",
                birth_date=AGE18_ELIGIBLE_BIRTH_DATE,
            ),
            fixtures.make_parsed_graphql_application(
                456,
                "accepte",
                email="email2@example.com",
                id_piece_number="123123122",
                birth_date=AGE18_ELIGIBLE_BIRTH_DATE,
            ),
            fixtures.make_parsed_graphql_application(
                789,
                "accepte",
                email="email3@example.com",
                id_piece_number="123123123",
                birth_date=AGE18_ELIGIBLE_BIRTH_DATE,
            ),
        ]

        dms_subscription_api.import_all_updated_dms_applications(6712558)
        assert activate_beneficiary_if_no_missing_step.call_count == 3

    @patch.object(api_dms.DMSGraphQLClient, "get_applications_with_details")
    @patch("pcapi.core.subscription.api.activate_beneficiary_if_no_missing_step")
    def test_application_for_already_beneficiary_is_not_downgraded(
        self, activate_beneficiary_if_no_missing_step, get_applications_with_details
    ):
        # same user, but different
        user = users_factories.BeneficiaryGrant18Factory(email="john.doe@example.com")
        get_applications_with_details.return_value = [
            fixtures.make_parsed_graphql_application(123, "accepte", email="john.doe@example.com")
        ]

        dms_subscription_api.import_all_updated_dms_applications(6712558)

        fraud_check = (
            db.session.query(subscription_models.BeneficiaryFraudCheck)
            .filter(subscription_models.BeneficiaryFraudCheck.type == subscription_models.FraudCheckType.DMS)
            .one()
        )
        assert fraud_check.userId == user.id
        assert fraud_check.thirdPartyId == "123"
        assert fraud_check.status == subscription_models.FraudCheckStatus.OK

        activate_beneficiary_if_no_missing_step.assert_called_once()

    @patch.object(api_dms.DMSGraphQLClient, "get_applications_with_details")
    @patch("pcapi.core.subscription.api.activate_beneficiary_if_no_missing_step")
    def test_beneficiary_is_created_with_procedure_number(
        self, activate_beneficiary_if_no_missing_step, get_applications_with_details
    ):
        applicant = users_factories.UserFactory(firstName="Doe", lastName="John", email="john.doe@test.com")
        get_applications_with_details.return_value = [
            fixtures.make_parsed_graphql_application(
                123,
                "accepte",
                id_piece_number="123123121",
                email=applicant.email,
                birth_date=AGE18_ELIGIBLE_BIRTH_DATE,
                procedure_number=6712558,
            )
        ]

        dms_subscription_api.import_all_updated_dms_applications(6712558)

        activate_beneficiary_if_no_missing_step.assert_called_with(user=applicant)


@pytest.mark.usefixtures("db_session")
class RunIntegrationTest:
    EMAIL = "john.doe@example.com"
    BENEFICIARY_BIRTH_DATE = datetime.date.today() - datetime.timedelta(days=6752)  # ~18.5 years

    @patch.object(api_dms.DMSGraphQLClient, "get_applications_with_details")
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
            fixtures.make_parsed_graphql_application(
                application_number=123, state="accepte", email=user.email, city="Strasbourg"
            )
        ]
        dms_subscription_api.import_all_updated_dms_applications(6712558)

        assert db.session.query(users_models.User).count() == 1
        user = db.session.query(users_models.User).first()
        assert user.firstName == "profile-firstname"
        assert user.postalCode == "12400"
        assert user.address == "Route de Gozon"
        assert user.phoneNumber is None

        fraud_check = (
            db.session.query(subscription_models.BeneficiaryFraudCheck)
            .filter(subscription_models.BeneficiaryFraudCheck.type == subscription_models.FraudCheckType.DMS)
            .one()
        )
        assert fraud_check.userId == user.id
        assert fraud_check.thirdPartyId == "123"
        assert fraud_check.status == subscription_models.FraudCheckStatus.OK
        assert len(push_testing.requests) == 3

        # Check that a PROFILE_COMPLETION fraud check is created
        profile_completion_fraud_checks = [
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type == subscription_models.FraudCheckType.PROFILE_COMPLETION
        ]
        assert len(profile_completion_fraud_checks) == 1
        profile_completion_fraud_check = profile_completion_fraud_checks[0]
        assert profile_completion_fraud_check.status == subscription_models.FraudCheckStatus.OK
        assert profile_completion_fraud_check.reason == "Completed in DMS application 123"

    @patch.object(api_dms.DMSGraphQLClient, "get_applications_with_details")
    def test_import_ex_underage_beneficiary(self, get_applications_with_details):
        with time_machine.travel(date_utils.get_naive_utc_now() - relativedelta(years=2, months=1)):
            user = users_factories.UnderageBeneficiaryFactory(
                email="john.doe@example.com",
                firstName="john",
                lastName="doe",
                dateOfBirth=AGE18_ELIGIBLE_BIRTH_DATE,
                subscription_age=15,
                phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
                deposit__expirationDate=date_utils.get_naive_utc_now() + relativedelta(years=2),
            )
        subscription_factories.ProfileCompletionFraudCheckFactory(user=user)
        details = fixtures.make_parsed_graphql_application(application_number=123, state="accepte", email=user.email)
        details.draft_date = date_utils.get_naive_utc_now().isoformat()
        get_applications_with_details.return_value = [details]

        with atomic():
            dms_subscription_api.import_all_updated_dms_applications(6712558)

        assert db.session.query(users_models.User).count() == 1
        user = db.session.query(users_models.User).first()
        assert user.has_beneficiary_role
        deposits = db.session.query(finance_models.Deposit).filter_by(user=user).all()
        age_18_deposit = next(deposit for deposit in deposits if deposit.type == finance_models.DepositType.GRANT_17_18)
        assert len(deposits) == 2
        assert age_18_deposit.amount == 150 + 20  # remaining amount

        fraud_check = (
            db.session.query(subscription_models.BeneficiaryFraudCheck)
            .filter(subscription_models.BeneficiaryFraudCheck.type == subscription_models.FraudCheckType.DMS)
            .one()
        )
        assert fraud_check.userId == user.id
        assert fraud_check.thirdPartyId == "123"
        assert fraud_check.status == subscription_models.FraudCheckStatus.OK

    @patch.object(api_dms.DMSGraphQLClient, "get_applications_with_details")
    def test_import_with_no_user_found(self, get_applications_with_details):
        # when
        get_applications_with_details.return_value = [
            fixtures.make_parsed_graphql_application(
                application_number=123, state="accepte", email="nonexistant@example.com", procedure_number=6712558
            )
        ]

        dms_subscription_api.import_all_updated_dms_applications(6712558)
        dms_application = (
            db.session.query(subscription_models.OrphanDmsApplication)
            .filter(subscription_models.OrphanDmsApplication.application_id == 123)
            .one()
        )
        assert dms_application.application_id == 123
        assert dms_application.process_id == 6712558
        assert dms_application.email == "nonexistant@example.com"
        assert dms_application.dateCreated is not None

    @patch.object(api_dms.DMSGraphQLClient, "get_applications_with_details")
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
            fixtures.make_parsed_graphql_application(
                application_number=123,
                state="accepte",
                email=user.email,
                construction_datetime=date_utils.get_naive_utc_now().strftime("%Y-%m-%dT%H:%M:%S+02:00"),
            )
        ]
        # when
        dms_subscription_api.import_all_updated_dms_applications(6712558)

        # then
        assert db.session.query(users_models.User).count() == 1
        user = db.session.query(users_models.User).first()

        assert len(user.beneficiaryFraudChecks) == 2

        honor_check = (
            db.session.query(subscription_models.BeneficiaryFraudCheck)
            .filter_by(user=user, type=subscription_models.FraudCheckType.HONOR_STATEMENT)
            .one_or_none()
        )
        assert honor_check
        dms_check = (
            db.session.query(subscription_models.BeneficiaryFraudCheck)
            .filter_by(
                user=user, type=subscription_models.FraudCheckType.DMS, status=subscription_models.FraudCheckStatus.OK
            )
            .one_or_none()
        )
        assert dms_check
        assert len(push_testing.requests) == 3

        assert not user.is_beneficiary
        assert not user.deposit
        assert get_user_subscription_state(user).next_step == subscription_schemas.SubscriptionStep.PHONE_VALIDATION

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"]["id_prod"] == 679  # complete subscription

    @patch.object(api_dms.DMSGraphQLClient, "get_applications_with_details")
    def test_import_makes_user_beneficiary(self, get_applications_with_details):
        """
        Test that an existing user with its phone number validated can become
        beneficiary.
        """
        date_of_birth = self.BENEFICIARY_BIRTH_DATE.strftime("%Y-%m-%dT%H:%M:%S")
        dms_validated_birth_date = datetime.date.today() - relativedelta(years=18)

        # Create a user that has validated its email and phone number, meaning it
        # should become beneficiary.
        user = users_factories.UserFactory(
            email=self.EMAIL,
            isEmailValidated=True,
            dateOfBirth=date_of_birth,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        subscription_factories.ProfileCompletionFraudCheckFactory(user=user)

        get_applications_with_details.return_value = [
            fixtures.make_parsed_graphql_application(
                application_number=123,
                state="accepte",
                email=user.email,
                birth_date=dms_validated_birth_date,
                construction_datetime=date_utils.get_naive_utc_now().strftime("%Y-%m-%dT%H:%M:%S+02:00"),
            ),
        ]

        dms_subscription_api.import_all_updated_dms_applications(6712558)

        assert db.session.query(users_models.User).count() == 1
        user = db.session.query(users_models.User).first()

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
            if fraud_check.type == subscription_models.FraudCheckType.DMS
        )
        assert dms_fraud_check.type == subscription_models.FraudCheckType.DMS
        fraud_content = dms_fraud_check.source_data()
        assert fraud_content.birth_date == dms_validated_birth_date
        assert fraud_content.address == "3 La Bigotais 22800 Saint-Donan"

        assert next(
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type == subscription_models.FraudCheckType.HONOR_STATEMENT
        )

        assert len(push_testing.requests) == 4

        assert len(mails_testing.outbox) == 1
        assert (
            mails_testing.outbox[0]["template"]["id_prod"]
            == TransactionalEmail.ACCEPTED_AS_BENEFICIARY_V3.value.id_prod
        )

    @patch.object(api_dms.DMSGraphQLClient, "get_applications_with_details")
    def test_import_makes_user_beneficiary_after_19_birthday(self, get_applications_with_details):
        date_of_birth = (date_utils.get_naive_utc_now() - relativedelta(years=19)).strftime("%Y-%m-%dT%H:%M:%S")

        # Create a user that has validated its email and phone number, meaning it
        # should become beneficiary.
        user = users_factories.UserFactory(
            email=self.EMAIL,
            isEmailValidated=True,
            dateOfBirth=date_of_birth,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        subscription_factories.ProfileCompletionFraudCheckFactory(user=user)
        get_applications_with_details.return_value = [
            fixtures.make_parsed_graphql_application(
                application_number=123,
                state="accepte",
                email=user.email,
                # For the user to be automatically credited, the DMS application must be created before user's 19th birthday
                construction_datetime=date_utils.get_naive_utc_now().strftime("%Y-%m-%dT%H:%M:%S+02:00"),
            )
        ]
        dms_subscription_api.import_all_updated_dms_applications(6712558)

        user = db.session.query(users_models.User).one()

        assert user.roles == [users_models.UserRole.BENEFICIARY]

    @patch.object(api_dms.DMSGraphQLClient, "get_applications_with_details")
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
            fixtures.make_parsed_graphql_application(
                application_number=123,
                state="accepte",
                email=user.email,
                birth_date=self.BENEFICIARY_BIRTH_DATE,
                construction_datetime=date_utils.get_naive_utc_now().isoformat(),
            )
        ]
        dms_subscription_api.import_all_updated_dms_applications(6712558)

        assert db.session.query(users_models.User).count() == 2

        user = db.session.get(users_models.User, user.id)
        assert len(user.beneficiaryFraudChecks) == 1
        fraud_check = user.beneficiaryFraudChecks[0]
        assert fraud_check.type == subscription_models.FraudCheckType.DMS
        assert subscription_models.FraudReasonCode.DUPLICATE_USER in fraud_check.reasonCodes
        assert fraud_check.status == subscription_models.FraudCheckStatus.SUSPICIOUS

        message = dms_subscription_api.get_dms_subscription_message(fraud_check)
        assert message.user_message == (
            "Ton dossier a été refusé car il y a déjà un compte bénéficiaire à ton nom. "
            "Connecte-toi avec l’adresse mail joh***@example.com ou contacte le support si tu penses qu’il s’agit d’une erreur. "
            "Si tu n’as plus ton mot de passe, tu peux effectuer une demande de réinitialisation."
        )
        assert message.call_to_action.icon == subscription_schemas.CallToActionIcon.EXTERNAL

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["params"] == {"DUPLICATE_BENEFICIARY_EMAIL": "joh***@example.com"}

    @patch.object(api_dms.DMSGraphQLClient, "get_applications_with_details")
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
            fixtures.make_parsed_graphql_application(
                application_number=123,
                state="accepte",
                email=applicant.email,
                id_piece_number="123412341234",
                birth_date=self.BENEFICIARY_BIRTH_DATE,
            )
        ]

        dms_subscription_api.import_all_updated_dms_applications(6712558)

        mocked_activate_beneficiary_if_no_missing_step.assert_not_called()
        assert db.session.query(users_models.User).count() == 2

        fraud_check = applicant.beneficiaryFraudChecks[0]
        assert fraud_check.type == subscription_models.FraudCheckType.DMS

        assert fraud_check.status == subscription_models.FraudCheckStatus.SUSPICIOUS
        assert (
            fraud_check.reason
            == f"La pièce d'identité n°123412341234 est déjà prise par l'utilisateur {beneficiary.id}"
        )

        fraud_content = dms_schemas.DMSContent(**fraud_check.resultContent)
        assert fraud_content.birth_date == applicant.dateOfBirth.date()
        assert fraud_content.address == "3 La Bigotais 22800 Saint-Donan"

    @patch.object(api_dms.DMSGraphQLClient, "get_applications_with_details")
    def test_import_native_app_user(self, get_applications_with_details):
        user = users_factories.UserFactory(
            email=self.EMAIL,
            dateOfBirth=self.BENEFICIARY_BIRTH_DATE,
            city="Quito",
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        subscription_factories.ProfileCompletionFraudCheckFactory(user=user)
        push_testing.reset_requests()
        get_applications_with_details.return_value = [
            fixtures.make_parsed_graphql_application(
                application_number=123,
                state="accepte",
                email=user.email,
                construction_datetime=date_utils.get_naive_utc_now().strftime("%Y-%m-%dT%H:%M:%S+02:00"),
            )
        ]
        dms_subscription_api.import_all_updated_dms_applications(6712558)

        # then
        assert db.session.query(users_models.User).count() == 1

        user = db.session.query(users_models.User).first()
        assert user.firstName == "John"
        assert user.postalCode == "67200"

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(
            TransactionalEmail.ACCEPTED_AS_BENEFICIARY_V3.value
        )

        assert len(push_testing.requests) == 4
        assert push_testing.requests[1]["attribute_values"]["u.is_beneficiary"]

    @patch.object(api_dms.DMSGraphQLClient, "get_applications_with_details")
    def test_dms_application_value_error(self, get_applications_with_details):
        user = users_factories.UserFactory()
        get_applications_with_details.return_value = [
            fixtures.make_parsed_graphql_application(
                application_number=123,
                state="accepte",
                email=user.email,
                postal_code="Strasbourg",
                id_piece_number="121314",
            )
        ]
        dms_subscription_api.import_all_updated_dms_applications(6712558)

        fraud_check = user.beneficiaryFraudChecks[0]
        assert fraud_check.status == subscription_models.FraudCheckStatus.ERROR
        assert fraud_check.thirdPartyId == "123"
        assert (
            fraud_check.reason
            == "Erreur dans les données soumises dans le dossier DMS : 'id_piece_number' (121314),'postal_code' (Strasbourg)"
        )
        assert fraud_check.reasonCodes == [subscription_models.FraudReasonCode.ERROR_IN_DATA]

        assert len(mails_testing.outbox) == 1
        assert (
            mails_testing.outbox[0]["template"]
            == TransactionalEmail.PRE_SUBSCRIPTION_DMS_ERROR_TO_BENEFICIARY.value.__dict__
        )

        # A second import should ignore the already processed application
        user_fraud_check_number = len(user.beneficiaryFraudChecks)
        dms_subscription_api.import_all_updated_dms_applications(6712558)
        assert len(user.beneficiaryFraudChecks) == user_fraud_check_number

    @patch.object(api_dms.DMSGraphQLClient, "get_applications_with_details")
    def test_dms_application_value_error_known_user(self, get_applications_with_details):
        user = users_factories.UserFactory()
        get_applications_with_details.return_value = [
            fixtures.make_parsed_graphql_application(
                application_number=1,
                state="accepte",
                postal_code="Strasbourg",
                id_piece_number="121314",
                email=user.email,
            )
        ]
        dms_subscription_api.import_all_updated_dms_applications(6712558)

        fraud_check = user.beneficiaryFraudChecks[0]
        assert fraud_check.status == subscription_models.FraudCheckStatus.ERROR
        assert fraud_check.thirdPartyId == "1"
        assert (
            fraud_check.reason
            == "Erreur dans les données soumises dans le dossier DMS : 'id_piece_number' (121314),'postal_code' (Strasbourg)"
        )
        assert fraud_check.reasonCodes == [subscription_models.FraudReasonCode.ERROR_IN_DATA]

        assert len(mails_testing.outbox) == 1
        assert (
            mails_testing.outbox[0]["template"]
            == TransactionalEmail.PRE_SUBSCRIPTION_DMS_ERROR_TO_BENEFICIARY.value.__dict__
        )

    @patch.object(api_dms.DMSGraphQLClient, "get_applications_with_details")
    def test_dms_application_without_city_does_not_validate_profile(self, get_applications_with_details):
        # instanciate user with validated phone number
        user = users_factories.UserFactory(
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            dateOfBirth=self.BENEFICIARY_BIRTH_DATE,
            city=None,
        )
        get_applications_with_details.return_value = [
            fixtures.make_parsed_graphql_application(
                email=user.email,
                application_number=123,
                state="accepte",
            )
        ]
        dms_subscription_api.import_all_updated_dms_applications(6712558)

        assert get_user_subscription_state(user).next_step == subscription_schemas.SubscriptionStep.PROFILE_COMPLETION

    @patch.object(api_dms.DMSGraphQLClient, "get_applications_with_details")
    def test_complete_dms_application_also_validates_profile(self, get_applications_with_details, client):
        # instanciate user with validated phone number
        user = users_factories.UserFactory(
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            dateOfBirth=self.BENEFICIARY_BIRTH_DATE,
            city=None,
        )
        get_applications_with_details.return_value = [
            fixtures.make_parsed_graphql_application(
                email=user.email,
                application_number=123,
                state="accepte",
                city="Strasbourg",
                construction_datetime=date_utils.get_naive_utc_now().strftime("%Y-%m-%dT%H:%M:%S+02:00"),
            )
        ]
        dms_subscription_api.import_all_updated_dms_applications(6712558)

        client.with_token(user)
        response = client.get("/native/v2/subscription/stepper")

        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] is None
        assert users_models.UserRole.BENEFICIARY in user.roles


@pytest.mark.usefixtures("db_session")
class GraphQLSourceProcessApplicationTest:
    @patch.object(api_dms.DMSGraphQLClient, "get_applications_with_details")
    def test_process_accepted_application_user_already_created(self, get_applications_with_details):
        user = users_factories.UserFactory(dateOfBirth=AGE18_ELIGIBLE_BIRTH_DATE)

        get_applications_with_details.return_value = [
            fixtures.make_parsed_graphql_application(123, "accepte", email=user.email),
        ]

        dms_subscription_api.import_all_updated_dms_applications(6712558)

        assert len(user.beneficiaryFraudChecks) == 2
        dms_fraud_check = next(
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type == subscription_models.FraudCheckType.DMS
        )
        assert not dms_fraud_check.reasonCodes
        assert dms_fraud_check.status == subscription_models.FraudCheckStatus.OK
        statement_fraud_check = next(
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type == subscription_models.FraudCheckType.HONOR_STATEMENT
        )
        assert statement_fraud_check.status == subscription_models.FraudCheckStatus.OK
        assert statement_fraud_check.reason == "honor statement contained in DMS application"

    @patch.object(api_dms.DMSGraphQLClient, "get_applications_with_details")
    def test_process_accepted_application_user_registered_at_18(self, get_applications_with_details):
        user = users_factories.UserFactory(
            dateOfBirth=AGE18_ELIGIBLE_BIRTH_DATE,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        subscription_factories.ProfileCompletionFraudCheckFactory(user=user)

        get_applications_with_details.return_value = [
            fixtures.make_parsed_graphql_application(
                123,
                "accepte",
                email=user.email,
                construction_datetime=date_utils.get_naive_utc_now().strftime("%Y-%m-%dT%H:%M:%S+02:00"),
            ),
        ]

        dms_subscription_api.import_all_updated_dms_applications(6712558)

        assert len(user.beneficiaryFraudChecks) == 3  # profile, DMS, honor statement
        assert user.roles == [users_models.UserRole.BENEFICIARY]

    @patch.object(api_dms.DMSGraphQLClient, "get_applications_with_details")
    def test_process_accepted_application_user_registered_at_18_dms_at_19(self, get_applications_with_details):
        user = users_factories.UserFactory(
            dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=19, months=4),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        subscription_factories.ProfileCompletionFraudCheckFactory(
            user=user,
            dateCreated=date_utils.get_naive_utc_now() - relativedelta(years=1, months=2),
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        get_applications_with_details.return_value = [
            fixtures.make_parsed_graphql_application(
                123123,
                "accepte",
                email=user.email,
                birth_date=user.dateOfBirth,
                # For the user to be automatically credited, the DMS application must be created before user's 19th birthday
                construction_datetime=(date_utils.get_naive_utc_now() - relativedelta(months=5)).strftime(
                    "%Y-%m-%dT%H:%M:%S+02:00"
                ),
            ),
        ]

        dms_subscription_api.import_all_updated_dms_applications(6712558)

        assert len(user.beneficiaryFraudChecks) == 3  # profile, DMS, honor statement
        assert user.roles == [users_models.UserRole.BENEFICIARY]

    @patch.object(api_dms.DMSGraphQLClient, "get_applications_with_details")
    def test_process_accepted_application_user_registered_at_18_dms_started_at_19(self, get_applications_with_details):
        user = users_factories.UserFactory(
            dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=19, days=1),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        subscription_factories.ProfileCompletionFraudCheckFactory(
            user=user,
            dateCreated=date_utils.get_naive_utc_now() - relativedelta(years=1),
        )

        get_applications_with_details.return_value = [
            fixtures.make_parsed_graphql_application(
                123123,
                "accepte",
                email=user.email,
                birth_date=user.dateOfBirth,
                # For the user to be automatically credited, the DMS application must be created before user's 19th birthday
                # Here it's created after 19yo, so requires a manual review
                construction_datetime=(date_utils.get_naive_utc_now()).strftime("%Y-%m-%dT%H:%M:%S+02:00"),
            ),
        ]

        dms_subscription_api.import_all_updated_dms_applications(6712558)

        assert len(user.beneficiaryFraudChecks) == 3  # profile, DMS, honor statement
        assert mails_testing.outbox[0]["subject"] == "Revue manuelle nécessaire"

    @patch.object(api_dms.DMSGraphQLClient, "get_applications_with_details")
    def test_process_accepted_application_user_not_eligible(self, get_applications_with_details):
        user = users_factories.UserFactory(
            dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=19, months=4),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )

        get_applications_with_details.return_value = [
            fixtures.make_parsed_graphql_application(
                123123,
                "accepte",
                email=user.email,
                birth_date=user.dateOfBirth,
                construction_datetime=date_utils.get_naive_utc_now().strftime("%Y-%m-%dT%H:%M:%S+02:00"),
            ),
        ]

        dms_subscription_api.import_all_updated_dms_applications(6712558)

        assert len(user.beneficiaryFraudChecks) == 1
        dms_fraud_check = user.beneficiaryFraudChecks[0]
        assert dms_fraud_check.status == subscription_models.FraudCheckStatus.KO
        assert subscription_models.FraudReasonCode.NOT_ELIGIBLE in dms_fraud_check.reasonCodes
        assert user.roles == []

    @patch.object(api_dms.DMSGraphQLClient, "get_applications_with_details")
    def test_dms_application_value_error(self, get_applications_with_details):
        user = users_factories.UserFactory()
        get_applications_with_details.return_value = [
            fixtures.make_parsed_graphql_application(
                application_number=1,
                state="accepte",
                postal_code="Strasbourg",
                id_piece_number="121314",
                email=user.email,
            )
        ]

        dms_subscription_api.import_all_updated_dms_applications(6712558)

        dms_fraud_check = db.session.query(subscription_models.BeneficiaryFraudCheck).first()
        assert dms_fraud_check.userId == user.id
        assert dms_fraud_check.status == subscription_models.FraudCheckStatus.ERROR
        assert dms_fraud_check.thirdPartyId == "1"
        assert (
            dms_fraud_check.reason
            == "Erreur dans les données soumises dans le dossier DMS : 'id_piece_number' (121314),'postal_code' (Strasbourg)"
        )
        assert dms_fraud_check.reasonCodes == [subscription_models.FraudReasonCode.ERROR_IN_DATA]

        assert len(mails_testing.outbox) == 1
        assert (
            mails_testing.outbox[0]["template"]
            == TransactionalEmail.PRE_SUBSCRIPTION_DMS_ERROR_TO_BENEFICIARY.value.__dict__
        )

    @patch.object(api_dms.DMSGraphQLClient, "get_applications_with_details")
    def test_reimport_same_user(self, get_applications_with_details):
        procedure_number = 42
        already_imported_user = users_factories.BeneficiaryGrant18Factory()

        get_applications_with_details.return_value = [
            fixtures.make_parsed_graphql_application(
                application_number=2,
                state="accepte",
                email=already_imported_user.email,
            ),
        ]

        dms_subscription_api.import_all_updated_dms_applications(procedure_number)

        fraud_check = (
            db.session.query(subscription_models.BeneficiaryFraudCheck)
            .filter(
                subscription_models.BeneficiaryFraudCheck.userId == already_imported_user.id,
                subscription_models.BeneficiaryFraudCheck.type == subscription_models.FraudCheckType.DMS,
            )
            .one()
        )
        assert fraud_check.status == subscription_models.FraudCheckStatus.OK


class DmsImportTest:
    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.get_applications_with_details")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.send_user_message")
    def test_initialize_latest_import_datetime(
        self,
        mock_send_user_message,
        mock_get_applications_with_details,
    ):
        mock_get_applications_with_details.return_value = [
            fixtures.make_parsed_graphql_application(
                123,
                "accepte",
                email="email1@example.com",
                id_piece_number="123123121",
                last_modification_date="2020-10-01T20:00:00+02:00",
                procedure_number=1,
            ),
            fixtures.make_parsed_graphql_application(
                456,
                "en_construction",
                email="email2@example.com",
                id_piece_number="123123122",
                last_modification_date="2020-10-01T20:10:00+02:00",
                procedure_number=1,
            ),
        ]
        user = users_factories.UserFactory(email="email1@example.com")
        dms_subscription_api.import_all_updated_dms_applications(1)
        user_dms_fraud_check = [
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type == subscription_models.FraudCheckType.DMS
        ][0]
        orphan_dms_application = db.session.query(subscription_models.OrphanDmsApplication).first()
        latest_import_record = db.session.query(dms_models.LatestDmsImport).first()

        assert mock_get_applications_with_details.call_count == 1
        assert user_dms_fraud_check.status == subscription_models.FraudCheckStatus.OK
        assert user_dms_fraud_check.type == subscription_models.FraudCheckType.DMS

        assert orphan_dms_application.email == "email2@example.com"

        assert latest_import_record.procedureId == 1
        assert latest_import_record.latestImportDatetime == datetime.datetime(2020, 10, 1, 18, 10, 0)

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.get_applications_with_details")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.send_user_message")
    def test_second_import_of_same_procedure_updates_latest_import_datetime(
        self,
        mock_send_user_message,
        mock_get_applications_with_details,
    ):
        mock_get_applications_with_details.return_value = [
            fixtures.make_parsed_graphql_application(
                123,
                "accepte",
                email="email1@example.com",
                id_piece_number="123123121",
                last_modification_date="2020-10-01T20:00:00+02:00",
                procedure_number=1,
            ),
            fixtures.make_parsed_graphql_application(
                456,
                "en_construction",
                email="email2@example.com",
                id_piece_number="123123122",
                last_modification_date="2020-10-01T21:00:00+02:00",
                procedure_number=1,
            ),
        ]
        dms_factories.LatestDmsImportFactory(
            procedureId=1, latestImportDatetime=datetime.datetime(2020, 10, 1, 15, 0, 0)
        )

        dms_subscription_api.import_all_updated_dms_applications(1)

        latest_import_record = (
            db.session.query(dms_models.LatestDmsImport)
            .order_by(dms_models.LatestDmsImport.latestImportDatetime.desc())
            .first()
        )
        assert latest_import_record.latestImportDatetime == datetime.datetime(2020, 10, 1, 19, 0, 0)
        mock_get_applications_with_details.assert_called_once_with(1, since=datetime.datetime(2020, 10, 1, 15, 0))

    @pytest.mark.usefixtures("db_session")
    @patch.object(api_dms.DMSGraphQLClient, "get_applications_with_details")
    def test_import_is_cancelled_if_another_is_already_in_progress(self, mock_get_applications_with_details):
        dms_factories.LatestDmsImportFactory(procedureId=1, isProcessing=True)

        dms_subscription_api.import_all_updated_dms_applications(1)

        assert db.session.query(dms_models.LatestDmsImport).count() == 1
        mock_get_applications_with_details.assert_not_called()

    @pytest.mark.usefixtures("db_session")
    @patch.object(api_dms.DMSGraphQLClient, "get_applications_with_details")
    def test_latest_import_datetime_stays_the_same_when_no_import_happened(self, mock_get_applications_with_details):
        dms_factories.LatestDmsImportFactory(procedureId=1, latestImportDatetime=datetime.datetime(2020, 10, 1, 15, 0))

        dms_subscription_api.import_all_updated_dms_applications(1)

        latest_import_record = db.session.query(dms_models.LatestDmsImport).first()
        assert latest_import_record.latestImportDatetime == datetime.datetime(2020, 10, 1, 15, 0)

    @pytest.mark.usefixtures("db_session")
    @patch.object(api_dms.DMSGraphQLClient, "get_applications_with_details")
    def test_import_with_forced_since(self, mock_get_applications_with_details):
        dms_factories.LatestDmsImportFactory(procedureId=1, latestImportDatetime=datetime.datetime(2025, 2, 19, 15, 0))

        dms_subscription_api.import_all_updated_dms_applications(1, forced_since=datetime.datetime(2025, 1, 1))

        mock_get_applications_with_details.assert_called_with(1, since=datetime.datetime(2025, 1, 1))


@pytest.mark.usefixtures("db_session")
class ArchiveDMSApplicationsTest:
    @patch.object(api_dms.DMSGraphQLClient, "get_applications_with_details")
    @patch.object(api_dms.DMSGraphQLClient, "archive_application")
    @pytest.mark.settings(DMS_ENROLLMENT_INSTRUCTOR="SomeInstructorId")
    def test_archive_applications(self, dms_archive, dms_applications):
        to_archive_applications_id = 123
        pending_applications_id = 456
        procedure_number = 1

        content = subscription_factories.DMSContentFactory(procedure_number=procedure_number)
        subscription_factories.BeneficiaryFraudCheckFactory(
            resultContent=content,
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.DMS,
            thirdPartyId=str(to_archive_applications_id),
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            resultContent=content,
            status=subscription_models.FraudCheckStatus.STARTED,
            type=subscription_models.FraudCheckType.DMS,
            thirdPartyId=str(pending_applications_id),
        )
        dms_applications.return_value = [
            fixtures.make_parsed_graphql_application(
                to_archive_applications_id, "accepte", application_techid="TO_ARCHIVE_TECHID"
            ),
            fixtures.make_parsed_graphql_application(
                pending_applications_id, "accepte", application_techid="PENDING_ID"
            ),
        ]

        dms_subscription_api.archive_applications(procedure_number, dry_run=False)

        dms_archive.assert_called_once()
        assert dms_archive.call_args[0] == ("TO_ARCHIVE_TECHID", "SomeInstructorId")


class HandleDeletedDmsApplicationsTest:
    @pytest.mark.usefixtures("db_session")
    @patch.object(api_dms.DMSGraphQLClient, "execute_query")
    def test_handle_deleted_dms_applications(self, execute_query):
        fraud_check_not_to_mark_as_deleted = subscription_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId="1", type=subscription_models.FraudCheckType.DMS
        )
        fraud_check_to_mark_as_deleted = subscription_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId="2", type=subscription_models.FraudCheckType.DMS
        )
        fraud_check_already_marked_as_deleted = subscription_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId="3",
            status=subscription_models.FraudCheckStatus.CANCELED,
            reason="Custom reason",
            type=subscription_models.FraudCheckType.DMS,
        )
        fraud_check_to_delete_with_empty_result_content = subscription_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId="4", type=subscription_models.FraudCheckType.DMS, resultContent=None
        )
        ok_fraud_check_not_to_mark_as_deleted = subscription_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId="5",
            type=subscription_models.FraudCheckType.DMS,
            status=subscription_models.FraudCheckStatus.OK,
        )

        procedure_number = 1
        execute_query.return_value = fixtures.make_graphql_deleted_applications(procedure_number, [2, 3, 4])

        dms_subscription_api.handle_deleted_dms_applications(procedure_number)

        assert fraud_check_not_to_mark_as_deleted.status == subscription_models.FraudCheckStatus.PENDING
        assert fraud_check_to_mark_as_deleted.status == subscription_models.FraudCheckStatus.CANCELED
        assert fraud_check_already_marked_as_deleted.status == subscription_models.FraudCheckStatus.CANCELED
        assert fraud_check_to_delete_with_empty_result_content.status == subscription_models.FraudCheckStatus.CANCELED
        assert ok_fraud_check_not_to_mark_as_deleted.status == subscription_models.FraudCheckStatus.OK

        assert (
            fraud_check_to_delete_with_empty_result_content.reason
            == "Dossier supprimé sur démarches-simplifiées. Motif: user_request"
        )
        assert (
            fraud_check_to_mark_as_deleted.reason == "Dossier supprimé sur démarches-simplifiées. Motif: user_request"
        )
        assert fraud_check_already_marked_as_deleted.reason == "Custom reason"

        assert fraud_check_not_to_mark_as_deleted.resultContent.get("deletion_datetime") is None
        assert fraud_check_to_mark_as_deleted.resultContent.get("deletion_datetime") == "2021-10-01T22:00:00"
        assert fraud_check_to_delete_with_empty_result_content.resultContent is None

    @pytest.mark.usefixtures("db_session")
    @patch.object(api_dms.DMSGraphQLClient, "execute_query")
    def test_get_latest_deleted_application_datetime(self, execute_query):
        procedure_number = 1
        latest_deletion_date = datetime.datetime(2020, 1, 1)

        dms_content_with_deletion_date = subscription_factories.DMSContentFactory(
            deletion_datetime=latest_deletion_date, procedure_number=procedure_number
        )
        dms_content_before_deletion_date = subscription_factories.DMSContentFactory(
            deletion_datetime=latest_deletion_date - datetime.timedelta(days=1), procedure_number=procedure_number
        )

        # fraud_check_deleted_last
        subscription_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId="8888",
            status=subscription_models.FraudCheckStatus.CANCELED,
            type=subscription_models.FraudCheckType.DMS,
            resultContent=dms_content_with_deletion_date,
        )
        # fraud_check_deleted_before_last
        subscription_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId="8889",
            status=subscription_models.FraudCheckStatus.CANCELED,
            type=subscription_models.FraudCheckType.DMS,
            resultContent=dms_content_before_deletion_date,
        )
        # fraud_check_with_empty_result_content
        subscription_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId="8890",
            status=subscription_models.FraudCheckStatus.CANCELED,
            type=subscription_models.FraudCheckType.DMS,
            resultContent=None,
        )

        execute_query.return_value = fixtures.make_graphql_deleted_applications(procedure_number, [8888, 8889, 8890])

        assert dms_subscription_api._get_latest_deleted_application_datetime(procedure_number) == latest_deletion_date


@pytest.mark.usefixtures("db_session")
class HandleInactiveApplicationTest:
    @patch.object(api_dms.DMSGraphQLClient, "mark_without_continuation")
    @patch.object(api_dms.DMSGraphQLClient, "get_applications_with_details")
    @pytest.mark.settings(DMS_ENROLLMENT_INSTRUCTOR="SomeInstructorId")
    def test_mark_without_continuation(self, dms_applications_mock, mark_without_continuation_mock):
        active_application = fixtures.make_parsed_graphql_application(
            application_number=1,
            state="en_construction",
            last_modification_date=datetime.datetime.today() - datetime.timedelta(days=25),
        )
        inactive_application = fixtures.make_parsed_graphql_application(
            application_number=2,
            state="en_construction",
            last_modification_date=datetime.datetime.today() - datetime.timedelta(days=190),
        )
        active_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.DMS,
            thirdPartyId=str(active_application.number),
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.DMSContentFactory(email=active_application.profile.email),
        )
        inactive_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.DMS,
            thirdPartyId=str(inactive_application.number),
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.DMSContentFactory(email=inactive_application.profile.email),
        )

        dms_applications_mock.return_value = [active_application, inactive_application]

        dms_subscription_api.handle_inactive_dms_applications(1)

        mark_without_continuation_mock.assert_called_once_with(
            inactive_application.id,
            "SomeInstructorId",
            motivation=(
                "Aucune activité n’a eu lieu sur ton dossier depuis plus de 30 jours.\n"
                "\n"
                "Conformément à nos CGUs, en cas d’absence de réponse ou de "
                "justification insuffisante, nous nous réservons le droit de "
                "refuser ta création de compte. Aussi nous avons classé sans "
                f"suite ton dossier n°{inactive_application.number}.\n"
                "\n"
                "Sous réserve d’être encore éligible, tu peux si tu le "
                "souhaites refaire une demande d’inscription. Nous t'"
                "invitons à soumettre un nouveau dossier en suivant ce lien : "
                f"https://demarche.numerique.gouv.fr/dossiers/new?procedure_id={inactive_application.procedure.number}\n"
                "\n"
                "Tu trouveras toutes les informations dans notre FAQ pour "
                "t'accompagner dans cette démarche : "
                "https://aide.passculture.app/hc/fr/sections/4411991878545-Inscription-et-modification-d-information-sur-Démarches-Simplifiées\n"
            ),
            from_draft=True,
        )
        assert active_fraud_check.status == subscription_models.FraudCheckStatus.STARTED
        assert inactive_fraud_check.status == subscription_models.FraudCheckStatus.CANCELED

    @patch.object(api_dms.DMSGraphQLClient, "mark_without_continuation")
    @patch.object(api_dms.DMSGraphQLClient, "make_on_going")
    @patch.object(api_dms.DMSGraphQLClient, "get_applications_with_details")
    @time_machine.travel("2022-04-27")
    def test_mark_without_continuation_skip_never_eligible(
        self, dms_applications_mock, make_on_going_mock, mark_without_continuation_mock
    ):
        inactive_application = fixtures.make_parsed_graphql_application(
            application_number=2,
            state="en_construction",
            last_modification_date="2021-11-11T00:00:00+02:00",
            birth_date=datetime.datetime(2002, 1, 1),
            postal_code="12400",
        )

        inactive_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.DMS,
            thirdPartyId=str(inactive_application.number),
            status=subscription_models.FraudCheckStatus.STARTED,
        )

        dms_applications_mock.return_value = [inactive_application]

        dms_subscription_api.handle_inactive_dms_applications(1, with_never_eligible_applicant_rule=True)

        make_on_going_mock.assert_not_called()
        mark_without_continuation_mock.assert_not_called()

        assert inactive_fraud_check.status == subscription_models.FraudCheckStatus.STARTED

    @patch.object(api_dms.DMSGraphQLClient, "mark_without_continuation")
    @patch.object(api_dms.DMSGraphQLClient, "get_applications_with_details")
    @time_machine.travel("2022-04-27")
    @pytest.mark.settings(DMS_ENROLLMENT_INSTRUCTOR="SomeInstructorId")
    def test_duplicated_application_can_be_cancelled(self, dms_applications_mock, mark_without_continuation_mock):
        old_email = "lucille.ellingson@example.com"
        new_email = "lucy.ellingson@example.com"
        inactive_application = fixtures.make_parsed_graphql_application(
            application_number=1,
            state="en_construction",
            last_modification_date="2021-11-11T00:00:00+02:00",
            email=new_email,
        )

        active_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.DMS,
            thirdPartyId=str(inactive_application.number),
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.DMSContentFactory(email=old_email),
        )
        inactive_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.DMS,
            thirdPartyId=str(inactive_application.number),
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.DMSContentFactory(email=new_email),
        )

        dms_applications_mock.return_value = [inactive_application]

        # When
        dms_subscription_api.handle_inactive_dms_applications(1)

        # Then
        mark_without_continuation_mock.assert_called_once_with(
            inactive_application.id,
            "SomeInstructorId",
            motivation=(
                "Aucune activité n’a eu lieu sur ton dossier depuis plus de 30 jours.\n"
                "\n"
                "Conformément à nos CGUs, en cas d’absence de réponse ou de "
                "justification insuffisante, nous nous réservons le droit de "
                "refuser ta création de compte. Aussi nous avons classé sans "
                f"suite ton dossier n°{inactive_application.number}.\n"
                "\n"
                "Sous réserve d’être encore éligible, tu peux si tu le "
                "souhaites refaire une demande d’inscription. Nous t'"
                "invitons à soumettre un nouveau dossier en suivant ce lien : "
                f"https://demarche.numerique.gouv.fr/dossiers/new?procedure_id={inactive_application.procedure.number}\n"
                "\n"
                "Tu trouveras toutes les informations dans notre FAQ pour "
                "t'accompagner dans cette démarche : "
                "https://aide.passculture.app/hc/fr/sections/4411991878545-Inscription-et-modification-d-information-sur-Démarches-Simplifiées\n"
            ),
            from_draft=True,
        )
        assert active_fraud_check.status == subscription_models.FraudCheckStatus.STARTED
        assert inactive_fraud_check.status == subscription_models.FraudCheckStatus.CANCELED


@pytest.mark.usefixtures("db_session")
class IsNeverEligibleTest:
    @time_machine.travel("2022-04-27")
    def test_19_yo_at_generalisation_from_not_test_department(self):
        inactive_application = fixtures.make_parsed_graphql_application(
            application_number=1,
            state="en_construction",
            birth_date=datetime.datetime(2002, 1, 1),
            postal_code="12400",
        )
        assert dms_subscription_api._is_never_eligible_applicant(inactive_application)

    @time_machine.travel("2022-04-27")
    def test_19_yo_at_generalisation_from_test_department(self):
        inactive_application = fixtures.make_parsed_graphql_application(
            application_number=1,
            state="en_construction",
            birth_date=datetime.datetime(2002, 1, 1),
            postal_code="56510",
        )
        assert not dms_subscription_api._is_never_eligible_applicant(inactive_application)

    @time_machine.travel("2022-04-27")
    def test_still_18_yo_after_generalisation(self):
        inactive_application = fixtures.make_parsed_graphql_application(
            application_number=1,
            state="en_construction",
            birth_date=datetime.datetime(2002, 6, 1),
            postal_code="12400",
        )
        assert not dms_subscription_api._is_never_eligible_applicant(inactive_application)


class HasInactivityDelayExpiredTest:
    def test_has_inactivity_delay_expired_without_message(self):
        no_message_application = fixtures.make_parsed_graphql_application(
            application_number=1,
            state="en_construction",
            last_modification_date="2022-01-01T00:00:00+02:00",
            messages=[],
        )

        assert not dms_subscription_api._has_inactivity_delay_expired(no_message_application)

    @time_machine.travel("2022-04-27")
    def test_has_inactivity_delay_expired_with_recent_message(self):
        no_message_application = fixtures.make_parsed_graphql_application(
            application_number=1,
            state="en_construction",
            last_modification_date="2022-01-01T00:00:00+02:00",
            messages=[
                {"createdAt": "2022-04-06T00:00:00+02:00", "email": "instrouctor@example.com"},
                {"createdAt": "2020-04-06T00:00:00+02:00", "email": "instrouctor@example.com"},
            ],
        )

        assert not dms_subscription_api._has_inactivity_delay_expired(no_message_application)

    @time_machine.travel("2022-04-27")
    def test_has_inactivity_delay_expired_with_old_message(self):
        no_message_application = fixtures.make_parsed_graphql_application(
            application_number=1,
            state="en_construction",
            last_modification_date="2022-01-01T00:00:00+02:00",
            messages=[
                {"createdAt": "2022-01-01T00:00:00+02:00", "email": "instrouctor@example.com"},
                {"createdAt": "2020-04-06T00:00:00+02:00", "email": "instrouctor@example.com"},
            ],
        )

        assert dms_subscription_api._has_inactivity_delay_expired(no_message_application)

    @time_machine.travel("2022-04-27")
    def test_has_inactivity_delay_expired_with_old_message_sent_by_user(self):
        applicant_email = "applikant@example.com"

        no_message_application = fixtures.make_parsed_graphql_application(
            application_number=1,
            email=applicant_email,
            state="en_construction",
            last_modification_date="2022-01-01T00:00:00+02:00",
            messages=[
                {"createdAt": "2021-01-01T00:00:00+02:00", "email": applicant_email},
                {"createdAt": "2020-04-06T00:00:00+02:00", "email": "instrouctor@example.com"},
            ],
        )

        assert not dms_subscription_api._has_inactivity_delay_expired(no_message_application)
