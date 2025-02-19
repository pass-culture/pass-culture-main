import datetime
from unittest.mock import patch

import time_machine

from pcapi.connectors.dms import api as api_dms
from pcapi.connectors.dms import api as dms_api
from pcapi.connectors.dms import models as dms_models

from tests.scripts.beneficiary.fixture import make_graphql_application
from tests.scripts.beneficiary.fixture import make_graphql_deleted_applications
from tests.scripts.beneficiary.fixture import make_single_application


DS_MAKE_ON_GOING_RESPONSE = {
    "dossierPasserEnInstruction": {
        "dossier": {
            "id": "RG9zc2llci0yMjU3MDE4NQ==",
            "number": 22570185,
            "state": "en_instruction",
            "dateDerniereModification": "2025-02-18T19:22:04+01:00",
            "dateDepot": "2025-02-18T18:06:47+01:00",
            "datePassageEnConstruction": "2025-02-18T18:06:47+01:00",
            "datePassageEnInstruction": "2025-02-18T19:21:08+01:00",
            "dateTraitement": None,
            "dateDerniereCorrectionEnAttente": None,
            "dateDerniereModificationChamps": "2025-02-18T18:05:45+01:00",
        },
        "errors": None,
    }
}

DS_MAKE_REFUSED_RESPONSE = {
    "dossierRefuser": {
        "dossier": {
            "id": "RG9zc2llci0yMjU3MDE4NQ==",
            "number": 22570185,
            "state": "refuse",
            "dateDerniereModification": "2025-02-18T19:22:04+01:00",
            "dateDepot": "2025-02-18T18:06:47+01:00",
            "datePassageEnConstruction": "2025-02-18T18:06:47+01:00",
            "datePassageEnInstruction": "2025-02-18T19:21:08+01:00",
            "dateTraitement": "2025-02-18T19:22:04+01:00",
            "dateDerniereCorrectionEnAttente": None,
            "dateDerniereModificationChamps": "2025-02-18T18:05:45+01:00",
        },
        "errors": None,
    }
}


class GraphqlResponseTest:
    @patch.object(api_dms.DMSGraphQLClient, "execute_query")
    def test_get_applications_with_details(self, execute_query):
        execute_query.side_effect = [
            make_graphql_application(123, "accepte", full_graphql_response=True, has_next_page=True),
            make_graphql_application(456, "accepte", full_graphql_response=True),
        ]

        client = api_dms.DMSGraphQLClient()
        results = list(client.get_applications_with_details(123, dms_models.GraphQLApplicationStates.accepted))
        assert client.execute_query.call_count == 2
        assert len(results) == 2
        assert results[0].messages == [
            dms_models.DMSMessage(
                created_at=datetime.datetime(2021, 9, 14, 14, 2, 33), email="contact@demarches-simplifiees.fr"
            )
        ]
        assert results[0].state == dms_models.GraphQLApplicationStates.accepted

    @patch.object(api_dms.DMSGraphQLClient, "execute_query")
    def test_archive_application(self, execute_query):
        technical_id = "RandomApplicationId"

        execute_query.return_value = {"dossierArchiver": {"dossier": {"id": technical_id}, "errors": None}}
        client = api_dms.DMSGraphQLClient()
        client.archive_application("ApplicationTechnicalId", "InstructorTechId")

        assert client.execute_query.call_count == 1

    @patch.object(api_dms.DMSGraphQLClient, "execute_query")
    def test_get_single_application_details(self, execute_query):
        execute_query.return_value = make_single_application(12, state="accepte")

        client = api_dms.DMSGraphQLClient()
        result = client.get_single_application_details(42)

        assert client.execute_query.call_count == 1
        assert result.messages == [
            dms_models.DMSMessage(
                created_at=datetime.datetime(2021, 9, 14, 14, 2, 33), email="contact@demarches-simplifiees.fr"
            )
        ]
        assert result.state == dms_models.GraphQLApplicationStates.accepted

    @patch.object(api_dms.DMSGraphQLClient, "execute_query")
    def test_update_annotations(self, execute_query):
        execute_query.return_value = {
            "dossierModifierAnnotationText": {"annotation": {"id": "XXXXXXXXX"}, "errors": None}
        }
        client = api_dms.DMSGraphQLClient()
        client.update_text_annotation(
            "dossier_id", "instructeur_id", "error_annotation_id", "Il y a une grosse erreur ici"
        )

        assert client.execute_query.call_count == 1

    @patch.object(
        api_dms.DMSGraphQLClient,
        "execute_query",
        return_value={"dossierAjouterLabel": {"errors": None, "label": {"id": "TGFiZWwtMzE5NjAw", "name": "Urgent"}}},
    )
    def test_add_label_to_application(self, execute_query):
        client = api_dms.DMSGraphQLClient()
        client.add_label_to_application("RG9zc2llci0yMjA2MDYyMw==", "TGFiZWwtMzE5NjAw")

        execute_query.assert_called_once_with(
            "add_label", variables={"input": {"dossierId": "RG9zc2llci0yMjA2MDYyMw==", "labelId": "TGFiZWwtMzE5NjAw"}}
        )

    @patch.object(
        api_dms.DMSGraphQLClient,
        "execute_query",
        return_value={
            "dossierAjouterLabel": {"errors": [{"message": "Ce label est déjà associé au dossier"}], "label": None}
        },
    )
    def test_add_label_to_application_already_set(self, execute_query):
        client = api_dms.DMSGraphQLClient()
        client.add_label_to_application("RG9zc2llci0yMjA2MDYyMw==", "TGFiZWwtMzE5NjAw")

        execute_query.assert_called_once_with(
            "add_label", variables={"input": {"dossierId": "RG9zc2llci0yMjA2MDYyMw==", "labelId": "TGFiZWwtMzE5NjAw"}}
        )

    @time_machine.travel("2020-01-01")
    @patch.object(api_dms.DMSGraphQLClient, "execute_query")
    def test_get_deleted_applications(self, execute_query):
        procedure_number = 1
        execute_query.return_value = make_graphql_deleted_applications(procedure_number, application_numbers=[1, 2, 3])

        client = api_dms.DMSGraphQLClient()

        deleted_application_count = 0
        for result in client.get_deleted_applications(procedure_number):
            assert result.deletion_datetime == datetime.datetime(2021, 10, 1, 22, 0, 0)
            assert result.reason == "user_request"
            deleted_application_count += 1

        assert client.execute_query.call_count == 1
        assert deleted_application_count == 3

    @patch.object(api_dms.DMSGraphQLClient, "execute_query", return_value=DS_MAKE_REFUSED_RESPONSE)
    def test_make_refused(self, execute_query):
        client = api_dms.DMSGraphQLClient()
        client.make_refused("RG9zc2llci0yMjU3MDE4NQ==", "SW5zdHJ1Y3RldXItMTAyOTgz", "Test")

        execute_query.assert_called_once_with(
            dms_api.MAKE_REFUSED_MUTATION_NAME,
            variables={
                "input": {
                    "dossierId": "RG9zc2llci0yMjU3MDE4NQ==",
                    "instructeurId": "SW5zdHJ1Y3RldXItMTAyOTgz",
                    "motivation": "Test",
                    "disableNotification": False,
                }
            },
        )

    @patch.object(
        api_dms.DMSGraphQLClient, "execute_query", side_effect=[DS_MAKE_ON_GOING_RESPONSE, DS_MAKE_REFUSED_RESPONSE]
    )
    def test_make_refused_when_draft(self, execute_query):
        client = api_dms.DMSGraphQLClient()
        client.make_refused("RG9zc2llci0yMjU3MDE4NQ==", "SW5zdHJ1Y3RldXItMTAyOTgz", "Test", from_draft=True)

        execute_query.assert_called()
        assert execute_query.call_count == 2

        assert execute_query.call_args_list[0].args == (dms_api.MAKE_ON_GOING_MUTATION_NAME,)
        assert execute_query.call_args_list[0].kwargs["variables"] == {
            "input": {
                "dossierId": "RG9zc2llci0yMjU3MDE4NQ==",
                "instructeurId": "SW5zdHJ1Y3RldXItMTAyOTgz",
                "disableNotification": True,
            }
        }

        assert execute_query.call_args_list[1].args == (dms_api.MAKE_REFUSED_MUTATION_NAME,)
        assert execute_query.call_args_list[1].kwargs["variables"] == {
            "input": {
                "dossierId": "RG9zc2llci0yMjU3MDE4NQ==",
                "instructeurId": "SW5zdHJ1Y3RldXItMTAyOTgz",
                "motivation": "Test",
                "disableNotification": False,
            }
        }
