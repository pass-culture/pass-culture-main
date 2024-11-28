import datetime

from dateutil.relativedelta import relativedelta
from flask import url_for
import pytest

from pcapi.connectors.dms import models as dms_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.routes.backoffice.filters import format_date_time

from .helpers import html_parser
from .helpers.get import GetEndpointHelper


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
        first_name_update_request = users_factories.UserAccountUpdateRequestFactory(
            user__firstName="Octave",
            user__lastName="César",
            user__email="heritier@example.com",
            user__civility="M.",
            firstName="Jules",
            lastName="César",
            email="imperator@example.com",
            newEmail=None,
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
            newEmail="juju.montaigu@example.com",
            newLastName="Montaigu",
            dateLastInstructorMessage=now - relativedelta(days=3),
            dateLastUserMessage=None,
            dateLastStatusUpdate=now - relativedelta(days=1),
        )
        phone_number_request = users_factories.UserAccountUpdateRequestFactory(
            user__firstName="Jean-Pierre",
            user__lastName="Impair",
            user__email="impair@example.com",
            user__phoneNumber="+33222222222",
            firstName="Jean-Pierre",
            lastName="Impair",
            email="impair@example.com",
            newEmail=None,
            newPhoneNumber="+33111111111",
            dateLastInstructorMessage=now - relativedelta(days=3),
            dateLastUserMessage=now - relativedelta(days=1),
            dateLastStatusUpdate=now - relativedelta(days=2),
        )
        unknown_user_request = users_factories.UserAccountUpdateRequestFactory(
            status=dms_models.GraphQLApplicationStates.draft,
            user=None,
            firstName="Martin",
            lastName="Connu",
            email="martinconnu@example.com",
            newEmail=None,
            newLastName="Inconnu",
            dateLastInstructorMessage=None,
            dateLastUserMessage=None,
            dateLastStatusUpdate=now,
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 4

        assert rows[0]["Dossier"] == str(unknown_user_request.dsApplicationId)
        assert rows[0]["État"] == "En construction"
        assert rows[0]["Date de dernière MàJ"] == f"{format_date_time(unknown_user_request.dateLastStatusUpdate)}"
        assert rows[0]["Date des derniers messages"] == ""
        assert (
            rows[0]["Demandeur"]
            == f"Martin Connu né(e) le {unknown_user_request.birthDate.strftime('%d/%m/%Y')} ({unknown_user_request.applicant_age} ans) martinconnu@example.com"
        )
        assert rows[0]["Jeune"] == "Compte jeune non trouvé"
        assert rows[0]["Modification"] == "Nom : => Inconnu"
        assert rows[0]["Instructeur"] == "Instructeur du Backoffice"

        assert rows[1]["Dossier"] == str(first_name_update_request.dsApplicationId)
        assert rows[1]["État"] == "En instruction"
        assert rows[1]["Date de dernière MàJ"] == f"{format_date_time(first_name_update_request.dateLastStatusUpdate)}"
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
            == f"Octave César ({first_name_update_request.user.id}) né le {first_name_update_request.user.birth_date.strftime('%d/%m/%Y')} ({last_name_and_email_update_request.user.age} ans) heritier@example.com"
        )
        assert rows[1]["Modification"] == "Prénom : Octave => Auguste"
        assert rows[1]["Instructeur"] == "Instructeur du Backoffice"

        assert rows[2]["Dossier"] == str(last_name_and_email_update_request.dsApplicationId)
        assert rows[2]["État"] == "En instruction"
        assert (
            rows[2]["Date de dernière MàJ"]
            == f"{format_date_time(last_name_and_email_update_request.dateLastStatusUpdate)}"
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
            == f"Juliette Capulet ({last_name_and_email_update_request.user.id}) née le {last_name_and_email_update_request.user.birth_date.strftime('%d/%m/%Y')} ({last_name_and_email_update_request.user.age} ans) juju.capulet@example.com"
        )
        assert (
            rows[2]["Modification"]
            == "Email : juju.capulet@example.com => juju.montaigu@example.com Nom : Capulet => Montaigu"
        )
        assert rows[2]["Instructeur"] == "Instructeur du Backoffice"

        assert rows[3]["Dossier"] == str(phone_number_request.dsApplicationId)
        assert rows[3]["État"] == "En instruction"
        assert rows[3]["Date de dernière MàJ"] == f"{format_date_time(phone_number_request.dateLastStatusUpdate)}"
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
            == f"Jean-Pierre Impair ({phone_number_request.user.id}) né(e) le {phone_number_request.user.birth_date.strftime('%d/%m/%Y')} ({phone_number_request.user.age} ans) impair@example.com"
        )
        assert rows[3]["Modification"] == "Téléphone : +33222222222 => +33111111111"
        assert rows[3]["Instructeur"] == "Instructeur du Backoffice"

    def test_list_filter_by_email(self, authenticated_client):
        specific_submitter_email_request = users_factories.UserAccountUpdateRequestFactory(
            user__email="notimportant@example.com",
            email="that.specific.email@example.com",
            newEmail=None,
            newFirstName="notimportant",
        )
        specific_new_email_request = users_factories.UserAccountUpdateRequestFactory(
            newEmail="that.specific.email@example.com"
        )
        specific_user_email_request = users_factories.UserAccountUpdateRequestFactory(
            user__email="that.specific.email@example.com", newEmail=None, newFirstName="notimportant"
        )
        users_factories.UserAccountUpdateRequestFactory()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q="that.specific.email@example.com"))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 3

        assert {row["Dossier"] for row in rows} == {
            str(request.dsApplicationId)
            for request in (
                specific_submitter_email_request,
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
        users_factories.UserAccountUpdateRequestFactory(
            dsApplicationId=100001, newEmail=None, newPhoneNumber="+33111111111"
        )
        users_factories.UserAccountUpdateRequestFactory(dsApplicationId=100002, user__phoneNumber="+33111111111")
        users_factories.UserAccountUpdateRequestFactory()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=q))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == expected_count
        assert {row["Dossier"] for row in rows} == expected_application_ids

    def test_list_filter_by_id(self, authenticated_client):
        specific_user_request = users_factories.UserAccountUpdateRequestFactory()
        specific_application_request = users_factories.UserAccountUpdateRequestFactory(
            dsApplicationId=specific_user_request.user.id,
        )
        users_factories.UserAccountUpdateRequestFactory()
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
            newEmail=None,
            firstName="Aucun",
            lastName="Rapport",
            user=None,
            newFirstName="Martin",
            newLastName="Cognito",
        )
        users_factories.UserAccountUpdateRequestFactory(
            dsApplicationId=100002,
            newEmail=None,
            firstName="Jean-Martin",
            lastName="Rapport",
            newFirstName="Aucun",
            newLastName="Incognito",
        )
        users_factories.UserAccountUpdateRequestFactory(
            dsApplicationId=100003,
            newEmail=None,
            firstName="Aucun",
            lastName="Rapport",
            user__firstName="Martine",
            user__lastName="Alaplage",
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
        users_factories.UserAccountUpdateRequestFactory(
            dsApplicationId=100001,
            dateLastUserMessage=None,
            dateLastStatusUpdate=now,
        )
        users_factories.UserAccountUpdateRequestFactory(
            dsApplicationId=100002,
            dateLastUserMessage=now,
            dateLastStatusUpdate=now - relativedelta(days=2),
        )
        users_factories.UserAccountUpdateRequestFactory(
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
        users_factories.UserAccountUpdateRequestFactory(dsApplicationId=100001)
        users_factories.UserAccountUpdateRequestFactory(dsApplicationId=100002, user=None)

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
        users_factories.UserAccountUpdateRequestFactory(
            dsApplicationId=100001, status=dms_models.GraphQLApplicationStates.draft
        )

        users_factories.UserAccountUpdateRequestFactory(
            dsApplicationId=100002, status=dms_models.GraphQLApplicationStates.on_going
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, status=status))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == expected_count
        assert {row["Dossier"] for row in rows} == expected_application_ids

    @pytest.mark.parametrize(
        "update_type, expected_count, expected_application_ids",
        (
            ("first_name", 1, {"100001"}),
            ("last_name", 2, {"100001", "100002"}),
            (["first_name", "email"], 0, set()),
            (["last_name", "email"], 1, {"100002"}),
        ),
    )
    def test_list_filter_by_update_type(
        self, authenticated_client, update_type, expected_count, expected_application_ids
    ):
        users_factories.UserAccountUpdateRequestFactory(
            dsApplicationId=100001,
            newEmail=None,
            newFirstName="Martin",
            newLastName="Cognito",
        )
        users_factories.UserAccountUpdateRequestFactory(
            dsApplicationId=100002,
            newEmail="shakespeare@example.com",
            newLastName="Montaigu",
        )
        users_factories.UserAccountUpdateRequestFactory(
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
        update_request = users_factories.UserAccountUpdateRequestFactory(lastInstructor=instructor)
        users_factories.UserAccountUpdateRequestFactory(lastInstructor=users_factories.AdminFactory())

        # +1 query to fill in instructor filter
        with assert_num_queries(self.expected_num_queries + 1):
            response = authenticated_client.get(url_for(self.endpoint, last_instructor=instructorId))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["Dossier"] == str(update_request.dsApplicationId)
