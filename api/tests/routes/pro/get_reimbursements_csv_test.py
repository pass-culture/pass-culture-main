import datetime
import urllib.parse

import pytest

import pcapi.core.finance.factories as finance_factories
import pcapi.core.finance.models as finance_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories


@pytest.mark.usefixtures("db_session")
def test_with_venue_filter(client):
    period = datetime.date(2021, 1, 1), datetime.date(2021, 1, 15)
    offerer = offerers_factories.OffererFactory()
    venue1 = offerers_factories.VenueFactory(managingOfferer=offerer, pricing_point="self")
    venue2 = offerers_factories.VenueFactory(managingOfferer=offerer, pricing_point=venue1)
    for venue in (venue1, venue2):
        finance_factories.PaymentStatusFactory(
            payment__booking__stock__offer__venue=venue,
            status=finance_models.TransactionStatus.SENT,
            payment__transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 01-21",
            date=datetime.datetime(2021, 1, 1),
        )
    pro = users_factories.ProFactory()
    offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

    # When
    client = client.with_session_auth(pro.email)
    response = client.get(
        "/reimbursements/csv?"
        + urllib.parse.urlencode(
            {
                "reimbursementPeriodBeginningDate": period[0].isoformat(),
                "reimbursementPeriodEndingDate": period[1].isoformat(),
                "venueId": venue1.id,
            }
        )
    )

    # Then
    assert response.status_code == 200
    assert response.headers["Content-type"] == "text/csv; charset=utf-8;"
    assert response.headers["Content-Disposition"] == "attachment; filename=remboursements_pass_culture.csv"
    rows = response.data.decode("utf-8").splitlines()
    assert len(rows) == 1 + 1  # header + payments


@pytest.mark.usefixtures("db_session")
def test_with_reimbursement_period_filter(client):
    period = datetime.date(2021, 1, 1), datetime.date(2021, 1, 15)
    user_offerer = offerers_factories.UserOffererFactory()
    offerer = user_offerer.offerer
    pro = user_offerer.user
    finance_factories.PaymentStatusFactory(
        payment__booking__stock__offer__venue__managingOfferer=offerer,
        payment__booking__stock__offer__venue__pricing_point="self",
        status=finance_models.TransactionStatus.SENT,
        payment__transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 01-21",
        date=datetime.datetime(2021, 1, 1),  # in requested period
    )
    finance_factories.PaymentStatusFactory(
        payment__booking__stock__offer__venue__managingOfferer=offerer,
        payment__booking__stock__offer__venue__pricing_point="self",
        status=finance_models.TransactionStatus.SENT,
        payment__transactionLabel="xxx",
        date=datetime.datetime(2020, 12, 1),  # before requested period
    )
    finance_factories.PaymentStatusFactory(
        payment__booking__stock__offer__venue__managingOfferer=offerer,
        payment__booking__stock__offer__venue__pricing_point="self",
        status=finance_models.TransactionStatus.SENT,
        payment__transactionLabel="pass Culture Pro - remboursement 2ème quinzaine 01-21",
        date=datetime.datetime(2021, 1, 4),  # in requested period
    )
    finance_factories.PaymentStatusFactory(
        payment__booking__stock__offer__venue__managingOfferer=offerer,
        payment__booking__stock__offer__venue__pricing_point="self",
        status=finance_models.TransactionStatus.SENT,
        payment__transactionLabel="xxx",
        date=datetime.datetime(2021, 2, 1),  # after requested period
    )

    # When
    client = client.with_session_auth(pro.email)
    response = client.get(
        "/reimbursements/csv?"
        + urllib.parse.urlencode(
            {
                "reimbursementPeriodBeginningDate": period[0].isoformat(),
                "reimbursementPeriodEndingDate": period[1].isoformat(),
            }
        )
    )

    # Then
    assert response.status_code == 200
    assert response.headers["Content-type"] == "text/csv; charset=utf-8;"
    assert response.headers["Content-Disposition"] == "attachment; filename=remboursements_pass_culture.csv"
    rows = response.data.decode("utf-8").splitlines()
    assert len(rows) == 1 + 2  # header + payments


@pytest.mark.usefixtures("db_session")
def test_without_reimbursement_period(client):
    user_offerer = offerers_factories.UserOffererFactory()
    pro = user_offerer.user

    # When
    response = client.with_session_auth(pro.email).get("/reimbursements/csv")

    # Then
    assert response.status_code == 400
    assert response.json["reimbursementPeriodBeginningDate"] == [
        "Vous devez renseigner une date au format ISO (ex. 2021-12-24)"
    ]
    assert response.json["reimbursementPeriodEndingDate"] == [
        "Vous devez renseigner une date au format ISO (ex. 2021-12-24)"
    ]


@pytest.mark.usefixtures("db_session")
def test_admin_can_access_reimbursements_data_with_venue_filter(client):
    # Given
    period = datetime.date(2021, 1, 1), datetime.date(2021, 1, 15)
    admin = users_factories.AdminFactory()
    user_offerer = offerers_factories.UserOffererFactory()
    offerer = user_offerer.offerer
    status = finance_factories.PaymentStatusFactory(
        payment__booking__stock__offer__venue__managingOfferer=offerer,
        payment__booking__stock__offer__venue__pricing_point="self",
        status=finance_models.TransactionStatus.SENT,
        payment__transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 06-21",
        date=datetime.datetime(2021, 1, 1),
    )
    venue = status.payment.booking.venue

    # When
    client = client.with_session_auth(admin.email)
    response = client.get(
        "/reimbursements/csv?"
        + urllib.parse.urlencode(
            {
                "reimbursementPeriodBeginningDate": period[0].isoformat(),
                "reimbursementPeriodEndingDate": period[1].isoformat(),
                "venueId": venue.id,
            }
        )
    )

    # Then
    assert response.status_code == 200
    assert response.headers["Content-type"] == "text/csv; charset=utf-8;"
    assert response.headers["Content-Disposition"] == "attachment; filename=remboursements_pass_culture.csv"
    rows = response.data.decode("utf-8").splitlines()
    assert len(rows) == 2  # header + payments


@pytest.mark.usefixtures("db_session")
def test_admin_cannot_access_reimbursements_data_without_venue_filter(client):
    # Given
    period = datetime.date(2021, 1, 1), datetime.date(2021, 1, 15)
    admin = users_factories.AdminFactory()

    # When
    client = client.with_session_auth(admin.email)
    response = client.get(
        "/reimbursements/csv?"
        + urllib.parse.urlencode(
            {
                "reimbursementPeriodBeginningDate": period[0].isoformat(),
                "reimbursementPeriodEndingDate": period[1].isoformat(),
            }
        )
    )

    # Then
    assert response.status_code == 400
