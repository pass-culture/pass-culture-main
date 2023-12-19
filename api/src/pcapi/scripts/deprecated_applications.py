import argparse
from collections import namedtuple
from typing import Generator

import gql
from pydantic.v1 import BaseModel

from pcapi.app import app
from pcapi.connectors.dms.api import DMSGraphQLClient
from pcapi.connectors.dms.models import GraphQLApplicationStates


app.app_context().push()


class DSInstructor(BaseModel):
    id: str
    email: str


class pageInfo(BaseModel):
    endCursor: str | None
    hasNextPage: bool


class Node(BaseModel):
    id: str
    state: GraphQLApplicationStates
    instructeurs: list[DSInstructor]


class DSResponse(BaseModel):
    nodes: list[Node]
    pageInfo: pageInfo


DeprecatedApplication = namedtuple("DeprecatedApplication", ["application_id", "state", "instructor_id", "motivation"])


def str2states(value: str) -> GraphQLApplicationStates:
    try:
        return GraphQLApplicationStates(value)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"`{value}` is not a valid GraphQLApplicationStates, following only exists: {list(state.value for state in GraphQLApplicationStates)}"
        )


def fetch_deprecated_applications(
    procedure_id: int, status: GraphQLApplicationStates, cursor: str | None = None
) -> Generator[DeprecatedApplication, None, None]:
    query = """
            query getApplicationsToMarkWithoutContinuation($demarcheNumber: Int!, $state: DossierState, $archived: Boolean, $after: String) {
          demarche(number: $demarcheNumber) {
            dossiers(archived: $archived, state: $state, after: $after) {
              nodes {
                state
                id
                instructeurs {
                  id
                  email
                }
              }
              pageInfo {
                endCursor
                hasNextPage
              }
            }
          }
        }
        """

    variables = {"demarcheNumber": procedure_id, "state": status.value, "archived": False}
    if cursor is not None:
        variables.update({"after": cursor})

    client = DMSGraphQLClient()
    raw_response = client.client.execute(gql.gql(query), variable_values=variables)
    response = DSResponse(**raw_response["demarche"]["dossiers"])  # pylint: disable=unsubscriptable-object

    for node in response.nodes:
        if not node.instructeurs:
            print(f"None instructors for this application ({node.id} - {node.state}), using default one.")
            instructor_id = DEFAULT_INSTRUCTOR_ID
        else:
            print(
                f"Found {len(node.instructeurs)} instructor for this application ({node.id} - {node.state}), using {node.instructeurs[0].email}"
            )
            instructor_id = node.instructeurs[0].id

        application_id = node.id
        state = node.state
        motivation = (
            "Deprecated application - Set `without_continuation` and archived through automated process (PC-24034)"
        )
        yield DeprecatedApplication(
            application_id=application_id, state=state, instructor_id=instructor_id, motivation=motivation
        )

    if response.pageInfo.hasNextPage is True:
        yield from fetch_deprecated_applications(
            procedure_id=procedure_id,
            status=status,
            cursor=response.pageInfo.endCursor,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Mark without continuation and archive related applications given a procedure ID and status"
    )
    parser.add_argument("--procedure_id", type=int, required=True)
    parser.add_argument("--status", type=str2states, action="extend", nargs="+", required=True)
    parser.add_argument(
        "--default-instructor-id",
        type=str,
        required=True,
        help="`draft` don't have instructor assign yet. We need a default one to change his state and archived it.",
    )
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    DEFAULT_INSTRUCTOR_ID = args.default_instructor_id

    if args.dry_run is True:
        print("--------- dry run ------------")

    applications_processed = 0

    graphql_client = DMSGraphQLClient()
    for given_status in args.status:
        for i, application in enumerate(
            fetch_deprecated_applications(procedure_id=args.procedure_id, status=given_status)
        ):
            if not args.dry_run:
                if application.state == GraphQLApplicationStates.draft:
                    # DS fordid us to mark an application `without_continuation` if not already in instruction
                    graphql_client.make_on_going(application.application_id, application.instructor_id)
                graphql_client.mark_without_continuation(
                    application.application_id, application.instructor_id, application.motivation
                )
                graphql_client.archive_application(application.application_id, application.instructor_id)

            applications_processed += 1

    print(f"Processed {applications_processed} applications")
