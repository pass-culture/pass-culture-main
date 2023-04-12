from datetime import datetime
import logging

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.categories import subcategories
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.models import db


logger = logging.getLogger(__name__)


def create_industrial_invoices() -> None:
    logger.info("create_industrial_invoices")

    finance_api.price_events()

    finance_api.generate_cashflows_and_payment_files(cutoff=datetime.utcnow())
    cashflows_created = finance_models.Cashflow.query.count()
    logger.info("Created %s Cashflows", cashflows_created)

    finance_api.generate_invoices()
    logger.info("Created %s Invoices", finance_models.Invoice.query.count())


def create_specific_invoice() -> None:
    logger.info("create_specific_invoice")
    bank_info = finance_factories.BankInformationFactory()
    offerer = offerers_factories.OffererFactory(name="0 - Structure avec justificatif copieux")
    pro = users_factories.ProFactory(email="pctest.pro.justificatif.copieux@example.com")
    offerers_factories.UserOffererFactory(offerer=offerer, user=pro)
    venue = offerers_factories.VenueFactory(
        name="0 - Lieu avec justificatif copieux",
        managingOfferer=offerer,
        pricing_point="self",
        reimbursement_point="self",
    )
    virtual_venue = offerers_factories.VirtualVenueFactory(
        managingOfferer=offerer,
        name=f"{venue.name} (Offre numérique)",
        pricing_point=venue,
        reimbursement_point=venue,
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
    finance_factories.CustomReimbursementRuleFactory(rate=0.94, offer=custom_rule_offer1)
    custom_rule_offer2 = offers_factories.ThingOfferFactory(venue=venue)
    finance_factories.CustomReimbursementRuleFactory(amount=22, offer=custom_rule_offer2)

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
        bookings_factories.UsedBookingFactory(
            stock=special_stock,
            user=special_user,
        ),
    ]
    for stock in stocks:
        booking = bookings_factories.UsedBookingFactory(
            stock=stock,
            user__deposit__source="create_specific_invoice() in industrial sandbox",
        )
        bookings.append(booking)
    for booking in bookings:
        finance_factories.UsedBookingFinanceEventFactory(booking=booking)
    for booking in bookings[:3]:
        event = finance_models.FinanceEvent.query.filter_by(booking=booking).one()
        finance_api.price_event(event)
    finance_api.generate_cashflows_and_payment_files(cutoff=datetime.utcnow())
    for booking in bookings[3:]:
        event = finance_models.FinanceEvent.query.filter_by(booking=booking).one()
        finance_api.price_event(event)
    finance_api.generate_cashflows_and_payment_files(cutoff=datetime.utcnow())
    cashflows = finance_models.Cashflow.query.filter_by(reimbursementPoint=venue).all()
    cashflow_ids = [c.id for c in cashflows]

    finance_api.generate_and_store_invoice(
        reimbursement_point_id=venue.id,
        cashflow_ids=cashflow_ids,
    )
    logger.info("Created specific Invoice")
