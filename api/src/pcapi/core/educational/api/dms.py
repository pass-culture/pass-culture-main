from datetime import datetime
import logging

import pytz

from pcapi.connectors.dms import api as dms_api
from pcapi.connectors.dms import models as dms_models
from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def import_dms_applications(procedure_number: int) -> None:
    """import dms applications for eac status"""
    previous_import = _get_previous_import(procedure_number)
    if previous_import and previous_import.isProcessing:
        logger.info(
            "[DMS] Procedure %s is already being processed.",
            procedure_number,
            extra={
                "procedure_number": procedure_number,
            },
        )
    else:
        since = previous_import.latestImportDatetime if previous_import else None
        update_dms_applications_for_procedure(
            procedure_number=procedure_number,
            since=since,
        )


def update_dms_applications_for_procedure(procedure_number: int, since: datetime | None) -> None:
    logger.info(
        "[DMS] Started processing EAC procedure %s.",
        procedure_number,
        extra={
            "procedure_number": procedure_number,
        },
    )

    current_import = dms_models.LatestDmsImport(
        procedureId=procedure_number,
        latestImportDatetime=datetime.utcnow(),
        isProcessing=True,
        processedApplications=[],
    )
    db.session.add(current_import)
    db.session.commit()

    dms_client = dms_api.DMSGraphQLClient()
    applications_number = []

    for node in dms_client.get_eac_nodes_siret_states(procedure_number=procedure_number, since=since):
        try:
            _get_or_create_application(procedure_number=procedure_number, node=node)
        except Exception as exp:  # pylint: disable=broad-exception-caught
            logger.exception(
                "[DMS] Application parsing failed with error %s",
                str(exp),
                extra={
                    "application_number": node.get("number"),
                    "application_scalar_id": node.get("id"),
                    "procedure_number": procedure_number,
                },
            )
        else:
            applications_number.append(node["number"])

    current_import.processedApplications = applications_number
    current_import.isProcessing = False
    db.session.commit()

    logger.info(
        "[DMS] Finished processing EAC procedure %s.",
        procedure_number,
        extra={
            "procedure_number": procedure_number,
        },
    )


def _get_or_create_application(procedure_number: int, node: dict) -> None:
    data = {
        "state": node["state"],
        "procedure": procedure_number,
        "application": node["number"],
        "siret": node["demandeur"].get("siret"),
        "lastChangeDate": _convert_iso_string_to_naive_utc_datetime(node["dateDerniereModification"]),
        "depositDate": _convert_iso_string_to_naive_utc_datetime(node["dateDepot"]),
        "expirationDate": _convert_iso_string_to_naive_utc_datetime(node["dateExpiration"]),
        "buildDate": _convert_iso_string_to_naive_utc_datetime(node["datePassageEnConstruction"]),
        "instructionDate": _convert_iso_string_to_naive_utc_datetime(node["datePassageEnInstruction"]),
        "processingDate": _convert_iso_string_to_naive_utc_datetime(node["dateTraitement"]),
        "userDeletionDate": _convert_iso_string_to_naive_utc_datetime(node["dateSuppressionParUsager"]),
    }

    if not data["siret"]:
        logger.info(
            "[DMS] Application parsing failed: no siret found",
            extra={
                "application_number": data["application"],
                "application_scalar_id": node.get("id"),
                "procedure_number": procedure_number,
            },
        )
        return

    application = educational_models.CollectiveDmsApplication.query.filter(
        educational_models.CollectiveDmsApplication.procedure == procedure_number,
        educational_models.CollectiveDmsApplication.application == data["application"],
    ).one_or_none()
    if application:
        for key, value in data.items():
            setattr(application, key, value)
    else:
        venue = offerers_models.Venue.query.filter(offerers_models.Venue.siret == data["siret"]).one_or_none()
        if not venue:
            logger.info(
                "[DMS] Application parsing failed: unknown siret",
                extra={
                    "application_number": data["application"],
                    "application_scalar_id": node.get("id"),
                    "procedure_number": procedure_number,
                },
            )
            return
        try:
            application = educational_models.CollectiveDmsApplication(venue=venue, **data)
            db.session.add(application)
        except Exception as exp:
            db.session.rollback()
            raise exp

    db.session.commit()


def _convert_iso_string_to_naive_utc_datetime(date_str: str | None) -> datetime | None:
    if not date_str:
        return None
    date = datetime.fromisoformat(date_str)
    return date.astimezone(pytz.utc).replace(tzinfo=None)


def _get_previous_import(procedure_number: int) -> dms_models.LatestDmsImport | None:
    previous_import_query = dms_models.LatestDmsImport.query.filter(
        dms_models.LatestDmsImport.procedureId == procedure_number
    )
    previous_import_query = previous_import_query.order_by(dms_models.LatestDmsImport.latestImportDatetime.desc())
    return previous_import_query.first()
