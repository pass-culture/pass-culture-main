import datetime
import decimal

import click
import sqlalchemy.orm as sqla_orm

import pcapi.core.finance.utils as finance_utils
import pcapi.core.offers.models as offers_models
import pcapi.core.payments.api as payments_api
from pcapi.utils import human_ids
from pcapi.utils.blueprint import Blueprint
import pcapi.utils.date as date_utils


blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("add_custom_offer_reimbursement_rule")
@click.option("--offer-humanized-id", required=True)
@click.option("--offer-original-amount", required=True)
@click.option("--offerer-id", type=int, required=True)
@click.option("--reimbursed-amount", required=True)
@click.option("--valid-from", required=True)
@click.option("--valid-until", required=False)
@click.option("--force", required=False, is_flag=True, help="Ignore warnings and create rule anyway")
def add_custom_offer_reimbursement_rule(
    offer_humanized_id: str,
    offer_original_amount: decimal.Decimal,
    offerer_id: int,
    reimbursed_amount: decimal.Decimal,
    valid_from: str,
    valid_until: str = None,
    force: bool = False,
):
    """Add a custom reimbursement rule that is linked to an offer."""
    offer_original_amount = decimal.Decimal(offer_original_amount.replace(",", "."))
    reimbursed_amount = decimal.Decimal(reimbursed_amount.replace(",", "."))

    offer_id = human_ids.dehumanize(offer_humanized_id)
    offer = (
        offers_models.Offer.query.options(
            sqla_orm.joinedload(offers_models.Offer.stocks, innerjoin=True),
            sqla_orm.joinedload(offers_models.Offer.venue, innerjoin=True),
        )
        .filter_by(id=offer_id)
        .one_or_none()
    )
    if not offer:
        print(f"Could not find offer: {offer_humanized_id}")
        return

    warnings = []
    if offer.venue.managingOffererId != offerer_id:
        warnings.append(f"Mismatch on offerer: given {offerer_id}, expected {offer.venue.managingOffererId}")

    stock_amounts = {stock.price for stock in offer.stocks}
    if len(stock_amounts) > 1:
        warnings.append(f"Possible mismatch on original amount: found multiple amounts in database: {stock_amounts}")
    stock_amount = stock_amounts.pop()
    if offer_original_amount != stock_amount:
        warnings.append(f"Mismatch on original amount: given {offer_original_amount}, expected {stock_amount}")

    if warnings:
        print("Found multiple warnings. Double-check that the command has been given the right information.")
        print("\n".join(warnings))
        if not force:
            print(
                "Command has failed. Use `--force` if you are really sure that you "
                "want to ignore warnings and proceed anyway."
            )
            return

    valid_from = date_utils.get_day_start(datetime.date.fromisoformat(valid_from), finance_utils.ACCOUNTING_TIMEZONE)
    valid_until = (
        date_utils.get_day_start(datetime.date.fromisoformat(valid_until), finance_utils.ACCOUNTING_TIMEZONE)
        if valid_until
        else None
    )

    rule = payments_api.create_offer_reimbursement_rule(
        offer_id=offer.id,
        amount=reimbursed_amount,
        start_date=valid_from,
        end_date=valid_until,
    )
    print(f"Created new rule: {rule.id}")
