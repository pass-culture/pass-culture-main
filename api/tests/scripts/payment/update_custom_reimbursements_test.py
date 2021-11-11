import datetime
import io

import pytest

import pcapi.core.offers.factories as offers_factories
import pcapi.core.payments.factories as payments_factories
import pcapi.core.payments.models as payments_models
from pcapi.scripts.payment.update_custom_reimbursements import update_from_csv_file
from pcapi.utils.human_ids import humanize


@pytest.mark.usefixtures("db_session")
def test_update_from_csv_file_basics():
    offer = offers_factories.OfferFactory()

    # fmt: off
    csv = "\n".join((
        "this,is,a,header",
        f"""name of offerer,{humanize(offer.id)},"12,34€",10€""",
    ))
    # fmt: on
    results = update_from_csv_file(io.StringIO(csv))

    rule = payments_models.CustomReimbursementRule.query.one()
    assert not results["errors"]
    assert results["created"] == [rule]
    assert rule.offer == offer
    assert rule.amount == 10
    assert rule.timespan.lower == datetime.datetime(2015, 1, 1)
    assert rule.timespan.upper is None


@pytest.mark.usefixtures("db_session")
def test_update_from_csv_file_unknown_offer():
    # fmt: off
    csv = "\n".join((
        "this,is,a,header",
        """name of offerer,ABCD,"12,34€",10€""",
    ))
    # fmt: on
    results = update_from_csv_file(io.StringIO(csv))

    assert not results["created"]
    assert results["errors"] == ["line 2: File references unknown offer ABCD (68)"]


@pytest.mark.usefixtures("db_session")
def test_update_from_csv_file_detects_existing_rules_and_mismatches():
    rule1 = payments_factories.CustomReimbursementRuleFactory(amount=8)
    rule2 = payments_factories.CustomReimbursementRuleFactory(amount=8)

    # fmt: off
    csv = "\n".join((
        "this,is,a,header",
        f"""name of offerer,{humanize(rule1.offerId)},"12,34€",8€""",
        f"""name of offerer,{humanize(rule2.offerId)},"12,34€",7€""",
    ))
    # fmt: on
    results = update_from_csv_file(io.StringIO(csv))

    assert not results["created"]
    assert results["errors"] == [
        f"line 3: Existing rule on offer {humanize(rule2.offerId)} ({rule2.offerId}) reimburses 8.00, file says 7"
    ]
