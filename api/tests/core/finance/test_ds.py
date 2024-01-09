import datetime
from unittest.mock import patch

import pytest

from pcapi import settings
from pcapi.connectors.dms import factories as ds_factories
from pcapi.connectors.dms import models as ds_models
from pcapi.core.finance.ds import MARK_WITHOUT_CONTINUATION_MOTIVATION
from pcapi.core.finance.ds import import_ds_bank_information_applications
from pcapi.core.finance.ds import mark_without_continuation_applications
from pcapi.core.finance.models import BankInformationStatus

from tests.connector_creators import demarches_simplifiees_creators as ds_creators


@pytest.mark.usefixtures("db_session")
class ImportDSBankInformationApplicationsTest:
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.get_pro_bank_nodes_states")
    @patch("pcapi.use_cases.save_venue_bank_informations.SaveVenueBankInformationsV4.execute")
    def test_import_empty_db(self, mocked_save_venue_bank_informations_execute, mocked_get_pro_bank_nodes):
        mocked_get_pro_bank_nodes.return_value = [
            ds_creators.get_bank_info_response_procedure_v4(),
            ds_creators.get_bank_info_response_procedure_v4(
                dms_token="987654321fedcba", dossier_id="AbLQmfezdf", application_id=10
            ),
        ]

        import_ds_bank_information_applications(procedure_number=settings.DMS_VENUE_PROCEDURE_ID_V4)

        assert mocked_save_venue_bank_informations_execute.call_count == 2
        application_detail_first_call_arg = mocked_save_venue_bank_informations_execute.mock_calls[0].kwargs[
            "application_details"
        ]
        assert application_detail_first_call_arg.status == BankInformationStatus.ACCEPTED
        assert application_detail_first_call_arg.application_id == 9
        assert application_detail_first_call_arg.modification_date == datetime.datetime(2020, 1, 3)
        assert application_detail_first_call_arg.iban == "FR7630007000111234567890144"
        assert application_detail_first_call_arg.bic == "SOGEFRPP"
        assert application_detail_first_call_arg.dms_token == "1234567890abcdef"
        assert application_detail_first_call_arg.dossier_id == "Q2zzbXAtNzgyODAw"

        application_detail_second_call_arg = mocked_save_venue_bank_informations_execute.mock_calls[1].kwargs[
            "application_details"
        ]
        assert application_detail_second_call_arg.status == BankInformationStatus.ACCEPTED
        assert application_detail_second_call_arg.application_id == 10
        assert application_detail_second_call_arg.modification_date == datetime.datetime(2020, 1, 3)
        assert application_detail_second_call_arg.iban == "FR7630007000111234567890144"
        assert application_detail_second_call_arg.bic == "SOGEFRPP"
        assert application_detail_second_call_arg.dms_token == "987654321fedcba"
        assert application_detail_second_call_arg.dossier_id == "AbLQmfezdf"

        latest_import = ds_models.LatestDmsImport.query.one()
        assert latest_import.procedureId == int(settings.DMS_VENUE_PROCEDURE_ID_V4)
        assert latest_import.latestImportDatetime
        assert not latest_import.isProcessing
        assert latest_import.processedApplications == [9, 10]

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.get_pro_bank_nodes_states")
    def test_only_call_from_last_update(self, mocked_get_pro_bank_nodes):
        mocked_get_pro_bank_nodes.return_value = []
        previous = ds_factories.LatestDmsImportFactory(procedureId=settings.DMS_VENUE_PROCEDURE_ID_V4)

        import_ds_bank_information_applications(procedure_number=settings.DMS_VENUE_PROCEDURE_ID_V4)

        mocked_get_pro_bank_nodes.assert_called_once_with(
            procedure_number=settings.DMS_VENUE_PROCEDURE_ID_V4, since=previous.latestImportDatetime
        )

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.get_pro_bank_nodes_states")
    def test_only_process_if_previous_ended(self, mocked_get_pro_bank_nodes):
        ds_factories.LatestDmsImportFactory(
            procedureId=settings.DMS_VENUE_PROCEDURE_ID_V4,
            isProcessing=True,
        )

        import_ds_bank_information_applications(procedure_number=settings.DMS_VENUE_PROCEDURE_ID_V4)

        mocked_get_pro_bank_nodes.assert_not_called()

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.get_pro_bank_nodes_states")
    def test_reset_import_if_stuck(self, mocked_get_pro_bank_nodes):
        latest_import = ds_factories.LatestDmsImportFactory(
            procedureId=settings.DMS_VENUE_PROCEDURE_ID_V4,
            isProcessing=True,
            latestImportDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=2),
        )

        import_ds_bank_information_applications(procedure_number=settings.DMS_VENUE_PROCEDURE_ID_V4)

        assert not latest_import.isProcessing


@pytest.mark.usefixtures("db_session")
class MarkWithoutApplicationTooOldApplicationsTest:
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.archive_application")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.mark_without_continuation")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.make_on_going")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.execute_query")
    def test_dsv4_within_application_deadline_is_not_set_without_continuantion(
        self, mock_graphql_client, mock_make_on_going, mock_mark_without_continuation, mock_archive_application
    ):
        dead_line_application = (datetime.datetime.utcnow() - datetime.timedelta(days=89)).isoformat()
        dead_line_annotation = (datetime.datetime.utcnow() - datetime.timedelta(days=6 * 31)).isoformat()
        application_meta_data = {
            "state": ds_models.GraphQLApplicationStates.draft.value,
            "last_modification_date": dead_line_application,
            "annotations": [
                {
                    "id": "Q2hhbXAtOTE1NDg5",
                    "label": "Erreur traitement pass Culture",
                    "stringValue": "Une erreur de traitement",
                    "checked": True,
                    "updatedAt": dead_line_annotation,
                },
            ],
        }
        empty_response = {"demarche": {"dossiers": {"pageInfo": {"hasNextPage": False}, "nodes": []}}}
        response = ds_creators.get_bank_info_response_procedure_v4_as_batch(**application_meta_data)
        mock_graphql_client.side_effect = [empty_response, empty_response, response, empty_response]

        mark_without_continuation_applications()

        mock_make_on_going.assert_not_called()
        mock_mark_without_continuation.assert_not_called()
        mock_archive_application.assert_not_called()

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.archive_application")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.mark_without_continuation")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.make_on_going")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.execute_query")
    def test_too_old_draft_dsv4_are_set_without_continuation(
        self, mock_graphql_client, mock_make_on_going, mock_mark_without_continuation, mock_archive_application
    ):
        dead_line_application = (datetime.datetime.utcnow() - datetime.timedelta(days=91)).isoformat()
        dead_line_annotation = (datetime.datetime.utcnow() - datetime.timedelta(days=6 * 31)).isoformat()
        application_meta_data = {
            "state": ds_models.GraphQLApplicationStates.draft.value,
            "last_modification_date": dead_line_application,
            "annotations": [
                {
                    "id": "Q2hhbXAtOTE1NDg5",
                    "label": "Erreur traitement pass Culture",
                    "stringValue": "Une erreur de traitement",
                    "checked": True,
                    "updatedAt": dead_line_annotation,
                },
            ],
        }
        empty_response = {"demarche": {"dossiers": {"pageInfo": {"hasNextPage": False}, "nodes": []}}}
        response = ds_creators.get_bank_info_response_procedure_v4_as_batch(**application_meta_data)
        mock_graphql_client.side_effect = [empty_response, empty_response, response, empty_response]

        mark_without_continuation_applications()

        mock_make_on_going.assert_called_once_with(
            application_techid="Q2zzbXAtNzgyODAw",
            instructeur_techid=settings.DS_MARK_WITHOUT_CONTINUATION_INSTRUCTOR_ID,
        )
        mock_mark_without_continuation.assert_called_once_with(
            application_techid="Q2zzbXAtNzgyODAw",
            instructeur_techid=settings.DS_MARK_WITHOUT_CONTINUATION_INSTRUCTOR_ID,
            motivation=MARK_WITHOUT_CONTINUATION_MOTIVATION,
        )
        mock_archive_application.assert_called_once_with(
            application_techid="Q2zzbXAtNzgyODAw",
            instructeur_techid=settings.DS_MARK_WITHOUT_CONTINUATION_INSTRUCTOR_ID,
        )

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.archive_application")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.mark_without_continuation")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.make_on_going")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.execute_query")
    def test_too_old_on_going_dsv4_are_set_without_continuation(
        self, mock_graphql_client, mock_make_on_going, mock_mark_without_continuation, mock_archive_application
    ):
        dead_line_application = (datetime.datetime.utcnow() - datetime.timedelta(days=91)).astimezone().isoformat()
        dead_line_annotation = (datetime.datetime.utcnow() - datetime.timedelta(days=6 * 31)).astimezone().isoformat()
        application_meta_data = {
            "state": ds_models.GraphQLApplicationStates.on_going.value,
            "last_modification_date": dead_line_application,
            "annotations": [
                {
                    "id": "Q2hhbXAtOTE1NDg5",
                    "label": "Erreur traitement pass Culture",
                    "stringValue": "Une erreur de traitement",
                    "checked": True,
                    "updatedAt": dead_line_annotation,
                },
            ],
        }
        empty_response = {"demarche": {"dossiers": {"pageInfo": {"hasNextPage": False}, "nodes": []}}}
        response = ds_creators.get_bank_info_response_procedure_v4_as_batch(**application_meta_data)
        mock_graphql_client.side_effect = [empty_response, empty_response, response, empty_response]

        mark_without_continuation_applications()

        mock_mark_without_continuation.assert_called_once_with(
            application_techid="Q2zzbXAtNzgyODAw",
            instructeur_techid=settings.DS_MARK_WITHOUT_CONTINUATION_INSTRUCTOR_ID,
            motivation=MARK_WITHOUT_CONTINUATION_MOTIVATION,
        )
        mock_archive_application.assert_called_once_with(
            application_techid="Q2zzbXAtNzgyODAw",
            instructeur_techid=settings.DS_MARK_WITHOUT_CONTINUATION_INSTRUCTOR_ID,
        )

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.archive_application")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.mark_without_continuation")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.make_on_going")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.execute_query")
    def test_too_old_dsv4_are_set_without_continuation_if_about_rct_after_annotation_deadline(
        self, mock_graphql_client, mock_make_on_going, mock_mark_without_continuation, mock_archive_application
    ):
        dead_line_application = (datetime.datetime.utcnow() - datetime.timedelta(days=91)).astimezone().isoformat()
        dead_line_annotation = (datetime.datetime.utcnow() - datetime.timedelta(days=6 * 31)).astimezone().isoformat()
        application_meta_data = {
            "state": ds_models.GraphQLApplicationStates.draft.value,
            "last_modification_date": dead_line_application,
            "annotations": [
                {
                    "id": "Q2hhbXAtOTE1NDg5",
                    "label": "Erreur traitement pass Culture",
                    "stringValue": "Une erreur de traitement en rapport avec RCT",
                    "checked": True,
                    "updatedAt": dead_line_annotation,
                },
            ],
        }
        empty_response = {"demarche": {"dossiers": {"pageInfo": {"hasNextPage": False}, "nodes": []}}}
        response = ds_creators.get_bank_info_response_procedure_v4_as_batch(**application_meta_data)
        mock_graphql_client.side_effect = [empty_response, empty_response, response, empty_response]

        mark_without_continuation_applications()

        mock_make_on_going.assert_called_once_with(
            application_techid="Q2zzbXAtNzgyODAw",
            instructeur_techid=settings.DS_MARK_WITHOUT_CONTINUATION_INSTRUCTOR_ID,
        )
        mock_mark_without_continuation.assert_called_once_with(
            application_techid="Q2zzbXAtNzgyODAw",
            instructeur_techid=settings.DS_MARK_WITHOUT_CONTINUATION_INSTRUCTOR_ID,
            motivation=MARK_WITHOUT_CONTINUATION_MOTIVATION,
        )
        mock_archive_application.assert_called_once_with(
            application_techid="Q2zzbXAtNzgyODAw",
            instructeur_techid=settings.DS_MARK_WITHOUT_CONTINUATION_INSTRUCTOR_ID,
        )

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.archive_application")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.mark_without_continuation")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.make_on_going")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.execute_query")
    def test_too_old_dsv4_is_not_set_without_continuation_if_about_adage(
        self, mock_graphql_client, mock_make_on_going, mock_mark_without_continuation, mock_archive_application
    ):
        dead_line_application = (datetime.datetime.utcnow() - datetime.timedelta(days=91)).astimezone().isoformat()
        dead_line_annotation = (datetime.datetime.utcnow() - datetime.timedelta(days=6 * 31)).astimezone().isoformat()
        application_meta_data = {
            "state": ds_models.GraphQLApplicationStates.draft.value,
            "last_modification_date": dead_line_application,
            "annotations": [
                {
                    "id": "Q2hhbXAtOTE1NDg5",
                    "label": "Erreur traitement pass Culture",
                    "stringValue": "Une erreur de traitement en rapport avec AdAgE",
                    "checked": True,
                    "updatedAt": dead_line_annotation,
                },
            ],
        }
        empty_response = {"demarche": {"dossiers": {"pageInfo": {"hasNextPage": False}, "nodes": []}}}
        response = ds_creators.get_bank_info_response_procedure_v4_as_batch(**application_meta_data)
        mock_graphql_client.side_effect = [response, empty_response, empty_response, empty_response]

        mark_without_continuation_applications()

        mock_make_on_going.assert_not_called()
        mock_mark_without_continuation.assert_not_called()
        mock_archive_application.assert_not_called()

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.archive_application")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.mark_without_continuation")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.make_on_going")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.execute_query")
    def test_too_old_dsv4_is_not_set_without_continuation_if_about_rct_within_dead_line_annotation(
        self, mock_graphql_client, mock_make_on_going, mock_mark_without_continuation, mock_archive_application
    ):
        dead_line_application = (datetime.datetime.utcnow() - datetime.timedelta(days=91)).astimezone().isoformat()
        dead_line_annotation = (datetime.datetime.utcnow() - datetime.timedelta(days=5 * 31)).astimezone().isoformat()
        application_meta_data = {
            "state": ds_models.GraphQLApplicationStates.draft.value,
            "last_modification_date": dead_line_application,
            "annotations": [
                {
                    "id": "Q2hhbXAtOTE1NDg5",
                    "label": "Erreur traitement pass Culture",
                    "stringValue": "Une erreur de traitement en rapport avec RCT",
                    "checked": True,
                    "updatedAt": dead_line_annotation,
                },
            ],
        }
        empty_response = {"demarche": {"dossiers": {"pageInfo": {"hasNextPage": False}, "nodes": []}}}
        response = ds_creators.get_bank_info_response_procedure_v4_as_batch(**application_meta_data)
        mock_graphql_client.side_effect = [response, empty_response, empty_response, empty_response]

        mark_without_continuation_applications()

        mock_make_on_going.assert_not_called()
        mock_mark_without_continuation.assert_not_called()
        mock_archive_application.assert_not_called()

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.archive_application")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.mark_without_continuation")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.make_on_going")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.execute_query")
    def test_too_old_draft_dsv5_are_set_without_continuation(
        self, mock_graphql_client, mock_make_on_going, mock_mark_without_continuation, mock_archive_application
    ):
        dead_line_application = (datetime.datetime.utcnow() - datetime.timedelta(days=91)).astimezone().isoformat()
        dead_line_annotation = (datetime.datetime.utcnow() - datetime.timedelta(days=6 * 31)).astimezone().isoformat()
        application_meta_data = {
            "state": ds_models.GraphQLApplicationStates.draft.value,
            "last_modification_date": dead_line_application,
            "annotations": [
                {
                    "id": "Q2hhbXAtOTE1NDg5",
                    "label": "En attente de validation de structure",
                    "stringValue": "true",
                    "checked": True,
                    "updatedAt": dead_line_annotation,
                },
                {
                    "id": "Q2hhbXAtMjc2NDk5MQ==",
                    "label": "En attente de validation ADAGE",
                    "stringValue": "false",
                    "updatedAt": dead_line_annotation,
                    "checked": False,
                },
            ],
        }
        empty_response = {"demarche": {"dossiers": {"pageInfo": {"hasNextPage": False}, "nodes": []}}}
        response = ds_creators.get_bank_info_response_procedure_v5(**application_meta_data)
        mock_graphql_client.side_effect = [empty_response, empty_response, response, empty_response]

        mark_without_continuation_applications()

        mock_make_on_going.assert_called_once_with(
            application_techid="RG9zc2llci0xNDc0MjY1NA==",
            instructeur_techid=settings.DS_MARK_WITHOUT_CONTINUATION_INSTRUCTOR_ID,
        )
        mock_mark_without_continuation.assert_called_once_with(
            application_techid="RG9zc2llci0xNDc0MjY1NA==",
            instructeur_techid=settings.DS_MARK_WITHOUT_CONTINUATION_INSTRUCTOR_ID,
            motivation=MARK_WITHOUT_CONTINUATION_MOTIVATION,
        )
        mock_archive_application.assert_called_once_with(
            application_techid="RG9zc2llci0xNDc0MjY1NA==",
            instructeur_techid=settings.DS_MARK_WITHOUT_CONTINUATION_INSTRUCTOR_ID,
        )

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.archive_application")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.mark_without_continuation")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.make_on_going")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.execute_query")
    def test_too_old_on_going_dsv5_are_set_without_continuation(
        self, mock_graphql_client, mock_make_on_going, mock_mark_without_continuation, mock_archive_application
    ):
        dead_line_application = (datetime.datetime.utcnow() - datetime.timedelta(days=91)).astimezone().isoformat()
        dead_line_annotation = (datetime.datetime.utcnow() - datetime.timedelta(days=6 * 31)).astimezone().isoformat()
        application_meta_data = {
            "state": ds_models.GraphQLApplicationStates.on_going.value,
            "last_modification_date": dead_line_application,
            "annotations": [
                {
                    "id": "Q2hhbXAtOTE1NDg5",
                    "label": "En attente de validation de structure",
                    "stringValue": "true",
                    "checked": True,
                    "updatedAt": dead_line_annotation,
                },
                {
                    "id": "Q2hhbXAtMjc2NDk5MQ==",
                    "label": "En attente de validation ADAGE",
                    "stringValue": "false",
                    "updatedAt": dead_line_annotation,
                    "checked": False,
                },
            ],
        }
        empty_response = {"demarche": {"dossiers": {"pageInfo": {"hasNextPage": False}, "nodes": []}}}
        response = ds_creators.get_bank_info_response_procedure_v5(**application_meta_data)
        mock_graphql_client.side_effect = [empty_response, empty_response, response, empty_response]

        mark_without_continuation_applications()

        mock_mark_without_continuation.assert_called_once_with(
            application_techid="RG9zc2llci0xNDc0MjY1NA==",
            instructeur_techid=settings.DS_MARK_WITHOUT_CONTINUATION_INSTRUCTOR_ID,
            motivation=MARK_WITHOUT_CONTINUATION_MOTIVATION,
        )
        mock_archive_application.assert_called_once_with(
            application_techid="RG9zc2llci0xNDc0MjY1NA==",
            instructeur_techid=settings.DS_MARK_WITHOUT_CONTINUATION_INSTRUCTOR_ID,
        )

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.archive_application")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.mark_without_continuation")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.make_on_going")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.execute_query")
    def test_dsv5_application_about_adage_is_not_set_without_continuation(
        self, mock_graphql_client, mock_make_on_going, mock_mark_without_continuation, mock_archive_application
    ):
        dead_line_application = (datetime.datetime.utcnow() - datetime.timedelta(days=91)).astimezone().isoformat()
        dead_line_annotation = (datetime.datetime.utcnow() - datetime.timedelta(days=6 * 31)).astimezone().isoformat()
        application_meta_data = {
            "state": ds_models.GraphQLApplicationStates.draft.value,
            "last_modification_date": dead_line_application,
            "annotations": [
                {
                    "id": "Q2hhbXAtOTE1NDg5",
                    "label": "En attente de validation de structure",
                    "stringValue": "true",
                    "checked": True,
                    "updatedAt": dead_line_annotation,
                },
                {
                    "id": "Q2hhbXAtMjc2NDk5MQ==",
                    "label": "En attente de validation ADAGE",
                    "stringValue": "true",
                    "updatedAt": dead_line_annotation,
                    "checked": True,
                },
            ],
        }
        empty_response = {"demarche": {"dossiers": {"pageInfo": {"hasNextPage": False}, "nodes": []}}}
        response = ds_creators.get_bank_info_response_procedure_v5(**application_meta_data)
        mock_graphql_client.side_effect = [empty_response, empty_response, response, empty_response]

        mark_without_continuation_applications()

        mock_make_on_going.assert_not_called()
        mock_mark_without_continuation.assert_not_called()
        mock_archive_application.assert_not_called()

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.archive_application")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.mark_without_continuation")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.make_on_going")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.execute_query")
    def test_dsv5_application_within_dead_line_annotation_is_not_set_without_continuation(
        self, mock_graphql_client, mock_make_on_going, mock_mark_without_continuation, mock_archive_application
    ):
        dead_line_application = (datetime.datetime.utcnow() - datetime.timedelta(days=91)).astimezone().isoformat()
        dead_line_annotation = (datetime.datetime.utcnow() - datetime.timedelta(days=5 * 31)).astimezone().isoformat()
        application_meta_data = {
            "state": ds_models.GraphQLApplicationStates.draft.value,
            "last_modification_date": dead_line_application,
            "annotations": [
                {
                    "id": "Q2hhbXAtOTE1NDg5",
                    "label": "En attente de validation de structure",
                    "stringValue": "true",
                    "checked": True,
                    "updatedAt": dead_line_annotation,
                },
                {
                    "id": "Q2hhbXAtMjc2NDk5MQ==",
                    "label": "En attente de validation ADAGE",
                    "stringValue": "false",
                    "updatedAt": dead_line_annotation,
                    "checked": False,
                },
            ],
        }
        empty_response = {"demarche": {"dossiers": {"pageInfo": {"hasNextPage": False}, "nodes": []}}}
        response = ds_creators.get_bank_info_response_procedure_v5(**application_meta_data)
        mock_graphql_client.side_effect = [empty_response, empty_response, response, empty_response]

        mark_without_continuation_applications()

        mock_make_on_going.assert_not_called()
        mock_mark_without_continuation.assert_not_called()
        mock_archive_application.assert_not_called()

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.archive_application")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.mark_without_continuation")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.make_on_going")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.execute_query")
    def test_dsv5_application_within_dead_line_application_is_not_set_without_continuation(
        self, mock_graphql_client, mock_make_on_going, mock_mark_without_continuation, mock_archive_application
    ):
        dead_line_application = (datetime.datetime.utcnow() - datetime.timedelta(days=89)).astimezone().isoformat()
        dead_line_annotation = (datetime.datetime.utcnow() - datetime.timedelta(days=6 * 31)).astimezone().isoformat()
        application_meta_data = {
            "state": ds_models.GraphQLApplicationStates.draft.value,
            "last_modification_date": dead_line_application,
            "annotations": [
                {
                    "id": "Q2hhbXAtOTE1NDg5",
                    "label": "En attente de validation de structure",
                    "stringValue": "true",
                    "checked": True,
                    "updatedAt": dead_line_annotation,
                },
                {
                    "id": "Q2hhbXAtMjc2NDk5MQ==",
                    "label": "En attente de validation ADAGE",
                    "stringValue": "false",
                    "updatedAt": dead_line_annotation,
                    "checked": False,
                },
            ],
        }
        empty_response = {"demarche": {"dossiers": {"pageInfo": {"hasNextPage": False}, "nodes": []}}}
        response = ds_creators.get_bank_info_response_procedure_v5(**application_meta_data)
        mock_graphql_client.side_effect = [empty_response, empty_response, response, empty_response]

        mark_without_continuation_applications()

        mock_make_on_going.assert_not_called()
        mock_mark_without_continuation.assert_not_called()
        mock_archive_application.assert_not_called()
