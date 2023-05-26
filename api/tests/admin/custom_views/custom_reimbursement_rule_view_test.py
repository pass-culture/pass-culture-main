import datetime
import decimal
from unittest import mock

import pcapi.core.finance.factories as finance_factories
import pcapi.core.finance.models as finance_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories

from tests.conftest import clean_database


@clean_database
@mock.patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
def test_create_rule(mocked_validate_csrf_token, client, app):
    admin = users_factories.AdminFactory()
    offerer = offerers_factories.OffererFactory()

    data = dict(
        offerer=offerer.id,
        subcategories=[],
        rate="80,25",
        start_date="2030-10-01",
        end_date="",
    )
    client = client.with_session_auth(admin.email)
    response = client.post("/pc/back-office/customreimbursementrule/new/", form=data)

    assert response.status_code == 302
    rule = finance_models.CustomReimbursementRule.query.one()
    assert rule.offerer == offerer
    assert rule.rate == decimal.Decimal("0.8025")
    assert rule.subcategories == []
    assert rule.timespan.lower == datetime.datetime(2030, 9, 30, 22, 0)  # UTC
    assert rule.timespan.upper is None


@clean_database
@mock.patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
def test_edit_rule(mocked_validate_csrf_token, client, app):
    admin = users_factories.AdminFactory()
    timespan = (datetime.datetime.today() + datetime.timedelta(days=10), None)
    rule = finance_factories.CustomReimbursementRuleFactory(timespan=timespan)

    client = client.with_session_auth(admin.email)
    data = {"end_date": "2030-10-01"}
    response = client.post(f"/pc/back-office/customreimbursementrule/edit/?id={rule.id}", form=data)

    assert response.status_code == 302
    rule = finance_models.CustomReimbursementRule.query.one()
    assert rule.timespan.lower == timespan[0]  # unchanged
    assert rule.timespan.upper == datetime.datetime(2030, 9, 30, 22, 0)  # UTC
