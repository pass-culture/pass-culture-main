import argparse
from datetime import datetime
import time
from typing import Iterable

from flask_sqlalchemy import BaseQuery
import sqlalchemy as sa

from pcapi.app import app
from pcapi.core.finance.models import BankAccount
from pcapi.core.finance.models import BankAccountApplicationStatus
from pcapi.core.finance.models import BankInformation
from pcapi.core.finance.models import BankInformationStatus
from pcapi.core.history.models import ActionHistory
from pcapi.core.history.models import ActionType
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.core.offerers.models import VenueBankAccountLink
from pcapi.core.offerers.models import VenueReimbursementPointLink
from pcapi.models import db


app.app_context().push()

comment = "(PC-23402) Migrate data from old bankInformation journey to new bankAccount journey"


def map_bank_information_status_to_bank_account_status(
    bank_information_status: BankInformationStatus,
) -> BankAccountApplicationStatus:
    match bank_information_status:
        case BankInformationStatus.REJECTED:
            return BankAccountApplicationStatus.REFUSED
        case BankInformationStatus.ACCEPTED:
            return BankAccountApplicationStatus.ACCEPTED
        case _:
            return BankAccountApplicationStatus.DRAFT


def fetch_all_up_to_date_reimbursement_point_links(
    reimbursement_point: Venue,
) -> Iterable[VenueReimbursementPointLink]:
    return VenueReimbursementPointLink.query.filter(
        VenueReimbursementPointLink.reimbursementPointId == reimbursement_point.id,
        VenueReimbursementPointLink.timespan.contains(datetime.utcnow()),
    ).all()


def fetch_all_bank_informations_used_by_a_reimbursement_point() -> BaseQuery:
    return (
        BankInformation.query.join(BankInformation.venue)
        .join(Venue.managingOfferer)
        .options(
            sa.orm.contains_eager(BankInformation.venue).load_only(
                Venue.id, Venue.name, Venue.publicName, Venue.siret, Venue.managingOffererId
            )
        )
        .options(
            sa.orm.contains_eager(BankInformation.venue)
            .contains_eager(Venue.managingOfferer)
            .load_only(Offerer.id, Offerer.name, Offerer.siren)
        )
    )


def fetch_all_bank_information_without_reimbursement_point() -> BaseQuery:
    return BankInformation.query.join(
        Offerer, sa.and_(BankInformation.offererId == Offerer.id, BankInformation.venueId.is_(None))
    ).options(sa.orm.contains_eager(BankInformation.offerer).load_only(Offerer.id, Offerer.name, Offerer.siren))


def construct_bank_account_label(bank_information: BankInformation) -> str:
    if bank_information.venue:
        reimbursement_point = bank_information.venue
        bank_accout_label = reimbursement_point.common_name
    else:
        offerer = bank_information.offerer
        bank_accout_label = f"{offerer.siren} - {offerer.name}"

    if len(bank_accout_label) > 100:
        bank_accout_label = f"{bank_accout_label[:97]}..."

    return bank_accout_label


def should_skip_this_bank_information(bank_information: BankInformation) -> bool:
    if not bank_information.iban or not bank_information.bic:
        print(f"Skipping <BankInformation {bank_information.id}>. Missing IBAN or BIC")
        return True

    return False


def process(dry_run: bool) -> None:
    processed_bank_informations = 0
    bank_accounts_created = 0
    venue_bank_account_link_created = 0
    skipped_bank_information_with_reimbursement_point = 0

    processed_bank_informations_without_reimbursement_point = 0
    bank_accounts_created_without_venue_bank_account_link = 0
    skipped_bank_information_without_reimbursement_point = 0

    if dry_run is True:
        print("--------- DRY RUN ------------")

    start = time.time()

    query = fetch_all_bank_informations_used_by_a_reimbursement_point()

    for bank_information in query.all():
        print(
            f"Processing <BankInformation {bank_information.id} - {bank_information.iban} - {bank_information.bic}> used by a reimbursementPoint"
        )
        if should_skip_this_bank_information(bank_information):
            skipped_bank_information_with_reimbursement_point += 1
            continue

        reimbursement_point = bank_information.venue
        print(
            f"Found <ReimbursementPoint {reimbursement_point.id} - {reimbursement_point.name} ({reimbursement_point.publicName})>"
        )

        reimbursement_point_links = fetch_all_up_to_date_reimbursement_point_links(reimbursement_point)
        bank_accout_label = construct_bank_account_label(bank_information)

        bank_account = BankAccount(
            id=reimbursement_point.id,
            offererId=reimbursement_point.managingOffererId,
            iban=bank_information.iban,
            bic=bank_information.bic,
            label=bank_accout_label,
            dsApplicationId=bank_information.applicationId,
            dateCreated=bank_information.dateModified,
            dateLastStatusUpdate=bank_information.dateModified,
            status=map_bank_information_status_to_bank_account_status(bank_information.status),
        )
        db.session.add(bank_account)
        db.session.flush()
        processed_bank_informations += 1
        bank_accounts_created += 1

        for link in reimbursement_point_links:
            print(f"Linking <Venue {link.venueId}> to <BankAccount {bank_account.id}>")
            venue_bank_account_link = VenueBankAccountLink(
                venueId=link.venueId, bankAccountId=bank_account.id, timespan=(datetime.utcnow(),)
            )
            action = ActionHistory(
                venueId=link.venueId,
                bankAccountId=bank_account.id,
                offererId=reimbursement_point.managingOffererId,
                actionType=ActionType.LINK_VENUE_BANK_ACCOUNT_CREATED,
                comment=comment,
            )
            db.session.add(venue_bank_account_link)
            db.session.add(action)
            db.session.flush()
            venue_bank_account_link_created += 1

    ### The critical part is behind us. We are now sure that for any reimbursementPoint we have created a matching BankAccount with the same id ###
    ### For accounting reasons, it was mandatory to ensure a perfect match betwenn any existing reimbursementPoint.id and his corresponding BankAccount.id ###

    # We can now fetch remaining BankInformation (carried by any reimbursementPoint), create a matching BankAccount and let the DB handle the autoincrement
    remaining_bank_information = fetch_all_bank_information_without_reimbursement_point()

    for bank_information in remaining_bank_information.all():
        print(
            f"Processing <BankInformation {bank_information.id} - {bank_information.iban} - {bank_information.bic}> without a reimbursementPoint"
        )
        if should_skip_this_bank_information(bank_information):
            skipped_bank_information_without_reimbursement_point += 1
            continue

        bank_accout_label = construct_bank_account_label(bank_information)

        bank_account = BankAccount(
            offererId=bank_information.offererId,
            iban=bank_information.iban,
            bic=bank_information.bic,
            label=bank_accout_label,
            dsApplicationId=bank_information.applicationId,
            dateCreated=bank_information.dateModified,
            dateLastStatusUpdate=bank_information.dateModified,
            status=map_bank_information_status_to_bank_account_status(bank_information.status),
        )
        db.session.add(bank_account)
        db.session.flush()
        processed_bank_informations_without_reimbursement_point += 1
        bank_accounts_created_without_venue_bank_account_link += 1

    if dry_run:
        db.session.rollback()
        print(f"Skipped {skipped_bank_information_with_reimbursement_point} bankInformation with a reimbursementPoint")
        print(f"Would have processed {processed_bank_informations} bankInformation with a reimbursementPoint")
        print(f"Would have created {bank_accounts_created} bankAccount")
        print(f"Would have created {venue_bank_account_link_created} VenueBankAccountLink")

        print(
            f"Skipped {skipped_bank_information_without_reimbursement_point} bankInformation without a reimbursementPoint"
        )
        print(
            f"Would have processed {processed_bank_informations_without_reimbursement_point} bankInformation without a reimbursementPoint"
        )
        print(
            f"Would have created {bank_accounts_created_without_venue_bank_account_link} bankAccount without any VenueBankAccountLink"
        )
    else:
        print(f"Skipped {skipped_bank_information_with_reimbursement_point} bankInformation with a reimbursementPoint")
        print(f"Processed {processed_bank_informations} bankInformation with a reimbursementPoint")
        print(f"Created {bank_accounts_created} bankAccount")
        print(f"Created {venue_bank_account_link_created} VenueBankAccountLink")

        print(
            f"Skipped {skipped_bank_information_without_reimbursement_point} bankInformation without a reimbursementPoint"
        )
        print(
            f"Processed {processed_bank_informations_without_reimbursement_point} bankInformation without a reimbursementPoint"
        )
        print(
            f"Created {bank_accounts_created_without_venue_bank_account_link} bankAccount without any VenueBankAccountLink"
        )
        db.session.commit()

    end = time.time()

    print(f"Took {end - start}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert any reimbursementPoint (venue carrying bankInformation) into a bankAccount"
    )
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    try:
        process(args.dry_run)
    except Exception as e:
        db.session.rollback()
        raise
