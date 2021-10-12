# FIXME (dbaty, 2021-10-29): remove this script once we're sure that
# the new Flask-admin-based interface is enough.
import csv
import datetime
from decimal import Decimal

from sqlalchemy.orm import joinedload

from pcapi.core.offers.models import Offer
from pcapi.core.payments.models import CustomReimbursementRule
from pcapi.repository import repository
from pcapi.utils.human_ids import dehumanize


FIELD_NAMES = (
    "offerer_name",
    "humanized_offer_id",
    "offer_amount",
    "reimbursed_amount",
)

DEFAULT_TIMESPAN = (datetime.datetime(2015, 1, 1), None)


def update_custom_reimbursements(path):
    """Create custom reimbursement rules.

    This function returns a dictionary with "created", "errors" and
    "warnings" keys that MUST be checked by the operator.

    - "created" key: list created CustomReimbursementRule objects;

    - "errors" key: list errors, i.e. lines for which no reimbursement
      rule has been created;

    - "warnings" keys: lines that have suspicious data, but for which
      the reimbursement rule HAS BEEN CREATED nevertheless.

    Usage::

        >>> results = update_custom_reimbursements("/path/to/rules.csv")
        >>> for key in ("created", "errors", "warnings"):
            ... print(key)
            ... print("\n".join(str(i) for i in results[key]))
    """
    with open(path, encoding="utf-8") as csv_file:
        return update_from_csv_file(csv_file)


def _get_amount(s: str) -> Decimal:
    # Turn "12,34€" into a Decimal object.
    return Decimal(s.strip("€ ").replace(",", "."))


def update_from_csv_file(csv_file):
    # XXX: We don't look at CustomReimbursementRule.timespan here,
    # since we currently don't have multiple rules for the same offer,
    # and this script does not support that for simplicity's sake.
    existing_rules = {rule.offerId: rule for rule in CustomReimbursementRule.query.all()}

    results = {"errors": [], "warnings": [], "created": []}
    reader = csv.DictReader(csv_file, fieldnames=FIELD_NAMES)
    for line_nb, row in enumerate(reader, 1):
        if line_nb == 1:
            continue  # ignore header
        offer_id = dehumanize(row["humanized_offer_id"])
        reimbursed_amount = _get_amount(row["reimbursed_amount"])
        file_offer_amount = _get_amount(row["offer_amount"])

        offer = Offer.query.options(joinedload(Offer.stocks)).filter_by(id=offer_id).one_or_none()
        if not offer:
            results["errors"].append(
                f"line {line_nb}: File references unknown offer {row['humanized_offer_id']} ({offer_id})"
            )
            continue

        rule = existing_rules.get(offer_id)
        if rule:
            if rule.amount != reimbursed_amount:
                results["errors"].append(
                    f"line {line_nb}: Existing rule on offer {row['humanized_offer_id']} ({offer_id}) reimburses {rule.amount}, file says {reimbursed_amount}"
                )
            continue

        prices = {stock.price for stock in offer.stocks}
        if len(prices) > 1:
            results["warnings"].append(
                f"line {line_nb}: Found multiple prices for offer {row['humanized_offer_id']} ({offer_id}): {prices}"
            )
        if not prices:
            results["warnings"].append(
                f"line {line_nb}: No stock found in database for offer {row['humanized_offer_id']} ({offer_id}), but reimbursement rule has been added nevertheless"
            )
        else:
            db_offer_amount = prices.pop()
            if file_offer_amount != db_offer_amount:
                results["warnings"].append(
                    f"line {line_nb}: Price in database for offer {row['humanized_offer_id']} ({offer_id}) is {db_offer_amount}, file says {file_offer_amount}"
                )

        rule = CustomReimbursementRule(offerId=offer_id, amount=reimbursed_amount, timespan=DEFAULT_TIMESPAN)
        repository.save(rule)
        existing_rules[offer_id] = rule
        results["created"].append(rule)

    return results
