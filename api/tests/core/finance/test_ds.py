import datetime
import random
from base64 import b64encode
from collections import namedtuple
from unittest.mock import patch

import pytest
import schwifty

import pcapi.core.finance.factories as finance_factories
import pcapi.core.mails.testing as mails_testing
import pcapi.core.offerers.factories as offerers_factories
from pcapi import settings
from pcapi.connectors.dms import factories as ds_factories
from pcapi.connectors.dms import models as ds_models
from pcapi.connectors.dms.models import GraphQLApplicationStates
from pcapi.connectors.dms.models import LatestDmsImport
from pcapi.connectors.dms.utils import import_ds_applications
from pcapi.core.finance import models as finance_models
from pcapi.core.finance.ds import MARK_WITHOUT_CONTINUATION_MOTIVATION
from pcapi.core.finance.ds import mark_without_continuation_applications
from pcapi.core.finance.ds import update_ds_applications_for_procedure
from pcapi.core.finance.factories import BankAccountFactory
from pcapi.core.finance.factories import BankAccountStatusHistoryFactory
from pcapi.core.finance.models import BankAccount
from pcapi.core.finance.models import BankAccountApplicationStatus
from pcapi.core.history import models as history_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers.factories import VenueBankAccountLinkFactory
from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.offers import factories as offers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.models import db
from pcapi.utils import date as date_utils
from pcapi.utils import siren as siren_utils

import tests.connector_creators.demarches_simplifiees_creators as dms_creators
from tests.connector_creators import demarches_simplifiees_creators as ds_creators


ActionOccurred = namedtuple("ActionOccurred", ["type", "authorUserId", "venueId", "offererId", "bankAccountId"])


@pytest.mark.usefixtures("db_session")
class ImportDSBankAccountApplicationsTest:
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.get_pro_bank_nodes_states")
    def test_only_call_from_last_update(self, mocked_get_pro_bank_nodes):
        mocked_get_pro_bank_nodes.return_value = []
        previous = ds_factories.LatestDmsImportFactory(procedureId=settings.DS_BANK_ACCOUNT_PROCEDURE_ID)

        import_ds_applications(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, update_ds_applications_for_procedure)

        mocked_get_pro_bank_nodes.assert_called_once_with(
            procedure_number=settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=previous.latestImportDatetime
        )

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.get_pro_bank_nodes_states")
    def test_only_process_if_previous_ended(self, mocked_get_pro_bank_nodes):
        ds_factories.LatestDmsImportFactory(
            procedureId=settings.DS_BANK_ACCOUNT_PROCEDURE_ID,
            isProcessing=True,
        )

        import_ds_applications(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, update_ds_applications_for_procedure)

        mocked_get_pro_bank_nodes.assert_not_called()

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.get_pro_bank_nodes_states")
    def test_reset_import_if_stuck(self, mocked_get_pro_bank_nodes):
        latest_import = ds_factories.LatestDmsImportFactory(
            procedureId=settings.DS_BANK_ACCOUNT_PROCEDURE_ID,
            isProcessing=True,
            latestImportDatetime=date_utils.get_naive_utc_now() - datetime.timedelta(days=2),
        )

        import_ds_applications(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, update_ds_applications_for_procedure)

        assert not latest_import.isProcessing

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.execute_query")
    @patch("pcapi.connectors.dms.api.update_demarches_simplifiees_text_annotations")
    @patch("pcapi.core.finance.ds.archive_dossier")
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
            iban="APOEBPOE:4AUIE APEAÉPSTEOBSTP4B34OBEPAÉDJT",
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
        dead_line_application = (date_utils.get_naive_utc_now() - datetime.timedelta(days=91)).astimezone().isoformat()
        dead_line_annotation = (
            (date_utils.get_naive_utc_now() - datetime.timedelta(days=6 * 31)).astimezone().isoformat()
        )
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
        assert bank_account.statusHistory[0].timespan.lower.timestamp() == pytest.approx(
            date_utils.get_naive_utc_now().timestamp()
        )

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.archive_application")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.mark_without_continuation")
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.execute_query")
    def test_too_old_on_going_dsv5_are_set_without_continuation(
        self, mock_graphql_client, mock_mark_without_continuation, mock_archive_application
    ):
        application_id = random.randint(1, 100000)
        status = BankAccountApplicationStatus.ON_GOING
        BankAccountFactory(dsApplicationId=application_id, status=status)
        dead_line_application = (date_utils.get_naive_utc_now() - datetime.timedelta(days=91)).astimezone().isoformat()
        dead_line_annotation = (
            (date_utils.get_naive_utc_now() - datetime.timedelta(days=6 * 31)).astimezone().isoformat()
        )
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
        assert bank_account.statusHistory[0].timespan.lower.timestamp() == pytest.approx(
            date_utils.get_naive_utc_now().timestamp()
        )

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
        dead_line_application = (date_utils.get_naive_utc_now() - datetime.timedelta(days=91)).astimezone().isoformat()
        dead_line_annotation = (
            (date_utils.get_naive_utc_now() - datetime.timedelta(days=6 * 31)).astimezone().isoformat()
        )
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
        dead_line_application = (date_utils.get_naive_utc_now() - datetime.timedelta(days=31)).astimezone().isoformat()
        dead_line_annotation = (
            (date_utils.get_naive_utc_now() - datetime.timedelta(days=2 * 31)).astimezone().isoformat()
        )
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
        dead_line_application = (date_utils.get_naive_utc_now() - datetime.timedelta(days=29)).astimezone().isoformat()
        dead_line_annotation = (
            (date_utils.get_naive_utc_now() - datetime.timedelta(days=6 * 31)).astimezone().isoformat()
        )
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
        dead_line_application = (date_utils.get_naive_utc_now() - datetime.timedelta(days=91)).astimezone().isoformat()
        dead_line_annotation = (
            (date_utils.get_naive_utc_now() - datetime.timedelta(days=6 * 31)).astimezone().isoformat()
        )
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
            bankAccount=bank_account, status=status, timespan=(date_utils.get_naive_utc_now(),)
        )
        venue = VenueFactory(managingOfferer=bank_account.offerer)
        # This shouldn't happen but we need to be sure that if any venue is linked to a bank account
        # that is going to be marked without continuation, it's unlinked.
        # We don't want any Cashflow to be generated using non valid bank accounts
        VenueBankAccountLinkFactory(bankAccount=bank_account, venue=venue)
        fields_application = (date_utils.get_naive_utc_now() - datetime.timedelta(days=91)).astimezone().isoformat()
        dead_line_application = (date_utils.get_naive_utc_now() - datetime.timedelta(days=91)).astimezone().isoformat()
        dead_line_annotation = (
            (date_utils.get_naive_utc_now() - datetime.timedelta(days=6 * 31)).astimezone().isoformat()
        )
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
                    "email": "contact.demarche.numerique@example.com",
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


@patch("pcapi.connectors.dms.api.DMSGraphQLClient.execute_query")
@patch("pcapi.connectors.dms.api.update_demarches_simplifiees_text_annotations")
@patch("pcapi.core.finance.ds.archive_dossier")
@pytest.mark.usefixtures("db_session")
class BankAccountJourneyTest:
    dsv5_application_id = 14742654
    b64_encoded_application_id = "RG9zc2llci0xNDc0MjY1NA=="
    error_annotation_id = "Q2hhbXAtMzYzMDA5NQ=="

    def test_v5_stop_using_bank_informations_and_bank_account_if_rejected(
        self, mock_archive_dossier, mock_update_text_annotation, mock_grapqhl_client
    ):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.accepted.value,
        )
        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        bank_account = db.session.query(finance_models.BankAccount).one()
        assert bank_account.status == finance_models.BankAccountApplicationStatus.ACCEPTED

        bank_account_link = db.session.query(offerers_models.VenueBankAccountLink).one()
        assert bank_account_link.venue == venue
        assert bank_account_link.bankAccount == bank_account
        assert bank_account_link.timespan.upper is None

        ### For compliance reasons, the DS application might be set to rejected, even if accepted before. ###

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.refused.value,
        )
        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        bank_account = db.session.query(finance_models.BankAccount).one()
        assert bank_account.status == finance_models.BankAccountApplicationStatus.REFUSED

        bank_account_link = db.session.query(offerers_models.VenueBankAccountLink).one()
        assert bank_account_link.venue == venue
        assert bank_account_link.bankAccount == bank_account
        assert bank_account_link.timespan.upper is not None

    def test_DSv5_is_handled(self, mock_archive_dossier, mock_update_text_annotation, mock_grapqhl_client):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)
        offerer = venue.managingOfferer

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.accepted.value,
        )
        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        bank_account = db.session.query(finance_models.BankAccount).one()
        assert bank_account.iban == "FR7630006000011234567890189"
        assert bank_account.offerer == offerer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.ACCEPTED
        assert bank_account.label == "Intitulé du compte bancaire"
        assert bank_account.dsApplicationId == self.dsv5_application_id
        bank_account_link = db.session.query(offerers_models.VenueBankAccountLink).one()
        assert bank_account_link.venue == venue

        mock_archive_dossier.assert_called_once_with("RG9zc2llci0xNDc0MjY1NA==")

        assert db.session.query(history_models.ActionHistory).count() == 1  # One link created
        assert db.session.query(finance_models.BankAccountStatusHistory).count() == 1  # One status change recorded

        assert len(mails_testing.outbox) == 0

    def test_edge_case_label_too_long_format_DSv5(
        self, mock_archive_dossier, mock_update_text_annotation, mock_grapqhl_client
    ):
        siret = "85331845900049"
        siren = siret[:9]
        offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)
        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.accepted.value,
            label="PARIS LIBRAIRIES ASSOCIATION DES LIBRAIRIES DE PARIS LIBRAIRIE COMME UN ROMAN 39 RUE DE BRETAGNE 75003 PARIS",
        )
        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)
        bank_account = db.session.query(finance_models.BankAccount).one()
        assert len(bank_account.label) <= 100
        assert bank_account.label[-3:] == "..."  # Check the placeholder indication

    def test_DSv5_link_is_not_created_if_several_venues_exists(
        self, mock_archive_dossier, mock_update_text_annotation, mock_grapqhl_client
    ):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)
        second_venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer=venue.managingOfferer)
        _third_venue_without_non_free_offer = offerers_factories.VenueFactory(
            pricing_point="self", managingOfferer=venue.managingOfferer
        )
        offers_factories.StockFactory(offer__venue=venue)
        offers_factories.StockFactory(offer__venue=second_venue)

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.accepted.value,
        )
        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        bank_account = db.session.query(finance_models.BankAccount).one()
        assert bank_account.iban == "FR7630006000011234567890189"
        assert bank_account.offerer == venue.managingOfferer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.ACCEPTED
        assert bank_account.label == "Intitulé du compte bancaire"
        assert bank_account.dsApplicationId == self.dsv5_application_id
        mock_archive_dossier.assert_called_once_with("RG9zc2llci0xNDc0MjY1NA==")

        assert not db.session.query(offerers_models.VenueBankAccountLink).count()

        assert not db.session.query(history_models.ActionHistory).count()
        assert db.session.query(finance_models.BankAccountStatusHistory).count() == 1  # One status change recorded

        assert len(mails_testing.outbox) == 2
        assert {mails_testing.outbox[0]["To"], mails_testing.outbox[1]["To"]} == {
            venue.bookingEmail,
            second_venue.bookingEmail,
        }

    def test_draft_dossier_are_not_archived(
        self, mock_archive_dossier, mock_update_text_annotation, mock_grapqhl_client
    ):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.draft.value,
        )
        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        bank_account = db.session.query(finance_models.BankAccount).one()
        assert bank_account.iban == "FR7630006000011234567890189"
        assert bank_account.offerer == venue.managingOfferer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.DRAFT
        assert bank_account.label == "Intitulé du compte bancaire"
        assert not bank_account.venueLinks
        assert bank_account.dsApplicationId == self.dsv5_application_id
        mock_archive_dossier.assert_not_called()

        assert not db.session.query(offerers_models.VenueBankAccountLink).count()
        assert not db.session.query(history_models.ActionHistory).count()

        assert db.session.query(finance_models.BankAccountStatusHistory).count() == 1

        assert len(mails_testing.outbox) == 0

    def test_on_going_dossier_are_not_archived(
        self, mock_archive_dossier, mock_update_text_annotation, mock_grapqhl_client
    ):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)
        offerers_factories.VenueFactory(pricing_point="self", managingOfferer=venue.managingOfferer)

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.on_going.value,
        )
        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        bank_account = db.session.query(finance_models.BankAccount).one()
        assert bank_account.iban == "FR7630006000011234567890189"
        assert bank_account.offerer == venue.managingOfferer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.ON_GOING
        assert bank_account.label == "Intitulé du compte bancaire"
        assert bank_account.dsApplicationId == self.dsv5_application_id
        mock_archive_dossier.assert_not_called()

        assert not db.session.query(offerers_models.VenueBankAccountLink).count()

        assert not db.session.query(history_models.ActionHistory).count()
        assert db.session.query(finance_models.BankAccountStatusHistory).count() == 1  # One status change recorded

    def test_DSv5_bank_account_get_successfully_updated_on_status_change(
        self, mock_archive_dossier, mock_update_text_annotation, mock_grapqhl_client, db_session
    ):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.on_going.value,
        )

        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        bank_account = db.session.query(finance_models.BankAccount).one()
        assert bank_account.iban == "FR7630006000011234567890189"
        assert bank_account.offerer == venue.managingOfferer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.ON_GOING
        assert bank_account.label == "Intitulé du compte bancaire"
        assert bank_account.dsApplicationId == self.dsv5_application_id
        mock_archive_dossier.assert_not_called()

        assert not db.session.query(offerers_models.VenueBankAccountLink).count()
        assert not db.session.query(history_models.ActionHistory).count()

        on_going_status_history = db.session.query(finance_models.BankAccountStatusHistory).one()

        assert on_going_status_history.status == bank_account.status
        assert on_going_status_history.timespan.upper is None

        # DS dossier status is updated to 'accepted' by the compliance team (without any change in bank account info)

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.accepted.value,
        )

        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        bank_account = db.session.query(finance_models.BankAccount).one()
        assert bank_account.iban == "FR7630006000011234567890189"
        assert bank_account.offerer == venue.managingOfferer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.ACCEPTED
        assert bank_account.label == "Intitulé du compte bancaire"
        mock_archive_dossier.assert_called_once_with("RG9zc2llci0xNDc0MjY1NA==")

        link = db.session.query(offerers_models.VenueBankAccountLink).one()
        assert link.bankAccount == bank_account
        assert link.venue == venue

        assert db.session.query(history_models.ActionHistory).count() == 1
        status_history = (
            db.session.query(finance_models.BankAccountStatusHistory)
            .order_by(finance_models.BankAccountStatusHistory.id)
            .all()
        )
        assert len(status_history) == 2
        accepted_status_history = status_history[-1]

        db.session.refresh(on_going_status_history)
        db.session.refresh(bank_account)

        assert on_going_status_history.timespan.upper is not None
        assert (
            accepted_status_history.status
            == bank_account.status
            == finance_models.BankAccountApplicationStatus.ACCEPTED
        )
        assert accepted_status_history.timespan.upper is None

    def test_DSv5_bank_account_get_successfully_updated_on_bank_account_info_change(
        self, mock_archive_dossier, mock_update_text_annotation, mock_grapqhl_client, db_session
    ):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)

        first_iban = "FR7630007000111234567890144"
        first_label = "Oupsie"

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.on_going.value, iban=first_iban, label=first_label
        )

        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        bank_account = db.session.query(finance_models.BankAccount).one()
        assert bank_account.label == first_label
        assert bank_account.iban == first_iban
        assert bank_account.offerer == venue.managingOfferer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.ON_GOING
        assert bank_account.dsApplicationId == self.dsv5_application_id
        mock_archive_dossier.assert_not_called()

        assert not db.session.query(offerers_models.VenueBankAccountLink).count()
        assert not db.session.query(history_models.ActionHistory).count()

        first_status_history = db.session.query(finance_models.BankAccountStatusHistory).one()
        assert first_status_history.status == bank_account.status
        assert first_status_history.timespan.upper is None

        # DS dossier is updated by the cultural partner (without any status modification from the compliance team)

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.on_going.value,
        )

        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        bank_account = db.session.query(finance_models.BankAccount).one()
        assert bank_account.label == "Intitulé du compte bancaire"
        assert bank_account.iban == "FR7630006000011234567890189"
        assert bank_account.offerer == venue.managingOfferer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.ON_GOING
        mock_archive_dossier.assert_not_called()

        assert not db.session.query(offerers_models.VenueBankAccountLink).count()
        assert not db.session.query(history_models.ActionHistory).count()

        last_status_history = db.session.query(finance_models.BankAccountStatusHistory).one()
        assert last_status_history == first_status_history

    def test_DSv5_bank_account_get_successfully_updated(
        self, mock_archive_dossier, mock_update_text_annotation, mock_grapqhl_client, db_session
    ):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)

        first_iban = "FR7630007000111234567890144"
        first_label = "Oupsie"

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.on_going.value, iban=first_iban, label=first_label
        )

        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        bank_account = db.session.query(finance_models.BankAccount).one()
        assert bank_account.label == first_label
        assert bank_account.iban == first_iban
        assert bank_account.offerer == venue.managingOfferer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.ON_GOING
        assert bank_account.dsApplicationId == self.dsv5_application_id
        mock_archive_dossier.assert_not_called()

        assert not db.session.query(offerers_models.VenueBankAccountLink).count()
        assert not db.session.query(history_models.ActionHistory).count()

        on_going_status_history = db.session.query(finance_models.BankAccountStatusHistory).one()

        assert on_going_status_history.status == bank_account.status
        assert on_going_status_history.timespan.upper is None

        # DS dossier is updated by the cultural partner and accepted by the compliance team

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.accepted.value,
        )

        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        bank_account = db.session.query(finance_models.BankAccount).one()
        assert bank_account.label == "Intitulé du compte bancaire"
        assert bank_account.iban == "FR7630006000011234567890189"
        assert bank_account.offerer == venue.managingOfferer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.ACCEPTED
        mock_archive_dossier.assert_called_once_with("RG9zc2llci0xNDc0MjY1NA==")

        link = db.session.query(offerers_models.VenueBankAccountLink).one()
        assert link.bankAccount == bank_account
        assert link.venue == venue

        assert db.session.query(history_models.ActionHistory).count() == 1
        status_history = (
            db.session.query(finance_models.BankAccountStatusHistory)
            .order_by(finance_models.BankAccountStatusHistory.id)
            .all()
        )
        assert len(status_history) == 2
        accepted_status_history = status_history[-1]

        db.session.refresh(on_going_status_history)
        db.session.refresh(bank_account)

        assert on_going_status_history.timespan.upper is not None
        assert (
            accepted_status_history.status
            == bank_account.status
            == finance_models.BankAccountApplicationStatus.ACCEPTED
        )
        assert accepted_status_history.timespan.upper is None

    def test_DSv5_pending_correction_status_handled(
        self, mock_archive_dossier, mock_update_text_annotation, mock_graph_client, db_session
    ):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)

        mock_graph_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.draft.value, last_pending_correction_date="2023-10-27T14:51:09+02:00"
        )

        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        bank_account = db.session.query(finance_models.BankAccount).one()
        assert bank_account.iban == "FR7630006000011234567890189"
        assert bank_account.offerer == venue.managingOfferer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.WITH_PENDING_CORRECTIONS
        assert bank_account.label == "Intitulé du compte bancaire"
        assert bank_account.dsApplicationId == self.dsv5_application_id
        mock_archive_dossier.assert_not_called()

        assert not db.session.query(offerers_models.VenueBankAccountLink).count()
        assert not db.session.query(history_models.ActionHistory).count()

        on_going_status_history = db.session.query(finance_models.BankAccountStatusHistory).one()

        assert on_going_status_history.status == bank_account.status
        assert not on_going_status_history.timespan.upper

    def test_dsv5_with_no_status_changes_does_not_create_nor_link_nor_status_changes_logs(
        self, mock_archive_dossier, mock_update_text_annotation, mock_grapqhl_client, db_session
    ):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.accepted.value,
        )
        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        bank_account = db.session.query(finance_models.BankAccount).one()
        assert bank_account.iban == "FR7630006000011234567890189"
        assert bank_account.offerer == venue.managingOfferer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.ACCEPTED
        assert bank_account.label == "Intitulé du compte bancaire"
        assert bank_account.dsApplicationId == self.dsv5_application_id

        link = db.session.query(offerers_models.VenueBankAccountLink).one()
        assert link.venue == venue
        assert link.bankAccount == bank_account

        assert db.session.query(history_models.ActionHistory).count() == 1
        assert db.session.query(finance_models.BankAccountStatusHistory).count() == 1  # One status change recorded

        # Multiple crons running without any changes

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.accepted.value,
        )

        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.accepted.value,
        )

        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.accepted.value,
        )

        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        link = db.session.query(offerers_models.VenueBankAccountLink).one()
        assert link.venue == venue
        assert link.bankAccount == bank_account

        assert db.session.query(history_models.ActionHistory).count() == 1
        assert db.session.query(finance_models.BankAccountStatusHistory).count() == 1  # One status change recorded

    def test_legacy_data_convert_into_bank_account_does_not_have_status_history(
        self, mock_archive_dossier, mock_update_text_annotation, mock_grapqhl_client, db_session
    ):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)
        # Legacy bankInformation turned into a bankAccount
        finance_factories.BankAccountFactory(
            iban="FR7630006000011234567890189",
            offerer=venue.managingOfferer,
            status=finance_models.BankAccountApplicationStatus.DRAFT,
            label="Intitulé du compte bancaire",
            dsApplicationId=self.dsv5_application_id,
        )

        # The DS application status change, this should work, even if the bankAccount doesn't have a BankAccountStatusHistory
        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.on_going.value,
        )
        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        bank_account = db.session.query(finance_models.BankAccount).one()
        assert bank_account.iban == "FR7630006000011234567890189"
        assert bank_account.offerer == venue.managingOfferer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.ON_GOING
        assert bank_account.label == "Intitulé du compte bancaire"
        assert bank_account.dsApplicationId == self.dsv5_application_id

        assert db.session.query(finance_models.BankAccountStatusHistory).count() == 1  # One status change recorded

    def test_offerer_can_have_several_bank_informations(
        self, mock_archive_dossier, mock_update_text_annotation, mock_grapqhl_client
    ):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)
        offerers_factories.VenueFactory(pricing_point="self", managingOfferer=venue.managingOfferer)

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.accepted.value,
        )
        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        bank_account = db.session.query(finance_models.BankAccount).one()
        assert bank_account.iban == "FR7630006000011234567890189"
        assert bank_account.offerer == venue.managingOfferer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.ACCEPTED
        assert bank_account.label == "Intitulé du compte bancaire"
        assert bank_account.dsApplicationId == self.dsv5_application_id
        mock_archive_dossier.assert_called_once_with("RG9zc2llci0xNDc0MjY1NA==")

        assert not db.session.query(offerers_models.VenueBankAccountLink).count()

        assert not db.session.query(history_models.ActionHistory).count()
        assert db.session.query(finance_models.BankAccountStatusHistory).count() == 1  # One status change recorded

        fake_iban = str(schwifty.IBAN.generate("FR", bank_code="30004", account_code="12345"))

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.accepted.value,
            b64_encoded_application_id=b64encode("Champ-123".encode()),
            application_id=123,
            iban=fake_iban,
        )
        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        bank_accounts = db.session.query(finance_models.BankAccount).order_by(finance_models.BankAccount.id).all()
        assert len(bank_accounts) == 2
        assert bank_accounts[0].iban == "FR7630006000011234567890189"
        assert bank_accounts[0].offerer == venue.managingOfferer
        assert bank_accounts[0].status == finance_models.BankAccountApplicationStatus.ACCEPTED
        assert bank_accounts[0].label == "Intitulé du compte bancaire"
        assert bank_accounts[0].dsApplicationId == self.dsv5_application_id

        assert bank_accounts[1].iban == fake_iban
        assert bank_accounts[1].offerer == venue.managingOfferer
        assert bank_accounts[1].status == finance_models.BankAccountApplicationStatus.ACCEPTED
        assert bank_accounts[1].label == "Intitulé du compte bancaire"
        assert bank_accounts[1].dsApplicationId == 123

        assert not db.session.query(offerers_models.VenueBankAccountLink).count()

        assert not db.session.query(history_models.ActionHistory).count()
        assert db.session.query(finance_models.BankAccountStatusHistory).count() == 2

    def test_association_to_physical_venue_if_both_virtual_and_physical_exists(
        self, mock_archive_dossier, mock_update_text_annotation, mock_dms_graphql_client
    ):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)
        mock_dms_graphql_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.accepted.value
        )

        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        bank_account = db.session.query(finance_models.BankAccount).one()
        assert bank_account.iban == "FR7630006000011234567890189"
        assert bank_account.offerer == venue.managingOfferer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.ACCEPTED
        assert bank_account.label == "Intitulé du compte bancaire"
        assert bank_account.dsApplicationId == self.dsv5_application_id

        link = db.session.query(offerers_models.VenueBankAccountLink).one()
        assert link.venue == venue
        assert link.bankAccount == bank_account

        assert db.session.query(history_models.ActionHistory).count() == 1
        assert db.session.query(finance_models.BankAccountStatusHistory).count() == 1  # One status change recorded

    def test_validation_on_iban(self, mock_archive_dossier, mock_update_text_annotation, mock_dms_graphql_client):
        siret = "85331845900049"
        siren = siret[:9]
        offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)

        mock_dms_graphql_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.draft.value, iban="XR7630006000011234567890189"
        )

        update_ds_applications_for_procedure(procedure_number=settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        assert not db.session.query(finance_models.BankAccount).all()
        mock_update_text_annotation.assert_any_call(
            dossier_id=self.b64_encoded_application_id,
            annotation_id=self.error_annotation_id,
            message="L'IBAN n'est pas valide",
        )

    def test_NC_is_handled(self, mock_archive_dossier, mock_update_text_annotation, mock_grapqhl_client):
        ridet = "1234567001"
        venue = offerers_factories.CaledonianVenueFactory(
            pricing_point="self",
            siret=siren_utils.ridet_to_siret(ridet),
            managingOfferer__siren=siren_utils.rid7_to_siren(ridet[:7]),
        )
        offerer = venue.managingOfferer

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_nc(
            state=GraphQLApplicationStates.accepted.value,
        )
        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_NC_PROCEDURE_ID, since=None)

        bank_account = db.session.query(finance_models.BankAccount).one()
        assert bank_account.iban == "NC2014889000000988000000100"
        assert bank_account.offerer == offerer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.ACCEPTED
        assert bank_account.label == "Compte bancaire calédonien"
        assert bank_account.dsApplicationId == 988
        bank_account_link = db.session.query(offerers_models.VenueBankAccountLink).one()
        assert bank_account_link.venue == venue

        mock_archive_dossier.assert_called_once_with("RG9zc2lldi0yOAMzNuAyMQ==")
        mock_update_text_annotation.assert_not_called()

        assert db.session.query(history_models.ActionHistory).count() == 1  # One link created
        assert db.session.query(finance_models.BankAccountStatusHistory).count() == 1  # One status change recorded

        assert len(mails_testing.outbox) == 0
