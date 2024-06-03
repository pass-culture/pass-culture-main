import datetime
import logging

from pcapi import settings
from pcapi.connectors.dms import api as ds_api
from pcapi.connectors.dms import models as ds_models
from pcapi.connectors.dms.models import GraphQLApplicationStates
from pcapi.connectors.dms.serializer import ApplicationDetail
from pcapi.connectors.dms.serializer import MarkWithoutContinuationApplicationDetail
from pcapi.domain.demarches_simplifiees import parse_raw_bank_info_data
from pcapi.models import db
from pcapi.use_cases.save_venue_bank_informations import ImportBankAccountFactory
from pcapi.use_cases.save_venue_bank_informations import PROCEDURE_ID_VERSION_MAP


logger = logging.getLogger(__name__)

MARK_WITHOUT_CONTINUATION_MOTIVATION = "Marked without continuation & archived through automatic process (PC-24035)"


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
            ImportBankAccount = ImportBankAccountFactory.get(procedure_version)
            application_details = ApplicationDetail(**{"application_type": procedure_version, **data})
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
            # If we don't rollback here, we will persist in the faulty transaction
            # and we won't be able to commit at the end of the process and to set the current import `isProcessing` attr to False
            # Therefore, this import could be seen as on going for other next attempts, forever.
            db.session.rollback()
        else:
            application_numbers.append(node["number"])
            # Committing here ensure that we have a proper transaction for each application successfully imported
            # And that for each faulty application, the failure only impact that particular one.
            db.session.commit()

    current_import.processedApplications = application_numbers
    current_import.isProcessing = False
    db.session.commit()

    logger.info(
        "[DS] Finished processing Bank Account procedure %s.",
        procedure_number,
        extra={"procedure_number": procedure_number},
    )


def mark_without_continuation_applications() -> None:
    """
    Mark without continuation following applications:
        - All DSv4 that:
            - are in `draft` or `on_going` states
            - haven't been updated since DS_MARK_WITHOUT_CONTINUATION_APPLICATION_DEADLINE days
            - have the field `Erreur traitement Pass Culture` filled
                - without mention of `ADAGE` or without mention of `RCT`
                or
                - with mention of `RCT` and haven't been updated since DS_MARK_WITHOUT_CONTINUATION_ANNOTATION_DEADLINE days

        - All DSv5 that:
            - are in `draft` or `on_going` states
            - haven't been updated since DS_MARK_WITHOUT_CONTINUATION_APPLICATION_DEADLINE days
                and
                    - have the field `En attente de validation de structure` checked since more than DS_MARK_WITHOUT_CONTINUATION_ANNOTATION_DEADLINE days
                    - don't have the field `En attente de validation Adage` checked at all
                    or
                    - don't have the field `En attente de validation de structure` checked at all
                    - don't have the field `En attente de validation Adage` checked at all
    """
    procedures = [settings.DMS_VENUE_PROCEDURE_ID_V4, settings.DS_BANK_ACCOUNT_PROCEDURE_ID]
    states = [GraphQLApplicationStates.draft, GraphQLApplicationStates.on_going]
    ds_client = ds_api.DMSGraphQLClient()

    # pylint: disable=too-many-nested-blocks
    for procedure in procedures:
        for state in states:
            for raw_node in ds_client.get_pro_bank_nodes_states(procedure_number=int(procedure), state=state):
                application = MarkWithoutContinuationApplicationDetail(**raw_node)

                try:
                    if application.should_be_marked_without_continuation:
                        logger.info(
                            "[DS] Found one application to mark `without_continuation`",
                            extra={"application_id": application.number},
                        )
                        if application.is_draft:
                            logger.info(
                                "[DS] Make the application `on_going` before being able to make it `without_continuation`"
                            )
                            ds_client.make_on_going(
                                application_techid=application.id,
                                instructeur_techid=settings.DS_MARK_WITHOUT_CONTINUATION_INSTRUCTOR_ID,
                            )
                        ds_client.mark_without_continuation(
                            application_techid=application.id,
                            instructeur_techid=settings.DS_MARK_WITHOUT_CONTINUATION_INSTRUCTOR_ID,
                            motivation=MARK_WITHOUT_CONTINUATION_MOTIVATION,
                        )
                        application.mark_without_continuation()
                        ds_client.archive_application(
                            application_techid=application.id,
                            instructeur_techid=settings.DS_MARK_WITHOUT_CONTINUATION_INSTRUCTOR_ID,
                        )
                        logger.info(
                            "[DS] Successfully mark `without_continuation` and archived an application",
                            extra={"application_id": application.number},
                        )
                except Exception:  # pylint: disable=broad-exception-caught
                    logger.exception(
                        "Error while trying to mark without continuation an application",
                        extra={"application_id": application.number},
                    )
                    db.session.rollback()
                else:
                    db.session.commit()
