from datetime import datetime
from datetime import timedelta
import logging
import random

from pcapi.connectors.big_query.queries.offerer_stats import DAILY_CONSULT_PER_OFFERER_LAST_180_DAYS_TABLE
from pcapi.connectors.big_query.queries.offerer_stats import TOP_3_MOST_CONSULTED_OFFERS_LAST_30_DAYS_TABLE
import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.models import db
from pcapi.models import feature


logger = logging.getLogger(__name__)


def create_industrial_invoices() -> None:
    logger.info("create_industrial_invoices")

    finance_api.price_events()

    batch = finance_api.generate_cashflows_and_payment_files(cutoff=datetime.utcnow())
    cashflows_created = finance_models.Cashflow.query.count()
    logger.info("Created %s Cashflows", cashflows_created)

    finance_api.generate_invoices(batch)
    logger.info("Created %s Invoices", finance_models.Invoice.query.count())


def create_specific_invoice() -> None:
    logger.info("create_specific_invoice")
    feature.Feature.query.filter(feature.Feature.name == "WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY").update(
        {"isActive": False}, synchronize_session=False
    )
    db.session.commit()
    bank_info = finance_factories.BankInformationFactory()
    offerer = offerers_factories.OffererFactory(name="0 - Structure avec justificatif copieux")
    offerers_factories.UserOffererFactory(offerer=offerer, user__email="activation@example.com")
    offerers_factories.OffererStatsFactory(
        offerer=offerer,
        table=TOP_3_MOST_CONSULTED_OFFERS_LAST_30_DAYS_TABLE,
        jsonData=offerers_models.OffererStatsData(top_offers=[], total_views_last_30_days=0),
    )
    offerers_factories.OffererStatsFactory(
        offerer=offerer,
        table=DAILY_CONSULT_PER_OFFERER_LAST_180_DAYS_TABLE,
        jsonData=offerers_models.OffererStatsData(daily_views=[]),
    )
    venue = offerers_factories.VenueFactory(
        name="Lieu avec justificatif copieux",
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

    # Add finance incidents to invoice

    booking_with_total_incident = bookings_factories.ReimbursedBookingFactory(
        stock=offers_factories.StockFactory(offer=thing_offer1, price=30),
        quantity=1,
        amount=30,
        user__deposit__source="create_specific_invoice() in industrial sandbox",
    )
    booking_with_partial_incident = bookings_factories.ReimbursedBookingFactory(
        stock=offers_factories.StockFactory(offer=book_offer1, price=30),
        quantity=1,
        amount=30,
        user__deposit__source="create_specific_invoice() in industrial sandbox",
    )
    bookings_with_incident = [booking_with_total_incident, booking_with_partial_incident]

    for booking in bookings_with_incident:
        event = finance_factories.UsedBookingFinanceEventFactory(booking=booking)
        pricing = finance_api.price_event(event)
        if pricing:
            pricing.status = finance_models.PricingStatus.INVOICED

    total_booking_finance_incident = finance_factories.IndividualBookingFinanceIncidentFactory(
        booking=booking_with_total_incident,
        newTotalAmount=0,
        incident__venue=venue,
        incident__status=finance_models.IncidentStatus.VALIDATED,
    )
    partial_booking_finance_incident = finance_factories.IndividualBookingFinanceIncidentFactory(
        booking=booking_with_partial_incident,
        newTotalAmount=2000,
        incident__venue=venue,
        incident__status=finance_models.IncidentStatus.VALIDATED,
    )
    booking_incidents = [total_booking_finance_incident, partial_booking_finance_incident]

    incident_events = []
    for booking_finance_incident in booking_incidents:
        incident_events += finance_api._create_finance_events_from_incident(
            booking_finance_incident, incident_validation_date=datetime.utcnow()
        )

    for event in incident_events:
        finance_api.price_event(event)

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
    for booking in bookings:
        event = finance_models.FinanceEvent.query.filter_by(booking=booking).one()
        finance_api.price_event(event)
    finance_api.generate_cashflows_and_payment_files(cutoff=datetime.utcnow())
    cashflows = finance_models.Cashflow.query.filter_by(reimbursementPoint=venue).all()
    cashflow_ids = [c.id for c in cashflows]

    finance_api.generate_and_store_invoice_legacy(
        reimbursement_point_id=venue.id,
        cashflow_ids=cashflow_ids,
    )
    logger.info("Created specific Invoice")
    feature.Feature.query.filter(feature.Feature.name == "WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY").update(
        {"isActive": True}, synchronize_session=False
    )
    db.session.commit()


def create_specific_invoice_with_bank_account() -> None:
    logger.info("create_specific_invoice_with_bank_account")
    offerer = offerers_factories.OffererFactory(name="0 - Structure avec justificatif et compte bancaire")
    bank_account = finance_factories.BankAccountFactory(offerer=offerer)
    offerers_factories.UserOffererFactory(offerer=offerer, user__email="activation@example.com")
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
    # This is a quick way to have a Venue reach the revenue threshold to reach the next ReimbursementRule,
    # without generating 60+ Bookings in bulk
    special_stock = offers_factories.StockFactory(offer=thing_offer2, price=19_950)
    special_user = users_factories.BeneficiaryGrant18Factory(
        firstName="This User has voluntarily a large deposit",
        deposit__source="create_specific_invoice_with_bank_account() in industrial sandbox",
    )
    special_user.deposit.amount = 20000
    db.session.add(special_user)
    db.session.commit()

    # Add finance incidents to invoice

    booking_with_total_incident = bookings_factories.ReimbursedBookingFactory(
        stock=offers_factories.StockFactory(offer=thing_offer1, price=30),
        quantity=1,
        amount=30,
        user__deposit__source="create_specific_invoice_with_bank_account() in industrial sandbox",
    )
    booking_with_partial_incident = bookings_factories.ReimbursedBookingFactory(
        stock=offers_factories.StockFactory(offer=book_offer1, price=30),
        quantity=1,
        amount=30,
        user__deposit__source="create_specific_invoice_with_bank_account() in industrial sandbox",
    )
    bookings_with_incident = [booking_with_total_incident, booking_with_partial_incident]

    for booking in bookings_with_incident:
        event = finance_factories.UsedBookingFinanceEventFactory(booking=booking)
        pricing = finance_api.price_event(event)
        if pricing:
            pricing.status = finance_models.PricingStatus.INVOICED

    total_booking_finance_incident = finance_factories.IndividualBookingFinanceIncidentFactory(
        booking=booking_with_total_incident,
        newTotalAmount=0,
        incident__venue=venue,
        incident__status=finance_models.IncidentStatus.VALIDATED,
    )
    partial_booking_finance_incident = finance_factories.IndividualBookingFinanceIncidentFactory(
        booking=booking_with_partial_incident,
        newTotalAmount=2000,
        incident__venue=venue,
        incident__status=finance_models.IncidentStatus.VALIDATED,
    )
    booking_incidents = [total_booking_finance_incident, partial_booking_finance_incident]

    incident_events = []
    for booking_finance_incident in booking_incidents:
        incident_events += finance_api._create_finance_events_from_incident(
            booking_finance_incident, incident_validation_date=datetime.utcnow()
        )

    for event in incident_events:
        finance_api.price_event(event)

    bookings = [
        bookings_factories.UsedBookingFactory(
            stock=special_stock,
            user=special_user,
        ),
    ]
    for stock in stocks:
        booking = bookings_factories.UsedBookingFactory(
            stock=stock,
            user__deposit__source="create_specific_invoice_with_bank_account() in industrial sandbox",
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
    logger.info("Created specific Invoice")


def create_specific_cashflow_batch_without_invoice() -> None:
    logger.info("create_specific_cashflow_batch_without_invoice")
    bank_info = finance_factories.BankInformationFactory()
    offerer = offerers_factories.OffererFactory(name="0 - Structure avec justificatif copié")
    offerers_factories.UserOffererFactory(offerer=offerer, user__email="activation@example.com")
    venue = offerers_factories.VenueFactory(
        name="Lieu avec justificatif copié",
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
    daily_views = []

    number_of_views = 0
    for i in range(7 * 30, 0, -1):  # 7 months
        date = datetime.today() - timedelta(days=i)
        number_of_views += date.day
        daily_views.append(offerers_models.OffererViewsModel(eventDate=date, numberOfViews=number_of_views))

    offerers_factories.OffererStatsFactory(
        offerer=offerer,
        syncDate=datetime.utcnow(),
        table=DAILY_CONSULT_PER_OFFERER_LAST_180_DAYS_TABLE,
        jsonData=offerers_models.OffererStatsData(daily_views=daily_views),
    )

    top_offers = random.choices(
        [thing_offer1, thing_offer2, book_offer1, book_offer2, digital_offer1, digital_offer2], k=3
    )

    offerers_factories.OffererStatsFactory(
        offerer=offerer,
        syncDate=datetime.utcnow(),
        table=TOP_3_MOST_CONSULTED_OFFERS_LAST_30_DAYS_TABLE,
        jsonData=offerers_models.OffererStatsData(
            top_offers=[
                offerers_models.TopOffersData(offerId=top_offers[0].id, numberOfViews=(random.randint(100, 1000))),
                offerers_models.TopOffersData(offerId=top_offers[1].id, numberOfViews=(random.randint(1000, 2000))),
                offerers_models.TopOffersData(offerId=top_offers[2].id, numberOfViews=(random.randint(2000, 3000))),
            ],
            total_views_last_30_days=random.randint(6000, 10000),
        ),
    )
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
    # This is a quick way to have a Venue reach the revenue threshold to reach the next ReimbursementRule,
    # without generating 60+ Bookings in bulk
    special_stock = offers_factories.StockFactory(offer=thing_offer2, price=19_950)
    special_user = users_factories.BeneficiaryGrant18Factory(
        firstName="This User has voluntarily a large deposit",
        deposit__source="create_specific_cashflow_batch_without_invoice() in industrial sandbox",
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
            user__deposit__source="create_specific_cashflow_batch_without_invoice() in industrial sandbox",
        )
        bookings.append(booking)
    for booking in bookings:
        finance_factories.UsedBookingFinanceEventFactory(booking=booking)
    for booking in bookings:
        event = finance_models.FinanceEvent.query.filter_by(booking=booking).one()
        finance_api.price_event(event)
    finance_api.generate_cashflows_and_payment_files(cutoff=datetime.utcnow())

    logger.info("Created specific CashflowBatch")
