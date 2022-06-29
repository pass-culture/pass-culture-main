import logging

from pcapi.connectors.dms import api as dms_connector_api
from pcapi.connectors.dms import models as dms_models
from pcapi.core.subscription.dms import api as dms_api
from pcapi.core.subscription.dms import repository as dms_repository


logger = logging.getLogger(__name__)


def import_dms_accepted_applications(procedure_id: int) -> None:
    logger.info("[DMS] Start import from Démarches Simplifiées for procedure %s", procedure_id)

    already_processed_applications_ids = dms_repository.get_already_processed_applications_ids(procedure_id)
    client = dms_connector_api.DMSGraphQLClient()
    processed_count = 0

    for application_details in client.get_applications_with_details(
        procedure_id, dms_models.GraphQLApplicationStates.accepted
    ):
        if application_details.number in already_processed_applications_ids:
            continue
        processed_count += 1
        try:
            dms_api.handle_dms_application(application_details)
        except Exception:  # pylint: disable=broad-except
            logger.exception("[DMS] Error in script while importing application %s", application_details.number)

    logger.info(
        "[DMS] End import from Démarches Simplifiées for procedure %s - Processed %s applications",
        procedure_id,
        processed_count,
    )
