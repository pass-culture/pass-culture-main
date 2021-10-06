import logging

from pcapi.connectors.api_demarches_simplifiees import DMSGraphQLClient
from pcapi.connectors.api_demarches_simplifiees import GraphQLApplicationStates
from pcapi.core.users import models as users_models
from pcapi.models.beneficiary_import import BeneficiaryImport
from pcapi.models.beneficiary_import_status import BeneficiaryImportStatus
from pcapi.models.beneficiary_import_status import ImportStatus


logger = logging.getLogger()


def archive_applications(procedure_id: int, dry_run: bool = True) -> None:
    total_applications = 0
    archived_applications = 0
    client = DMSGraphQLClient()
    for application_details in client.get_applications_with_details(procedure_id, GraphQLApplicationStates.accepted):
        application_techid = application_details["id"]
        application_number = application_details["number"]
        total_applications += 1
        bi = (
            BeneficiaryImport.query.join(BeneficiaryImportStatus)
            .join(users_models.User)
            .filter(BeneficiaryImport.applicationId == application_number, BeneficiaryImport.sourceId == procedure_id)
            .filter(BeneficiaryImportStatus.status == ImportStatus.CREATED)
        ).one_or_none()
        if bi:
            instructeur_techid = application_details["instructeurs"][0]["id"]
            if not dry_run:
                client.archive_application(application_techid, instructeur_techid)
            logger.info(
                "Archiving application %d on procedure %d for user_id %d",
                application_number,
                procedure_id,
                bi.beneficiaryId,
            )
            archived_applications += 1
    logger.info(
        "script ran : total applications : %d to archive applications : %d", total_applications, archived_applications
    )
