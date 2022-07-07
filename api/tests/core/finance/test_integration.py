import datetime

import pytest

import pcapi.core.bookings.api as bookings_api
import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.finance import api
from pcapi.core.finance import models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.testing import override_features
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


@override_features(
    USE_PRICING_POINT_FOR_PRICING=False,
    USE_REIMBURSEMENT_POINT_FOR_CASHFLOWS=False,
)
def test_integration_legacy_with_business_unit():
    booking = bookings_factories.IndividualBookingFactory()
    bookings_api.mark_as_used(booking)

    pricing = api.price_booking(booking, use_pricing_point=False)
    assert pricing.status == models.PricingStatus.VALIDATED

    cutoff = datetime.datetime.utcnow()
    api.generate_cashflows_and_payment_files(cutoff)
    assert len(pricing.cashflows) == 1
    cashflow = pricing.cashflows[0]
    assert cashflow.status == models.CashflowStatus.UNDER_REVIEW
    db.session.refresh(pricing)
    assert pricing.status == models.PricingStatus.PROCESSED

    api.generate_invoices()
    db.session.refresh(cashflow)
    assert cashflow.status == models.CashflowStatus.ACCEPTED
    db.session.refresh(pricing)
    assert pricing.status == models.PricingStatus.INVOICED


@override_features(
    USE_PRICING_POINT_FOR_PRICING=True,
    USE_REIMBURSEMENT_POINT_FOR_CASHFLOWS=True,
)
def test_integration():
    venue = offerers_factories.VenueFactory(pricing_point="self", reimbursement_point="self")
    offers_factories.BankInformationFactory(venue=venue)
    booking = bookings_factories.IndividualBookingFactory(stock__offer__venue=venue)

    bookings_api.mark_as_used(booking)
    pricing = api.price_booking(booking, use_pricing_point=True)
    assert pricing.status == models.PricingStatus.VALIDATED

    cutoff = datetime.datetime.utcnow()
    api.generate_cashflows_and_payment_files(cutoff)
    assert len(pricing.cashflows) == 1
    cashflow = pricing.cashflows[0]
    assert cashflow.status == models.CashflowStatus.UNDER_REVIEW
    db.session.refresh(pricing)
    assert pricing.status == models.PricingStatus.PROCESSED

    # FIXME (dbaty, 2022-06-29): uncomment below once invoice
    # generation can deal with reimbursement points.
    # api.generate_invoices()
    # db.session.refresh(cashflow)
    # assert cashflow.status == models.CashflowStatus.ACCEPTED
    # db.session.refresh(pricing)
    # assert pricing.status == models.PricingStatus.INVOICED
