import logging

from pcapi import settings
from pcapi.connectors.dms import api as api_dms
from pcapi.connectors.dms import models as dms_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.models.beneficiary_import import BeneficiaryImport
from pcapi.models.beneficiary_import_status import BeneficiaryImportStatus
from pcapi.models.beneficiary_import_status import ImportStatus


logger = logging.getLogger()


def archive_applications(procedure_id: int, dry_run: bool = True) -> None:
    total_applications = 0
    archived_applications = 0
    client = api_dms.DMSGraphQLClient()
    for application_details in client.get_applications_with_details(
        procedure_id, dms_models.GraphQLApplicationStates.accepted
    ):
        application_techid = application_details.id
        application_number = application_details.number
        total_applications += 1
        bi = (
            BeneficiaryImport.query.join(users_models.User, users_models.User.id == BeneficiaryImport.beneficiaryId)
            .join(BeneficiaryImportStatus, BeneficiaryImportStatus.beneficiaryImportId == BeneficiaryImport.id)
            .filter(BeneficiaryImport.applicationId == application_number, BeneficiaryImport.sourceId == procedure_id)
            .filter(BeneficiaryImportStatus.status == ImportStatus.CREATED)
        ).one_or_none()
        if bi and bi.beneficiary.has_beneficiary_role:
            instructeur_techid = settings.DMS_ENROLLMENT_INSTRUCTOR
            if not dry_run:
                client.archive_application(application_techid, instructeur_techid)
            logger.info(
                "Archiving application %d on procedure %d for user_id %d",
                application_number,
                procedure_id,
                bi.beneficiaryId,
            )
            archived_applications += 1
        # remove object from SQLAlchemy session's cache and release read locks
        db.session.rollback()
    logger.info(
        "script ran : total applications : %d to archive applications : %d", total_applications, archived_applications
    )
