from datetime import date
from datetime import timedelta

import pytest

import pcapi.core.finance.factories as finance_factories
import pcapi.core.finance.models as finance_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
def test_with_venue_filter(app):
    beginning_date_iso_format = (date.today() - timedelta(days=2)).isoformat()
    ending_date_iso_format = (date.today() + timedelta(days=2)).isoformat()
    offerer = offerers_factories.OffererFactory()
    venue1 = offerers_factories.VenueFactory(managingOfferer=offerer)
    venue2 = offerers_factories.VenueFactory(managingOfferer=offerer)
    for venue in (venue1, venue2):
        finance_factories.PaymentStatusFactory(
            payment__booking__stock__offer__venue=venue,
            status=finance_models.TransactionStatus.SENT,
            payment__transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 06-21",
        )
    pro = users_factories.ProFactory()
    offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

    # When
    client = TestClient(app.test_client()).with_session_auth(pro.email)
    response = client.get(
        f"/reimbursements/csv?reimbursementPeriodBeginningDate={beginning_date_iso_format}&reimbursementPeriodEndingDate={ending_date_iso_format}&venueId={humanize(venue1.id)}"
    )

    # Then
    assert response.status_code == 200
    assert response.headers["Content-type"] == "text/csv; charset=utf-8;"
    assert response.headers["Content-Disposition"] == "attachment; filename=remboursements_pass_culture.csv"
    rows = response.data.decode("utf-8").splitlines()
    assert len(rows) == 1 + 1  # header + payments


@pytest.mark.usefixtures("db_session")
def test_with_reimbursement_period_filter(app):
    beginning_date_iso_format = (date.today() - timedelta(days=2)).isoformat()
    ending_date_iso_format = (date.today() + timedelta(days=2)).isoformat()
    user_offerer = offerers_factories.UserOffererFactory()
    offerer = user_offerer.offerer
    pro = user_offerer.user
    finance_factories.PaymentStatusFactory(
        payment__booking__stock__offer__venue__managingOfferer=offerer,
        status=finance_models.TransactionStatus.SENT,
        payment__transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 06-21",
        date=date.today() - timedelta(days=2),
    )
    finance_factories.PaymentStatusFactory(
        payment__booking__stock__offer__venue__managingOfferer=offerer,
        status=finance_models.TransactionStatus.SENT,
        payment__transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 06-21",
        date=date.today() - timedelta(days=3),
    )
    finance_factories.PaymentStatusFactory(
        payment__booking__stock__offer__venue__managingOfferer=offerer,
        status=finance_models.TransactionStatus.SENT,
        payment__transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 06-21",
        date=date.today() + timedelta(days=2),
    )
    finance_factories.PaymentStatusFactory(
        payment__booking__stock__offer__venue__managingOfferer=offerer,
        status=finance_models.TransactionStatus.SENT,
        payment__transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 06-21",
        date=date.today() + timedelta(days=3),
    )

    # When
    client = TestClient(app.test_client()).with_session_auth(pro.email)
    response = client.get(
        f"/reimbursements/csv?reimbursementPeriodBeginningDate={beginning_date_iso_format}&reimbursementPeriodEndingDate={ending_date_iso_format}"
    )

    # Then
    assert response.status_code == 200
    assert response.headers["Content-type"] == "text/csv; charset=utf-8;"
    assert response.headers["Content-Disposition"] == "attachment; filename=remboursements_pass_culture.csv"
    rows = response.data.decode("utf-8").splitlines()
    assert len(rows) == 1 + 2  # header + payments


@pytest.mark.usefixtures("db_session")
def test_with_non_given_reimbursement_period(app):
    user_offerer = offerers_factories.UserOffererFactory()
    pro = user_offerer.user

    # When
    client = TestClient(app.test_client()).with_session_auth(pro.email)
    response = client.get("/reimbursements/csv")

    # Then
    assert response.status_code == 400
    assert response.json["reimbursementPeriodBeginningDate"] == [
        "Vous devez renseigner une date au format ISO (ex. 2021-12-24)"
    ]
    assert response.json["reimbursementPeriodEndingDate"] == [
        "Vous devez renseigner une date au format ISO (ex. 2021-12-24)"
    ]


@pytest.mark.usefixtures("db_session")
def test_admin_can_access_reimbursements_data_with_venue_filter(app, client):
    # Given
    beginning_date = date.today() - timedelta(days=2)
    ending_date = date.today() + timedelta(days=2)
    admin = users_factories.AdminFactory()
    user_offerer = offerers_factories.UserOffererFactory()
    offerer = user_offerer.offerer
    status = finance_factories.PaymentStatusFactory(
        payment__booking__stock__offer__venue__managingOfferer=offerer,
        status=finance_models.TransactionStatus.SENT,
        payment__transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 06-21",
        date=date.today(),
    )
    venue = status.payment.booking.venue

    # When
    admin_client = client.with_session_auth(admin.email)
    response = admin_client.get(
        "/reimbursements/csv?venueId={}&reimbursementPeriodBeginningDate={}&reimbursementPeriodEndingDate={}".format(
            humanize(venue.id), beginning_date.isoformat(), ending_date.isoformat()
        )
    )

    # Then
    assert response.status_code == 200
    assert response.headers["Content-type"] == "text/csv; charset=utf-8;"
    assert response.headers["Content-Disposition"] == "attachment; filename=remboursements_pass_culture.csv"
    rows = response.data.decode("utf-8").splitlines()
    assert len(rows) == 2  # header + payments


@pytest.mark.usefixtures("db_session")
def test_admin_cannot_access_reimbursements_data_without_venue_filter(app, client):
    # Given
    beginning_date = date.today() - timedelta(days=2)
    ending_date = date.today() + timedelta(days=2)
    admin = users_factories.AdminFactory()
    user_offerer = offerers_factories.UserOffererFactory()
    offerer = user_offerer.offerer
    finance_factories.PaymentStatusFactory(
        payment__booking__stock__offer__venue__managingOfferer=offerer,
        status=finance_models.TransactionStatus.SENT,
        payment__transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 06-21",
        date=date.today(),
    )

    # When
    admin_client = client.with_session_auth(admin.email)
    response = admin_client.get(
        "/reimbursements/csv?reimbursementPeriodBeginningDate={}&reimbursementPeriodEndingDate={}".format(
            beginning_date.isoformat(), ending_date.isoformat()
        )
    )

    # Then
    assert response.status_code == 400
