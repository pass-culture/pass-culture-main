import logging

from pcapi import settings
from pcapi.connectors.dms import api as dms_connector_api
from pcapi.connectors.dms import models as dms_models
from pcapi.core.subscription.dms import api as dms_api
from pcapi.core.subscription.dms import repository as dms_repository
from pcapi.repository import repository


logger = logging.getLogger(__name__)


def import_dms_accepted_applications(procedure_number: int) -> None:
    logger.info(
        "[DMS] Start import of accepted applications from Démarches Simplifiées for procedure %s", procedure_number
    )

    already_processed_applications_ids = dms_repository.get_already_processed_applications_ids(procedure_number)
    client = dms_connector_api.DMSGraphQLClient()
    processed_count = 0

    for application_details in client.get_applications_with_details(
        procedure_number, dms_models.GraphQLApplicationStates.accepted
    ):
        if application_details.number in already_processed_applications_ids:
            continue
        processed_count += 1
        try:
            dms_api.handle_dms_application(application_details)
        except Exception:  # pylint: disable=broad-except
            logger.exception("[DMS] Error in script while importing application %s", application_details.number)

    logger.info(
        "[DMS] End import of accepted applications from Démarches Simplifiées for procedure %s - Processed %s applications",
        procedure_number,
        processed_count,
    )


def _import_all_dms_applications_initial_import(procedure_id: int) -> None:
    already_processed_applications_ids = dms_repository.get_already_processed_applications_ids(procedure_id)
    client = dms_connector_api.DMSGraphQLClient()
    processed_applications: list = []
    new_import_datetime = None
    for application_details in client.get_applications_with_details(procedure_id):
        if application_details.number in already_processed_applications_ids:
            continue
        try:
            dms_api.handle_dms_application(application_details)
            processed_applications.append(application_details.number)
            if new_import_datetime is None or application_details.latest_modification_datetime > new_import_datetime:
                new_import_datetime = application_details.latest_modification_datetime
        except Exception:  # pylint: disable=broad-except
            logger.exception("[DMS] Error in script while importing application %s", application_details.number)
    if new_import_datetime is None:
        # This is a normal situation outside prod, when we have few
        # applications to process (and often no applications at all).
        log = logger.error if settings.IS_PROD else logger.info
        log("[DMS] No import for procedure %s", procedure_id)
        return
    new_import_record = dms_models.LatestDmsImport(
        procedureId=procedure_id,
        latestImportDatetime=new_import_datetime,
        isProcessing=False,
        processedApplications=processed_applications,
    )
    repository.save(new_import_record)
    logger.info(
        "[DMS] End import of all applications from Démarches Simplifiées for procedure %s - Processed %s applications",
        procedure_id,
        len(processed_applications),
    )


def import_all_updated_dms_applications(procedure_number: int) -> None:
    logger.info("[DMS] Start import of all applications from Démarches Simplifiées for procedure %s", procedure_number)

    latest_dms_import_record: dms_models.LatestDmsImport | None = (
        dms_models.LatestDmsImport.query.filter(dms_models.LatestDmsImport.procedureId == procedure_number)
        .order_by(dms_models.LatestDmsImport.latestImportDatetime.desc())
        .first()
    )
    if latest_dms_import_record is None:
        logger.info("[DMS] No previous import found for procedure %s. Running first import.", procedure_number)
        _import_all_dms_applications_initial_import(procedure_number)
        logger.info(
            "[DMS] End import of all applications from Démarches Simplifiées for procedure %s", procedure_number
        )
        return

    new_import_datetime = None
    if latest_dms_import_record.isProcessing:
        logger.info("[DMS] Previous import is still processing for procedure %s", procedure_number)
        return

    latest_dms_import_record.isProcessing = True
    repository.save(latest_dms_import_record)
    processed_applications: list = []

    try:
        client = dms_connector_api.DMSGraphQLClient()

        # It is OK to pass a UTC datetime as a param to DMS.
        # Their API understands it is a UTC datetime and interprets it correctly, even if they return time in the local timezone.
        for application_details in client.get_applications_with_details(
            procedure_number, since=latest_dms_import_record.latestImportDatetime
        ):
            try:
                latest_modification_datetime = application_details.latest_modification_datetime
                if new_import_datetime is None or latest_modification_datetime > new_import_datetime:
                    new_import_datetime = latest_modification_datetime
                dms_api.handle_dms_application(application_details)
                processed_applications.append(application_details.number)
            except Exception:  # pylint: disable=broad-except
                logger.exception("[DMS] Error in script while importing application %s", application_details.number)

    except Exception as e:  # pylint: disable=broad-except
        logger.exception(
            "[DMS] Error in script while importing all applications for procedure %s", procedure_number, exc_info=e
        )
    latest_dms_import_record.isProcessing = False

    if new_import_datetime is None:
        new_import_datetime = latest_dms_import_record.latestImportDatetime

    new_import_record = dms_models.LatestDmsImport(
        procedureId=procedure_number,
        latestImportDatetime=new_import_datetime,
        isProcessing=False,
        processedApplications=processed_applications,
    )
    repository.save(latest_dms_import_record, new_import_record)
    logger.info(
        "[DMS] End import of all applications from Démarches Simplifiées for procedure %s - Processed %s applications",
        procedure_number,
        len(processed_applications),
    )
