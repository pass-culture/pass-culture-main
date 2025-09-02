"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/pc-37661-check-ds-bank-accounts/api/src/pcapi/scripts/pc_37661_check_ds_bank_accounts/main.py

"""

import argparse
import csv
import logging
import os

from pcapi.app import app
from pcapi.connectors.dms import api as ds_api
from pcapi.connectors.dms.serializer import ApplicationDetail
from pcapi.core.finance import ds as finance_ds
from pcapi.core.finance import models as finance_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def _check_bank_accounts(procedure_number: int) -> None:
    logger.info("[DS] Started processing Bank Account procedure %s", procedure_number)

    ds_client = ds_api.DMSGraphQLClient()
    procedure_version = finance_ds.PROCEDURE_ID_VERSION_MAP[str(procedure_number)]
    read_count = 0
    exc_count = 0
    not_found_count = 0
    mismatch_count = 0

    output_dir = os.environ.get("OUTPUT_DIRECTORY")
    assert output_dir is not None  # helps mypy
    output_file = os.path.join(output_dir, f"output-{procedure_number}.csv")
    with open(output_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile, dialect=csv.excel, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(
            [
                "N° dossier",
                "État du dossier",
                "SIREN",
                "IBAN DS",
                "BIC DS",
                "Label DS",
                "IBAN en base de données",
                "BIC en base de données",
                "Label en base de données",
                "Erreur",
            ]
        )

        for node in ds_client.get_pro_bank_nodes_states(procedure_number=procedure_number, archived=None):
            data = finance_ds.parse_raw_bank_info_data(node, procedure_version)
            try:
                application_details = ApplicationDetail(**{"application_type": procedure_version, **data})
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
                exc_count += 1
            else:
                # print(application_details.application_id, application_details.status.value, application_details.siren, application_details.iban, application_details.bic, application_details.label)
                read_count += 1

                bank_account = (
                    db.session.query(finance_models.BankAccount)
                    .filter_by(dsApplicationId=application_details.application_id)
                    .one_or_none()
                )
                if bank_account:
                    error = ""
                    if bank_account.iban != application_details.iban:
                        logger.warning("[DS] Mismatched IBAN for application %s", application_details.application_id)
                        error += "iban"
                    if bank_account.bic != application_details.bic:
                        logger.warning("[DS] Mismatched BIC for application %s", application_details.application_id)
                        error += ",bic" if error else "bic"
                    if bank_account.label.strip() != (application_details.label or "").strip():
                        logger.warning("[DS] Mismatched label for application %s", application_details.application_id)
                        error += ",label" if error else "label"
                    if error:
                        writer.writerow(
                            [
                                application_details.application_id,
                                application_details.status.value,
                                application_details.siren,
                                application_details.iban,
                                application_details.bic,
                                application_details.label,
                                bank_account.iban,
                                bank_account.bic,
                                bank_account.label,
                                error,
                            ]
                        )
                        mismatch_count += 1
                else:
                    logger.warning("[DS] Application %s not found in database", application_details.application_id)
                    writer.writerow(
                        [
                            application_details.application_id,
                            application_details.status.value,
                            application_details.siren,
                            application_details.iban,
                            application_details.bic,
                            application_details.label,
                            "",
                            "",
                            "",
                            "NON TROUVÉ",
                        ]
                    )
                    not_found_count += 1

    logger.info(
        "[DS] Finished processing Bank Account procedure %s.",
        procedure_number,
        extra={"procedure_number": procedure_number},
    )
    logger.info("[DS] %s applications failed (exception)", exc_count)
    logger.info("[DS] %s applications checked", read_count)
    logger.info("[DS] %s applications not found", not_found_count)
    logger.info("[DS] %s applications with data mismatch", mismatch_count)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--procedure-number", type=int, required=True)
    args = parser.parse_args()

    _check_bank_accounts(args.procedure_number)

    logger.info("Finished")
