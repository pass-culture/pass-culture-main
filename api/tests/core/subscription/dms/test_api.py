import datetime
from unittest import mock
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
import freezegun
import pytest

from pcapi.connectors.dms import api as api_dms
from pcapi.connectors.dms import models as dms_models
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
import pcapi.core.mails.testing as mails_testing
from pcapi.core.subscription import messages as subscription_messages
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.dms import api as dms_subscription_api
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.repository import repository

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
        "Nous avons bien reçu ton dossier, mais il y a une erreur dans le champ contenant ton numéro de pièce d'identité, inscrit sur le formulaire en ligne :\n"
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

    @patch("pcapi.core.subscription.dms.api._process_in_progress_application")
    @freezegun.freeze_time("2016-11-02")
    def test_multiple_call_for_same_application(self, mock_process_in_progress, db_session):
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

        mock_process_in_progress.assert_called_once()
        dms_fraud_check = next(
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type == fraud_models.FraudCheckType.DMS
        )
        assert (
            dms_fraud_check.source_data().get_latest_modification_datetime()
            == dms_response.latest_modification_datetime
        )

        mock_process_in_progress.reset_mock()
        dms_subscription_api.handle_dms_application(dms_response)

        mock_process_in_progress.assert_not_called()
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

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(user=user).one()
        message = dms_subscription_api.get_dms_subscription_message(fraud_check)
        assert message == subscription_models.SubscriptionMessage(
            user_message="Il semblerait que le champ ‘numéro de pièce d'identité’ soit invalide. Tu peux te rendre sur le site Démarches-simplifiées pour le rectifier.",
            call_to_action=subscription_messages.REDIRECT_TO_DMS_CALL_TO_ACTION,
            pop_over_icon=None,
        )

        send_dms_message_mock.assert_called_once()
        assert send_dms_message_mock.call_args[0][0] == "XYZQVM"
        assert send_dms_message_mock.call_args[0][2] == self.id_piece_number_not_accepted_message
        assert len(mails_testing.outbox) == 0

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(userId=user.id).one()
        assert fraud_check.status == fraud_models.FraudCheckStatus.STARTED
        assert fraud_check.reasonCodes == [fraud_models.FraudReasonCode.ERROR_IN_DATA]
        assert fraud_check.source_data().field_errors == [
            fraud_models.DmsFieldErrorDetails(
                key=fraud_models.DmsFieldErrorKeyEnum.id_piece_number, value="(wrong_number)"
            )
        ]

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

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(user=user).one()
        message = dms_subscription_api.get_dms_subscription_message(fraud_check)
        assert message == subscription_models.SubscriptionMessage(
            user_message="Ton dossier déposé sur le site Démarches-Simplifiées a été refusé : le champ ‘numéro de pièce d'identité’ est invalide.",
            call_to_action=None,
            pop_over_icon=subscription_models.PopOverIcon.ERROR,
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

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(user=user).one()
        message = dms_subscription_api.get_dms_subscription_message(fraud_check)
        assert message == subscription_models.SubscriptionMessage(
            user_message="Ton dossier déposé sur le site Démarches-Simplifiées a été refusé : le champ ‘numéro de pièce d'identité’ est invalide.",
            call_to_action=None,
            pop_over_icon=subscription_models.PopOverIcon.ERROR,
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

        send_dms_message_mock.assert_not_called()
        assert len(mails_testing.outbox) == 0

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(userId=user.id).one()
        assert fraud_check.status == fraud_models.FraudCheckStatus.KO

        message = dms_subscription_api.get_dms_subscription_message(fraud_check)
        assert message == subscription_models.SubscriptionMessage(
            user_message="Ton dossier déposé sur le site Démarches-Simplifiées a été refusé : le champ ‘numéro de pièce d'identité’ est invalide.",
            call_to_action=None,
            pop_over_icon=subscription_models.PopOverIcon.ERROR,
        )

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
        assert result_content.field_errors == [
            fraud_models.DmsFieldErrorDetails(key=fraud_models.DmsFieldErrorKeyEnum.first_name, value=""),
            fraud_models.DmsFieldErrorDetails(
                key=fraud_models.DmsFieldErrorKeyEnum.id_piece_number, value="(wrong_number)"
            ),
        ]

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


@pytest.mark.usefixtures("db_session")
class HandleDmsAnnotationsTest:
    @pytest.mark.parametrize(
        "field_errors,birth_date_error,expected_annotation",
        [
            ([], None, "Aucune erreur détectée. Le dossier peut être passé en instruction."),
            (
                [],
                fraud_models.DmsFieldErrorDetails(key=fraud_models.DmsFieldErrorKeyEnum.birth_date, value="2000-01-01"),
                "La date de naissance (2000-01-01) indique que le demandeur n'est pas éligible au pass Culture (doit avoir entre 15 et 18 ans). ",
            ),
            (
                [fraud_models.DmsFieldErrorDetails(key=fraud_models.DmsFieldErrorKeyEnum.first_name, value="/taylor")],
                fraud_models.DmsFieldErrorDetails(key=fraud_models.DmsFieldErrorKeyEnum.birth_date, value="2000-01-01"),
                (
                    "La date de naissance (2000-01-01) indique que le demandeur n'est pas éligible au pass Culture (doit avoir entre 15 et 18 ans). "
                    "Champs invalides: Le prénom (/taylor)"
                ),
            ),
            (
                [
                    fraud_models.DmsFieldErrorDetails(
                        key=fraud_models.DmsFieldErrorKeyEnum.first_name, value="/taylor"
                    ),
                    fraud_models.DmsFieldErrorDetails(
                        key=fraud_models.DmsFieldErrorKeyEnum.birth_date, value="trente juillet deux mille quatre"
                    ),
                ],
                None,
                ("Champs invalides: Le prénom (/taylor), La date de naissance (trente juillet deux mille quatre)"),
            ),
        ],
    )
    def test_compute_new_annotation(self, field_errors, birth_date_error, expected_annotation):
        assert dms_subscription_api._compute_new_annotation(field_errors, birth_date_error) == expected_annotation

    @mock.patch("pcapi.core.subscription.dms.api.update_demarches_simplifiees_text_annotations")
    def test_update_application_annotations(self, mock_update_annotations):
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(type=fraud_models.FraudCheckType.DMS)
        dms_subscription_api._update_application_annotations(
            "St1l3s",
            fraud_factories.DMSContentFactory(
                annotation=fraud_models.DmsAnnotation(
                    id="AnnotationId",
                    label="AN_001: Some label",
                    text="This is a test annotation",
                )
            ),
            birth_date_error=None,
            fraud_check=fraud_check,
        )
        repository.save(fraud_check)

        mock_update_annotations.assert_called_once_with(
            "St1l3s", "AnnotationId", "Aucune erreur détectée. Le dossier peut être passé en instruction."
        )
        assert fraud_check.resultContent["annotation"]["label"] == "AN_001: Some label"
        assert (
            fraud_check.resultContent["annotation"]["text"]
            == "Aucune erreur détectée. Le dossier peut être passé en instruction."
        )

    @mock.patch("pcapi.core.subscription.dms.api.update_demarches_simplifiees_text_annotations")
    def test_update_application_annotations_dont_update_if_no_modification(self, mock_update_annotations):
        dms_subscription_api._update_application_annotations(
            "St1l3s",
            fraud_factories.DMSContentFactory(
                annotation=fraud_models.DmsAnnotation(
                    id="AnnotationId",
                    label="AN_001: Some label",
                    text="Aucune erreur détectée. Le dossier peut être passé en instruction.",
                )
            ),
            birth_date_error=None,
            fraud_check=fraud_factories.BeneficiaryFraudCheckFactory(),
        )

        mock_update_annotations.assert_not_called()

    @mock.patch("pcapi.core.subscription.dms.api.update_demarches_simplifiees_text_annotations")
    def test_update_application_annotations_with_no_annotation_logs_error(self, mock_update_annotations, caplog):
        dms_content = fraud_factories.DMSContentFactory()
        dms_subscription_api._update_application_annotations(
            "St1l3s",
            dms_content,
            birth_date_error=None,
            fraud_check=fraud_factories.BeneficiaryFraudCheckFactory(),
        )

        mock_update_annotations.assert_not_called()
        assert f"[DMS] No annotation defined for procedure {dms_content.procedure_number}" in caplog.text


@pytest.mark.usefixtures("db_session")
class DmsSubscriptionMessageTest:
    user_email = "déesse@dms.com"

    @patch("pcapi.core.subscription.dms.api.dms_connector_api.DMSGraphQLClient.send_user_message")
    def test_started_no_error(self, mock_send_user_message):
        users_factories.UserFactory(email=self.user_email)
        dms_response = make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.draft,
            email=self.user_email,
            birth_date=datetime.datetime.utcnow() - relativedelta(years=18),
        )
        fraud_check = dms_subscription_api.handle_dms_application(dms_response)

        message = dms_subscription_api.get_dms_subscription_message(fraud_check)

        assert message == subscription_models.SubscriptionMessage(
            user_message=f"Nous avons bien reçu ton dossier le {fraud_check.dateCreated.date():%d/%m/%Y}. Rends-toi sur la messagerie du site Démarches-Simplifiées pour être informé en temps réel.",
            call_to_action=None,
            pop_over_icon=subscription_models.PopOverIcon.FILE,
        )

    @patch("pcapi.core.subscription.dms.api.dms_connector_api.DMSGraphQLClient.send_user_message")
    def test_started_error_wrong_birth_date(self, mock_send_user_message):
        users_factories.UserFactory(email=self.user_email)
        wrong_birth_date_application = make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.draft,
            email=self.user_email,
            birth_date=datetime.datetime.utcnow(),
        )
        fraud_check = dms_subscription_api.handle_dms_application(wrong_birth_date_application)

        message = dms_subscription_api.get_dms_subscription_message(fraud_check)

        assert message == subscription_models.SubscriptionMessage(
            user_message="Il semblerait que le champ ‘date de naissance’ soit invalide. Tu peux te rendre sur le site Démarches-simplifiées pour le rectifier.",
            call_to_action=subscription_messages.REDIRECT_TO_DMS_CALL_TO_ACTION,
            pop_over_icon=None,
        )

    @patch("pcapi.core.subscription.dms.api.dms_connector_api.DMSGraphQLClient.send_user_message")
    def test_started_error_wrong_birth_date_and_id_piece_number(self, mock_send_user_message):
        users_factories.UserFactory(email=self.user_email)
        wrong_birth_date_application = make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.draft,
            email=self.user_email,
            birth_date=datetime.datetime.utcnow(),
            id_piece_number="r2d2",
        )
        fraud_check = dms_subscription_api.handle_dms_application(wrong_birth_date_application)

        message = dms_subscription_api.get_dms_subscription_message(fraud_check)

        assert message == subscription_models.SubscriptionMessage(
            user_message="Il semblerait que les champs ‘numéro de pièce d'identité, date de naissance’ soient invalides. Tu peux te rendre sur le site Démarches-simplifiées pour les rectifier.",
            call_to_action=subscription_messages.REDIRECT_TO_DMS_CALL_TO_ACTION,
            pop_over_icon=None,
        )

    @patch("pcapi.core.subscription.dms.api.dms_connector_api.DMSGraphQLClient.send_user_message")
    def test_pending_error_not_eligible_date(self, mock_send_user_message):
        users_factories.UserFactory(email=self.user_email)
        not_eligible_application = make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.on_going,
            email=self.user_email,
            birth_date=datetime.datetime.utcnow() - relativedelta(years=20),
            construction_datetime=datetime.datetime.utcnow(),
        )
        fraud_check = dms_subscription_api.handle_dms_application(not_eligible_application)

        message = dms_subscription_api.get_dms_subscription_message(fraud_check)

        assert message == subscription_models.SubscriptionMessage(
            user_message="Ton dossier déposé sur le site Démarches-Simplifiées a été refusé : la date de naissance indique que tu n'es pas éligible. Tu dois avoir entre 15 et 18 ans.",
            call_to_action=None,
            pop_over_icon=subscription_models.PopOverIcon.ERROR,
        )

    @patch("pcapi.core.subscription.dms.api.dms_connector_api.DMSGraphQLClient.send_user_message")
    def test_ko_not_eligible(self, mock_send_user_message):
        users_factories.UserFactory(email=self.user_email)
        not_eligible_application = make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.accepted,
            email=self.user_email,
            birth_date=datetime.datetime.utcnow() - relativedelta(years=20),
            construction_datetime=datetime.datetime.utcnow(),
        )
        fraud_check = dms_subscription_api.handle_dms_application(not_eligible_application)

        message = dms_subscription_api.get_dms_subscription_message(fraud_check)

        assert message == subscription_models.SubscriptionMessage(
            user_message="Ton dossier déposé sur le site Démarches-Simplifiées a été refusé : la date de naissance indique que tu n'es pas éligible. Tu dois avoir entre 15 et 18 ans.",
            call_to_action=None,
            pop_over_icon=subscription_models.PopOverIcon.ERROR,
        )

    @patch("pcapi.core.subscription.dms.api.dms_connector_api.DMSGraphQLClient.send_user_message")
    def test_accepted(self, mock_send_user_message):
        users_factories.UserFactory(email=self.user_email)
        application_ok = make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.accepted,
            email=self.user_email,
            birth_date=datetime.datetime.utcnow() - relativedelta(years=18),
        )
        fraud_check = dms_subscription_api.handle_dms_application(application_ok)

        assert dms_subscription_api.get_dms_subscription_message(fraud_check) is None

    @patch("pcapi.core.subscription.dms.api.dms_connector_api.DMSGraphQLClient.send_user_message")
    def test_refused_by_operator(self, mock_send_user_message):
        users_factories.UserFactory(email=self.user_email)
        refused_application = make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.refused,
            email=self.user_email,
            birth_date=datetime.datetime.utcnow() - relativedelta(years=18),
        )
        fraud_check = dms_subscription_api.handle_dms_application(refused_application)

        message = dms_subscription_api.get_dms_subscription_message(fraud_check)

        assert message == subscription_models.SubscriptionMessage(
            user_message="Ton dossier déposé sur le site Démarches-Simplifiées a été refusé : tu n'es malheureusement pas éligible au pass Culture.",
            call_to_action=None,
            pop_over_icon=subscription_models.PopOverIcon.ERROR,
        )

    @patch("pcapi.core.subscription.dms.api.dms_connector_api.DMSGraphQLClient.send_user_message")
    def test_duplicate(self, mock_send_user_message):
        first_name = "Jean-Michel"
        last_name = "Doublon"
        birth_date = datetime.datetime.utcnow() - relativedelta(years=18, days=1)
        users_factories.BeneficiaryGrant18Factory(firstName=first_name, lastName=last_name, dateOfBirth=birth_date)

        applicant = users_factories.UserFactory(email=self.user_email)
        duplicate_application = make_parsed_graphql_application(
            application_number=1,
            state=dms_models.GraphQLApplicationStates.accepted,
            email=self.user_email,
            birth_date=birth_date,
            first_name=first_name,
            last_name=last_name,
        )
        fraud_check = dms_subscription_api.handle_dms_application(duplicate_application)

        message = dms_subscription_api.get_dms_subscription_message(fraud_check)

        assert message == subscription_models.SubscriptionMessage(
            user_message="Ton dossier déposé sur le site Démarches-Simplifiées a été refusé : il y a déjà un compte à ton nom sur le pass Culture. Tu peux contacter le support pour plus d'informations.",
            call_to_action=subscription_models.CallToActionMessage(
                title="Contacter le support",
                link=f"mailto:support@example.com?subject=%23{applicant.id}+-+Mon+inscription+sur+le+pass+Culture+est+bloqu%C3%A9e",
                icon=subscription_models.CallToActionIcon.EMAIL,
            ),
            pop_over_icon=None,
        )

    def test_ko_no_info(self):
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.DMS,
            resultContent=None,
            status=fraud_models.FraudCheckStatus.KO,
            reasonCodes=None,
        )

        message = dms_subscription_api.get_dms_subscription_message(fraud_check)

        assert message == subscription_models.SubscriptionMessage(
            user_message="Ton dossier déposé sur le site Démarches-Simplifiées a été refusé.",
            call_to_action=None,
            pop_over_icon=subscription_models.PopOverIcon.ERROR,
        )
