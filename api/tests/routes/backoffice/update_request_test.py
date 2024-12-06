import datetime
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
import factory
from flask import url_for
import pytest

from pcapi.connectors.dms import exceptions as dms_exceptions
from pcapi.connectors.dms import models as dms_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.routes.backoffice.filters import format_date_time

from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


class ListAccountUpdateRequestsTest(GetEndpointHelper):
    endpoint = "backoffice_web.account_update.list_account_update_requests"
    needed_permission = perm_models.Permissions.MANAGE_ACCOUNT_UPDATE_REQUEST

    # session + current_user + results + results count + FF
    expected_num_queries = 5

    def test_list_account_update_requests(self, authenticated_client):
        now = datetime.datetime.utcnow()
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
        assert rows[1]["Modification"] == "Prénom : Octave => Auguste"
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
            == "Email : juju.capulet@example.com => juju.montaigu@example.com Nom : Capulet => Montaigu"
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
        assert rows[3]["Modification"] == "Téléphone : +33222222222 => +33111111111"
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
            == f"Saisie incomplète Email en doublon Email : {update_request.oldEmail} => {update_request.newEmail} Téléphone : =>"
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
    def test_list_filter_by_status(self, authenticated_client, flags, expected_count, expected_application_ids):
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

        response = self.post_to_endpoint(authenticated_client, ds_application_id=update_request.dsApplicationId)
        assert response.status_code == 303

        db.session.refresh(update_request)
        assert update_request.status == dms_models.GraphQLApplicationStates.on_going
        assert update_request.dateLastStatusUpdate == datetime.datetime(2024, 12, 2, 17, 20, 53)
        assert update_request.lastInstructor == legit_user

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.make_on_going")
    def test_instruct_with_error(self, mock_make_on_going, legit_user, authenticated_client):
        update_request = users_factories.UserAccountUpdateRequestFactory(
            status=dms_models.GraphQLApplicationStates.draft
        )

        mock_make_on_going.side_effect = dms_exceptions.DmsGraphQLApiError([{"message": "Test!"}])

        response = self.post_to_endpoint(authenticated_client, ds_application_id=update_request.dsApplicationId)
        assert response.status_code == 303

        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "Le dossier ne peut pas passer en instruction : Test!"
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
        response = self.post_to_endpoint(client, ds_application_id=update_request.dsApplicationId)
        assert response.status_code == 403

        mock_make_on_going.assert_not_called()

    def test_instruct_not_found(self, authenticated_client):
        response = self.post_to_endpoint(authenticated_client, ds_application_id=1)
        assert response.status_code == 404
