from datetime import datetime
from datetime import timedelta
import logging
import typing

from pcapi import settings
from pcapi.connectors.dms import api as dms_api
from pcapi.connectors.dms import models as dms_models
from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def update_dms_status(procedure_id: int = 0) -> None:
    """import dms applications for eac status"""
    if procedure_id:
        procedures = [procedure_id]
    else:
        procedures = [
            settings.DMS_EAC_PROCEDURE_INDEPENDANTS_CANDIDATE_ID,
            settings.DMS_EAC_PROCEDURE_STRUCTURE_CANDIDATE_ID,
            settings.DMS_EAC_PROCEDURE_MENJS_CANDIDATE_ID,
        ]

    for procedure in procedures:
        previous_import = _get_previous_import(procedure)
        if previous_import and previous_import.isProcessing:
            logger.info(
                "[DMS] Procedure %s is already being processed.",
                procedure,
                extra={
                    "procedure_number": procedure,
                },
            )
            continue
        since = previous_import.latestImportDatetime if previous_import else None

        _update_dms_status_for_procedure(
            procedure_number=procedure,
            since=since,
        )


def _update_dms_status_for_procedure(procedure_number: int, since: datetime | None) -> None:
    logger.info(
        "[DMS] Starting to process procedure %s.",
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
    applications_id = []

    for node in dms_client.get_eac_nodes_siret_states(procedure_id=procedure_number, since=since):
        try:
            _get_or_create_application(procedure_number=procedure_number, node=node)
        except Exception as exp:  # pylint: disable=broad-exception-caught
            logger.error(
                "[DMS] Application parsing failed with error %s",
                str(exp),
                extra={
                    "application_number": node.get("number"),
                    "application_scalar_id": node.get("id"),
                    "procedure_number": procedure_number,
                },
            )
        else:
            applications_id.append(node["number"])

    current_import.processedApplications = applications_id
    current_import.isProcessing = False
    db.session.commit()

    logger.info(
        "[DMS] Finishing to process procedure %s.",
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
        "expirationdate": _convert_iso_string_to_naive_utc_datetime(node["dateExpiration"]),
        "buildDate": _convert_iso_string_to_naive_utc_datetime(node["datePassageEnConstruction"]),
        "instructionDate": _convert_iso_string_to_naive_utc_datetime(node["datePassageEnInstruction"]),
        "processingDate": _convert_iso_string_to_naive_utc_datetime(node["dateTraitement"]),
        "userdeletiondate": _convert_iso_string_to_naive_utc_datetime(node["dateSuppressionParUsager"]),
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
        educational_models.CollectiveDmsApplication.siret == data["siret"],
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
        application = educational_models.CollectiveDmsApplication(venue=venue, **data)
        db.session.add(application)
    db.session.commit()


def _convert_iso_string_to_naive_utc_datetime(date_str: str | None) -> datetime | None:
    if not date_str:
        return None
    date = datetime.fromisoformat(date_str)
    # dms always returns an iso date with timezone therefore utcoffset nerver returns None
    offset = typing.cast(timedelta, date.utcoffset())
    utc_date = date - offset
    naive_date = utc_date.replace(tzinfo=None)
    return naive_date


def _get_previous_import(procedure_number: int) -> dms_models.LatestDmsImport | None:
    previous_import_query = dms_models.LatestDmsImport.query.filter(
        dms_models.LatestDmsImport.procedureId == procedure_number
    )
    previous_import_query = previous_import_query.order_by(dms_models.LatestDmsImport.latestImportDatetime.desc())
    previous_import_query = previous_import_query.limit(1)
    previous_import = previous_import_query.one_or_none()
    return previous_import
