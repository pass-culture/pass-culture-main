from datetime import date
from datetime import timedelta

import pytest

import pcapi.core.offers.factories as offers_factories
import pcapi.core.payments.factories as payments_factories
from pcapi.core.testing import override_features
import pcapi.core.users.factories as users_factories
from pcapi.models.payment_status import TransactionStatus
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
def test_with_user_linked_to_offerers(app):
    offerer1 = offers_factories.OffererFactory()
    offerer2 = offers_factories.OffererFactory(siren="123456788")
    venue1 = offers_factories.VenueFactory(managingOfferer=offerer1)
    venue2 = offers_factories.VenueFactory(managingOfferer=offerer1)
    venue3 = offers_factories.VenueFactory(managingOfferer=offerer1)
    venue4 = offers_factories.VenueFactory(managingOfferer=offerer2)
    for venue in (venue1, venue2, venue3, venue4):
        payments_factories.PaymentFactory(
            booking__stock__offer__venue=venue, transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 06-21"
        )
    pro = users_factories.ProFactory(offerers=[offerer1, offerer2])

    # When
    client = TestClient(app.test_client()).with_auth(pro.email)
    response = client.get("/reimbursements/csv")

    # Then
    assert response.status_code == 200
    assert response.headers["Content-type"] == "text/csv; charset=utf-8;"
    assert response.headers["Content-Disposition"] == "attachment; filename=remboursements_pass_culture.csv"
    rows = response.data.decode("utf-8").splitlines()
    assert len(rows) == 1 + 4  # header + payments


@pytest.mark.usefixtures("db_session")
def test_with_user_with_no_offerer(app):
    # Given
    pro = users_factories.ProFactory()

    # When
    client = TestClient(app.test_client()).with_auth(pro.email)
    response = client.get("/reimbursements/csv")

    # Then
    assert response.status_code == 200
    rows = response.data.decode("utf-8").splitlines()
    assert len(rows) == 1  # header


@pytest.mark.usefixtures("db_session")
@override_features(DISABLE_BOOKINGS_RECAP_FOR_SOME_PROS=True)
def test_with_blacklisted_offerer(app):
    # Given
    offerer = offers_factories.OffererFactory(siren="343282380")
    payments_factories.PaymentFactory(
        booking__stock__offer__venue__managingOfferer=offerer,
        transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 06-21",
    )
    pro = users_factories.ProFactory(offerers=[offerer])

    # When
    client = TestClient(app.test_client()).with_auth(pro.email)
    response = client.get("/reimbursements/csv")

    # Then
    assert response.status_code == 200
    rows = response.data.decode("utf-8").splitlines()
    assert len(rows) == 1  # header


@pytest.mark.usefixtures("db_session")
@override_features(PRO_REIMBURSEMENTS_FILTERS=True)
def test_with_venue_filter(app):
    beginning_date_iso_format = (date.today() - timedelta(days=2)).isoformat()
    ending_date_iso_format = (date.today() + timedelta(days=2)).isoformat()
    offerer = offers_factories.OffererFactory()
    venue1 = offers_factories.VenueFactory(managingOfferer=offerer)
    venue2 = offers_factories.VenueFactory(managingOfferer=offerer)
    for venue in (venue1, venue2):
        payments_factories.PaymentStatusFactory(
            payment__booking__stock__offer__venue=venue,
            status=TransactionStatus.SENT,
            payment__transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 06-21",
        )
    pro = users_factories.ProFactory(offerers=[offerer])

    # When
    client = TestClient(app.test_client()).with_auth(pro.email)
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
@override_features(PRO_REIMBURSEMENTS_FILTERS=True)
def test_with_reimbursement_period_filter(app):
    beginning_date_iso_format = (date.today() - timedelta(days=2)).isoformat()
    ending_date_iso_format = (date.today() + timedelta(days=2)).isoformat()
    user_offerer = offers_factories.UserOffererFactory()
    offerer = user_offerer.offerer
    pro = user_offerer.user
    payments_factories.PaymentStatusFactory(
        payment__booking__stock__offer__venue__managingOfferer=offerer,
        status=TransactionStatus.SENT,
        payment__transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 06-21",
        date=date.today() - timedelta(days=2),
    )
    payments_factories.PaymentStatusFactory(
        payment__booking__stock__offer__venue__managingOfferer=offerer,
        status=TransactionStatus.SENT,
        payment__transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 06-21",
        date=date.today() - timedelta(days=3),
    )
    payments_factories.PaymentStatusFactory(
        payment__booking__stock__offer__venue__managingOfferer=offerer,
        status=TransactionStatus.SENT,
        payment__transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 06-21",
        date=date.today() + timedelta(days=2),
    )
    payments_factories.PaymentStatusFactory(
        payment__booking__stock__offer__venue__managingOfferer=offerer,
        status=TransactionStatus.SENT,
        payment__transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 06-21",
        date=date.today() + timedelta(days=3),
    )

    # When
    client = TestClient(app.test_client()).with_auth(pro.email)
    response = client.get(
        f"/reimbursements/csv?reimbursementPeriodBeginningDate={beginning_date_iso_format}&reimbursementPeriodEndingDate={ending_date_iso_format}"
    )

    # Then
    assert response.status_code == 200
    assert response.headers["Content-type"] == "text/csv; charset=utf-8;"
    assert response.headers["Content-Disposition"] == "attachment; filename=remboursements_pass_culture.csv"
    rows = response.data.decode("utf-8").splitlines()
    assert len(rows) == 1 + 2  # header + payments
