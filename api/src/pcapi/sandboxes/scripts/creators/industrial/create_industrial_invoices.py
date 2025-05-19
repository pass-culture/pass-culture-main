import logging
import random
import typing
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from unittest.mock import patch

import sqlalchemy as sa

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models
from pcapi.connectors.big_query.queries.offerer_stats import DAILY_CONSULT_PER_OFFERER_LAST_180_DAYS_TABLE
from pcapi.connectors.big_query.queries.offerer_stats import TOP_3_MOST_CONSULTED_OFFERS_LAST_30_DAYS_TABLE
from pcapi.core.bookings import api as bookings_api
from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import subcategories
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.finance import utils as finance_utils
from pcapi.models import db


logger = logging.getLogger(__name__)


def create_industrial_invoices() -> None:
    logger.info("create_industrial_invoices")

    finance_api.price_events()

    batch = finance_api.generate_cashflows_and_payment_files(cutoff=datetime.utcnow())
    cashflows_created = db.session.query(finance_models.Cashflow).count()
    logger.info("Created %s Cashflows", cashflows_created)

    finance_api.generate_invoices_and_debit_notes_legacy(batch)
    logger.info("Created %s Invoices", db.session.query(finance_models.Invoice).count())


def create_free_invoice() -> None:
    logger.info("create_free_invoice")
    offerer = offerers_factories.OffererFactory.create(name="0 - Structure avec compte bancaire et justificatif à 0€")
    bank_account = finance_factories.BankAccountFactory.create(offerer=offerer)
    offerers_factories.UserOffererFactory.create(offerer=offerer, user__email="activation@example.com")
    pricing_point = offerers_factories.VenueFactory.create(
        name="Point de valorisation pour justificatifs à 0€",
        managingOfferer=offerer,
    )
    venue = offerers_factories.VirtualVenueFactory.create(
        name="Lieu avec justificatif à 0€",
        managingOfferer=offerer,
        pricing_point=pricing_point,
        bank_account=bank_account,
    )
    digital_offer1 = offers_factories.DigitalOfferFactory.create(
        name="Specific free invoice digital offer 1", venue=venue
    )
    digital_offer2 = offers_factories.DigitalOfferFactory.create(
        name="Specific free invoice digital offer 2", venue=venue
    )
    stocks = [
        offers_factories.StockFactory.create(offer=digital_offer1, price=27),
        offers_factories.StockFactory.create(offer=digital_offer2, price=31),
    ]
    for stock in stocks:
        booking = bookings_factories.BookingFactory.create(
            stock=stock,
            user__deposit__source="create_free_invoice() in industrial sandbox",
        )
        bookings_api.mark_as_used(
            booking=booking,
            validation_author_type=bookings_models.BookingValidationAuthorType.OFFERER,
        )

        for finance_event in booking.finance_events:
            finance_api.price_event(finance_event)

    finance_api.generate_cashflows_and_payment_files(cutoff=datetime.utcnow())

    cashflows = db.session.query(finance_models.Cashflow).filter_by(bankAccount=bank_account).all()
    cashflow_ids = [c.id for c in cashflows]

    finance_api.generate_and_store_invoice_legacy(
        bank_account_id=bank_account.id,
        cashflow_ids=cashflow_ids,
    )
    logger.info("Created free Invoice")


def create_specific_invoice() -> None:
    logger.info("create_specific_invoice")
    offerer = offerers_factories.OffererFactory.create(name="0 - Structure avec justificatif et compte bancaire")
    bank_account = finance_factories.BankAccountFactory.create(offerer=offerer)
    offerers_factories.UserOffererFactory.create(offerer=offerer, user__email="activation@example.com")
    venue = offerers_factories.VenueFactory.create(
        name="Lieu avec justificatif",
        managingOfferer=offerer,
        pricing_point="self",
        bank_account=bank_account,
    )
    virtual_venue = offerers_factories.VirtualVenueFactory.create(
        managingOfferer=offerer,
        name=f"{venue.name} (Offre numérique)",
        pricing_point=venue,
    )

    thing_offer1 = offers_factories.ThingOfferFactory.create(name="Specific invoice offer 1", venue=venue)
    thing_offer2 = offers_factories.ThingOfferFactory.create(name="Specific invoice offer 2", venue=venue)
    book_offer1 = offers_factories.OfferFactory.create(
        name="Specific invoice book 1", venue=venue, subcategoryId=subcategories.LIVRE_PAPIER.id
    )
    book_offer2 = offers_factories.OfferFactory.create(
        name="Specific invoice book 2", venue=venue, subcategoryId=subcategories.LIVRE_PAPIER.id
    )
    digital_offer1 = offers_factories.DigitalOfferFactory.create(
        name="Specific invoice digital offer 1", venue=virtual_venue
    )
    digital_offer2 = offers_factories.DigitalOfferFactory.create(
        name="Specific invoice digital offer 2", venue=virtual_venue
    )
    custom_rule_offer1 = offers_factories.ThingOfferFactory.create(
        name="Specific invoice custom rule offer 1", venue=venue
    )
    finance_factories.CustomReimbursementRuleFactory.create(rate=0.94, offer=custom_rule_offer1)
    custom_rule_offer2 = offers_factories.ThingOfferFactory.create(
        name="Specific invoice custom rule offer 1", venue=venue
    )
    finance_factories.CustomReimbursementRuleFactory.create(amount=2200, offer=custom_rule_offer2)

    stocks = [
        offers_factories.StockFactory.create(offer=thing_offer1, price=30),
        offers_factories.StockFactory.create(offer=book_offer1, price=20),
        offers_factories.StockFactory.create(offer=thing_offer2, price=81.3),
        offers_factories.StockFactory.create(offer=book_offer2, price=40),
        offers_factories.StockFactory.create(offer=digital_offer1, price=27),
        offers_factories.StockFactory.create(offer=digital_offer2, price=31),
        offers_factories.StockFactory.create(offer=custom_rule_offer1, price=20),
        offers_factories.StockFactory.create(offer=custom_rule_offer2, price=23),
    ]
    # This is a quick way to have a Venue reach the revenue threshold to reach the next ReimbursementRule,
    # without generating 60+ Bookings in bulk
    special_stock = offers_factories.StockFactory.create(offer=thing_offer2, price=19_950)
    special_user = users_factories.BeneficiaryGrant18Factory.create(
        firstName="This User has voluntarily a large deposit",
        deposit__source="create_specific_invoice() in industrial sandbox",
    )
    special_user.deposit.amount = 20000
    db.session.add(special_user)
    db.session.commit()

    # Add finance incidents to invoice

    booking_with_total_incident = bookings_factories.ReimbursedBookingFactory.create(
        stock=offers_factories.StockFactory.create(offer=thing_offer1, price=30),
        quantity=1,
        amount=30,
        user__deposit__source="create_specific_invoice() in industrial sandbox",
    )
    booking_with_partial_incident = bookings_factories.ReimbursedBookingFactory.create(
        stock=offers_factories.StockFactory.create(offer=book_offer1, price=30),
        quantity=1,
        amount=30,
        user__deposit__source="create_specific_invoice() in industrial sandbox",
    )
    bookings_with_incident = [booking_with_total_incident, booking_with_partial_incident]

    for booking in bookings_with_incident:
        event = finance_factories.UsedBookingFinanceEventFactory.create(booking=booking)
        pricing = finance_api.price_event(event)
        if pricing:
            pricing.status = finance_models.PricingStatus.INVOICED

    total_booking_finance_incident = finance_factories.IndividualBookingFinanceIncidentFactory.create(
        booking=booking_with_total_incident,
        newTotalAmount=0,
        incident__venue=venue,
        incident__status=finance_models.IncidentStatus.VALIDATED,
    )
    partial_booking_finance_incident = finance_factories.IndividualBookingFinanceIncidentFactory.create(
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
        bookings_factories.UsedBookingFactory.create(
            stock=special_stock,
            user=special_user,
        ),
    ]
    for stock in stocks:
        booking = bookings_factories.UsedBookingFactory.create(
            stock=stock,
            user__deposit__source="create_specific_invoice() in industrial sandbox",
        )
        bookings.append(booking)
    for booking in bookings:
        finance_factories.UsedBookingFinanceEventFactory.create(booking=booking)
    for booking in bookings:
        event = db.session.query(finance_models.FinanceEvent).filter_by(booking=booking).one()
        finance_api.price_event(event)
    finance_api.generate_cashflows_and_payment_files(cutoff=datetime.utcnow())
    cashflows = db.session.query(finance_models.Cashflow).filter_by(bankAccount=bank_account).all()
    cashflow_ids = [c.id for c in cashflows]

    finance_api.generate_and_store_invoice_legacy(
        bank_account_id=bank_account.id,
        cashflow_ids=cashflow_ids,
    )
    logger.info("Created specific Invoice")


def build_many_extra_invoices(count: int = 32) -> None:
    """Build a bank account, a venue and many invoices.

    Those invoices will be created in the past in order to be
    more or less meaningful. This needs some dirty tricks since all this
    process has never meant to be done in the past.

    The process builds invoices for every invoice-period (twice a
    month), starting from the past and moving forward.

    Warning: this function should not be called many times unless one
    wants to add many bank accounts and venue to an existing offerer. It
    might also not work because of the whole cutoff build process.

    Warning (important!): this function should be the first to build
    invoices or the last one. Otherwise, invoices generation will break
    for various reasons.
    """

    def cashflow_batch_label_generator(start: int, count: int) -> typing.Generator:
        return (finance_api.CASHFLOW_BATCH_LABEL_PREFIX + str(start + x) for x in range(1, count + 1))

    def book_offer_and_build_invoices(
        current_idx: int,
        start: datetime,
        offer: offers_models.Offer,
        beneficiary: users_models.User | None,
        bank_account: finance_models.BankAccount,
    ) -> bookings_models.Booking:
        stock_start = start + timedelta(days=15 * current_idx)

        booking_beneficiary = {"user": beneficiary} if beneficiary else {}
        booking = bookings_factories.UsedBookingFactory.create(
            **booking_beneficiary,
            dateCreated=stock_start + timedelta(days=1),
            dateUsed=stock_start + timedelta(days=2),
            stock__quantity=2,
            stock__price=1,
            stock__offer=offer,
        )

        finance_factories.UsedBookingFinanceEventFactory.create(booking=booking)
        event = db.session.query(finance_models.FinanceEvent).filter_by(booking=booking).one()
        finance_api.price_event(event)

        last_day = stock_start - timedelta(days=1)
        cutoff = finance_utils.get_cutoff_as_datetime(last_day)

        finance_api.generate_cashflows_and_payment_files(cutoff=cutoff)

        bank_account = venue.current_bank_account
        cashflows = db.session.query(finance_models.Cashflow).filter_by(bankAccount=bank_account).all()
        cashflow_ids = [c.id for c in cashflows]

        max_invoice_id_before = db.session.query(sa.func.max(finance_models.Invoice.id)).scalar()

        finance_api.generate_and_store_invoice_legacy(
            bank_account_id=bank_account.id,
            cashflow_ids=cashflow_ids,
        )

        # the default date is used when built, which is now()
        # but... we would like something more realistic: an invoice
        # built in the past.
        # But... please do not change invoice date created in other modules!
        invoice = (
            db.session.query(finance_models.Invoice)
            .filter(finance_models.Invoice.id > max_invoice_id_before)
            .order_by(finance_models.Invoice.id.desc())
            .first()
        )
        if invoice:
            invoice.date = last_day
            db.session.add(invoice)

        return booking

    # start in the past, move on to today
    start = datetime.now(timezone.utc) - timedelta(days=15 * count)

    beneficiary = None

    # since invoices and cashflow batches are built in the past,
    # the batch label generation will not work: the label is
    # set far away after normal increment so that this ugly code
    # does not break cashflow generation in dev and testing which
    # next label is based on the most recent one (sorted by date).
    mock_path = "pcapi.core.finance.api._get_next_cashflow_batch_label"
    with patch(mock_path) as mock_cashflow_label:
        mock_cashflow_label.side_effect = cashflow_batch_label_generator(1000, count)

        try:
            user = db.session.query(users_models.User).filter_by(email="activation@example.com").one_or_none()
            if not user:
                user = users_factories.ProFactory.create(
                    lastName="PRO",
                    firstName="Activation",
                    email="activation@example.com",
                )

            offerer = offerers_factories.OffererFactory.create(name="Structure avec de nombreux remboursements")
            offerers_factories.UserOffererFactory.create(offerer=offerer, user=user)

            current_timestamp = int(datetime.now().timestamp())
            bank_account = finance_factories.BankAccountFactory.create(
                label=f"Compte bancaire avec plein de remboursements #{current_timestamp}",
                offerer=offerer,
                dsApplicationId=current_timestamp,
            )
            venue = offerers_factories.VenueFactory.create(
                name="Lieu avec plein de remboursements",
                managingOfferer=offerer,
                pricing_point="self",
                bank_account=bank_account,
            )
            offer = offers_factories.OfferFactory.create(venue=venue, dateCreated=start)

            for idx in range(1, count + 1):
                booking = book_offer_and_build_invoices(
                    current_idx=idx,
                    start=start,
                    beneficiary=beneficiary,
                    offer=offer,
                    bank_account=bank_account,
                )

                # first booking will create a beneficiary,
                # no need to create a new one for each booking
                if not beneficiary and booking:
                    beneficiary = booking.user

                db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        logger.info(f"Created {count} invoices for venue #{venue.id}/{venue.name} and offer #{offer.id}/{offer.name}")


def create_specific_cashflow_batch_without_invoice() -> None:
    logger.info("create_specific_cashflow_batch_without_invoice")
    offerer = offerers_factories.OffererFactory.create(name="0 - Structure avec justificatif copié")
    offerers_factories.UserOffererFactory.create(offerer=offerer, user__email="activation@example.com")
    venue = offerers_factories.VenueFactory.create(
        name="Lieu avec justificatif copié",
        managingOfferer=offerer,
        pricing_point="self",
    )
    bank_account = finance_factories.BankAccountFactory.create(offerer=venue.managingOfferer)
    offerers_factories.VenueBankAccountLinkFactory.create(
        bankAccount=bank_account,
        venue=venue,
    )
    virtual_venue = offerers_factories.VirtualVenueFactory.create(
        managingOfferer=offerer,
        name=f"{venue.name} (Offre numérique)",
        pricing_point=venue,
    )
    offerers_factories.VenueBankAccountLinkFactory.create(bankAccount=bank_account, venue=virtual_venue)
    thing_offer1 = offers_factories.ThingOfferFactory.create(name="Specific invoice offer 1", venue=venue)
    thing_offer2 = offers_factories.ThingOfferFactory.create(name="Specific invoice offer 2", venue=venue)
    book_offer1 = offers_factories.OfferFactory.create(
        name="Specific invoice book 1", venue=venue, subcategoryId=subcategories.LIVRE_PAPIER.id
    )
    book_offer2 = offers_factories.OfferFactory.create(
        name="Specific invoice book 2", venue=venue, subcategoryId=subcategories.LIVRE_PAPIER.id
    )
    digital_offer1 = offers_factories.DigitalOfferFactory.create(
        name="Specific invoice digital offer 1", venue=virtual_venue
    )
    digital_offer2 = offers_factories.DigitalOfferFactory.create(
        name="Specific invoice digital offer 2", venue=virtual_venue
    )
    daily_views = []

    number_of_views = 0
    for i in range(7 * 30, 0, -1):  # 7 months
        date = datetime.today() - timedelta(days=i)
        number_of_views += date.day
        daily_views.append(offerers_models.OffererViewsModel(eventDate=date, numberOfViews=number_of_views))

    offerers_factories.OffererStatsFactory.create(
        offerer=offerer,
        syncDate=datetime.utcnow(),
        table=DAILY_CONSULT_PER_OFFERER_LAST_180_DAYS_TABLE,
        jsonData=offerers_models.OffererStatsData(daily_views=daily_views),
    )

    top_offers = random.choices(
        [thing_offer1, thing_offer2, book_offer1, book_offer2, digital_offer1, digital_offer2], k=3
    )

    offerers_factories.OffererStatsFactory.create(
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
    custom_rule_offer1 = offers_factories.ThingOfferFactory.create(
        name="Specific invoice custom rule offer 1", venue=venue
    )
    finance_factories.CustomReimbursementRuleFactory.create(rate=0.94, offer=custom_rule_offer1)
    custom_rule_offer2 = offers_factories.ThingOfferFactory.create(
        name="Specific invoice custom rule offer 1", venue=venue
    )
    finance_factories.CustomReimbursementRuleFactory.create(amount=2200, offer=custom_rule_offer2)

    stocks = [
        offers_factories.StockFactory.create(offer=thing_offer1, price=30),
        offers_factories.StockFactory.create(offer=book_offer1, price=20),
        offers_factories.StockFactory.create(offer=thing_offer2, price=81.3),
        offers_factories.StockFactory.create(offer=book_offer2, price=40),
        offers_factories.StockFactory.create(offer=digital_offer1, price=27),
        offers_factories.StockFactory.create(offer=digital_offer2, price=31),
        offers_factories.StockFactory.create(offer=custom_rule_offer1, price=20),
        offers_factories.StockFactory.create(offer=custom_rule_offer2, price=23),
    ]
    # This is a quick way to have a Venue reach the revenue threshold to reach the next ReimbursementRule,
    # without generating 60+ Bookings in bulk
    special_stock = offers_factories.StockFactory.create(offer=thing_offer2, price=19_950)
    special_user = users_factories.BeneficiaryGrant18Factory.create(
        firstName="This User has voluntarily a large deposit",
        deposit__source="create_specific_cashflow_batch_without_invoice() in industrial sandbox",
    )
    special_user.deposit.amount = 20000
    db.session.add(special_user)
    db.session.commit()

    bookings = [
        bookings_factories.UsedBookingFactory.create(
            stock=special_stock,
            user=special_user,
        ),
    ]
    for stock in stocks:
        booking = bookings_factories.UsedBookingFactory.create(
            stock=stock,
            user__deposit__source="create_specific_cashflow_batch_without_invoice() in industrial sandbox",
        )
        bookings.append(booking)
    for booking in bookings:
        finance_factories.UsedBookingFinanceEventFactory.create(booking=booking)
    for booking in bookings:
        event = db.session.query(finance_models.FinanceEvent).filter_by(booking=booking).one()
        finance_api.price_event(event)
    finance_api.generate_cashflows_and_payment_files(cutoff=datetime.utcnow())

    logger.info("Created specific CashflowBatch")
