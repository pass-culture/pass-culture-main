import datetime
import logging

from pcapi import settings
from pcapi.connectors.dms import api as ds_api
from pcapi.connectors.dms.models import GraphQLApplicationStates
from pcapi.connectors.dms.serializer import ApplicationDetail
from pcapi.connectors.dms.serializer import MarkWithoutContinuationApplicationDetail
from pcapi.domain.demarches_simplifiees import parse_raw_bank_info_data
from pcapi.models import db
from pcapi.use_cases.save_venue_bank_informations import PROCEDURE_ID_VERSION_MAP
from pcapi.use_cases.save_venue_bank_informations import ImportBankAccountFactory


logger = logging.getLogger(__name__)

MARK_WITHOUT_CONTINUATION_MOTIVATION = "Classé sans suite et archivé automatiquement"  # visible in DS


def update_ds_applications_for_procedure(
    procedure_number: int,
    since: datetime.datetime | None,
    set_without_continuation: bool = False,
) -> list:
    logger.info("[DS] Started processing Bank Account procedure %s", procedure_number)

    ds_client = ds_api.DMSGraphQLClient()
    application_numbers = []
    procedure_version = PROCEDURE_ID_VERSION_MAP[str(procedure_number)]

    for node in ds_client.get_pro_bank_nodes_states(procedure_number=procedure_number, since=since):
        data = parse_raw_bank_info_data(node, procedure_version)
        try:
            ImportBankAccount = ImportBankAccountFactory.get(procedure_version)
            application_details = ApplicationDetail(**{"application_type": procedure_version, **data})
            ImportBankAccount(application_details).execute()
        except Exception as exc:
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
            # Committing here ensures that we have a proper transaction for each application successfully imported
            # And that for each faulty application, the failure only impacts that particular one.
            db.session.commit()

    logger.info(
        "[DS] Finished processing Bank Account procedure %s.",
        procedure_number,
        extra={"procedure_number": procedure_number},
    )

    return application_numbers


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
                        ds_client.mark_without_continuation(
                            application_techid=application.id,
                            instructeur_techid=settings.DS_MARK_WITHOUT_CONTINUATION_INSTRUCTOR_ID,
                            motivation=MARK_WITHOUT_CONTINUATION_MOTIVATION,
                            from_draft=application.is_draft,
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
                except Exception:
                    logger.exception(
                        "Error while trying to mark without continuation an application",
                        extra={"application_id": application.number},
                    )
                    db.session.rollback()
                else:
                    db.session.commit()
