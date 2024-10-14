import datetime
import json
import logging

# from pcapi import settings
from pcapi.connectors.dms import api as ds_api


# from pcapi.connectors.dms import models as ds_models
# from pcapi.connectors.dms.models import GraphQLApplicationStates
# from pcapi.connectors.dms.serializer import ApplicationDetail
# from pcapi.domain.demarches_simplifiees import parse_raw_bank_info_data
# from pcapi.models import db
# from pcapi.use_cases.save_venue_bank_informations import ImportBankAccountFactory
# from pcapi.use_cases.save_venue_bank_informations import PROCEDURE_ID_VERSION_MAP


logger = logging.getLogger(__name__)


def test_procedure(procedure_number: int, since: datetime.datetime | None) -> None:
    logger.info("[DS] Started processing User Account Update procedure %s", procedure_number)

    ds_client = ds_api.DMSGraphQLClient()

    for i, node in enumerate(
        ds_client.get_beneficiary_account_update_nodes_states(procedure_number=procedure_number, since=since)
    ):
        print("****", i)
        print(json.dumps(node, indent=4))


# def import_ds_bank_information_applications(procedure_number: int, ignore_previous: bool = False) -> None:
#     logger.info("[DS] Start import of all applications from Démarches Simplifiées for procedure %s", procedure_number)
#     last_import = (
#         ds_models.LatestDmsImport.query.filter(ds_models.LatestDmsImport.procedureId == procedure_number)
#         .order_by(ds_models.LatestDmsImport.latestImportDatetime.desc())
#         .first()
#     )
#     if last_import and last_import.isProcessing:
#         if datetime.datetime.utcnow() < last_import.latestImportDatetime + datetime.timedelta(days=1):
#             logger.info("[DS] Procedure %s is already being processed.", procedure_number)
#         else:
#             last_import.isProcessing = False
#             db.session.add(last_import)
#             db.session.commit()
#             logger.info(
#                 "[DS] Procedure %s stopped after having been in treatment since %s",
#                 procedure_number,
#                 last_import.latestImportDatetime,
#             )
#
#     else:
#         since = last_import.latestImportDatetime if last_import else None
#         update_ds_applications_for_procedure(
#             procedure_number=procedure_number, since=None if ignore_previous else since
#         )

#
# def update_ds_applications_for_procedure(procedure_number: int, since: datetime.datetime | None) -> None:
#     logger.info("[DS] Started processing Bank Account procedure %s", procedure_number)
#     current_import = ds_models.LatestDmsImport(
#         procedureId=procedure_number,
#         latestImportDatetime=datetime.datetime.utcnow(),
#         isProcessing=True,
#         processedApplications=[],
#     )
#     db.session.add(current_import)
#     db.session.commit()
#
#     ds_client = ds_api.DMSGraphQLClient()
#     application_numbers = []
#     procedure_version = PROCEDURE_ID_VERSION_MAP[str(procedure_number)]
#
#     for node in ds_client.get_pro_bank_nodes_states(procedure_number=procedure_number, since=since):
#         data = parse_raw_bank_info_data(node, procedure_version)
#         try:
#             ImportBankAccount = ImportBankAccountFactory.get(procedure_version)
#             application_details = ApplicationDetail(**{"application_type": procedure_version, **data})
#             ImportBankAccount(application_details).execute()
#         except Exception as exc:  zzpylint: disable=broad-exception-caught
#             logger.exception(
#                 "[DS] Application parsing failed with error %s",
#                 str(exc),
#                 extra={
#                     "application_number": node.get("number"),
#                     "application_scalar_id": node.get("id"),
#                     "procedure_number": procedure_number,
#                 },
#             )
#             # If we don't rollback here, we will persist in the faulty transaction
#             # and we won't be able to commit at the end of the process and to set the current import `isProcessing` attr to False
#             # Therefore, this import could be seen as on going for other next attempts, forever.
#             db.session.rollback()
#         else:
#             application_numbers.append(node["number"])
#             # Committing here ensure that we have a proper transaction for each application successfully imported
#             # And that for each faulty application, the failure only impact that particular one.
#             db.session.commit()
#
#     current_import.processedApplications = application_numbers
#     current_import.isProcessing = False
#     db.session.commit()
#
#     logger.info(
#         "[DS] Finished processing Bank Account procedure %s.",
#         procedure_number,
#         extra={"procedure_number": procedure_number},
#     )
