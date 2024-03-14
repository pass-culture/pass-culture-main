import argparse
import datetime
import time
from typing import Iterable

import sqlalchemy as sa
from sqlalchemy.engine.row import Row

from pcapi.app import app
from pcapi.core.finance.models import BankAccount
from pcapi.core.history.models import ActionHistory
from pcapi.core.history.models import ActionType
from pcapi.core.offerers.models import VenueBankAccountLink
from pcapi.models import db
from pcapi.utils import db as db_utils


app.app_context().push()

comment = "(PC-28501) Suppression des coordonnées bancaires en doublon"


class SoftDeleteBankAccounts:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run

        # metadata about the current processing
        self.duration = 0

        self.closed_venue_bank_account_link = 0
        self.opened_venue_bank_account_link = 0
        self.action_history_created = 0
        self.bank_account_soft_deleted = 0

    def go(self) -> None:
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
            print(f"{self.bank_account_soft_deleted} bank accounts would have been soft deleted")
            print(f"{self.closed_venue_bank_account_link} links would have been closed")
            print(f"{self.action_history_created} action history would have been created")
        else:
            print(f"{self.bank_account_soft_deleted} bank accounts soft deleted")
            print(f"{self.closed_venue_bank_account_link} links closed")
            print(f"{self.action_history_created} action history created")

    def _go(self) -> None:
        rows = self.fetch_duplicates_without_finance_data()
        for row in rows:
            for bank_account_id in row.duplicates:
                print(
                    f"processing bank_account {bank_account_id} ({row.bank_account_iban}) from offerer {row.offererId}"
                )
                self.close_current_venues_links(bank_account_id, row)
                self.soft_delete_bank_account(bank_account_id)

    def link_venues_on_main_bank_account(self, duplicate_id: int, row: Row, venues_ids: list[int]) -> None:
        try:
            main_bank_account = BankAccount.query.filter(
                BankAccount.iban == row.bank_account_iban,
                BankAccount.bic == row.bank_account_bic,
                BankAccount.dsApplicationId.is_not(None),
                BankAccount.offererId == row.offererId,
                BankAccount.id != duplicate_id,
            ).one()
        except sa.orm.exc.MultipleResultsFound:
            print(f"multiple candidates found for main bank account of duplicate {duplicate_id}")
            return
        except sa.orm.exc.NoResultFound:
            print(f"No candidate found for main bank_account of duplicate {duplicate_id}")
            return

        new_links = []
        action_history = []
        now = datetime.datetime.utcnow()

        for venue_id in venues_ids:
            new_links.append(
                {
                    "venueId": venue_id,
                    "bankAccountId": main_bank_account.id,
                    "timespan": db_utils.make_timerange(now),
                }
            )
            action_history.append(
                {
                    "actionType": ActionType.LINK_VENUE_BANK_ACCOUNT_CREATED,
                    "venueId": venue_id,
                    "bankAccountId": main_bank_account.id,
                    "comment": comment,
                }
            )

        db.session.bulk_insert_mappings(VenueBankAccountLink, new_links)
        db.session.bulk_insert_mappings(ActionHistory, action_history)
        db.session.flush()
        self.action_history_created += len(action_history)
        self.opened_venue_bank_account_link += len(new_links)
        print(
            f"created {len(new_links)} link on main bank_account {main_bank_account.id} from duplicate {duplicate_id}"
        )
        print(f"created {len(action_history)} action history accordingly")

    def close_current_venues_links(self, bank_account_id: int, row: Row) -> None:
        venues_ids_linked = []
        mapping = []
        now = datetime.datetime.utcnow()
        for current_link in self.fetch_current_venues_links(bank_account_id):
            mapping.append(
                {"id": current_link.id, "timespan": db_utils.make_timerange(current_link.timespan.lower, now)}
            )
            action_history = ActionHistory(
                actionType=ActionType.LINK_VENUE_BANK_ACCOUNT_DEPRECATED,
                venueId=current_link.venueId,
                bankAccountId=current_link.bankAccountId,
                comment=comment,
            )
            db.session.add(action_history)
            venues_ids_linked.append(current_link.venueId)
            self.closed_venue_bank_account_link += 1
            self.action_history_created += 1
        print(f"closed {len(mapping)} current links")
        db.session.bulk_update_mappings(VenueBankAccountLink, mapping)
        db.session.flush()

        # We just close active venues link on a duplicate
        # Now we need to switch them to a main bank account, if possible
        self.link_venues_on_main_bank_account(bank_account_id, row, venues_ids_linked)

    def soft_delete_bank_account(self, bank_account_id: int) -> None:
        db.session.query(BankAccount).filter_by(id=bank_account_id).update(
            {"isActive": False}, synchronize_session=False
        )
        db.session.flush()
        print(f"bank account {bank_account_id} soft deleted")
        self.bank_account_soft_deleted += 1

    def fetch_current_venues_links(self, bank_account_id: int) -> Iterable[VenueBankAccountLink]:
        return VenueBankAccountLink.query.filter(
            VenueBankAccountLink.bankAccountId == bank_account_id,
            VenueBankAccountLink.timespan.contains(datetime.datetime.utcnow()),
        )

    def fetch_duplicates_without_finance_data(self) -> Iterable[Row]:
        rows = db.session.execute(
            sa.text(
                """
                -- All offerer that have at least one duplicate bank account (i.e. same IBAN & BIC):
                --      without a dsApplicationId
                --      without any cashflow
                --      without any invoice

                SELECT *,
                       cardinality(duplicates) AS how_much_duplicates
                FROM
                  (SELECT bank_account."offererId",
                          bank_account."iban" AS bank_account_iban,
                          bank_account."bic" AS bank_account_bic,
                          array_agg(DISTINCT duplicate."id") AS duplicates 
                   FROM bank_account
                   JOIN bank_account AS duplicate ON bank_account.id != duplicate.id
                   AND bank_account."iban"=duplicate."iban"
                   AND bank_account."bic"=duplicate."bic"
                   AND bank_account."offererId"=duplicate."offererId"
                   LEFT OUTER JOIN cashflow on duplicate.id=cashflow."bankAccountId"
                   LEFT OUTER JOIN invoice on duplicate.id=invoice."bankAccountId"
                   WHERE 
                        bank_account."dsApplicationId" IS NOT NULL
                        AND bank_account."isActive" is True
                        AND duplicate."dsApplicationId" IS NULL
                        AND duplicate."isActive" is True
                        AND cashflow."bankAccountId" IS NULL
                        AND invoice."bankAccountId" IS NULL
                   GROUP BY bank_account."offererId",
                            bank_account.iban, bank_account.bic) as duplicates_query
                ORDER BY cardinality(duplicates) DESC;
            """
            )
        )

        return rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    soft_delete = SoftDeleteBankAccounts(args.dry_run)
    soft_delete.go()
