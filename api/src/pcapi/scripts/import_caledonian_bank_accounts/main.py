"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-37631-script-generate-BA-for-NC \
  -f NAMESPACE=generate_bank_accounts_nc \
  -f SCRIPT_ARGUMENTS="";
"""

import argparse
import csv
import logging
import os
import typing
from textwrap import shorten

import schwifty
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

import pcapi.core.mails.transactional as transactional_mails
from pcapi.app import app
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import models as finance_models
from pcapi.core.history import models as history_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.utils import date as date_utils
from pcapi.utils import siren as siren_utils
from pcapi.utils.db import make_timerange


logger = logging.getLogger(__name__)


def validated_bank_account_email_notification(
    bank_account: finance_models.BankAccount, new_linked_venue: offerers_models.Venue
) -> None:
    offerer_id = bank_account.offerer.id
    venue_id = new_linked_venue.id

    has_non_free_offers_subquery = (
        sa.select(1)
        .select_from(offers_models.Stock)
        .join(
            offers_models.Offer,
            sa.and_(
                offers_models.Stock.offerId == offers_models.Offer.id,
                offers_models.Stock.price > 0,
                offers_models.Stock.isSoftDeleted.is_(False),
                offers_models.Offer.isActive,
                offers_models.Offer.venueId == offerers_models.Venue.id,
            ),
        )
        .correlate(offerers_models.Venue)
        .exists()
    )

    has_non_free_collective_offers_subquery = (
        sa.select(1)
        .select_from(educational_models.CollectiveStock)
        .join(
            educational_models.CollectiveOffer,
            sa.and_(
                educational_models.CollectiveStock.collectiveOfferId == educational_models.CollectiveOffer.id,
                educational_models.CollectiveStock.price > 0,
                educational_models.CollectiveOffer.isActive.is_(True),
                educational_models.CollectiveOffer.venueId == offerers_models.Venue.id,
            ),
        )
        .correlate(offerers_models.Venue)
        .exists()
    )

    venues = (
        db.session.query(offerers_models.Venue)
        .filter(
            offerers_models.Venue.managingOffererId == offerer_id,
            offerers_models.Venue.id != venue_id,
            sa.or_(has_non_free_offers_subquery, has_non_free_collective_offers_subquery),
        )
        .join(offerers_models.Offerer)
        .outerjoin(
            offerers_models.VenueBankAccountLink,
            sa.and_(
                offerers_models.VenueBankAccountLink.venueId == offerers_models.Venue.id,
                offerers_models.VenueBankAccountLink.timespan.contains(date_utils.get_naive_utc_now()),
            ),
        )
        .options(
            sa_orm.contains_eager(offerers_models.Venue.bankAccountLinks)
            .load_only(offerers_models.VenueBankAccountLink.id)
            .load_only(offerers_models.VenueBankAccountLink.timespan)
        )
        .all()
    )
    for venue in venues:
        if not venue.current_bank_account_link and venue.bookingEmail:
            transactional_mails.send_bank_account_validated_email(venue.bookingEmail)


def link_venue_to_bank_account(
    bank_account: finance_models.BankAccount, venue: offerers_models.Venue, ds_id: int
) -> offerers_models.VenueBankAccountLink | None:
    for link in bank_account.venueLinks:
        if (
            link.timespan.upper is None
            and link.timespan.lower <= date_utils.get_naive_utc_now()
            and link.venue == venue
        ):
            logger.info(
                "bank_account already linked to its venue",
                extra={
                    "application_id": ds_id,
                    "bank_account_id": bank_account.id,
                    "venue_id": venue.id,
                },
            )
            return None

    now = date_utils.get_naive_utc_now()

    if deprecated_link := venue.current_bank_account_link:
        lower_bound = deprecated_link.timespan.lower
        timespan = make_timerange(start=lower_bound, end=now)
        deprecated_link.timespan = timespan
        deprecated_log = history_models.ActionHistory(
            actionType=history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_DEPRECATED,
            venueId=venue.id,
            bankAccountId=deprecated_link.bankAccountId,
        )
        db.session.add(deprecated_log)
    link = offerers_models.VenueBankAccountLink(bankAccount=bank_account, venue=venue, timespan=(now,))
    created_log = history_models.ActionHistory(
        actionType=history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_CREATED,
        venue=venue,
        bankAccount=bank_account,
        comment="PC-37631 - Compte bancaire créé par script pour la Nouvelle-Calédonie (données DS)",
    )
    db.session.add(created_log)
    db.session.add(link)
    return link


def keep_track_of_bank_account_status_changes(bank_account: finance_models.BankAccount, ds_id: int) -> None:
    now = date_utils.get_naive_utc_now()
    if bank_account.statusHistory:
        current_link = bank_account.statusHistory[0]
        if current_link.status == bank_account.status:
            logger.info(
                "bank_account status did not change. Nothing to track.",
                extra={
                    "application_id": ds_id,
                    "bank_account_id": bank_account.id,
                    "bank_account_status": bank_account.status,
                },
            )
            return
        current_link.timespan = make_timerange(start=current_link.timespan.lower, end=now)
        db.session.add(current_link)

    bank_account_status_history = finance_models.BankAccountStatusHistory(
        bankAccount=bank_account, status=bank_account.status, timespan=(now,)
    )
    db.session.add(bank_account_status_history)


def create_or_update_bank_account(
    offerer: offerers_models.Offerer, venue: offerers_models.Venue, bank_account_data: dict
) -> finance_models.BankAccount:
    now = date_utils.get_naive_utc_now()
    bank_account = (
        db.session.query(finance_models.BankAccount)
        .filter(
            finance_models.BankAccount.iban == bank_account_data["iban"],
            finance_models.BankAccount.offererId == offerer.id,
        )
        .options(sa_orm.load_only(finance_models.BankAccount.id))
        .outerjoin(
            finance_models.BankAccountStatusHistory,
            sa.and_(
                finance_models.BankAccountStatusHistory.bankAccountId == finance_models.BankAccount.id,
                finance_models.BankAccountStatusHistory.timespan.contains(now),
            ),
        )
        .outerjoin(
            offerers_models.VenueBankAccountLink,
            sa.and_(
                offerers_models.VenueBankAccountLink.bankAccountId == finance_models.BankAccount.id,
                offerers_models.VenueBankAccountLink.timespan.contains(now),
            ),
        )
        .outerjoin(offerers_models.Venue, offerers_models.Venue.id == offerers_models.VenueBankAccountLink.venueId)
        .options(sa_orm.contains_eager(finance_models.BankAccount.statusHistory))
        .options(
            sa_orm.contains_eager(finance_models.BankAccount.venueLinks)
            .contains_eager(offerers_models.VenueBankAccountLink.venue)
            .load_only(offerers_models.Venue.id)
        )
        .one_or_none()
    )

    if bank_account is None:
        bank_account = finance_models.BankAccount(
            offerer=offerer,
            dsApplicationId=bank_account_data["ds_id"],
        )

    label = bank_account_data["label"]
    if label is None:
        label = venue.common_name
        label = shorten(label, width=100, placeholder="...")
    bank_account.label = label
    bank_account.iban = bank_account_data["iban"]
    bank_account.status = finance_models.BankAccountApplicationStatus.ACCEPTED
    db.session.add(bank_account)
    db.session.flush()
    return bank_account


def is_iban_valid(iban: str) -> bool:
    try:
        schwifty.IBAN(iban)
    except schwifty.exceptions.SchwiftyException:
        return False
    return True


def generate_bank_account(bank_account_data: dict) -> None:
    venue = (
        db.session.query(offerers_models.Venue)
        .filter(offerers_models.Venue.siret == bank_account_data["siret"])
        .one_or_none()
    )
    if not venue:
        logger.info(f"No venue found for siret {bank_account_data['siret']}")
        return

    offerer = venue.managingOfferer

    if not is_iban_valid(bank_account_data["iban"]):
        logger.error(f"Invalid IBAN {bank_account_data['iban']} for siret {bank_account_data['siret']}")
        return

    bank_account = create_or_update_bank_account(offerer, venue, bank_account_data)
    logger.info(f"Created bank account {bank_account.id}")
    keep_track_of_bank_account_status_changes(bank_account, bank_account_data["ds_id"])
    link = link_venue_to_bank_account(bank_account, venue, bank_account_data["ds_id"])
    if link:
        logger.info(f"Linked BA {bank_account.id} to venue {venue.id} with link {link.id}")
    else:
        logger.info(f"No link created for BA {bank_account.id} and venue {venue.id}")
    validated_bank_account_email_notification(bank_account, venue)
    return


def _read_csv_file(filename: str) -> typing.Iterator[dict[str, str]]:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(namespace_dir, filename), "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=",")
        yield from csv_rows


def main(filename: str, not_dry: bool) -> None:
    rows = _read_csv_file(filename)
    for row in rows:
        ds_id = int(row["ID"])
        ridet = row["RIDET"]

        if len(ridet) != 10:
            logger.error("Invalid RIDET: %s", ridet)
            continue

        if row["État du dossier"] != "Accepté":
            logger.error("DS application %s is not accepted: %s", ds_id, row["État du dossier"])
            continue

        bank_account_data = {
            "ds_id": ds_id,
            "siret": siren_utils.ridet_to_siret(ridet),
            "iban": row["IBAN"].replace(" ", ""),
            "label": row["Intitulé du compte bancaire"],
        }
        generate_bank_account(bank_account_data)

        if not_dry:
            db.session.commit()
        else:
            db.session.rollback()


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--filename", type=str, required=True)
    args = parser.parse_args()

    main(filename=args.filename, not_dry=args.not_dry)
