import datetime

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
            dateLastUserMessage=None,
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
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 4

        assert rows[0]["Dossier"] == str(unknown_user_request.dsApplicationId)
        assert rows[0]["État"] == "En construction"
        assert rows[0]["Date des derniers messages"] == ""
        assert (
            rows[0]["Demandeur"]
            == f"Martin Connu né(e) le {unknown_user_request.birthDate.strftime('%d/%m/%Y')} ({unknown_user_request.applicant_age} ans) martinconnu@example.com"
        )
        assert rows[0]["Jeune"] == "Compte jeune non trouvé"
        assert rows[0]["Modification"] == "Nom : => Inconnu"
        assert rows[0]["Instructeur"] == "Instructeur du Backoffice"

        assert rows[1]["Dossier"] == str(phone_number_request.dsApplicationId)
        assert rows[1]["État"] == "En instruction"
        assert (
            rows[1]["Date des derniers messages"]
            == f"Demandeur : {format_date_time(phone_number_request.dateLastUserMessage)} Instructeur : {format_date_time(phone_number_request.dateLastInstructorMessage)}"
        )
        assert (
            rows[1]["Demandeur"]
            == f"Jean-Pierre Impair né(e) le {phone_number_request.birthDate.strftime('%d/%m/%Y')} ({phone_number_request.applicant_age} ans) impair@example.com"
        )
        assert (
            rows[1]["Jeune"]
            == f"Jean-Pierre Impair ({phone_number_request.user.id}) né(e) le {phone_number_request.user.birth_date.strftime('%d/%m/%Y')} ({phone_number_request.user.age} ans) impair@example.com"
        )
        assert rows[1]["Modification"] == "Téléphone : +33222222222 => +33111111111"
        assert rows[1]["Instructeur"] == "Instructeur du Backoffice"

        assert rows[2]["Dossier"] == str(last_name_and_email_update_request.dsApplicationId)
        assert rows[2]["État"] == "En instruction"
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

        assert rows[3]["Dossier"] == str(first_name_update_request.dsApplicationId)
        assert rows[3]["État"] == "En instruction"
        assert (
            rows[3]["Date des derniers messages"]
            == f"Demandeur : {format_date_time(first_name_update_request.dateLastUserMessage)}"
        )
        assert (
            rows[3]["Demandeur"]
            == f"Jules César né(e) le {first_name_update_request.birthDate.strftime('%d/%m/%Y')} ({first_name_update_request.applicant_age} ans) imperator@example.com"
        )
        assert (
            rows[3]["Jeune"]
            == f"Octave César ({first_name_update_request.user.id}) né le {first_name_update_request.user.birth_date.strftime('%d/%m/%Y')} ({last_name_and_email_update_request.user.age} ans) heritier@example.com"
        )
        assert rows[3]["Modification"] == "Prénom : Octave => Auguste"
        assert rows[3]["Instructeur"] == "Instructeur du Backoffice"
