import datetime
from unittest.mock import patch

import freezegun
import pytest

from pcapi.connectors.dms import api as api_dms
from pcapi.connectors.dms import models as dms_models
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
import pcapi.core.mails.testing as mails_testing
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.dms import api as dms_subscription_api
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models

from tests.scripts.beneficiary.fixture import make_parsed_graphql_application
from tests.scripts.beneficiary.fixture import make_single_application


@pytest.mark.usefixtures("db_session")
@freezegun.freeze_time("2022-11-02")
class DMSSubscriptionItemStatusTest:
    def test_not_eligible(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime(year=2002, month=1, day=1))

        status = dms_subscription_api.get_dms_subscription_item_status(user, users_models.EligibilityType.UNDERAGE, [])

        assert status == subscription_models.SubscriptionItemStatus.VOID

    def test_eligible(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime(year=2004, month=1, day=1))

        status = dms_subscription_api.get_dms_subscription_item_status(user, users_models.EligibilityType.AGE18, [])

        assert status == subscription_models.SubscriptionItemStatus.TODO

    def test_ko_and_ok(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime(year=2002, month=1, day=1))

        ok_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.DMS, status=fraud_models.FraudCheckStatus.OK
        )
        ko_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.DMS, status=fraud_models.FraudCheckStatus.KO
        )

        status = dms_subscription_api.get_dms_subscription_item_status(
            user, users_models.EligibilityType.UNDERAGE, [ok_check, ko_check]
        )

        assert status == subscription_models.SubscriptionItemStatus.OK

    def test_ko(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime(year=2006, month=1, day=1))

        ko_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.DMS, status=fraud_models.FraudCheckStatus.KO
        )
        suspicious_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.DMS, status=fraud_models.FraudCheckStatus.SUSPICIOUS
        )

        status = dms_subscription_api.get_dms_subscription_item_status(
            user, users_models.EligibilityType.UNDERAGE, [ko_check, suspicious_check]
        )

        assert status == subscription_models.SubscriptionItemStatus.KO

    def test_started(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime(year=2006, month=1, day=1))

        pending_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.DMS, status=fraud_models.FraudCheckStatus.STARTED
        )

        status = dms_subscription_api.get_dms_subscription_item_status(
            user, users_models.EligibilityType.UNDERAGE, [pending_check]
        )

        assert status == subscription_models.SubscriptionItemStatus.PENDING


@pytest.mark.usefixtures("db_session")
@freezegun.freeze_time("2022-11-02")
class DMSOrphanSubsriptionTest:
    @patch.object(api_dms.DMSGraphQLClient, "execute_query")
    def test_dms_orphan_corresponding_user(self, execute_query):
        application_number = 1234
        procedure_number = 4321
        email = "dms_orphan@example.com"

        user = users_factories.UserFactory(email=email)
        fraud_factories.OrphanDmsApplicationFactory(
            email=email, application_id=application_number, process_id=procedure_number
        )

        execute_query.return_value = make_single_application(
            application_number, dms_models.GraphQLApplicationStates.draft, email=email
        )

        dms_subscription_api.try_dms_orphan_adoption(user)

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(userId=user.id).first()
        assert fraud_check is not None

        dms_orphan = fraud_models.OrphanDmsApplication.query.filter_by(email=user.email).first()
        assert dms_orphan is None

    @patch.object(api_dms.DMSGraphQLClient, "execute_query")
    def test_dms_orphan_corresponding_user_with_field_error(self, execute_query):
        application_number = 1234
        procedure_number = 4321
        email = "dms_orphan@example.com"

        user = users_factories.UserFactory(email=email)
        fraud_factories.OrphanDmsApplicationFactory(
            email=email, application_id=application_number, process_id=procedure_number
        )

        execute_query.return_value = make_single_application(
            application_number, dms_models.GraphQLApplicationStates.draft, email=email, postal_code="1234"
        )

        dms_subscription_api.try_dms_orphan_adoption(user)

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(userId=user.id).first()
        assert fraud_check is not None

        dms_orphan = fraud_models.OrphanDmsApplication.query.filter_by(email=user.email).first()
        assert dms_orphan is None


@pytest.mark.usefixtures("db_session")
class HandleDmsApplicationTest:
    id_piece_number_not_accepted_message = (
        "Bonjour,\n"
        "\n"
        "Nous avons bien reçu ton dossier, mais il y a une erreur dans le champ contenant ta pièce d'identité, inscrit sur le formulaire en ligne:\n"
        "Ton numéro de pièce d’identité doit être renseigné sous format alphanumérique sans espace et sans caractères spéciaux\n"
        '<a href="https://aide.passculture.app/hc/fr/articles/4411999008657--Jeunes-Où-puis-je-trouver-le-numéro-de-ma-pièce-d-identité">Où puis-je trouver le numéro de ma pièce d’identité ?</a>\n'
        "\n"
        "Merci de corriger ton dossier.\n"
        "\n"
        'Tu trouveras de l’aide dans cet article : <a href="https://aide.passculture.app/hc/fr/articles/4411999116433--Jeunes-Où-puis-je-trouver-de-l-aide-concernant-mon-dossier-d-inscription-sur-Démarches-Simplifiées-">Où puis-je trouver de l’aide concernant mon dossier d’inscription sur Démarches Simplifiées ?</a>\n'
        "\n"
        "Nous te souhaitons une belle journée.\n"
        "\n"
        "L’équipe du pass Culture"
    )

    def test_concurrent_accepted_calls(self):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime(2000, 1, 1), roles=[users_models.UserRole.UNDERAGE_BENEFICIARY]
        )
        application_number = 1234
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            thirdPartyId=str(application_number),
            status=fraud_models.FraudCheckStatus.OK,
            type=fraud_models.FraudCheckType.DMS,
        )
        dms_response = make_parsed_graphql_application(
            application_number=application_number,
            state=dms_models.GraphQLApplicationStates.accepted,
            email=user.email,
            birth_date=datetime.datetime(2016, 1, 1),
        )

        dms_subscription_api.handle_dms_application(dms_response)

        assert fraud_models.BeneficiaryFraudCheck.query.first().status == fraud_models.FraudCheckStatus.OK

    @patch("pcapi.core.subscription.dms.api.subscription_messages.on_dms_application_received")
    @freezegun.freeze_time("2016-11-02")
    def test_multiple_call_for_same_application(self, mock_on_dms_application_received, db_session):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime(2000, 1, 1), roles=[users_models.UserRole.UNDERAGE_BENEFICIARY]
        )
        application_number = 1234
        dms_response = make_parsed_graphql_application(
            application_number=application_number,
            state=dms_models.GraphQLApplicationStates.on_going,
            email=user.email,
            birth_date=datetime.datetime(2000, 1, 1),
        )

        dms_subscription_api.handle_dms_application(dms_response)

        mock_on_dms_application_received.assert_called_once_with(user)
        mock_on_dms_application_received.reset_mock()
        dms_fraud_check = [
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type == fraud_models.FraudCheckType.DMS
        ][0]
        assert (
            dms_fraud_check.source_data().get_latest_modification_datetime()
            == dms_response.latest_modification_datetime
        )

        dms_subscription_api.handle_dms_application(dms_response)
        mock_on_dms_application_received.assert_not_called()
        db_session.refresh(dms_fraud_check)
        assert (
            dms_fraud_check.source_data().get_latest_modification_datetime()
            == dms_response.latest_modification_datetime
        )

    @patch("pcapi.connectors.dms.serializer.parse_beneficiary_information_graphql")
    def test_field_error(self, mocked_parse_beneficiary_information):
        user = users_factories.UserFactory()
        dms_response = make_parsed_graphql_application(
            application_number=1, state=dms_models.GraphQLApplicationStates.draft, email=user.email
        )
        mocked_parse_beneficiary_information.side_effect = [Exception()]

        with pytest.raises(Exception):
            dms_subscription_api.handle_dms_application(dms_response)

        assert fraud_models.BeneficiaryFraudCheck.query.first() is None

    @patch.object(api_dms.DMSGraphQLClient, "send_user_message")
    def test_field_error_when_draft(self, send_dms_message_mock):
        user = users_factories.UserFactory()
        dms_response = make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.draft,
            email=user.email,
            id_piece_number="(wrong_number)",
            application_techid="XYZQVM",
        )

        dms_subscription_api.handle_dms_application(dms_response)

        subscription_message = subscription_models.SubscriptionMessage.query.filter_by(userId=user.id).one()
        assert (
            subscription_message.userMessage
            == "Il semblerait que le champ ‘ta pièce d'identité’ soit erroné. Tu peux te rendre sur le site Démarches-simplifiées pour le rectifier."
        )

        send_dms_message_mock.assert_called_once()
        assert send_dms_message_mock.call_args[0][0] == "XYZQVM"
        assert send_dms_message_mock.call_args[0][2] == self.id_piece_number_not_accepted_message
        assert len(mails_testing.outbox) == 0

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(userId=user.id).one()
        assert fraud_check.status == fraud_models.FraudCheckStatus.STARTED
        assert fraud_check.reasonCodes == [fraud_models.FraudReasonCode.ERROR_IN_DATA]

    @patch.object(api_dms.DMSGraphQLClient, "send_user_message")
    def test_field_error_when_on_going(self, send_dms_message_mock):
        application_number = 1
        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            thirdPartyId=str(application_number),
            status=fraud_models.FraudCheckStatus.STARTED,
            type=fraud_models.FraudCheckType.DMS,
        )
        dms_response = make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.on_going,
            email=user.email,
            id_piece_number="(wrong_number)",
            application_techid="XYZQVM",
        )

        dms_subscription_api.handle_dms_application(dms_response)

        subscription_message = subscription_models.SubscriptionMessage.query.filter_by(userId=user.id).one()
        assert (
            subscription_message.userMessage
            == "Ton dossier déposé sur le site Démarches-Simplifiées a été refusé : le champ ‘ta pièce d'identité’ n’est pas valide."
        )

        send_dms_message_mock.assert_not_called()
        assert len(mails_testing.outbox) == 0

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(userId=user.id).one()
        assert fraud_check.status == fraud_models.FraudCheckStatus.PENDING

    @patch.object(api_dms.DMSGraphQLClient, "send_user_message")
    def test_field_error_when_accepted(self, send_dms_message_mock):
        application_number = 1
        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            thirdPartyId=str(application_number),
            status=fraud_models.FraudCheckStatus.STARTED,
            type=fraud_models.FraudCheckType.DMS,
        )
        dms_response = make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.accepted,
            email=user.email,
            id_piece_number="(wrong_number)",
            application_techid="XYZQVM",
        )

        dms_subscription_api.handle_dms_application(dms_response)

        subscription_message = subscription_models.SubscriptionMessage.query.filter_by(userId=user.id).one()
        assert (
            subscription_message.userMessage
            == "Ton dossier déposé sur le site Démarches-Simplifiées a été refusé : le champ ‘ta pièce d'identité’ n’est pas valide."
        )

        send_dms_message_mock.assert_not_called()
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["template"]["id_prod"] == 510

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(userId=user.id).one()
        assert fraud_check.status == fraud_models.FraudCheckStatus.ERROR

    @patch.object(api_dms.DMSGraphQLClient, "send_user_message")
    def test_field_error_when_refused(self, send_dms_message_mock):
        application_number = 1
        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            thirdPartyId=str(application_number),
            status=fraud_models.FraudCheckStatus.STARTED,
            type=fraud_models.FraudCheckType.DMS,
        )
        dms_response = make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.refused,
            email=user.email,
            id_piece_number="(wrong_number)",
            application_techid="XYZQVM",
        )

        dms_subscription_api.handle_dms_application(dms_response)

        subscription_message = subscription_models.SubscriptionMessage.query.filter_by(userId=user.id).one()
        assert (
            subscription_message.userMessage
            == "Ton dossier déposé sur le site Démarches-Simplifiées a été refusé : tu n’es malheureusement pas éligible au pass Culture."
        )

        send_dms_message_mock.assert_not_called()
        assert len(mails_testing.outbox) == 0

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(userId=user.id).one()
        assert fraud_check.status == fraud_models.FraudCheckStatus.KO

    @override_features(DISABLE_USER_NAME_AND_FIRST_NAME_VALIDATION_IN_TESTING_AND_STAGING=False)
    def test_field_error_allows_fraud_check_content(self):
        user = users_factories.UserFactory()
        dms_response = make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.refused,
            email=user.email,
            id_piece_number="(wrong_number)",
            first_name="",
            application_techid="XYZQVM",
        )
        dms_subscription_api.handle_dms_application(dms_response)

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(
            userId=user.id, type=fraud_models.FraudCheckType.DMS
        ).first()
        assert fraud_check.status == fraud_models.FraudCheckStatus.KO

        result_content = fraud_check.source_data()
        assert result_content.application_number == 1
        assert result_content.birth_date == datetime.date(2004, 1, 1)
        assert result_content.registration_datetime == datetime.datetime(
            2020, 5, 13, 9, 9, 46, tzinfo=datetime.timezone(datetime.timedelta(seconds=7200))
        )
        assert result_content.first_name == ""

    @patch("pcapi.core.mails.transactional.send_create_account_after_dms_email")
    def test_processing_accepted_orphan_application_is_idempotent(self, mock_send_create_account_after_dms_email):
        dms_response = make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.accepted,
            email="orphan@example.com",
            last_modification_date="2020-05-13T09:09:46.000+02:00",
        )

        dms_subscription_api.handle_dms_application(dms_response)
        dms_subscription_api.handle_dms_application(dms_response)
        orphan = fraud_models.OrphanDmsApplication.query.filter_by(application_id=1).one()

        mock_send_create_account_after_dms_email.assert_called_once_with("orphan@example.com")
        assert orphan.latest_modification_datetime == datetime.datetime(2020, 5, 13, 7, 9, 46)

    @patch("pcapi.core.subscription.dms.api.dms_connector_api.DMSGraphQLClient.send_user_message")
    def test_processing_draft_orphan_application_is_idempotent(self, mock_send_user_message):
        dms_response = make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.draft,
            email="orphan@example.com",
            last_modification_date="2020-05-13T09:09:46.000+02:00",
        )

        dms_subscription_api.handle_dms_application(dms_response)
        dms_subscription_api.handle_dms_application(dms_response)
        orphan = fraud_models.OrphanDmsApplication.query.filter_by(application_id=1).one()

        mock_send_user_message.assert_called_once()
        assert orphan.latest_modification_datetime == datetime.datetime(2020, 5, 13, 7, 9, 46)

    @patch("pcapi.core.subscription.dms.api.dms_connector_api.DMSGraphQLClient.send_user_message")
    @freezegun.freeze_time("2022-05-13")
    def test_correcting_application_resets_errors(self, mock_send_user_message, db_session):
        user = users_factories.UserFactory(email="john.stiles@example.com")
        dms_response = make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.draft,
            email="john.stiles@example.com",
            last_modification_date="2022-05-13T09:09:46.000+02:00",
            birth_date=datetime.datetime(2000, 1, 1),
        )

        dms_subscription_api.handle_dms_application(dms_response)

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(
            userId=user.id, type=fraud_models.FraudCheckType.DMS
        ).first()

        assert fraud_check.reasonCodes == [fraud_models.FraudReasonCode.AGE_NOT_VALID]
        assert fraud_check.reason == "Erreur dans les données soumises dans le dossier DMS : 'birth_date' (2000-01-01)"

        # User then fixes date error
        dms_response = make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.draft,
            email="john.stiles@example.com",
            last_modification_date="2022-05-15T09:09:46.000+02:00",
            birth_date=datetime.datetime(2004, 1, 1),
        )

        dms_subscription_api.handle_dms_application(dms_response)

        db_session.refresh(fraud_check)

        assert fraud_check.reasonCodes == []
        assert fraud_check.reason is None
