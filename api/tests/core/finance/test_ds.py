import datetime
import random
from collections import namedtuple
from unittest.mock import patch

import pytest

from pcapi import settings
from pcapi.connectors.dms import factories as ds_factories
from pcapi.connectors.dms import models as ds_models
from pcapi.connectors.dms.models import GraphQLApplicationStates
from pcapi.connectors.dms.models import LatestDmsImport
from pcapi.connectors.dms.utils import import_ds_applications
from pcapi.core.finance.ds import MARK_WITHOUT_CONTINUATION_MOTIVATION
from pcapi.core.finance.ds import mark_without_continuation_applications
from pcapi.core.finance.ds import update_ds_applications_for_procedure
from pcapi.core.finance.factories import BankAccountFactory
from pcapi.core.finance.factories import BankAccountStatusHistoryFactory
from pcapi.core.finance.models import BankAccount
from pcapi.core.finance.models import BankAccountApplicationStatus
from pcapi.core.history import models as history_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers.factories import VenueBankAccountLinkFactory
from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.testing import assert_num_queries
from pcapi.models import db

from tests.connector_creators import demarches_simplifiees_creators as ds_creators


ActionOccurred = namedtuple("ActionOccurred", ["type", "authorUserId", "venueId", "offererId", "bankAccountId"])


@pytest.mark.usefixtures("db_session")
class ImportDSBankAccountApplicationsTest:
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.get_pro_bank_nodes_states")
    def test_only_call_from_last_update(self, mocked_get_pro_bank_nodes):
        mocked_get_pro_bank_nodes.return_value = []
        previous = ds_factories.LatestDmsImportFactory(procedureId=settings.DMS_VENUE_PROCEDURE_ID_V4)

        import_ds_applications(settings.DMS_VENUE_PROCEDURE_ID_V4, update_ds_applications_for_procedure)

        mocked_get_pro_bank_nodes.assert_called_once_with(
            procedure_number=settings.DMS_VENUE_PROCEDURE_ID_V4, since=previous.latestImportDatetime
        )

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.get_pro_bank_nodes_states")
    def test_only_process_if_previous_ended(self, mocked_get_pro_bank_nodes):
        ds_factories.LatestDmsImportFactory(
            procedureId=settings.DMS_VENUE_PROCEDURE_ID_V4,
            isProcessing=True,
        )

        import_ds_applications(settings.DMS_VENUE_PROCEDURE_ID_V4, update_ds_applications_for_procedure)

        mocked_get_pro_bank_nodes.assert_not_called()

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.get_pro_bank_nodes_states")
    def test_reset_import_if_stuck(self, mocked_get_pro_bank_nodes):
        latest_import = ds_factories.LatestDmsImportFactory(
            procedureId=settings.DMS_VENUE_PROCEDURE_ID_V4,
            isProcessing=True,
            latestImportDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=2),
        )

        import_ds_applications(settings.DMS_VENUE_PROCEDURE_ID_V4, update_ds_applications_for_procedure)

        assert not latest_import.isProcessing

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.execute_query")
    @patch("pcapi.use_cases.save_venue_bank_informations.update_demarches_simplifiees_text_annotations")
    @patch("pcapi.use_cases.save_venue_bank_informations.archive_dossier")
    def test_if_an_import_issue_an_error_it_doesnt_get_stuck_in_import_state(
        self, mock_archive_dossier, mock_update_text_annotation, mock_graphql_client
    ):
        assert not db.session.query(LatestDmsImport).all()
        siret = "85331845900049"
        siren = siret[:9]
        offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)

        mock_graphql_client.return_value = ds_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.draft.value, application_id=1
        )
        import_ds_applications(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, update_ds_applications_for_procedure)

        first_import = db.session.query(LatestDmsImport).first()
        assert first_import.isProcessing is False

        # One hour later...

        siret_2 = "96331845900050"
        siren = siret_2[:9]
        offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)

        # Mock a faulty application
        mock_graphql_client.return_value = ds_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.draft.value,
            bic="APOEBPOE:4AUIE APEAÉPSTEOBSTP4B34OBEPAÉDJT",
            application_id=2,
            siret=siret_2,
        )
        import_ds_applications(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, update_ds_applications_for_procedure)

        latest_imports = db.session.query(LatestDmsImport).order_by(LatestDmsImport.id).all()

        assert latest_imports[0].id == first_import.id
        assert latest_imports[0].isProcessing == first_import.isProcessing == False

        assert latest_imports[1].isProcessing is False


@pytest.mark.usefixtures("db_session")
class MarkWithoutApplicationTooOldApplicationsTest:
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.archive_application")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.mark_without_continuation")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.execute_query")
    def test_too_old_draft_dsv5_are_set_without_continuation(
        self, mock_graphql_client, mock_mark_without_continuation, mock_archive_application
    ):
        application_id = random.randint(1, 100000)
        status = BankAccountApplicationStatus.DRAFT
        BankAccountFactory(dsApplicationId=application_id, status=status)
        dead_line_application = (datetime.datetime.utcnow() - datetime.timedelta(days=91)).astimezone().isoformat()
        dead_line_annotation = (datetime.datetime.utcnow() - datetime.timedelta(days=6 * 31)).astimezone().isoformat()
        application_meta_data = {
            "state": ds_models.GraphQLApplicationStates.draft.value,
            "last_modification_date": dead_line_application,
            "application_id": application_id,
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
            from_draft=True,
        )
        mock_archive_application.assert_called_once_with(
            application_techid="RG9zc2llci0xNDc0MjY1NA==",
            instructeur_techid=settings.DS_MARK_WITHOUT_CONTINUATION_INSTRUCTOR_ID,
        )

        bank_account = db.session.query(BankAccount).filter_by(dsApplicationId=application_id).one()
        assert bank_account.status == BankAccountApplicationStatus.WITHOUT_CONTINUATION
        assert bank_account.dateLastStatusUpdate.timestamp() == pytest.approx(datetime.datetime.utcnow().timestamp())

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.archive_application")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.mark_without_continuation")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.execute_query")
    def test_too_old_on_going_dsv5_are_set_without_continuation(
        self, mock_graphql_client, mock_mark_without_continuation, mock_archive_application
    ):
        application_id = random.randint(1, 100000)
        status = BankAccountApplicationStatus.ON_GOING
        BankAccountFactory(dsApplicationId=application_id, status=status)
        dead_line_application = (datetime.datetime.utcnow() - datetime.timedelta(days=91)).astimezone().isoformat()
        dead_line_annotation = (datetime.datetime.utcnow() - datetime.timedelta(days=6 * 31)).astimezone().isoformat()
        application_meta_data = {
            "state": ds_models.GraphQLApplicationStates.on_going.value,
            "last_modification_date": dead_line_application,
            "application_id": application_id,
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
            from_draft=False,
        )
        mock_archive_application.assert_called_once_with(
            application_techid="RG9zc2llci0xNDc0MjY1NA==",
            instructeur_techid=settings.DS_MARK_WITHOUT_CONTINUATION_INSTRUCTOR_ID,
        )

        bank_account = db.session.query(BankAccount).filter_by(dsApplicationId=application_id).one()
        assert bank_account.status == BankAccountApplicationStatus.WITHOUT_CONTINUATION
        assert bank_account.dateLastStatusUpdate.timestamp() == pytest.approx(datetime.datetime.utcnow().timestamp())

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.archive_application")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.mark_without_continuation")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.make_on_going")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.execute_query")
    def test_dsv5_application_about_adage_is_not_set_without_continuation(
        self, mock_graphql_client, mock_make_on_going, mock_mark_without_continuation, mock_archive_application
    ):
        application_id = random.randint(1, 100000)
        status = BankAccountApplicationStatus.DRAFT
        BankAccountFactory(dsApplicationId=application_id, status=status)
        dead_line_application = (datetime.datetime.utcnow() - datetime.timedelta(days=91)).astimezone().isoformat()
        dead_line_annotation = (datetime.datetime.utcnow() - datetime.timedelta(days=6 * 31)).astimezone().isoformat()
        application_meta_data = {
            "state": ds_models.GraphQLApplicationStates.draft.value,
            "last_modification_date": dead_line_application,
            "application_id": application_id,
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

        bank_account = db.session.query(BankAccount).filter_by(dsApplicationId=application_id).one()
        assert bank_account.status == BankAccountApplicationStatus.DRAFT

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.archive_application")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.mark_without_continuation")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.make_on_going")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.execute_query")
    def test_dsv5_application_within_dead_line_annotation_is_not_set_without_continuation(
        self, mock_graphql_client, mock_make_on_going, mock_mark_without_continuation, mock_archive_application
    ):
        application_id = random.randint(1, 100000)
        status = BankAccountApplicationStatus.DRAFT
        BankAccountFactory(dsApplicationId=application_id, status=status)
        dead_line_application = (datetime.datetime.utcnow() - datetime.timedelta(days=31)).astimezone().isoformat()
        dead_line_annotation = (datetime.datetime.utcnow() - datetime.timedelta(days=2 * 31)).astimezone().isoformat()
        application_meta_data = {
            "state": ds_models.GraphQLApplicationStates.draft.value,
            "last_modification_date": dead_line_application,
            "application_id": application_id,
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

        bank_account = db.session.query(BankAccount).filter_by(dsApplicationId=application_id).one()
        assert bank_account.status == BankAccountApplicationStatus.DRAFT

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.archive_application")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.mark_without_continuation")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.make_on_going")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.execute_query")
    def test_dsv5_application_within_dead_line_application_is_not_set_without_continuation(
        self, mock_graphql_client, mock_make_on_going, mock_mark_without_continuation, mock_archive_application
    ):
        application_id = random.randint(1, 100000)
        status = BankAccountApplicationStatus.DRAFT
        BankAccountFactory(dsApplicationId=application_id, status=status)
        dead_line_application = (datetime.datetime.utcnow() - datetime.timedelta(days=29)).astimezone().isoformat()
        dead_line_annotation = (datetime.datetime.utcnow() - datetime.timedelta(days=6 * 31)).astimezone().isoformat()
        application_meta_data = {
            "state": ds_models.GraphQLApplicationStates.draft.value,
            "last_modification_date": dead_line_application,
            "application_id": application_id,
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

        bank_account = db.session.query(BankAccount).filter_by(dsApplicationId=application_id).one()
        assert bank_account.status == BankAccountApplicationStatus.DRAFT

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.archive_application")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.mark_without_continuation")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.make_on_going")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.execute_query")
    def test_too_old_dsv5_application_with_no_instructor_message_is_not_set_without_continuation(
        self, mock_graphql_client, mock_make_on_going, mock_mark_without_continuation, mock_archive_application
    ):
        application_id = random.randint(1, 100000)
        status = BankAccountApplicationStatus.DRAFT
        BankAccountFactory(dsApplicationId=application_id, status=status)
        dead_line_application = (datetime.datetime.utcnow() - datetime.timedelta(days=91)).isoformat()
        dead_line_annotation = (datetime.datetime.utcnow() - datetime.timedelta(days=6 * 31)).isoformat()
        application_meta_data = {
            "state": ds_models.GraphQLApplicationStates.draft.value,
            "last_modification_date": dead_line_application,
            "last_fields_modification": dead_line_application,
            "application_id": application_id,
            "annotations": [
                {
                    "id": "Q2hhbXAtOTE1NDg5",
                    "label": "En attente de validation de structure",
                    "stringValue": "false",
                    "checked": False,
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

        bank_account = db.session.query(BankAccount).filter_by(dsApplicationId=application_id).one()
        assert bank_account.status == BankAccountApplicationStatus.DRAFT

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.archive_application")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.mark_without_continuation")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.execute_query")
    def test_too_old_dsv5_application_waiting_for_nothing_and_unanswered_is_mark_without_continuation(
        self, mock_graphql_client, mock_mark_without_continuation, mock_archive_application
    ):
        application_id = random.randint(1, 100000)
        status = BankAccountApplicationStatus.DRAFT
        bank_account = BankAccountFactory(dsApplicationId=application_id, status=status)
        status_history = BankAccountStatusHistoryFactory(
            bankAccount=bank_account, status=status, timespan=(datetime.datetime.utcnow(),)
        )
        venue = VenueFactory(managingOfferer=bank_account.offerer)
        # This shouldn't happen but we need to be sure that if any venue is linked to a bank account
        # that is going to be marked without continuation, it's unlinked.
        # We don't want any Cashflow to be generated using non valid bank accounts
        VenueBankAccountLinkFactory(bankAccount=bank_account, venue=venue)
        fields_application = (datetime.datetime.utcnow() - datetime.timedelta(days=91)).isoformat()
        dead_line_application = (datetime.datetime.utcnow() - datetime.timedelta(days=91)).isoformat()
        dead_line_annotation = (datetime.datetime.utcnow() - datetime.timedelta(days=6 * 31)).isoformat()
        application_meta_data = {
            "state": ds_models.GraphQLApplicationStates.draft.value,
            "last_modification_date": dead_line_application,
            "last_fields_modification": fields_application,
            "application_id": application_id,
            "annotations": [
                {
                    "id": "Q2hhbXAtOTE1NDg5",
                    "label": "En attente de validation de structure",
                    "stringValue": "false",
                    "checked": False,
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
            "messages": [
                {
                    "email": "contact@demarches-simplifiees.fr",
                    "createdAt": fields_application,
                },
                {
                    # unanswered message to user
                    "email": "instructeur@passculture.app",
                    "createdAt": dead_line_application,
                },
            ],
        }
        empty_response = {"demarche": {"dossiers": {"pageInfo": {"hasNextPage": False}, "nodes": []}}}
        response = ds_creators.get_bank_info_response_procedure_v5(**application_meta_data)
        mock_graphql_client.side_effect = [empty_response, empty_response, response, empty_response]

        # Fetch the bank account
        # Update the bank account status
        # Update the current status history row
        # Create a new status history row
        # Create an ActionHistory
        # Deprecate venue-bank_account link
        with assert_num_queries(6):
            mark_without_continuation_applications()

        action_occurred = ActionOccurred(
            type=history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_DEPRECATED,
            venueId=venue.id,
            bankAccountId=bank_account.id,
            offererId=None,
            authorUserId=None,
        )

        mock_mark_without_continuation.assert_called_once_with(
            application_techid="RG9zc2llci0xNDc0MjY1NA==",
            instructeur_techid=settings.DS_MARK_WITHOUT_CONTINUATION_INSTRUCTOR_ID,
            motivation=MARK_WITHOUT_CONTINUATION_MOTIVATION,
            from_draft=True,
        )
        mock_archive_application.assert_called_once_with(
            application_techid="RG9zc2llci0xNDc0MjY1NA==",
            instructeur_techid=settings.DS_MARK_WITHOUT_CONTINUATION_INSTRUCTOR_ID,
        )

        bank_account = db.session.query(BankAccount).filter_by(dsApplicationId=application_id).one()
        assert bank_account.status == BankAccountApplicationStatus.WITHOUT_CONTINUATION
        assert bank_account.dateLastStatusUpdate.timestamp() == pytest.approx(datetime.datetime.utcnow().timestamp())
        assert bank_account.venueLinks
        assert len(bank_account.statusHistory) == 2
        for status_history in bank_account.statusHistory:
            if status_history.status == BankAccountApplicationStatus.DRAFT:
                assert status_history.timespan.upper is not None
            elif status_history.status == BankAccountApplicationStatus.WITHOUT_CONTINUATION:
                assert status_history.timespan.upper is None
            else:
                raise AssertionError("Found unexpected status")
        for link in bank_account.venueLinks:
            assert link.timespan.upper is not None

        action_history_logged = db.session.query(history_models.ActionHistory).one()
        assert action_history_logged.venueId == action_occurred.venueId
        assert action_history_logged.bankAccountId == action_occurred.bankAccountId
        assert action_history_logged.actionType == action_occurred.type
