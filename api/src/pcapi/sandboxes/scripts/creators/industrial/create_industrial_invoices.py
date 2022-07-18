from datetime import datetime
import logging

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.categories import subcategories
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.payments.factories as payments_factories
import pcapi.core.users.factories as users_factories
from pcapi.models import db
from pcapi.models.feature import FeatureToggle


logger = logging.getLogger(__name__)


def create_industrial_invoices() -> None:
    logger.info("create_industrial_invoices")

    finance_api.price_bookings()

    finance_api.generate_cashflows_and_payment_files(cutoff=datetime.utcnow())
    cashflows_created = finance_models.Cashflow.query.count()
    logger.info("Created %s Cashflows", cashflows_created)

    finance_api.generate_invoices()
    logger.info("Created %s Invoices", finance_models.Invoice.query.count())


def create_specific_invoice() -> None:
    logger.info("create_specific_invoice")
    bank_info = finance_factories.BankInformationFactory()
    business_unit = finance_factories.BusinessUnitFactory(
        name="0 - Point de remboursement avec justificatif copieux",
        bankAccount=bank_info,
    )
    offerer = offerers_factories.OffererFactory(name="0 - Structure avec justificatif copieux")
    pro = users_factories.ProFactory(email="pctest.pro.justificatif.copieux@example.com")
    offerers_factories.UserOffererFactory(offerer=offerer, user=pro)
    venue = offerers_factories.VenueFactory(
        name="0 - Lieu avec justificatif copieux",
        siret=business_unit.siret,
        businessUnit=business_unit,
        managingOfferer=offerer,
        pricing_point="self",
        reimbursement_point="self",
    )
    virtual_venue = offerers_factories.VirtualVenueFactory(
        managingOfferer=offerer, name=f"{venue.name} (Offre numérique)", businessUnit__name=offerer.name
    )
    bank_info.venue = venue
    db.session.add(bank_info)
    db.session.commit()
    thing_offer1 = offers_factories.ThingOfferFactory(venue=venue)
    thing_offer2 = offers_factories.ThingOfferFactory(venue=venue)
    book_offer1 = offers_factories.OfferFactory(venue=venue, subcategoryId=subcategories.LIVRE_PAPIER.id)
    book_offer2 = offers_factories.OfferFactory(venue=venue, subcategoryId=subcategories.LIVRE_PAPIER.id)
    digital_offer1 = offers_factories.DigitalOfferFactory(venue=virtual_venue)
    digital_offer2 = offers_factories.DigitalOfferFactory(venue=virtual_venue)
    custom_rule_offer1 = offers_factories.ThingOfferFactory(venue=venue)
    payments_factories.CustomReimbursementRuleFactory(rate=0.94, offer=custom_rule_offer1)
    custom_rule_offer2 = offers_factories.ThingOfferFactory(venue=venue)
    payments_factories.CustomReimbursementRuleFactory(amount=22, offer=custom_rule_offer2)

    stocks = [
        offers_factories.StockFactory(offer=thing_offer1, price=30),
        offers_factories.StockFactory(offer=book_offer1, price=20),
        offers_factories.StockFactory(offer=thing_offer2, price=81.3),
        offers_factories.StockFactory(offer=book_offer2, price=40),
        offers_factories.StockFactory(offer=digital_offer1, price=27),
        offers_factories.StockFactory(offer=digital_offer2, price=31),
        offers_factories.StockFactory(offer=custom_rule_offer1, price=20),
        offers_factories.StockFactory(offer=custom_rule_offer2, price=23),
    ]
    # This is a quick way to have a Venue reach the revenue threshold to reach the next ReimbursementRule,
    # without generating 60+ Bookings in bulk
    special_stock = offers_factories.StockFactory(offer=thing_offer2, price=19_950)
    special_user = users_factories.BeneficiaryGrant18Factory(
        firstName="This User has voluntarily a large deposit",
        deposit__source="create_specific_invoice() in industrial sandbox",
    )
    special_user.deposit.amount = 20000
    db.session.add(special_user)
    db.session.commit()

    bookings = [
        bookings_factories.UsedIndividualBookingFactory(
            stock=special_stock,
            individualBooking__user=special_user,
        ),
    ]
    for stock in stocks:
        booking = bookings_factories.UsedIndividualBookingFactory(
            stock=stock,
            user__deposit__source="create_specific_invoice() in industrial sandbox",
        )
        bookings.append(booking)
    use_pricing_point = FeatureToggle.USE_PRICING_POINT_FOR_PRICING.is_active()
    for booking in bookings[:3]:
        finance_api.price_booking(booking, use_pricing_point)
    finance_api.generate_cashflows_and_payment_files(cutoff=datetime.utcnow())
    for booking in bookings[3:]:
        finance_api.price_booking(booking, use_pricing_point)
    finance_api.generate_cashflows_and_payment_files(cutoff=datetime.utcnow())
    cashflows = (
        finance_models.Cashflow.query.join(finance_models.Cashflow.pricings)
        .filter(finance_models.Pricing.businessUnitId == business_unit.id)
        .all()
    )
    cashflow_ids = [c.id for c in cashflows]

    finance_api.generate_and_store_invoice(
        business_unit_id=business_unit.id,
        cashflow_ids=cashflow_ids,
    )
    logger.info("Created specific Invoice")
