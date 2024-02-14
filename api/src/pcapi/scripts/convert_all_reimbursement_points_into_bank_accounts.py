import argparse
import time
from typing import Iterable

import sqlalchemy as sa

from pcapi.app import app
from pcapi.core.finance.models import BankAccount
from pcapi.core.finance.models import BankAccountApplicationStatus
from pcapi.core.finance.models import BankInformation
from pcapi.core.finance.models import BankInformationStatus
from pcapi.core.finance.models import Cashflow
from pcapi.core.finance.models import Invoice
from pcapi.core.history.models import ActionHistory
from pcapi.core.history.models import ActionType
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.core.offerers.models import VenueBankAccountLink
from pcapi.core.offerers.models import VenueReimbursementPointLink
from pcapi.models import db


app.app_context().push()

comment = "(PC-23402) data migration"


class MigrateData:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run

        # metadata about the current processing
        self.duration = 0

        self.processed_bank_informations_used_by_reimbursement_point = 0
        self.processed_bank_informations_without_reimbursement_point = 0
        self.processed_bank_informations_without_rp_nor_offerer = 0
        self.processed_venue_reimbursement_point_link = 0

        self.created_bank_accounts = 0
        self.created_venue_bank_account_link = 0
        self.created_action_history = 0

        self.updated_cashflows = 0
        self.updated_invoices = 0

    @staticmethod
    def has_reimbursement_point(bank_information: BankInformation) -> bool:
        return bool(bank_information.venue)

    @staticmethod
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

    def process(self) -> None:
        try:
            self.start = time.time()
            self._go()
        except Exception:
            db.session.rollback()
            raise
        else:
            if self.dry_run:
                db.session.rollback()
            else:
                db.session.commit()
        finally:
            self.end = time.time()
            self.stdout()

    def stdout(self) -> None:
        print(f"Duration: {self.end - self.start}")
        if self.dry_run:
            print(
                f"processed_bank_informations_used_by_reimbursement_point: {self.processed_bank_informations_used_by_reimbursement_point}"
            )
            print(
                f"processed_bank_informations_without_reimbursement_point: {self.processed_bank_informations_without_reimbursement_point}"
            )
            print(
                f"processed_bank_informations_without_rp_nor_offerer: {self.processed_bank_informations_without_rp_nor_offerer}"
            )
            print(f"processed_venue_reimbursement_point_link: {self.processed_venue_reimbursement_point_link}")
            print(f"Would have created {self.created_bank_accounts} bank account")
            print(f"Would have created {self.created_venue_bank_account_link} links")
            print(f"Would have created {self.created_action_history} ActionHistory")
            print(f"Would have updated {self.updated_cashflows} cashflows")
            print(f"Would have updated {self.updated_invoices} invoices")
        else:
            print(
                f"processed_bank_informations_used_by_reimbursement_point: {self.processed_bank_informations_used_by_reimbursement_point}"
            )
            print(
                f"processed_bank_informations_without_reimbursement_point: {self.processed_bank_informations_without_reimbursement_point}"
            )
            print(
                f"processed_bank_informations_without_rp_nor_offerer: {self.processed_bank_informations_without_rp_nor_offerer}"
            )
            print(f"processed_venue_reimbursement_point_link: {self.processed_venue_reimbursement_point_link}")
            print(f"Created {self.created_bank_accounts} bank account")
            print(f"Created {self.created_venue_bank_account_link} links")
            print(f"Created {self.created_action_history} ActionHistory")
            print(f"Updated {self.updated_cashflows} cashflows")
            print(f"Updated {self.updated_invoices} invoices")

    def _go(self) -> None:
        # First, convert reimbursement_point into bank_account, and all related data (links, cashflows and invoices)
        for bank_information in self.fetch_all_bank_informations_used_by_a_reimbursement_point():
            reimbursement_point = bank_information.venue
            self.log_bank_information(bank_information)
            bank_account = self.convert_reimbursement_point(bank_information)
            self.convert_venue_reimbursement_point_link(reimbursement_point, bank_account)
            self.update_cashflows_by_reimbursement_point(reimbursement_point, bank_information, bank_account)
            self.update_invoices_by_reimbursement_point(reimbursement_point, bank_account)

            self.sanity_checks(bank_information, bank_account)

        # Then, convert every bank_information that is not used by a reimbursement_point, but that is still linked to an offerer
        for bank_information in self.fetch_all_bank_informations_without_reimbursement_point():
            self.log_bank_information(bank_information)
            bank_account = self.convert_bank_information(bank_information)
            self.update_cashflows_by_bank_information(bank_information, bank_account)

            self.sanity_checks(bank_information, bank_account)

        # Finally, convert orphans bank_information that still are related to cashflows
        for bank_information in self.fetch_all_bank_information_without_rp_nor_offerer():
            self.log_bank_information(bank_information)
            bank_account = self.convert_bank_information(bank_information)
            self.update_cashflows_by_bank_information(bank_information, bank_account)

            self.sanity_checks(bank_information, bank_account)

    def sanity_checks(self, bank_information: BankInformation, bank_account: BankAccount) -> None:
        """Sanity checks at the end of the process of each bankInformation"""
        if self.has_reimbursement_point(bank_information):
            assert bank_information.venue.id == bank_account.id
            assert bank_information.venue.managingOffererId == bank_account.offererId
        if bank_information.offererId:
            assert bank_information.offererId == bank_account.offererId
        assert bank_information.iban == bank_account.iban
        assert bank_information.bic == bank_account.bic

    def log_bank_information(self, bank_information: BankInformation) -> None:
        print(f"bank_information {bank_information.id} {bank_information.iban} {bank_information.bic}")
        if self.has_reimbursement_point(bank_information):
            print(
                f"reimbursement_point {bank_information.venue.id} {bank_information.venue.name} ({bank_information.venue.publicName}) {bank_information.venue.siret}"
            )
        elif bank_information.offererId:
            print("without a reimbursement_point")
        else:
            print("orphan")

    def construct_bank_account_label(self, bank_information: BankInformation) -> str:
        if self.has_reimbursement_point(bank_information):
            reimbursement_point = bank_information.venue
            bank_accout_label = reimbursement_point.common_name
        elif bank_information.offererId:
            offerer = bank_information.offerer
            bank_accout_label = f"{offerer.siren} - {offerer.name}"
        else:
            # orphan bank_information
            bank_accout_label = f"XXXX XXXX XXXX {bank_information.iban[-4:]}"

        if len(bank_accout_label) > 100:
            bank_accout_label = f"{bank_accout_label[:97]}..."

        return bank_accout_label

    def fetch_all_bank_informations_used_by_a_reimbursement_point(self) -> Iterable[BankInformation]:
        return (
            BankInformation.query.join(BankInformation.venue)
            .join(Venue.managingOfferer)
            .filter(BankInformation.iban.is_not(None), BankInformation.bic.is_not(None))
            .options(
                sa.orm.contains_eager(BankInformation.venue)
                .load_only(Venue.id, Venue.name, Venue.publicName, Venue.siret, Venue.managingOffererId)
                .contains_eager(Venue.managingOfferer)
                .load_only(Offerer.id, Offerer.name, Offerer.siren)
            )
        ).all()

    def fetch_all_bank_informations_without_reimbursement_point(self) -> Iterable[BankInformation]:
        return (
            BankInformation.query.filter(
                BankInformation.iban.is_not(None),
                BankInformation.bic.is_not(None),
                BankInformation.venueId.is_(None),
                BankInformation.offererId.is_not(None),
            )
            .join(BankInformation.offerer)
            .options(sa.orm.contains_eager(BankInformation.offerer).load_only(Offerer.id, Offerer.name, Offerer.siren))
            .all()
        )

    def fetch_all_bank_information_without_rp_nor_offerer(self) -> Iterable[BankInformation]:
        """Return orphans bankInformation (i.e. used by any reimbursementPoint or link to any Offerer)
        while still being link to Cashflows."""
        return (
            BankInformation.query.join(Cashflow, BankInformation.id == Cashflow.bankInformationId)
            .filter(
                BankInformation.iban.is_not(None),
                BankInformation.bic.is_not(None),
                BankInformation.venueId.is_(None),
                BankInformation.offererId.is_(None),
            )
            .all()
        )

    def fetch_reimbursement_points_links(self, reimbursement_point: Venue) -> Iterable[VenueReimbursementPointLink]:
        return VenueReimbursementPointLink.query.filter(
            VenueReimbursementPointLink.reimbursementPointId == reimbursement_point.id
        ).all()

    def fetch_cashflows_by_reimbursement_point(self, reimbursement_point: Venue) -> Iterable[Cashflow]:
        return (
            Cashflow.query.join(Cashflow.reimbursementPoint)
            .filter(Cashflow.reimbursementPointId == reimbursement_point.id)
            .with_entities(Cashflow.id, Cashflow.bankInformationId)
            .all()
        )

    def fetch_cashflows_by_bank_information(self, bank_information: BankInformation) -> Iterable[Cashflow]:
        return (
            Cashflow.query.join(Cashflow.reimbursementPoint)
            .join(Venue.managingOfferer)
            .filter(Cashflow.bankInformationId == bank_information.id)
            .options(
                sa.orm.contains_eager(Cashflow.reimbursementPoint)
                .contains_eager(Venue.managingOfferer)
                .load_only(Offerer.id)
            )
            .all()
        )

    def fetch_invoices(self, reimbursement_point: Venue) -> Iterable[Invoice]:
        return (
            Invoice.query.filter(Invoice.reimbursementPointId == reimbursement_point.id)
            .with_entities(Invoice.id, Invoice.reimbursementPointId)
            .all()
        )

    def convert_venue_reimbursement_point_link(self, reimbursement_point: Venue, bank_account: BankAccount) -> None:
        """
        Convert all existing VenueReimbursementPointLink into their new-journey-equivalent VenueBankAccountLink

        An ActionHistory is also created so we can keep track of this action in the BackOffice.
        """
        links = self.fetch_reimbursement_points_links(reimbursement_point)
        processed = 0

        for link in links:
            new_link = VenueBankAccountLink(
                venueId=link.venueId, bankAccountId=bank_account.id, timespan=(link.timespan.lower, link.timespan.upper)
            )
            action_history = ActionHistory(
                actionType=ActionType.LINK_VENUE_BANK_ACCOUNT_CREATED,
                venueId=link.venueId,
                bankAccountId=bank_account.id,
                comment=comment,
            )
            db.session.add(new_link)
            db.session.add(action_history)
            db.session.flush()
            processed += 1

        self.processed_venue_reimbursement_point_link += processed
        self.created_venue_bank_account_link += processed
        self.created_action_history += processed

        print(f"Processed {processed} links for reimbursement_point {reimbursement_point.id}")

    def convert_reimbursement_point(self, bank_information: BankInformation) -> BankAccount:
        """
        Convert a reimbursementPoint into a BankAccount.

        BankAccount.id == ReimbursementPoint.id
        BankAccount.offererId == ReimbursementPoint.managingOffererId
        BankAccount.iban == BankInformation.iban
        BankAccount.bic == BankInformation.bic
        BankAccount.dsApplicationId == BankInformation.applicationId
        BankAccount.label == ReimbursementPoint.common_name
        """
        assert bank_information  # type hinting
        assert bank_information.iban
        assert bank_information.bic

        bank_account_label = self.construct_bank_account_label(bank_information)

        bank_account = BankAccount(
            id=bank_information.venue.id,
            iban=bank_information.iban,
            bic=bank_information.bic,
            label=bank_account_label,
            dsApplicationId=bank_information.applicationId,
            dateCreated=bank_information.dateModified,
            dateLastStatusUpdate=bank_information.dateModified,
            status=self.map_bank_information_status_to_bank_account_status(bank_information.status),
            offererId=bank_information.venue.managingOffererId,
        )

        db.session.add(bank_account)
        db.session.flush()

        self.processed_bank_informations_used_by_reimbursement_point += 1
        self.created_bank_accounts += 1

        return bank_account

    def convert_bank_information(self, bank_information: BankInformation) -> BankAccount:
        """
        Convert every BankInformation into a BankAccount.

        BankAccount.iban == BankInformation.iban
        BankAccount.bic == BankInformation.bic
        BankAccount.dsApplicationId == BankInformation.applicationId
        BankAccount.label == Offerer.siren + Offerer.name

        If the bankInformation is not link to any offerer, we try to retrieve it from the cashflows
        to which it's link.
        """
        assert bank_information  # type hinting
        assert bank_information.iban
        assert bank_information.bic

        bank_account_label = self.construct_bank_account_label(bank_information)

        offerer_id = bank_information.offererId
        if not bank_information.offererId:
            cashflows = self.fetch_cashflows_by_bank_information(bank_information)
            offerer_ids = set(cashflow.reimbursementPoint.managingOffererId for cashflow in cashflows)
            assert len(offerer_ids) == 1
            offerer_id = offerer_ids.pop()
        assert offerer_id

        bank_account = BankAccount(
            iban=bank_information.iban,
            bic=bank_information.bic,
            label=bank_account_label,
            dsApplicationId=bank_information.applicationId,
            dateCreated=bank_information.dateModified,
            dateLastStatusUpdate=bank_information.dateModified,
            status=self.map_bank_information_status_to_bank_account_status(bank_information.status),
            offererId=offerer_id,
        )

        db.session.add(bank_account)
        db.session.flush()

        if bank_information.offererId:
            self.processed_bank_informations_without_reimbursement_point += 1
        else:
            self.processed_bank_informations_without_rp_nor_offerer += 1
        self.created_bank_accounts += 1

        return bank_account

    def update_cashflows_by_reimbursement_point(
        self, reimbursement_point: Venue, bank_information: BankInformation, bank_account: BankAccount
    ) -> Iterable[Cashflow]:
        cashflows = self.fetch_cashflows_by_reimbursement_point(reimbursement_point)
        mapping = []
        for cashflow in cashflows:
            if bank_information.id != cashflow.bankInformationId:
                # The denormalize bankInformation doesn't match the bankInformation used
                # by the reimbursementPoint. This isn't the bankAccountId we want to set here
                # This cashflow will be process later while fetching bankInformation without reimbursementPoint
                continue
            mapping.append({"id": cashflow.id, "bankAccountId": bank_account.id})

        db.session.bulk_update_mappings(Cashflow, mapping)
        db.session.flush()

        self.updated_cashflows += len(mapping)
        print(f"Updated {len(mapping)} cashflows for reimbursement_point {reimbursement_point.id}")

        return cashflows

    def update_cashflows_by_bank_information(
        self, bank_information: BankInformation, bank_account: BankAccount
    ) -> None:
        cashflows = self.fetch_cashflows_by_bank_information(bank_information)
        mapping = [{"id": cashflow.id, "bankAccountId": bank_account.id} for cashflow in cashflows]

        db.session.bulk_update_mappings(Cashflow, mapping)
        db.session.flush()

        self.updated_cashflows += len(mapping)
        print(f"Updated {len(mapping)} cashflows for bank_information {bank_information.id}")

    def update_invoices_by_reimbursement_point(self, reimbursement_point: Venue, bank_account: BankAccount) -> None:
        invoices = self.fetch_invoices(reimbursement_point)
        mapping = [{"id": invoice.id, "bankAccountId": bank_account.id} for invoice in invoices]

        db.session.bulk_update_mappings(Invoice, mapping)
        db.session.flush()

        self.updated_invoices += len(mapping)
        print(f"Updated {len(mapping)} invoices for reimbursement_point {reimbursement_point.id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Migrate data from the old bankInformation journey to the new bankAccount one"
    )
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    migrate_data = MigrateData(args.dry_run)
    migrate_data.process()
