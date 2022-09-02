import datetime
import os
import pathlib

from gql import Client
from gql import gql

from pcapi.connectors.dms import models as dms_models

from .schema import DmsSchema


class DMSGraphQLTest:
    def setup(self):
        self.client = Client(schema=DmsSchema)
        self.expected_dossier = dms_models.DmsApplicationResponse(
            annotations=[],
            champs=[
                dms_models.DmsField(id="1", label="champ 1 address", stringValue="valeur 1"),
                dms_models.DmsField(id="2", label="champ 2 piece justificative", stringValue="valeur 2"),
            ],
            dateDepot=datetime.datetime(
                2020, 3, 25, 12, 35, 51, tzinfo=datetime.timezone(datetime.timedelta(seconds=3600))
            ),
            dateDerniereModification=datetime.datetime(
                2020, 3, 25, 12, 35, 51, tzinfo=datetime.timezone(datetime.timedelta(seconds=3600))
            ),
            datePassageEnConstruction=datetime.datetime(
                2020, 3, 24, 12, 35, 51, tzinfo=datetime.timezone(datetime.timedelta(seconds=3600))
            ),
            datePassageEnInstruction=None,
            dateTraitement=None,
            demarche=dms_models.DemarcheDescriptor(id="demarche_id", number=1),
            demandeur=dms_models.Applicant(
                dateDeNaissance=datetime.date(2020, 3, 25),
                civilite=dms_models.Civility.M,
                prenom="John",
                id="personne_id",
                nom="Stiles",
            ),
            id="RandomGeneratedId",
            messages=[
                dms_models.DMSMessage(
                    created_at=datetime.datetime(
                        2020, 3, 25, 12, 35, 51, tzinfo=datetime.timezone(datetime.timedelta(seconds=3600))
                    ),
                    email="message_email@example.com",
                )
            ],
            number=1,
            state=dms_models.GraphQLApplicationStates.draft,
            usager=dms_models.Profile(email="lucille.ellingson@example.com", id="usager_id"),
        )

    def test_get_application_details_has_all_mandatory_fields(self):
        query = gql(
            (
                pathlib.Path(os.path.dirname("src/pcapi/connectors/dms/graphql/"))
                / "beneficiaries/get_single_application_details.graphql"
            ).read_text()
        )
        query_result = self.client.execute(query, variable_values={"applicationNumber": 1})

        result = dms_models.DmsApplicationResponse(**query_result["dossier"])  # pylint: disable=unsubscriptable-object
        assert result == self.expected_dossier

    def test_get_applications_with_details_has_all_mandatory_fields(self):
        query = gql(
            (
                pathlib.Path(os.path.dirname("src/pcapi/connectors/dms/graphql/"))
                / "beneficiaries/get_applications_with_details.graphql"
            ).read_text()
        )
        result_query = self.client.execute(query, variable_values={"demarcheNumber": 1})

        expected = dms_models.DmsProcessApplicationsResponse(
            pageInfo=dms_models.ApplicationPageInfo(endCursor=None, hasNextPage=False),
            nodes=[self.expected_dossier],
        )

        result = dms_models.DmsProcessApplicationsResponse(
            **result_query["demarche"]["dossiers"]  # pylint: disable=unsubscriptable-object
        )
        assert result == expected
