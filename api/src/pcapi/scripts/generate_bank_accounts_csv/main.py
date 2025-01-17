import datetime
import logging
import pathlib

import sqlalchemy.sql.functions as sqla_func

import pcapi.core.finance.api as finance_api
import pcapi.core.finance.models as finance_models
import pcapi.core.offerers.models as offerers_models
from pcapi.utils import human_ids


logger = logging.getLogger(__name__)


def generate_old_bank_accounts_file(cutoff: datetime.datetime) -> pathlib.Path:
    header = (
        "Lieux liés au compte bancaire",
        "Identifiant humanisé des coordonnées bancaires",
        "Identifiant des coordonnées bancaires",
        "SIREN de la structure",
        "Nom de la structure - Libellé des coordonnées bancaires",
        "IBAN",
        "BIC",
    )
    query = (
        finance_models.BankAccount.query.filter(
            finance_models.BankAccount.id.in_(
                offerers_models.VenueBankAccountLink.query.filter(
                    offerers_models.VenueBankAccountLink.timespan.contains(cutoff)
                ).with_entities(offerers_models.VenueBankAccountLink.bankAccountId)
            )
        )
        .join(finance_models.BankAccount.offerer)
        .join(finance_models.BankAccount.venueLinks)
        .group_by(
            finance_models.BankAccount.id,
            finance_models.BankAccount.label,
            finance_models.BankAccount.iban,
            finance_models.BankAccount.bic,
            offerers_models.Offerer.name,
            offerers_models.Offerer.siren,
            offerers_models.Offerer.street,
            offerers_models.Offerer.city,
            offerers_models.Offerer.postalCode,
        )
        .order_by(finance_models.BankAccount.id)
    ).with_entities(
        finance_models.BankAccount.id,
        sqla_func.array_agg(offerers_models.VenueBankAccountLink.venueId.distinct()).label("venue_ids"),
        offerers_models.Offerer.name.label("offerer_name"),
        offerers_models.Offerer.siren.label("offerer_siren"),
        finance_models.BankAccount.label.label("label"),
        finance_models.BankAccount.iban.label("iban"),
        finance_models.BankAccount.bic.label("bic"),
    )

    row_formatter = lambda row: (
        ", ".join(str(venue_id) for venue_id in sorted(row.venue_ids)),
        human_ids.humanize(row.id),
        str(row.id),
        finance_api._clean_for_accounting(row.offerer_siren),
        finance_api._clean_for_accounting(f"{row.offerer_name} - {row.label}"),
        finance_api._clean_for_accounting(row.iban),
        finance_api._clean_for_accounting(row.bic),
    )
    return finance_api._write_csv("bank_accounts", header, rows=query, row_formatter=row_formatter)


def generate_bank_accounts_csv(batch: finance_models.CashflowBatch) -> None:
    file_paths = {}
    logger.info("Generating bank accounts file")
    file_paths["bank_accounts"] = generate_old_bank_accounts_file(batch.cutoff)

    drive_folder_name = finance_api._get_drive_folder_name(batch)
    finance_api._upload_files_to_google_drive(drive_folder_name, file_paths.values())


if __name__ == "__main__":
    from pcapi.flask_app import app

    with app.app_context():
        print("Starting script")
        cashflow_batch = finance_models.CashflowBatch.query.filter(finance_models.CashflowBatch.label == "VIR130").one()
        generate_bank_accounts_csv(cashflow_batch)
        print("Script done")
