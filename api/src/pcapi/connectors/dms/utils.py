import datetime
import logging
import typing

from pcapi.connectors.dms import models as ds_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def import_ds_applications(
    procedure_number: int,
    callback: typing.Callable[[int, datetime.datetime | None], list],
    ignore_previous: bool = False,
) -> None:
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

        current_import = ds_models.LatestDmsImport(
            procedureId=procedure_number,
            latestImportDatetime=datetime.datetime.utcnow(),
            isProcessing=True,
            processedApplications=[],
        )
        db.session.add(current_import)
        db.session.commit()

        application_numbers = callback(procedure_number, None if ignore_previous else since)

        current_import.processedApplications = application_numbers
        current_import.isProcessing = False
        db.session.commit()
