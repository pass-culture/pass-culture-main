import dataclasses
import datetime
from unittest.mock import patch

import factory
import pytest
from dateutil.relativedelta import relativedelta
from flask import url_for

import pcapi.core.mails.testing as mails_testing
from pcapi import settings
from pcapi.connectors.dms import exceptions as dms_exceptions
from pcapi.connectors.dms import models as dms_models
from pcapi.core.history import models as history_models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.routes.backoffice.filters import format_date_time
from pcapi.utils import date as date_utils
from pcapi.utils import requests

from .helpers import flash
from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("clean_database"),
    pytest.mark.backoffice,
]


class ListAccountUpdateRequestsTest(GetEndpointHelper):
    endpoint = "backoffice_web.account_update.list_account_update_requests"
    needed_permission = perm_models.Permissions.MANAGE_ACCOUNT_UPDATE_REQUEST

    # session + results + results count
    expected_num_queries = 3

    def test_list_account_update_requests(self, authenticated_client):
        now = date_utils.get_naive_utc_now()
        first_name_update_request = users_factories.FirstNameUpdateRequestFactory(
            user__firstName="Octave",
            user__lastName="César",
            user__email="heritier@example.com",
            user__civility="M.",
            firstName="Jules",
            lastName="César",
            email="imperator@example.com",
            newFirstName="Auguste",
            dateLastInstructorMessage=None,
            dateLastUserMessage=now - relativedelta(days=2),
            dateLastStatusUpdate=now - relativedelta(days=1),
        )

        last_name_and_email_update_request = users_factories.UserAccountUpdateRequestFactory(
            user__firstName="Juliette",
            user__lastName="Capulet",
            user__email="juju.capulet@example.com",
            user__civility="Mme",
            firstName="Juliette",
            lastName="Montaigu",
            email="juju.montaigu@example.com",
            updateTypes=[
                users_models.UserAccountUpdateType.LAST_NAME,
                users_models.UserAccountUpdateType.EMAIL,
            ],
            oldEmail="juju.capulet@example.com",
            newEmail="juju.montaigu@example.com",
            newLastName="Montaigu",
            dateLastInstructorMessage=now - relativedelta(days=3),
            dateLastUserMessage=None,
            dateLastStatusUpdate=now - relativedelta(days=1),
        )
        phone_number_request = users_factories.PhoneNumberUpdateRequestFactory(
            user__firstName="Jean-Pierre",
            user__lastName="Impair",
            user__email="impair@example.com",
            user__phoneNumber="+33222222222",
            firstName="Jean-Pierre",
            lastName="Impair",
            email="impair@example.com",
            newPhoneNumber="+33111111111",
            dateLastInstructorMessage=now - relativedelta(days=3),
            dateLastUserMessage=now - relativedelta(days=1),
            dateLastStatusUpdate=now - relativedelta(days=2),
        )
        unknown_user_request = users_factories.LastNameUpdateRequestFactory(
            status=dms_models.GraphQLApplicationStates.draft,
            user=None,
            firstName="Martin",
            lastName="Connu",
            email="martinconnu@example.com",
            newLastName="Inconnu",
            dateLastInstructorMessage=None,
            dateLastUserMessage=None,
            dateLastStatusUpdate=now,
        )
        accepted_user_request = users_factories.LastNameUpdateRequestFactory(
            status=dms_models.GraphQLApplicationStates.accepted,
            lastName=factory.SelfAttribute("newLastName"),
            dateLastInstructorMessage=None,
            dateLastUserMessage=None,
            dateLastStatusUpdate=now - relativedelta(days=5),
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 5

        assert rows[0]["Dossier"] == str(unknown_user_request.dsApplicationId)
        assert rows[0]["État"] == "En construction"
        assert rows[0]["Date de dernière MàJ"] == format_date_time(unknown_user_request.dateLastStatusUpdate)
        assert rows[0]["Date des derniers messages"] == ""
        assert (
            rows[0]["Demandeur"]
            == f"Martin Connu né(e) le {unknown_user_request.birthDate.strftime('%d/%m/%Y')} ({unknown_user_request.applicant_age} ans) martinconnu@example.com"
        )
        assert rows[0]["Jeune"] == "Compte jeune non trouvé"
        assert rows[0]["Modification"] == "Nom : Inconnu"
        assert rows[0]["Instructeur"] == "Instructeur du Backoffice"

        assert rows[1]["Dossier"] == str(first_name_update_request.dsApplicationId)
        assert rows[1]["État"] == "En instruction"
        assert rows[1]["Date de dernière MàJ"] == format_date_time(first_name_update_request.dateLastStatusUpdate)
        assert (
            rows[1]["Date des derniers messages"]
            == f"Demandeur : {format_date_time(first_name_update_request.dateLastUserMessage)}"
        )
        assert (
            rows[1]["Demandeur"]
            == f"Jules César né(e) le {first_name_update_request.birthDate.strftime('%d/%m/%Y')} ({first_name_update_request.applicant_age} ans) imperator@example.com"
        )
        assert (
            rows[1]["Jeune"]
            == f"Octave César ({first_name_update_request.user.id}) né le {first_name_update_request.user.birth_date.strftime('%d/%m/%Y')} ({last_name_and_email_update_request.user.age} ans) heritier@example.com Pass 18"
        )
        assert rows[1]["Modification"] == "Prénom : Octave → Auguste"
        assert rows[1]["Instructeur"] == "Instructeur du Backoffice"

        assert rows[2]["Dossier"] == str(last_name_and_email_update_request.dsApplicationId)
        assert rows[2]["État"] == "En instruction"
        assert rows[2]["Date de dernière MàJ"] == format_date_time(
            last_name_and_email_update_request.dateLastStatusUpdate
        )
        assert (
            rows[2]["Date des derniers messages"]
            == f"Instructeur : {format_date_time(last_name_and_email_update_request.dateLastInstructorMessage)}"
        )
        assert (
            rows[2]["Demandeur"]
            == f"Juliette Montaigu né(e) le {last_name_and_email_update_request.birthDate.strftime('%d/%m/%Y')} ({last_name_and_email_update_request.applicant_age} ans) juju.montaigu@example.com"
        )
        assert (
            rows[2]["Jeune"]
            == f"Juliette Capulet ({last_name_and_email_update_request.user.id}) née le {last_name_and_email_update_request.user.birth_date.strftime('%d/%m/%Y')} ({last_name_and_email_update_request.user.age} ans) juju.capulet@example.com Pass 18"
        )
        assert (
            rows[2]["Modification"]
            == "Email : juju.capulet@example.com → juju.montaigu@example.com Nom : Capulet → Montaigu"
        )
        assert rows[2]["Instructeur"] == "Instructeur du Backoffice"

        assert rows[3]["Dossier"] == str(phone_number_request.dsApplicationId)
        assert rows[3]["État"] == "En instruction"
        assert rows[3]["Date de dernière MàJ"] == format_date_time(phone_number_request.dateLastStatusUpdate)
        assert (
            rows[3]["Date des derniers messages"]
            == f"Demandeur : {format_date_time(phone_number_request.dateLastUserMessage)} Instructeur : {format_date_time(phone_number_request.dateLastInstructorMessage)}"
        )
        assert (
            rows[3]["Demandeur"]
            == f"Jean-Pierre Impair né(e) le {phone_number_request.birthDate.strftime('%d/%m/%Y')} ({phone_number_request.applicant_age} ans) impair@example.com"
        )
        assert (
            rows[3]["Jeune"]
            == f"Jean-Pierre Impair ({phone_number_request.user.id}) né(e) le {phone_number_request.user.birth_date.strftime('%d/%m/%Y')} ({phone_number_request.user.age} ans) impair@example.com Pass 18"
        )
        assert rows[3]["Modification"] == "Téléphone : +33222222222 → +33111111111"
        assert rows[3]["Instructeur"] == "Instructeur du Backoffice"

        assert rows[4]["Dossier"] == str(accepted_user_request.dsApplicationId)
        assert rows[4]["État"] == "Accepté"
        assert rows[4]["Date de dernière MàJ"] == format_date_time(accepted_user_request.dateLastStatusUpdate)
        assert rows[4]["Date des derniers messages"] == ""
        assert (
            rows[4]["Demandeur"]
            == f"Jeune Nouveau-Nom né(e) le {accepted_user_request.birthDate.strftime('%d/%m/%Y')} ({accepted_user_request.applicant_age} ans) {accepted_user_request.email}"
        )
        assert (
            rows[4]["Jeune"]
            == f"Jeune Nouveau-Nom ({accepted_user_request.user.id}) né(e) le {accepted_user_request.user.birth_date.strftime('%d/%m/%Y')} ({accepted_user_request.user.age} ans) {accepted_user_request.email} Pass 18"
        )
        assert rows[4]["Modification"] == "Nom : Nouveau-Nom"
        assert rows[4]["Instructeur"] == "Instructeur du Backoffice"

    def test_list_account_update_requests_order_asc(self, authenticated_client):
        update_request_1 = users_factories.EmailUpdateRequestFactory()
        update_request_2 = users_factories.EmailUpdateRequestFactory()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, order="asc"))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2
        assert rows[0]["Dossier"] == str(update_request_1.dsApplicationId)
        assert rows[1]["Dossier"] == str(update_request_2.dsApplicationId)

    def test_list_account_update_requests_with_flags(self, authenticated_client):
        update_request = users_factories.EmailUpdateRequestFactory(
            status=dms_models.GraphQLApplicationStates.draft,
            updateTypes=[
                users_models.UserAccountUpdateType.EMAIL,
                users_models.UserAccountUpdateType.PHONE_NUMBER,
            ],
            flags=[
                users_models.UserAccountUpdateFlag.WAITING_FOR_CORRECTION,
                users_models.UserAccountUpdateFlag.MISSING_VALUE,
                users_models.UserAccountUpdateFlag.DUPLICATE_NEW_EMAIL,
            ],
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["État"] == "En construction En attente de correction"
        assert (
            rows[0]["Modification"]
            == f"Saisie incomplèteEmail en doublon Email : {update_request.oldEmail} → {update_request.newEmail} Téléphone : {update_request.user.phoneNumber} →"
        )

    def test_list_filter_by_email(self, authenticated_client):
        specific_submitter_email_request = users_factories.FirstNameUpdateRequestFactory(
            user__email="notimportant@example.com",
            email="that.specific.email@example.com",
            newFirstName="notimportant",
        )
        specific_old_email_request = users_factories.EmailUpdateRequestFactory(
            oldEmail="that.specific.email@example.com"
        )
        specific_new_email_request = users_factories.EmailUpdateRequestFactory(
            newEmail="that.specific.email@example.com"
        )
        specific_user_email_request = users_factories.FirstNameUpdateRequestFactory(
            user__email="that.specific.email@example.com", newFirstName="notimportant"
        )
        users_factories.EmailUpdateRequestFactory()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q="that.specific.email@example.com"))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 4

        assert {row["Dossier"] for row in rows} == {
            str(request.dsApplicationId)
            for request in (
                specific_submitter_email_request,
                specific_old_email_request,
                specific_new_email_request,
                specific_user_email_request,
            )
        }

    @pytest.mark.parametrize(
        "q, expected_count, expected_application_ids",
        (
            ("+33111111111", 2, {"100001", "100002"}),
            ("0111111111", 2, {"100001", "100002"}),
        ),
    )
    def test_list_filter_by_phone_number(self, authenticated_client, q, expected_count, expected_application_ids):
        users_factories.PhoneNumberUpdateRequestFactory(dsApplicationId=100001, newPhoneNumber="+33111111111")
        users_factories.EmailUpdateRequestFactory(dsApplicationId=100002, user__phoneNumber="+33111111111")
        users_factories.EmailUpdateRequestFactory()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=q))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == expected_count
        assert {row["Dossier"] for row in rows} == expected_application_ids

    def test_list_filter_by_id(self, authenticated_client):
        specific_user_request = users_factories.EmailUpdateRequestFactory()
        specific_application_request = users_factories.EmailUpdateRequestFactory(
            dsApplicationId=specific_user_request.user.id,
        )
        users_factories.EmailUpdateRequestFactory()
        search_id = specific_user_request.user.id

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=search_id))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2

        assert {row["Dossier"] for row in rows} == {
            str(request.dsApplicationId)
            for request in (
                specific_user_request,
                specific_application_request,
            )
        }

    @pytest.mark.parametrize(
        "q, expected_count, expected_application_ids",
        (
            ("Martin", 3, {"100001", "100002", "100003"}),
            ("Cognito", 2, {"100001", "100002"}),
            ("Aucun Rapport", 3, {"100001", "100002", "100003"}),
            ("Martine", 1, {"100003"}),
            ("Aucun", 3, {"100001", "100002", "100003"}),
            ("Martin Matin", 1, {"100003"}),
        ),
    )
    def test_list_filter_by_name(self, authenticated_client, q, expected_count, expected_application_ids):
        users_factories.UserAccountUpdateRequestFactory(
            dsApplicationId=100001,
            firstName="Aucun",
            lastName="Rapport",
            user=None,
            updateTypes=[users_models.UserAccountUpdateType.FIRST_NAME, users_models.UserAccountUpdateType.LAST_NAME],
            newFirstName="Martin",
            newLastName="Cognito",
        )
        users_factories.UserAccountUpdateRequestFactory(
            dsApplicationId=100002,
            firstName="Jean-Martin",
            lastName="Rapport",
            updateTypes=[users_models.UserAccountUpdateType.FIRST_NAME, users_models.UserAccountUpdateType.LAST_NAME],
            newFirstName="Aucun",
            newLastName="Incognito",
        )
        users_factories.UserAccountUpdateRequestFactory(
            dsApplicationId=100003,
            firstName="Aucun",
            lastName="Rapport",
            user__firstName="Martine",
            user__lastName="Alaplage",
            updateTypes=[users_models.UserAccountUpdateType.FIRST_NAME, users_models.UserAccountUpdateType.LAST_NAME],
            newFirstName="Martin",
            newLastName="Matin",
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=q))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == expected_count
        assert {row["Dossier"] for row in rows} == expected_application_ids

    @pytest.mark.parametrize(
        "from_to_date, expected_count, expected_application_ids",
        (
            ("25/09/2024 - 30/09/2024", 3, {"100001", "100002", "100003"}),
            ("25/09/2024 - 27/09/2024", 2, {"100002", "100003"}),
            ("27/09/2024 - 30/09/2024", 3, {"100001", "100002", "100003"}),
        ),
    )
    def test_list_filter_by_date(self, authenticated_client, from_to_date, expected_count, expected_application_ids):
        now = datetime.datetime(2024, 9, 28)
        users_factories.EmailUpdateRequestFactory(
            dsApplicationId=100001,
            dateLastUserMessage=None,
            dateLastStatusUpdate=now,
        )
        users_factories.EmailUpdateRequestFactory(
            dsApplicationId=100002,
            dateLastUserMessage=now,
            dateLastStatusUpdate=now - relativedelta(days=2),
        )
        users_factories.EmailUpdateRequestFactory(
            dsApplicationId=100003,
            dateLastUserMessage=now - relativedelta(days=2),
            dateLastStatusUpdate=now,
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, from_to_date=from_to_date))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == expected_count
        assert {row["Dossier"] for row in rows} == expected_application_ids

    @pytest.mark.parametrize("has_found_user,expected_application_id", [("true", "100001"), ("false", "100002")])
    def test_list_filter_by_found_user(self, authenticated_client, has_found_user, expected_application_id):
        users_factories.EmailUpdateRequestFactory(dsApplicationId=100001)
        users_factories.EmailUpdateRequestFactory(dsApplicationId=100002, user=None)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, has_found_user=has_found_user))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1

        assert rows[0]["Dossier"] == expected_application_id

    @pytest.mark.parametrize(
        "status, expected_count, expected_application_ids",
        (
            (dms_models.GraphQLApplicationStates.draft.name, 1, {"100001"}),
            (dms_models.GraphQLApplicationStates.on_going.name, 1, {"100002"}),
            (
                [dms_models.GraphQLApplicationStates.draft.name, dms_models.GraphQLApplicationStates.on_going.name],
                2,
                {"100001", "100002"},
            ),
        ),
    )
    def test_list_filter_by_status(self, authenticated_client, status, expected_count, expected_application_ids):
        users_factories.EmailUpdateRequestFactory(
            dsApplicationId=100001, status=dms_models.GraphQLApplicationStates.draft
        )

        users_factories.EmailUpdateRequestFactory(
            dsApplicationId=100002, status=dms_models.GraphQLApplicationStates.on_going
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, status=status))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == expected_count
        assert {row["Dossier"] for row in rows} == expected_application_ids

    @pytest.mark.parametrize(
        "flags, expected_count, expected_application_ids",
        (
            (users_models.UserAccountUpdateFlag.DUPLICATE_NEW_EMAIL.value, 1, {"100001"}),
            (users_models.UserAccountUpdateFlag.INVALID_VALUE.value, 2, {"100001", "100002"}),
            (
                [
                    users_models.UserAccountUpdateFlag.DUPLICATE_NEW_EMAIL.value,
                    users_models.UserAccountUpdateFlag.WAITING_FOR_CORRECTION.value,
                ],
                2,
                {"100001", "100002"},
            ),
        ),
    )
    def test_list_filter_by_error_status(self, authenticated_client, flags, expected_count, expected_application_ids):
        users_factories.EmailUpdateRequestFactory(
            dsApplicationId=100001,
            flags=[
                users_models.UserAccountUpdateFlag.INVALID_VALUE,
                users_models.UserAccountUpdateFlag.DUPLICATE_NEW_EMAIL,
            ],
        )

        users_factories.EmailUpdateRequestFactory(
            dsApplicationId=100002,
            flags=[
                users_models.UserAccountUpdateFlag.INVALID_VALUE,
                users_models.UserAccountUpdateFlag.WAITING_FOR_CORRECTION,
            ],
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, flags=flags))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == expected_count
        assert {row["Dossier"] for row in rows} == expected_application_ids

    @pytest.mark.parametrize(
        "update_type, expected_count, expected_application_ids",
        (
            (users_models.UserAccountUpdateType.FIRST_NAME.name, 1, {"100001"}),
            (users_models.UserAccountUpdateType.LAST_NAME.name, 2, {"100001", "100002"}),
            (
                [users_models.UserAccountUpdateType.FIRST_NAME.name, users_models.UserAccountUpdateType.EMAIL.name],
                0,
                set(),
            ),
            (
                [users_models.UserAccountUpdateType.LAST_NAME.name, users_models.UserAccountUpdateType.EMAIL.name],
                1,
                {"100002"},
            ),
        ),
    )
    def test_list_filter_by_update_type(
        self, authenticated_client, update_type, expected_count, expected_application_ids
    ):
        users_factories.UserAccountUpdateRequestFactory(
            dsApplicationId=100001,
            updateTypes=[users_models.UserAccountUpdateType.FIRST_NAME, users_models.UserAccountUpdateType.LAST_NAME],
            newFirstName="Martin",
            newLastName="Cognito",
        )
        users_factories.UserAccountUpdateRequestFactory(
            dsApplicationId=100002,
            updateTypes=[users_models.UserAccountUpdateType.EMAIL, users_models.UserAccountUpdateType.LAST_NAME],
            newEmail="shakespeare@example.com",
            newLastName="Montaigu",
        )
        users_factories.EmailUpdateRequestFactory(
            dsApplicationId=100003,
            newEmail="something.else@example.com",
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, update_type=update_type))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == expected_count
        assert {row["Dossier"] for row in rows} == expected_application_ids

    def test_list_filter_by_last_instructor(self, authenticated_client):
        instructor = users_factories.AdminFactory()
        instructorId = instructor.id
        update_request = users_factories.EmailUpdateRequestFactory(lastInstructor=instructor)
        users_factories.EmailUpdateRequestFactory(lastInstructor=users_factories.AdminFactory())

        # +1 query to fill in instructor filter
        with assert_num_queries(self.expected_num_queries + 1):
            response = authenticated_client.get(url_for(self.endpoint, last_instructor=instructorId))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["Dossier"] == str(update_request.dsApplicationId)

    def test_list_filter_by_no_instructor(self, authenticated_client):
        update_request = users_factories.EmailUpdateRequestFactory(lastInstructor=None)
        users_factories.EmailUpdateRequestFactory()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, only_unassigned="on"))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["Dossier"] == str(update_request.dsApplicationId)


class InstructTest(PostEndpointHelper):
    endpoint = "backoffice_web.account_update.instruct"
    endpoint_kwargs = {"ds_application_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_ACCOUNT_UPDATE_REQUEST

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.make_on_going")
    def test_instruct_success(self, mock_make_on_going, legit_user, authenticated_client):
        update_request = users_factories.UserAccountUpdateRequestFactory(
            status=dms_models.GraphQLApplicationStates.draft
        )

        mock_make_on_going.return_value = {
            "id": "RG9zc2llci0yMTI3Mzc3Mw==",
            "number": 21273773,
            "state": "en_instruction",
            "dateDerniereModification": "2024-12-02T18:20:53+01:00",
            "dateDepot": "2024-12-02T18:16:50+01:00",
            "datePassageEnConstruction": "2024-12-02T18:19:39+01:00",
            "datePassageEnInstruction": "2024-12-02T18:20:53+01:00",
            "dateTraitement": None,
            "dateDerniereCorrectionEnAttente": None,
            "dateDerniereModificationChamps": "2024-12-02T18:16:49+01:00",
        }

        response = self.post_to_endpoint(
            authenticated_client,
            ds_application_id=update_request.dsApplicationId,
            headers={"hx-request": "true"},
        )
        assert response.status_code == 200
        cells = html_parser.extract_plain_row(response.data, id=f"request-row-{update_request.dsApplicationId}")
        assert str(update_request.dsApplicationId) in cells[1]

        mock_make_on_going.assert_called_once()

        db.session.refresh(update_request)
        assert update_request.status == dms_models.GraphQLApplicationStates.on_going
        assert update_request.dateLastStatusUpdate == datetime.datetime(2024, 12, 2, 17, 20, 53)
        assert update_request.lastInstructor == legit_user

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.make_on_going")
    def test_instruct_with_error(self, mock_make_on_going, legit_user, authenticated_client):
        update_request = users_factories.UserAccountUpdateRequestFactory(
            dsApplicationId=1234567, status=dms_models.GraphQLApplicationStates.draft
        )

        mock_make_on_going.side_effect = dms_exceptions.DmsGraphQLApiError([{"message": "Test!"}])

        response = self.post_to_endpoint(
            authenticated_client,
            ds_application_id=update_request.dsApplicationId,
            headers={"hx-request": "true"},
        )
        assert response.status_code == 200
        cells = html_parser.extract_plain_row(response.data, id=f"request-row-{update_request.dsApplicationId}")
        assert str(update_request.dsApplicationId) in cells[1]

        alerts = flash.get_htmx_flash_messages(authenticated_client)
        assert "Le dossier 1234567 ne peut pas passer en instruction : Test!" in alerts["warning"]

        db.session.refresh(update_request)
        assert update_request.status == dms_models.GraphQLApplicationStates.draft
        assert update_request.lastInstructor != legit_user

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.make_on_going")
    def test_instruct_with_ds_connection_error(self, mock_make_on_going, legit_user, authenticated_client):
        update_request = users_factories.UserAccountUpdateRequestFactory(
            dsApplicationId=1234567, status=dms_models.GraphQLApplicationStates.draft
        )

        message = (
            "HTTPSConnectionPool(host='demarche.numerique.gouv.fr', port=443): Max retries exceeded with url: "
            "/api/v2/graphql (Caused by ProtocolError('Connection aborted.', RemoteDisconnected('Remote end closed"
            " connection without response')))"
        )
        mock_make_on_going.side_effect = dms_exceptions.DmsGraphQLAPIConnectError(message)

        response = self.post_to_endpoint(
            authenticated_client,
            ds_application_id=update_request.dsApplicationId,
            headers={"hx-request": "true"},
        )
        assert response.status_code == 200
        cells = html_parser.extract_plain_row(response.data, id=f"request-row-{update_request.dsApplicationId}")
        assert str(update_request.dsApplicationId) in cells[1]

        alerts = flash.get_htmx_flash_messages(authenticated_client)
        assert (
            f"Le dossier 1234567 ne peut pas passer en instruction : La connexion à Démarche Numérique a échoué : {message}"
            in alerts["warning"]
        )

        db.session.refresh(update_request)
        assert update_request.status == dms_models.GraphQLApplicationStates.draft
        assert update_request.lastInstructor != legit_user

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.make_on_going")
    def test_instruct_not_instructor(self, mock_make_on_going, client):
        not_instructor = users_factories.AdminFactory()
        update_request = users_factories.UserAccountUpdateRequestFactory(
            status=dms_models.GraphQLApplicationStates.draft
        )

        client = client.with_bo_session_auth(not_instructor)
        response = self.post_to_endpoint(
            client,
            ds_application_id=update_request.dsApplicationId,
            headers={"hx-request": "true"},
        )
        assert response.status_code == 403

        mock_make_on_going.assert_not_called()

    def test_instruct_not_found(self, authenticated_client):
        response = self.post_to_endpoint(
            authenticated_client,
            ds_application_id=1,
            headers={"hx-request": "true"},
        )
        assert response.status_code == 404


class GetAcceptFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.account_update.get_accept_form"
    endpoint_kwargs = {"ds_application_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_ACCOUNT_UPDATE_REQUEST

    # session + update request joined with user
    expected_num_queries = 2
    # + search for duplicate in case of email update
    expected_num_queries_email_update = expected_num_queries + 1

    button_label = "Appliquer les modifications et accepter"

    def test_email_update(self, authenticated_client):
        update_request = users_factories.EmailUpdateRequestFactory(
            user__email="ancien_email@example.com",
            oldEmail="ancien_email@example.com",
        )
        ds_application_id = update_request.dsApplicationId

        with assert_num_queries(self.expected_num_queries_email_update):
            response = authenticated_client.get(url_for(self.endpoint, ds_application_id=ds_application_id))
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)
        assert (
            f"Jeune : {update_request.user.firstName} {update_request.user.lastName} ({update_request.user.id}) Pass 18 "
            in content
        )
        assert f"Email : {update_request.user.email} " in content
        assert f"Date de naissance : {update_request.user.birth_date.strftime('%d/%m/%Y')} " in content
        assert f"Âge : {update_request.user.age} ans " in content
        assert "Modifications demandées : Email " in content
        assert f"Dossier : {update_request.dsApplicationId} " in content
        assert f"Dépôt de la demande : {update_request.dateCreated.strftime('%d/%m/%Y')} " in content
        assert f"Ancien email : {update_request.user.email} " in content
        assert f"Nouvel email : {update_request.newEmail} " in content
        assert "Ancien numéro " not in content
        assert "Nouveau numéro " not in content
        assert "Nouveau prénom " not in content
        assert "Nouveau nom " not in content
        assert "Doublon" not in content
        assert self.button_label in content

    def test_lost_credentials(self, authenticated_client):
        user = users_factories.BeneficiaryGrant18Factory()
        update_request = users_factories.LostCredentialsUpdateRequestFactory(user=user)
        ds_application_id = update_request.dsApplicationId

        with assert_num_queries(self.expected_num_queries_email_update):
            response = authenticated_client.get(url_for(self.endpoint, ds_application_id=ds_application_id))
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)
        assert (
            f"Jeune : {update_request.user.firstName} {update_request.user.lastName} ({update_request.user.id}) Pass 18 "
            in content
        )
        assert f"Email : {update_request.user.email} " in content
        assert f"Date de naissance : {update_request.user.birth_date.strftime('%d/%m/%Y')} " in content
        assert f"Âge : {update_request.user.age} ans " in content
        assert "Modifications demandées : Perte de l'identifiant " in content
        assert f"Dossier : {update_request.dsApplicationId} " in content
        assert f"Dépôt de la demande : {update_request.dateCreated.strftime('%d/%m/%Y')} " in content
        assert "Ancien email " not in content
        assert f"Nouvel email : {update_request.newEmail} " in content
        assert "Ancien numéro " not in content
        assert "Nouveau numéro " not in content
        assert "Nouveau prénom " not in content
        assert "Nouveau nom " not in content
        assert "Doublon" not in content
        assert self.button_label in content

    def test_phone_number_update(self, authenticated_client):
        ds_application_id = 21268381
        update_request = users_factories.PhoneNumberUpdateRequestFactory(
            dsApplicationId=ds_application_id, user__phoneNumber="+33612345678"
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, ds_application_id=ds_application_id))
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)
        assert "Modifications demandées : Numéro de téléphone " in content
        assert f"Dossier : {update_request.dsApplicationId} " in content
        assert f"Dépôt de la demande : {update_request.dateCreated.strftime('%d/%m/%Y')} " in content
        assert "Ancien numéro : +33612345678 " in content
        assert f"Nouveau numéro : {update_request.newPhoneNumber} " in content
        assert "Ancien email " not in content
        assert "Nouvel email " not in content
        assert "Nouveau prénom " not in content
        assert "Nouveau nom " not in content
        assert "Doublon" not in content
        assert self.button_label in content

    def test_names_update(self, authenticated_client):
        ds_application_id = 21268381
        update_request = users_factories.UserAccountUpdateRequestFactory(
            dsApplicationId=ds_application_id,
            updateTypes=[
                users_models.UserAccountUpdateType.FIRST_NAME,
                users_models.UserAccountUpdateType.LAST_NAME,
            ],
            newFirstName="Nouveau-Prénom",
            newLastName="Nouveau-Nom",
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, ds_application_id=ds_application_id))
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)
        assert "Modifications demandées : Prénom + Nom " in content
        assert f"Dossier : {update_request.dsApplicationId} " in content
        assert f"Dépôt de la demande : {update_request.dateCreated.strftime('%d/%m/%Y')} " in content
        assert f"Ancien prénom : {update_request.user.firstName} " in content
        assert f"Nouveau prénom : {update_request.newFirstName} " in content
        assert f"Ancien nom : {update_request.user.lastName} " in content
        assert f"Nouveau nom : {update_request.newLastName} " in content
        assert "Ancien email " not in content
        assert "Nouvel email " not in content
        assert "Ancien numéro " not in content
        assert "Nouveau numéro " not in content
        assert "Doublon" not in content
        assert self.button_label in content

    def test_email_update_with_duplicate(self, authenticated_client):
        duplicate_user = users_factories.UserFactory(email="nouvel_email@example.com")
        ds_application_id = 21268381
        update_request = users_factories.EmailUpdateRequestFactory(
            user__email="ancien_email@example.com",
            oldEmail="ancien_email@example.com",
            newEmail="nouvel_email@example.com",
            dsApplicationId=ds_application_id,
            flags=[users_models.UserAccountUpdateFlag.DUPLICATE_NEW_EMAIL],
        )

        with assert_num_queries(self.expected_num_queries_email_update):
            response = authenticated_client.get(url_for(self.endpoint, ds_application_id=ds_application_id))
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)
        assert (
            f"Jeune : {update_request.user.firstName} {update_request.user.lastName} ({update_request.user.id}) Pass 18 "
            in content
        )
        assert (
            f"Doublon : {duplicate_user.firstName} {duplicate_user.lastName} ({duplicate_user.id}) "
            f"Email : {duplicate_user.email} "
            f"Création du compte : {duplicate_user.dateCreated.strftime('%d/%m/%Y')} "
            f"Date de naissance : {duplicate_user.dateOfBirth.strftime('%d/%m/%Y')} "
            f"Âge : {duplicate_user.age} ans " in content
        )
        assert self.button_label in content

    def test_email_update_duplicate_with_beneficiary_role(self, authenticated_client):
        duplicate_user = users_factories.BeneficiaryFactory(email="nouvel_email@example.com")
        ds_application_id = 21268381
        update_request = users_factories.EmailUpdateRequestFactory(
            user__email="ancien_email@example.com",
            oldEmail="ancien_email@example.com",
            newEmail="nouvel_email@example.com",
            dsApplicationId=ds_application_id,
            flags=[users_models.UserAccountUpdateFlag.DUPLICATE_NEW_EMAIL],
        )

        with assert_num_queries(self.expected_num_queries_email_update):
            response = authenticated_client.get(url_for(self.endpoint, ds_application_id=ds_application_id))
            assert response.status_code == 200

        alert = html_parser.extract_alert(response.data)
        assert (
            alert
            == "Un compte doublon avec la nouvelle adresse demandée a déjà reçu un crédit. Le dossier ne peut donc pas être accepté."
        )

        content = html_parser.content_as_text(response.data)
        assert (
            f"Jeune : {update_request.user.firstName} {update_request.user.lastName} ({update_request.user.id}) Pass 18 "
            in content
        )
        assert (
            f"Doublon : {duplicate_user.firstName} {duplicate_user.lastName} ({duplicate_user.id}) Pass 18 " in content
        )
        assert self.button_label not in content

    def test_email_update_duplicate_with_pro_role(self, authenticated_client):
        duplicate_user = users_factories.ProFactory(email="nouvel_email@example.com")
        ds_application_id = 21268381
        update_request = users_factories.EmailUpdateRequestFactory(
            user__email="ancien_email@example.com",
            oldEmail="ancien_email@example.com",
            newEmail="nouvel_email@example.com",
            dsApplicationId=ds_application_id,
            flags=[users_models.UserAccountUpdateFlag.DUPLICATE_NEW_EMAIL],
        )

        with assert_num_queries(self.expected_num_queries_email_update):
            response = authenticated_client.get(url_for(self.endpoint, ds_application_id=ds_application_id))
            assert response.status_code == 200

        alert = html_parser.extract_alert(response.data)
        assert alert == "Attention ! Le compte doublon qui sera suspendu est un compte pro ou admin."

        content = html_parser.content_as_text(response.data)
        assert (
            f"Jeune : {update_request.user.firstName} {update_request.user.lastName} ({update_request.user.id}) Pass 18 "
            in content
        )
        assert f"Doublon : {duplicate_user.firstName} {duplicate_user.lastName} ({duplicate_user.id}) Pro " in content
        assert self.button_label in content

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.make_accepted")
    def test_not_instructor(self, mock_make_accepted, client):
        not_instructor = users_factories.AdminFactory()
        update_request = users_factories.UserAccountUpdateRequestFactory(
            status=dms_models.GraphQLApplicationStates.draft
        )

        client = client.with_bo_session_auth(not_instructor)
        response = client.get(url_for(self.endpoint, ds_application_id=update_request.dsApplicationId))
        assert response.status_code == 403

        mock_make_accepted.assert_not_called()

    def test_not_found(self, authenticated_client):
        response = authenticated_client.get(url_for(self.endpoint, ds_application_id=1))
        assert response.status_code == 404


class AcceptTest(PostEndpointHelper):
    endpoint = "backoffice_web.account_update.accept"
    endpoint_kwargs = {"ds_application_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_ACCOUNT_UPDATE_REQUEST

    def _test_successful_request(self, update_request, mock_make_accepted, legit_user, authenticated_client):
        motivation = "Test !"

        mock_make_accepted.return_value = {
            "id": "UHJvY4VkdXKlLTI5NTgw",
            "number": 21268381,
            "state": "accepte",
            "dateDerniereModification": "2024-12-05T12:17:10+01:00",
            "dateDepot": "2024-12-02T15:37:29+01:00",
            "datePassageEnConstruction": "2024-12-05T12:15:55+01:00",
            "datePassageEnInstruction": "2024-12-05T12:16:03+01:00",
            "dateTraitement": "2024-12-05T12:17:10+01:00",
            "dateDerniereCorrectionEnAttente": None,
            "dateDerniereModificationChamps": "2024-12-02T15:37:28+01:00",
        }

        response = self.post_to_endpoint(
            authenticated_client,
            ds_application_id=update_request.dsApplicationId,
            form={"motivation": motivation},
            headers={"hx-request": "true"},
        )
        assert response.status_code == 200
        mock_make_accepted.assert_called_once()
        cells = html_parser.extract_plain_row(response.data, id=f"request-row-{update_request.dsApplicationId}")
        assert str(update_request.dsApplicationId) in cells[1]

        db.session.refresh(update_request)
        assert update_request.status == dms_models.GraphQLApplicationStates.accepted
        assert update_request.dateLastStatusUpdate == datetime.datetime(2024, 12, 5, 11, 17, 10)
        assert update_request.lastInstructor == legit_user

        action = (
            db.session.query(history_models.ActionHistory)
            .filter_by(actionType=history_models.ActionType.USER_ACCOUNT_UPDATE_INSTRUCTED)
            .one()
        )
        assert action.authorUser == legit_user
        assert action.user == update_request.user
        assert action.comment == motivation
        assert action.extraData == {
            "ds_procedure_id": int(settings.DS_USER_ACCOUNT_UPDATE_PROCEDURE_ID),
            "ds_dossier_id": update_request.dsApplicationId,
            "ds_status": dms_models.GraphQLApplicationStates.accepted.value,
        }

    def _check_accept_email_update(self, update_request, old_email):
        assert update_request.user.email == update_request.newEmail

        assert len(update_request.user.action_history) == 1

        assert len(update_request.user.email_history) == 1
        history = update_request.user.email_history[0]
        assert history.oldEmail == old_email
        assert history.newEmail == update_request.newEmail
        assert history.eventType == users_models.EmailHistoryEventTypeEnum.ADMIN_UPDATE

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(
            TransactionalEmail.PERSONAL_DATA_UPDATED_FROM_BACKOFFICE.value
        )
        assert mails_testing.outbox[0]["params"] == {
            "FIRSTNAME": update_request.user.firstName,
            "LASTNAME": update_request.user.lastName,
            "UPDATED_FIELD": "EMAIL",
        }

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.make_accepted")
    def test_accept_email_update(self, mock_make_accepted, legit_user, authenticated_client):
        update_request = users_factories.EmailUpdateRequestFactory(
            user__email="ancien_email@example.com", oldEmail="ancien_email@example.com", dsApplicationId=21268381
        )

        self._test_successful_request(update_request, mock_make_accepted, legit_user, authenticated_client)
        self._check_accept_email_update(update_request, update_request.oldEmail)

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.make_accepted")
    def test_accept_lost_credentials(self, mock_make_accepted, legit_user, authenticated_client):
        old_email = "perdu@example.com"
        user = users_factories.BeneficiaryGrant18Factory(email=old_email)
        update_request = users_factories.LostCredentialsUpdateRequestFactory(user=user)

        self._test_successful_request(update_request, mock_make_accepted, legit_user, authenticated_client)
        self._check_accept_email_update(update_request, old_email)

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.make_accepted")
    def test_accept_phone_number_update(self, mock_make_accepted, legit_user, authenticated_client):
        update_request = users_factories.PhoneNumberUpdateRequestFactory(
            dsApplicationId=21268381, user__phoneNumber="+33612345678"
        )

        self._test_successful_request(update_request, mock_make_accepted, legit_user, authenticated_client)

        assert update_request.user.phoneNumber == update_request.newPhoneNumber

        assert len(update_request.user.action_history) == 2
        action = (
            db.session.query(history_models.ActionHistory)
            .filter_by(actionType=history_models.ActionType.INFO_MODIFIED)
            .one()
        )
        assert action.authorUser == legit_user
        assert action.user == update_request.user
        assert action.extraData == {
            "modified_info": {"phoneNumber": {"old_info": "+33612345678", "new_info": "+33730405060"}}
        }

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(
            TransactionalEmail.PERSONAL_DATA_UPDATED_FROM_BACKOFFICE.value
        )
        assert mails_testing.outbox[0]["params"] == {
            "FIRSTNAME": update_request.user.firstName,
            "LASTNAME": update_request.user.lastName,
            "UPDATED_FIELD": "PHONE_NUMBER",
        }

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.make_accepted")
    def test_accept_names_update(self, mock_make_accepted, legit_user, authenticated_client):
        update_request = users_factories.UserAccountUpdateRequestFactory(
            dsApplicationId=21268381,
            updateTypes=[
                users_models.UserAccountUpdateType.FIRST_NAME,
                users_models.UserAccountUpdateType.LAST_NAME,
            ],
            newFirstName="Nouveau-Prénom",
            newLastName="Nouveau-Nom",
        )

        self._test_successful_request(update_request, mock_make_accepted, legit_user, authenticated_client)

        assert update_request.user.firstName == update_request.newFirstName
        assert update_request.user.lastName == update_request.newLastName

        assert len(update_request.user.action_history) == 2
        action = (
            db.session.query(history_models.ActionHistory)
            .filter_by(actionType=history_models.ActionType.INFO_MODIFIED)
            .one()
        )
        assert action.authorUser == legit_user
        assert action.user == update_request.user
        assert action.extraData == {
            "modified_info": {
                "firstName": {"old_info": "Jeune", "new_info": "Nouveau-Prénom"},
                "lastName": {"old_info": "Demandeur", "new_info": "Nouveau-Nom"},
            }
        }

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(
            TransactionalEmail.PERSONAL_DATA_UPDATED_FROM_BACKOFFICE.value
        )
        assert mails_testing.outbox[0]["params"] == {
            "FIRSTNAME": update_request.newFirstName,
            "LASTNAME": update_request.newLastName,
            "UPDATED_FIELD": "FIRST_NAME,LAST_NAME",
        }

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.make_accepted")
    def test_application_not_found(self, mock_make_accepted, legit_user, authenticated_client):
        update_request = users_factories.EmailUpdateRequestFactory(user__email="original@example.com")

        mock_make_accepted.side_effect = dms_exceptions.DmsGraphQLApiError(
            [
                {
                    "message": "Dossier not found",
                    "locations": [{"line": 2, "column": 3}],
                    "path": ["dossierAccepter"],
                    "extensions": {"code": "not_found"},
                }
            ]
        )

        response = self.post_to_endpoint(
            authenticated_client,
            ds_application_id=update_request.dsApplicationId,
            form={"motivation": "Test"},
            headers={"hx-request": "true"},
        )
        assert response.status_code == 200
        cells = html_parser.extract_plain_row(response.data, id=f"request-row-{update_request.dsApplicationId}")
        assert str(update_request.dsApplicationId) in cells[1]
        mock_make_accepted.assert_called_once()

        db.session.refresh(update_request)
        assert update_request.status == dms_models.GraphQLApplicationStates.on_going
        assert update_request.lastInstructor != legit_user
        assert update_request.user.email == "original@example.com"
        assert len(update_request.user.action_history) == 0
        assert len(update_request.user.email_history) == 0
        assert len(mails_testing.outbox) == 0

        alerts = flash.get_htmx_flash_messages(authenticated_client)
        assert (
            f"Le dossier {update_request.dsApplicationId} ne peut pas être accepté : dossier non trouvé"
            in alerts["warning"]
        )

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.make_accepted")
    def test_wrong_remote_state(self, mock_make_accepted, legit_user, authenticated_client):
        update_request = users_factories.PhoneNumberUpdateRequestFactory(user__phoneNumber="+33612345678")

        mock_make_accepted.side_effect = dms_exceptions.DmsGraphQLApiError(
            [{"message": "Le dossier est d\u00e9j\u00e0 en construction"}]
        )

        response = self.post_to_endpoint(
            authenticated_client,
            ds_application_id=update_request.dsApplicationId,
            form={"motivation": "Test"},
            headers={"hx-request": "true"},
        )
        assert response.status_code == 200
        cells = html_parser.extract_plain_row(response.data, id=f"request-row-{update_request.dsApplicationId}")
        assert str(update_request.dsApplicationId) in cells[1]
        mock_make_accepted.assert_called_once()

        db.session.refresh(update_request)
        assert update_request.status == dms_models.GraphQLApplicationStates.on_going
        assert update_request.lastInstructor != legit_user
        assert update_request.user.phoneNumber == "+33612345678"
        assert len(update_request.user.action_history) == 0
        assert len(update_request.user.email_history) == 0
        assert len(mails_testing.outbox) == 0

        alerts = flash.get_htmx_flash_messages(authenticated_client)
        assert (
            f"Le dossier {update_request.dsApplicationId} ne peut pas être accepté : Le dossier est déjà en construction"
            in alerts["warning"]
        )

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.make_accepted")
    def test_accept_email_update_with_duplicate(self, mock_make_accepted, legit_user, authenticated_client):
        duplicate_user = users_factories.UserFactory(email="nouvel_email@example.com")
        update_request = users_factories.EmailUpdateRequestFactory(
            user__email="ancien_email@example.com",
            oldEmail="ancien_email@example.com",
            newEmail="nouvel_email@example.com",
            dsApplicationId=21268381,
            flags=[users_models.UserAccountUpdateFlag.DUPLICATE_NEW_EMAIL],
        )

        self._test_successful_request(update_request, mock_make_accepted, legit_user, authenticated_client)

        assert update_request.user.email == update_request.newEmail

        assert len(update_request.user.action_history) == 1

        assert len(update_request.user.email_history) == 1
        history = update_request.user.email_history[0]
        assert history.oldEmail == update_request.oldEmail
        assert history.newEmail == update_request.newEmail
        assert history.eventType == users_models.EmailHistoryEventTypeEnum.ADMIN_UPDATE

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(
            TransactionalEmail.PERSONAL_DATA_UPDATED_FROM_BACKOFFICE.value
        )
        assert mails_testing.outbox[0]["params"] == {
            "FIRSTNAME": update_request.user.firstName,
            "LASTNAME": update_request.user.lastName,
            "UPDATED_FIELD": "EMAIL",
        }

        db.session.refresh(duplicate_user)
        assert not duplicate_user.isActive
        assert duplicate_user.email != update_request.newEmail
        assert len(duplicate_user.action_history) == 1
        assert duplicate_user.action_history[0].actionType == history_models.ActionType.USER_SUSPENDED
        assert duplicate_user.action_history[0].authorUser == legit_user
        assert duplicate_user.action_history[0].extraData == {
            "ds_dossier_id": 21268381,
            "ds_procedure_id": 104118,
            "reason": "duplicate reported by user",
        }

    @pytest.mark.parametrize(
        "duplicate_factory",
        [users_factories.BeneficiaryFactory, users_factories.ProFactory, users_factories.AdminFactory],
    )
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.make_accepted")
    def test_do_not_accept_email_update_duplicate_with_role(
        self, mock_make_accepted, legit_user, authenticated_client, duplicate_factory
    ):
        duplicate_user = duplicate_factory(email="nouvel_email@example.com")
        update_request = users_factories.EmailUpdateRequestFactory(
            user__email="ancien_email@example.com",
            oldEmail="ancien_email@example.com",
            newEmail="nouvel_email@example.com",
        )

        response = self.post_to_endpoint(
            authenticated_client,
            ds_application_id=update_request.dsApplicationId,
            form={"motivation": "Test"},
            headers={"hx-request": "true"},
        )
        assert response.status_code == 200
        cells = html_parser.extract_plain_row(response.data, id=f"request-row-{update_request.dsApplicationId}")
        assert str(update_request.dsApplicationId) in cells[1]
        mock_make_accepted.assert_not_called()

        db.session.refresh(update_request)
        assert update_request.status == dms_models.GraphQLApplicationStates.on_going
        assert update_request.lastInstructor != legit_user
        assert update_request.user.email == update_request.oldEmail
        assert len(update_request.user.action_history) == 0
        assert len(update_request.user.email_history) == 0
        assert len(mails_testing.outbox) == 0

        db.session.refresh(duplicate_user)
        assert duplicate_user.isActive
        assert duplicate_user.email == update_request.newEmail

        alerts = flash.get_htmx_flash_messages(authenticated_client)
        assert (
            f"Le dossier {update_request.dsApplicationId} ne peut pas être accepté : l'email nouvel_email@example.com est déjà associé à un compte bénéficiaire ou ex-bénéficiaire, pro ou admin."
            in alerts["warning"]
        )

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.make_accepted")
    def test_not_instructor(self, mock_make_accepted, client):
        not_instructor = users_factories.AdminFactory()
        update_request = users_factories.UserAccountUpdateRequestFactory(
            status=dms_models.GraphQLApplicationStates.draft
        )

        client = client.with_bo_session_auth(not_instructor)
        response = self.post_to_endpoint(
            client,
            ds_application_id=update_request.dsApplicationId,
            form={"motivation": "Test"},
            headers={"hx-request": "true"},
        )
        assert response.status_code == 403

        mock_make_accepted.assert_not_called()

    def test_not_found(self, authenticated_client):
        response = self.post_to_endpoint(
            authenticated_client,
            ds_application_id=1,
            form={"motivation": "Test"},
            headers={"hx-request": "true"},
        )
        assert response.status_code == 404


class GetAskForCorrectionFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.account_update.get_ask_for_correction_form"
    endpoint_kwargs = {"ds_application_id": 1, "correction_reason": "unreadable-photo"}
    needed_permission = perm_models.Permissions.MANAGE_ACCOUNT_UPDATE_REQUEST

    # user session + update request joined with user
    expected_num_queries = 2

    def test_get_form(self, authenticated_client):
        ds_application_id = 21268381
        users_factories.UserAccountUpdateRequestFactory(dsApplicationId=ds_application_id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(self.endpoint, ds_application_id=ds_application_id, correction_reason="unreadable-photo")
            )
            assert response.status_code == 200

    def test_not_instructor(self, client):
        not_instructor = users_factories.AdminFactory()
        update_request = users_factories.UserAccountUpdateRequestFactory(
            status=dms_models.GraphQLApplicationStates.on_going
        )

        client = client.with_bo_session_auth(not_instructor)
        response = client.get(url_for(self.endpoint, ds_application_id=update_request.dsApplicationId))
        assert response.status_code == 403

    def test_not_found(self, authenticated_client):
        response = authenticated_client.get(url_for(self.endpoint, ds_application_id=1))
        assert response.status_code == 404


class AskForCorrectionTest(PostEndpointHelper):
    endpoint = "backoffice_web.account_update.ask_for_correction"
    endpoint_kwargs = {"ds_application_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_ACCOUNT_UPDATE_REQUEST

    @pytest.mark.parametrize("correction_reason", ("unreadable-photo", "missing-file", "refused-file"))
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.send_user_message")
    def test_ask_for_correction(self, mock_send_user_message, legit_user, authenticated_client, correction_reason):
        update_request = users_factories.UserAccountUpdateRequestFactory(dsApplicationId=2126838)

        mock_send_user_message.return_value = {
            "dossierEnvoyerMessage": {
                "message": {
                    "id": "Q29tbWVudGFpcmUtNTIzNjcxODc=",
                    "createdAt": "2025-01-29T15:21:17+01:00",
                },
            }
        }
        response = self.post_to_endpoint(
            authenticated_client,
            ds_application_id=update_request.dsApplicationId,
            correction_reason=correction_reason,
            headers={"hx-request": "true"},
        )

        assert response.status_code == 200
        cells = html_parser.extract_plain_row(response.data, id=f"request-row-{update_request.dsApplicationId}")
        assert str(update_request.dsApplicationId) in cells[1]
        mock_send_user_message.assert_called_once()

        db.session.refresh(update_request)
        assert update_request.status == dms_models.GraphQLApplicationStates.draft
        assert update_request.dateLastStatusUpdate == datetime.datetime(2025, 1, 29, 14, 21, 17)
        assert update_request.dateLastInstructorMessage == datetime.datetime(2025, 1, 29, 14, 21, 17)
        assert update_request.lastInstructor == legit_user

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(
            TransactionalEmail.UPDATE_REQUEST_ASK_FOR_CORRECTION.value
        )
        assert mails_testing.outbox[0]["params"] == {
            "CORRECTION_REASON": correction_reason,
            "DS_APPLICATION_NUMBER": update_request.dsApplicationId,
        }
        assert mails_testing.outbox[0]["To"] == update_request.email

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.send_user_message")
    def test_ask_for_correction_with_unknown_reason(self, mock_send_user_message, legit_user, authenticated_client):
        update_request = users_factories.UserAccountUpdateRequestFactory(dsApplicationId=2126838)

        mock_send_user_message.return_value = {
            "dossierEnvoyerMessage": {
                "message": {
                    "id": "Q29tbWVudGFpcmUtNTIzNjcxODc=",
                    "createdAt": "2025-01-29T15:21:17+01:00",
                },
            }
        }
        response = self.post_to_endpoint(
            authenticated_client,
            ds_application_id=update_request.dsApplicationId,
            correction_reason="parce-que",
            headers={"hx-request": "true"},
        )

        assert response.status_code == 200
        cells = html_parser.extract_plain_row(response.data, id=f"request-row-{update_request.dsApplicationId}")
        assert str(update_request.dsApplicationId) in cells[1]
        mock_send_user_message.assert_not_called()

        db.session.refresh(update_request)
        assert update_request.status == dms_models.GraphQLApplicationStates.on_going

        assert len(mails_testing.outbox) == 0

        alerts = flash.get_htmx_flash_messages(authenticated_client)
        assert (
            "Les données envoyées comportent des erreurs. Raison de demande de correction : Not a valid choice. ;"
            in alerts["warning"]
        )

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.send_user_message")
    def test_application_not_found(self, mock_send_user_message, legit_user, authenticated_client):
        update_request = users_factories.EmailUpdateRequestFactory(user__email="original@example.com")

        mock_send_user_message.side_effect = dms_exceptions.DmsGraphQLApiError(
            [
                {
                    "message": "DossierEnvoyerMessagePayload not found",
                    "locations": [{"line": 2, "column": 3}],
                    "path": ["dossierEnvoyerMessage"],
                    "extensions": {"code": "not_found"},
                }
            ]
        )

        response = self.post_to_endpoint(
            authenticated_client,
            ds_application_id=update_request.dsApplicationId,
            correction_reason="unreadable-photo",
            headers={"hx-request": "true"},
        )
        assert response.status_code == 200
        cells = html_parser.extract_plain_row(response.data, id=f"request-row-{update_request.dsApplicationId}")
        assert str(update_request.dsApplicationId) in cells[1]
        mock_send_user_message.assert_called_once()

        db.session.refresh(update_request)
        assert update_request.status == dms_models.GraphQLApplicationStates.on_going
        assert update_request.lastInstructor != legit_user
        assert update_request.user.email == "original@example.com"
        assert len(update_request.user.action_history) == 0
        assert len(update_request.user.email_history) == 0
        assert len(mails_testing.outbox) == 0

        alerts = flash.get_htmx_flash_messages(authenticated_client)
        assert (
            f"Le dossier {update_request.dsApplicationId} ne peut pas recevoir de demande de correction : dossier non trouvé"
            in alerts["warning"]
        )

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.execute_query")
    def test_ds_unavailable(self, mock_execute_query, authenticated_client):
        update_request = users_factories.EmailUpdateRequestFactory(user__email="original@example.com")

        mock_execute_query.side_effect = requests.exceptions.HTTPError()

        response = self.post_to_endpoint(
            authenticated_client,
            ds_application_id=update_request.dsApplicationId,
            correction_reason="unreadable-photo",
            headers={"hx-request": "true"},
        )
        assert response.status_code == 200
        cells = html_parser.extract_plain_row(response.data, id=f"request-row-{update_request.dsApplicationId}")
        assert str(update_request.dsApplicationId) in cells[1]
        mock_execute_query.assert_called_once()

        db.session.refresh(update_request)
        assert update_request.status == dms_models.GraphQLApplicationStates.on_going
        assert len(mails_testing.outbox) == 0

        alerts = flash.get_htmx_flash_messages(authenticated_client)
        assert (
            f"Le dossier {update_request.dsApplicationId} ne peut pas recevoir de demande de correction : La connexion à Démarche Numérique a échoué :"
            in alerts["warning"]
        )

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.send_user_message")
    def test_not_instructor(self, mock_send_user_message, client):
        not_instructor = users_factories.AdminFactory()
        update_request = users_factories.UserAccountUpdateRequestFactory(
            status=dms_models.GraphQLApplicationStates.on_going
        )

        client = client.with_bo_session_auth(not_instructor)
        response = self.post_to_endpoint(
            client,
            ds_application_id=update_request.dsApplicationId,
            correction_reason="unreadable-photo",
            headers={"hx-request": "true"},
        )
        assert response.status_code == 403

        mock_send_user_message.assert_not_called()

    def test_not_found(self, authenticated_client):
        response = self.post_to_endpoint(
            authenticated_client,
            ds_application_id=1,
            correction_reason="unreadable-photo",
            headers={"hx-request": "true"},
        )
        assert response.status_code == 404


class GetIdentityTheftFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.account_update.get_identity_theft_form"
    endpoint_kwargs = {"ds_application_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_ACCOUNT_UPDATE_REQUEST

    # user session + update request joined with user
    expected_num_queries = 2

    def test_get_form(self, authenticated_client):
        ds_application_id = 21268381
        users_factories.UserAccountUpdateRequestFactory(dsApplicationId=ds_application_id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, ds_application_id=ds_application_id))
            assert response.status_code == 200

    def test_not_instructor(self, client):
        not_instructor = users_factories.AdminFactory()
        update_request = users_factories.UserAccountUpdateRequestFactory(
            status=dms_models.GraphQLApplicationStates.on_going
        )

        client = client.with_bo_session_auth(not_instructor)
        response = client.get(url_for(self.endpoint, ds_application_id=update_request.dsApplicationId))
        assert response.status_code == 403

    def test_not_found(self, authenticated_client):
        response = authenticated_client.get(url_for(self.endpoint, ds_application_id=1))
        assert response.status_code == 404


class IdentityTheftTest(PostEndpointHelper):
    endpoint = "backoffice_web.account_update.identity_theft"
    endpoint_kwargs = {"ds_application_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_ACCOUNT_UPDATE_REQUEST

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.make_refused")
    def test_identity_theft(self, mock_make_refused, legit_user, authenticated_client):
        update_request = users_factories.UserAccountUpdateRequestFactory(dsApplicationId=24346321)

        mock_make_refused.return_value = {
            "id": update_request.dsApplicationId,
            "number": 24346321,
            "state": "refuse",
            "dateDerniereModification": "2025-05-21T16:53:08+02:00",
            "dateDepot": "2025-05-21T16:23:45+02:00",
            "datePassageEnConstruction": "2025-05-21T16:23:45+02:00",
            "datePassageEnInstruction": "2025-05-21T16:51:42+02:00",
            "dateTraitement": "2025-05-21T16:53:08+02:00",
            "dateDerniereCorrectionEnAttente": None,
            "dateDerniereModificationChamps": "2025-05-21T16:23:41+02:00",
        }
        response = self.post_to_endpoint(
            authenticated_client,
            ds_application_id=update_request.dsApplicationId,
            headers={"hx-request": "true"},
        )

        assert response.status_code == 200
        cells = html_parser.extract_plain_row(response.data, id=f"request-row-{update_request.dsApplicationId}")
        assert str(update_request.dsApplicationId) in cells[1]
        mock_make_refused.assert_called_once()

        db.session.refresh(update_request)
        assert update_request.status == dms_models.GraphQLApplicationStates.refused
        assert update_request.dateLastStatusUpdate == datetime.datetime(2025, 5, 21, 14, 53, 8)
        assert update_request.lastInstructor == legit_user

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(
            TransactionalEmail.UPDATE_REQUEST_IDENTITY_THEFT.value
        )
        assert mails_testing.outbox[0]["params"] == {"DS_APPLICATION_NUMBER": update_request.dsApplicationId}
        assert mails_testing.outbox[0]["To"] == update_request.email

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.make_refused")
    def test_application_not_found(self, mock_make_refused, legit_user, authenticated_client):
        update_request = users_factories.EmailUpdateRequestFactory(user__email="original@example.com")

        mock_make_refused.side_effect = dms_exceptions.DmsGraphQLApiError(
            [
                {
                    "message": "DossierEnvoyerMessagePayload not found",
                    "locations": [{"line": 2, "column": 3}],
                    "path": ["dossierEnvoyerMessage"],
                    "extensions": {"code": "not_found"},
                }
            ]
        )

        response = self.post_to_endpoint(
            authenticated_client,
            ds_application_id=update_request.dsApplicationId,
            headers={"hx-request": "true"},
        )
        assert response.status_code == 200
        cells = html_parser.extract_plain_row(response.data, id=f"request-row-{update_request.dsApplicationId}")
        assert str(update_request.dsApplicationId) in cells[1]
        mock_make_refused.assert_called_once()

        db.session.refresh(update_request)
        assert update_request.status == dms_models.GraphQLApplicationStates.on_going
        assert update_request.lastInstructor != legit_user
        assert update_request.user.email == "original@example.com"
        assert len(update_request.user.action_history) == 0
        assert len(update_request.user.email_history) == 0
        assert len(mails_testing.outbox) == 0

        alerts = flash.get_htmx_flash_messages(authenticated_client)
        assert (
            f"Le dossier {update_request.dsApplicationId} ne peut pas être rejeté : dossier non trouvé"
            in alerts["warning"]
        )

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.make_refused")
    def test_not_instructor(self, mock_make_refused, client):
        not_instructor = users_factories.AdminFactory()
        update_request = users_factories.UserAccountUpdateRequestFactory(
            status=dms_models.GraphQLApplicationStates.on_going
        )

        client = client.with_bo_session_auth(not_instructor)
        response = self.post_to_endpoint(
            client,
            ds_application_id=update_request.dsApplicationId,
            headers={"hx-request": "true"},
        )
        assert response.status_code == 403

        mock_make_refused.assert_not_called()

    def test_not_found(self, authenticated_client):
        response = self.post_to_endpoint(authenticated_client, ds_application_id=1)
        assert response.status_code == 404
