import argparse
import datetime

from pcapi.core.finance import models as finance_models
from pcapi.core.history import models as history_models
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db


def create_bank_account(do_update: bool, bic: str, iban: str, venue_id: str) -> None:
    venue = offerers_models.Venue.query.filter(offerers_models.Venue.id == int(venue_id)).one_or_none()
    if venue:
        bank_account = finance_models.BankAccount(
            iban=iban,
            bic=bic,
            label=venue.common_name,
            offerer=venue.managingOfferer,
            dsApplicationId=None,
            status=finance_models.BankAccountApplicationStatus.ACCEPTED,
        )
        db.session.add(bank_account)
        db.session.flush()
        link = offerers_models.VenueBankAccountLink(
            bankAccount=bank_account, venue=venue, timespan=(datetime.datetime.utcnow(),)
        )
        created_log = history_models.ActionHistory(
            actionType=history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_CREATED,
            venue=venue,
            bankAccount=bank_account,
            comment="(PC-33982) Compte bancaire créé manuellement pour contourner un dossier DS CB bloqué",
        )
        db.session.add(created_log)
        db.session.add(link)

    if do_update:
        db.session.commit()
    else:
        db.session.rollback()


if __name__ == "__main__":
    from pcapi.flask_app import app

    app.app_context().push()

    parser = argparse.ArgumentParser(description="Manually create BankAccount")
    parser.add_argument("--not-dry", action="store_true", help="set to really process (dry-run by default)")
    parser.add_argument("--bic", help="bic of the bank account")
    parser.add_argument("--iban", help="iban of the bank account")
    parser.add_argument("--venue-id", help="id of the concerned venue")
    args = parser.parse_args()

    create_bank_account(do_update=args.not_dry, bic=args.bic, iban=args.iban, venue_id=args.venue_id)
