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
        application_id = 1234
        procedure_id = 4321
        email = "dms_orphan@example.com"

        user = users_factories.UserFactory(email=email)
        fraud_factories.OrphanDmsApplicationFactory(email=email, application_id=application_id, process_id=procedure_id)

        execute_query.return_value = make_single_application(
            application_id, dms_models.GraphQLApplicationStates.draft, email=email
        )

        dms_subscription_api.try_dms_orphan_adoption(user)

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(userId=user.id).first()
        assert fraud_check is not None

        dms_orphan = fraud_models.OrphanDmsApplication.query.filter_by(email=user.email).first()
        assert dms_orphan is None

    @patch.object(api_dms.DMSGraphQLClient, "execute_query")
    def test_dms_orphan_corresponding_user_with_parsing_error(self, execute_query):
        application_id = 1234
        procedure_id = 4321
        email = "dms_orphan@example.com"

        user = users_factories.UserFactory(email=email)
        fraud_factories.OrphanDmsApplicationFactory(email=email, application_id=application_id, process_id=procedure_id)

        execute_query.return_value = make_single_application(
            application_id, dms_models.GraphQLApplicationStates.draft, email=email, postal_code="1234"
        )

        dms_subscription_api.try_dms_orphan_adoption(user)

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(userId=user.id).first()
        assert fraud_check is not None

        dms_orphan = fraud_models.OrphanDmsApplication.query.filter_by(email=user.email).first()
        assert dms_orphan is None


@pytest.mark.usefixtures("db_session")
class HandleDmsApplicationTest:
    @patch("pcapi.connectors.dms.serializer.parse_beneficiary_information_graphql")
    def test_parsing_failure(self, mocked_parse_beneficiary_information):
        user = users_factories.UserFactory()
        dms_response = make_parsed_graphql_application(
            application_id=1, state=dms_models.GraphQLApplicationStates.draft, email=user.email
        )
        mocked_parse_beneficiary_information.side_effect = [Exception()]

        with pytest.raises(Exception):
            dms_subscription_api.handle_dms_application(dms_response, 123)

        assert fraud_models.BeneficiaryFraudCheck.query.first() is None

    @patch.object(api_dms.DMSGraphQLClient, "send_user_message")
    def test_parsing_error_when_draft(self, send_dms_message_mock):
        user = users_factories.UserFactory()
        dms_response = make_parsed_graphql_application(
            application_id=1,
            state=dms_models.GraphQLApplicationStates.draft,
            email=user.email,
            id_piece_number="(wrong_number)",
            application_techid="XYZQVM",
        )

        dms_subscription_api.handle_dms_application(dms_response, 123)

        subscription_message = subscription_models.SubscriptionMessage.query.filter_by(userId=user.id).one()
        assert (
            subscription_message.userMessage
            == "Il semblerait que le champ ‘ta pièce d'identité’ soit erroné. Tu peux te rendre sur le site Démarches-simplifiées pour le rectifier."
        )

        send_dms_message_mock.assert_called_once()
        assert send_dms_message_mock.call_args[0][0] == "XYZQVM"
        assert (
            "Nous avons bien reçu ton dossier, mais le numéro de pièce d'identité sur le formulaire ne correspond pas à celui indiqué sur ta pièce d'identité."
            in send_dms_message_mock.call_args[0][2]
        )
        assert len(mails_testing.outbox) == 0

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(userId=user.id).one()
        assert fraud_check.status == fraud_models.FraudCheckStatus.STARTED

    @patch.object(api_dms.DMSGraphQLClient, "send_user_message")
    def test_parsing_error_when_on_going(self, send_dms_message_mock):
        application_id = 1
        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            thirdPartyId=str(application_id),
            status=fraud_models.FraudCheckStatus.STARTED,
            type=fraud_models.FraudCheckType.DMS,
        )
        dms_response = make_parsed_graphql_application(
            application_id=1,
            state=dms_models.GraphQLApplicationStates.on_going,
            email=user.email,
            id_piece_number="(wrong_number)",
            application_techid="XYZQVM",
        )

        dms_subscription_api.handle_dms_application(dms_response, 123)

        subscription_message = subscription_models.SubscriptionMessage.query.filter_by(userId=user.id).one()
        assert (
            subscription_message.userMessage
            == "Il semblerait que le champ ‘ta pièce d'identité’ soit erroné. Tu peux te rendre sur le site Démarches-simplifiées pour le rectifier."
        )

        send_dms_message_mock.assert_not_called()
        assert len(mails_testing.outbox) == 0

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(userId=user.id).one()
        assert fraud_check.status == fraud_models.FraudCheckStatus.PENDING

    @patch.object(api_dms.DMSGraphQLClient, "send_user_message")
    def test_parsing_error_when_accepted(self, send_dms_message_mock):
        application_id = 1
        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            thirdPartyId=str(application_id),
            status=fraud_models.FraudCheckStatus.STARTED,
            type=fraud_models.FraudCheckType.DMS,
        )
        dms_response = make_parsed_graphql_application(
            application_id=1,
            state=dms_models.GraphQLApplicationStates.accepted,
            email=user.email,
            id_piece_number="(wrong_number)",
            application_techid="XYZQVM",
        )

        dms_subscription_api.handle_dms_application(dms_response, 123)

        subscription_message = subscription_models.SubscriptionMessage.query.filter_by(userId=user.id).one()
        assert (
            subscription_message.userMessage
            == "Ton dossier déposé sur le site Démarches-Simplifiées a été refusé car le champ ‘ta pièce d'identité’ n’est pas valide."
        )

        send_dms_message_mock.assert_not_called()
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["template"]["id_prod"] == 510

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(userId=user.id).one()
        assert fraud_check.status == fraud_models.FraudCheckStatus.ERROR

    @patch.object(api_dms.DMSGraphQLClient, "send_user_message")
    def test_parsing_error_when_refused(self, send_dms_message_mock):
        application_id = 1
        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            thirdPartyId=str(application_id),
            status=fraud_models.FraudCheckStatus.STARTED,
            type=fraud_models.FraudCheckType.DMS,
        )
        dms_response = make_parsed_graphql_application(
            application_id=1,
            state=dms_models.GraphQLApplicationStates.refused,
            email=user.email,
            id_piece_number="(wrong_number)",
            application_techid="XYZQVM",
        )

        dms_subscription_api.handle_dms_application(dms_response, 123)

        subscription_message = subscription_models.SubscriptionMessage.query.filter_by(userId=user.id).one()
        assert (
            subscription_message.userMessage
            == "Ton dossier déposé sur le site Démarches-Simplifiées a été refusé car le champ ‘ta pièce d'identité’ n’est pas valide."
        )

        send_dms_message_mock.assert_not_called()
        assert len(mails_testing.outbox) == 0

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(userId=user.id).one()
        assert fraud_check.status == fraud_models.FraudCheckStatus.KO
