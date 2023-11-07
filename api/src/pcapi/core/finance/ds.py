import datetime
import logging

from pcapi.connectors.dms import api as ds_api
from pcapi.connectors.dms import models as ds_models
from pcapi.connectors.dms.serializer import ApplicationDetailNewJourney
from pcapi.connectors.dms.serializer import ApplicationDetailOldJourney
from pcapi.domain.demarches_simplifiees import parse_raw_bank_info_data
from pcapi.infrastructure.repository.bank_informations.bank_informations_sql_repository import (
    BankInformationsSQLRepository,
)
from pcapi.infrastructure.repository.venue.venue_with_basic_information.venue_with_basic_information_sql_repository import (
    VenueWithBasicInformationSQLRepository,
)
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
from pcapi.use_cases.save_venue_bank_informations import ImportBankAccountFactory
from pcapi.use_cases.save_venue_bank_informations import PROCEDURE_ID_VERSION_MAP
from pcapi.use_cases.save_venue_bank_informations import SaveVenueBankInformationsFactory


logger = logging.getLogger(__name__)


def import_ds_bank_information_applications(procedure_number: int, ignore_previous: bool = False) -> None:
    logger.info("[DS] Start import of all applications from Démarches Simplifiées for procedure %s", procedure_number)
    last_import = (
        ds_models.LatestDmsImport.query.filter(ds_models.LatestDmsImport.procedureId == procedure_number)
        .order_by(ds_models.LatestDmsImport.latestImportDatetime.desc())
        .first()
    )
    if last_import and last_import.isProcessing:
        if datetime.datetime.utcnow() < last_import.latestImportDatetime + datetime.timedelta(days=1):
            logger.info("[DS] Procedure %s is already being processed.", procedure_number)
        else:
            last_import.isProcessing = False
            db.session.add(last_import)
            db.session.commit()
            logger.info(
                "[DS] Procedure %s stopped after having been in treatment since %s",
                procedure_number,
                last_import.latestImportDatetime,
            )

    else:
        since = last_import.latestImportDatetime if last_import else None
        update_ds_applications_for_procedure(
            procedure_number=procedure_number, since=None if ignore_previous else since
        )


def update_ds_applications_for_procedure(procedure_number: int, since: datetime.datetime | None) -> None:
    logger.info("[DS] Started processing Bank Account procedure %s", procedure_number)

    current_import = ds_models.LatestDmsImport(
        procedureId=procedure_number,
        latestImportDatetime=datetime.datetime.utcnow(),
        isProcessing=True,
        processedApplications=[],
    )
    db.session.add(current_import)
    db.session.commit()

    ds_client = ds_api.DMSGraphQLClient()
    application_numbers = []
    procedure_version = PROCEDURE_ID_VERSION_MAP[str(procedure_number)]

    for node in ds_client.get_pro_bank_nodes_states(procedure_number=procedure_number, since=since):
        data = parse_raw_bank_info_data(node, procedure_version)
        try:
            SaveVenueBankInformations = SaveVenueBankInformationsFactory.get(procedure_id=str(procedure_number))
            save_venue_bank_informations = SaveVenueBankInformations(
                venue_repository=VenueWithBasicInformationSQLRepository(),
                bank_informations_repository=BankInformationsSQLRepository(),
            )
            save_venue_bank_informations.execute(
                application_details=ApplicationDetailOldJourney(**{"application_type": procedure_version, **data})
            )
            if FeatureToggle.WIP_ENABLE_DOUBLE_MODEL_WRITING.is_active() and procedure_version in (4, 5):
                ImportBankAccount = ImportBankAccountFactory.get(procedure_version)
                application_details = ApplicationDetailNewJourney(**{"application_type": procedure_version, **data})
                ImportBankAccount(application_details).execute()
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.exception(
                "[DS] Application parsing failed with error %s",
                str(exc),
                extra={
                    "application_number": node.get("number"),
                    "application_scalar_id": node.get("id"),
                    "procedure_number": procedure_number,
                },
            )
        else:
            application_numbers.append(node["number"])

    current_import.processedApplications = application_numbers
    current_import.isProcessing = False
    db.session.commit()

    logger.info(
        "[DS] Finished processing Bank Account procedure %s.",
        procedure_number,
        extra={"procedure_number": procedure_number},
    )
