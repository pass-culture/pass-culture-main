from pcapi.flask_app import app

app.app_context().push()

import csv
import datetime
import decimal
import sys
import sqlalchemy as sa
import pcapi.core.finance.api as finance_api
import pcapi.core.finance.models as finance_models
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
from pcapi.core.categories.subcategories import ALL_SUBCATEGORIES


BOUNDARY_DATE = datetime.datetime(2022, 12, 31, 23, 0)  # => 01/01/2023 CET


def process_file(path, apply_changes):
    offerers_by_siren = {
        siren: id
        for id, siren in offerers_models.Offerer.query.filter(
            offerers_models.Offerer.siren.isnot(None)
        ).with_entities(
            offerers_models.Offerer.id,
            offerers_models.Offerer.siren,
        )
    }

    with open(path, "r") as csv_file:
        reader = csv.DictReader(csv_file)
        for i_line, row in enumerate(reader, 1):
            siren = row["SIREN"]
            offerer_id = offerers_by_siren.get(siren)
            if not offerer_id:
                print(f"ERR:{i_line}: Unknown SIREN - {siren}")
                continue

            rule_to_close = bool(row["Règle à supprimer"])
            rule_to_create = bool(row["Nouvelle règle"])
            if rule_to_create:
                new_rate = parse_rate(row["Nouvelle règle"])
                if new_rate is None:
                    print(
                        f"ERR:{i_line}: Unparseable new rate: \"{row['Nouvelle règle']}\""
                    )
                    continue
            else:
                new_rate = None

            offer_related = {
                "Sous catégorie": False,
                "Offre": True,
            }[row["Niveau règle"]]
            if offer_related:
                offer_name = row["Règle"]
                offer = (
                    offers_models.Offer.query.filter(
                        offers_models.Offer.name == offer_name
                    )
                    .join(offers_models.Offer.venue)
                    .filter(offerers_models.Venue.managingOffererId == offerer_id)
                    .one()
                )
                subcategory = None
            else:
                offer = None
                subcategory = get_subcategory_by_label(row["Règle"])
                if not subcategory:
                    print(f"ERR:{i_line}: Unknown subcategory: \"{row['Règle']}\"")
                    continue

            if rule_to_close:
                if offer_related:
                    rule = finance_models.CustomReimbursementRule.query.filter(
                        finance_models.CustomReimbursementRule.offerId == offer.id,
                    ).filter(
                        sa.func.upper(finance_models.CustomReimbursementRule.timespan)
                        == None
                    )
                    rule = rule.one_or_none()
                else:
                    rule = (
                        finance_models.CustomReimbursementRule.query.filter_by(
                            offererId=offerer_id,
                            subcategories=[subcategory.id],
                        )
                        .filter(
                            sa.func.upper(
                                finance_models.CustomReimbursementRule.timespan
                            )
                            == None
                        )
                        .one_or_none()
                    )
                if not rule:
                    print(f"ERR:{i_line}: Could not find rule to close")
                    continue
                if apply_changes:
                    finance_api.edit_reimbursement_rule(rule, BOUNDARY_DATE)
                else:
                    print(
                        f"INF:{i_line}: would end rule {rule.id} [{rule.rate} - {rule.amount}] - siren : {siren} - "
                    )

            if rule_to_create:
                if offer:
                    if apply_changes:
                        print(f"ERR:{i_line}: Not implemented.")
                        # No rules should be created for offers for the 2023 batch
                        # finance_api.create_offer_reimbursement_rule(
                        #     offer.id,
                        #     amount=amount,
                        #     start_date=BOUNDARY_DATE,
                        #     end_date=None,
                        # )
                    else:
                        print(
                            f"INF:{i_line}: would create rule for offer {offer.id} - siren : {siren}"
                        )
                else:
                    if apply_changes:
                        finance_api.create_offerer_reimbursement_rule(
                            offerer_id,
                            subcategories=[subcategory.id],
                            rate=new_rate,
                            start_date=BOUNDARY_DATE,
                            end_date=None,
                        )
                    else:
                        print(
                            f"INF:{i_line}: would create rule for subcategories [{subcategory.id} - {new_rate}] - siren : {siren}"
                        )


def get_subcategory_by_label(label):
    for subcategory in ALL_SUBCATEGORIES:
        if subcategory.pro_label == label:
            return subcategory
    return None


def parse_rate(rate):
    if "%" not in rate:
        return None
    # rate must be between 0 and 1, not a percentage.
    rate = decimal.Decimal(rate.rstrip("% ").replace(",", ".")) / 100
    return rate


process_file(sys.argv[1], "--apply-changes" in sys.argv[1:])
