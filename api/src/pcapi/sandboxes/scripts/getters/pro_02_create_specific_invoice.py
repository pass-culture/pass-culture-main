from datetime import datetime

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.users import factories as users_factories
from pcapi.sandboxes.scripts.utils.helpers import get_pro_user_helper


def create_specific_invoice() -> dict:
    pro_user = users_factories.ProFactory(email="activation_new_nav@example.com")
    users_factories.UserProNewNavStateFactory(user=pro_user)
    offerer = offerers_factories.OffererFactory(name="0 - Structure avec justificatif et compte bancaire")
    bank_account = finance_factories.BankAccountFactory(offerer=offerer)
    offerers_factories.UserOffererFactory(offerer=offerer, user__email=pro_user.email)
    venue = offerers_factories.VenueFactory(
        name="Lieu avec justificatif",
        managingOfferer=offerer,
        pricing_point="self",
    )
    virtual_venue = offerers_factories.VirtualVenueFactory(
        managingOfferer=offerer,
        name=f"{venue.name} (Offre numérique)",
        pricing_point=venue,
    )
    offerers_factories.VenueBankAccountLinkFactory(venue=venue, bankAccount=bank_account)
    thing_offer1 = offers_factories.ThingOfferFactory(name="Specific invoice offer 1", venue=venue)
    thing_offer2 = offers_factories.ThingOfferFactory(name="Specific invoice offer 2", venue=venue)
    book_offer1 = offers_factories.OfferFactory(
        name="Specific invoice book 1", venue=venue, subcategoryId=subcategories.LIVRE_PAPIER.id
    )
    book_offer2 = offers_factories.OfferFactory(
        name="Specific invoice book 2", venue=venue, subcategoryId=subcategories.LIVRE_PAPIER.id
    )
    digital_offer1 = offers_factories.DigitalOfferFactory(name="Specific invoice digital offer 1", venue=virtual_venue)
    digital_offer2 = offers_factories.DigitalOfferFactory(name="Specific invoice digital offer 2", venue=virtual_venue)
    custom_rule_offer1 = offers_factories.ThingOfferFactory(name="Specific invoice custom rule offer 1", venue=venue)
    finance_factories.CustomReimbursementRuleFactory(rate=0.94, offer=custom_rule_offer1)
    custom_rule_offer2 = offers_factories.ThingOfferFactory(name="Specific invoice custom rule offer 1", venue=venue)
    finance_factories.CustomReimbursementRuleFactory(amount=2200, offer=custom_rule_offer2)

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
    bookings = []
    for stock in stocks:
        booking = bookings_factories.UsedBookingFactory(
            stock=stock,
            user__deposit__source="create_specific_invoice() in industrial sandbox",
        )
        bookings.append(booking)
    for booking in bookings:
        finance_factories.UsedBookingFinanceEventFactory(booking=booking)
    for booking in bookings:
        event = finance_models.FinanceEvent.query.filter_by(booking=booking).one()
        finance_api.price_event(event)
    finance_api.generate_cashflows_and_payment_files(cutoff=datetime.utcnow())
    cashflows = finance_models.Cashflow.query.filter_by(bankAccount=bank_account).all()
    cashflow_ids = [c.id for c in cashflows]

    finance_api.generate_and_store_invoice(
        bank_account_id=bank_account.id,
        cashflow_ids=cashflow_ids,
    )

    return {"user": get_pro_user_helper(pro_user)}
