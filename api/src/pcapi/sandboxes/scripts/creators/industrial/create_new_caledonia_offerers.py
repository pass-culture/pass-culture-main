import datetime
import decimal
import logging

from pcapi.core.bookings import api as bookings_api
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.geography import factories as geography_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.routes.backoffice.finance import validation
from pcapi.sandboxes.scripts.creators.test_cases import create_movie_products
from pcapi.sandboxes.scripts.creators.test_cases import create_offer_and_stocks_for_cinemas
from pcapi.utils import siren as siren_utils


logger = logging.getLogger(__name__)


def create_new_caledonia_offerers() -> None:
    logger.info("create_new_caledonia_offerers")

    beneficiary = _create_nc_beneficiary()
    _create_nc_active_offerer(beneficiary)
    _create_nc_new_offerer()
    _create_nc_cinema()

    logger.info("created New Caledonia offerers")

    _create_nc_invoice()
    _create_one_nc_individual_incident()


def _create_nc_beneficiary() -> users_models.User:
    return users_factories.CaledonianBeneficiaryGrant18Factory(
        email="beneficiaire.nc@example.com",
        firstName="Bénéficiaire",
        lastName="Néo-Calédonien",
    )


def _create_nc_active_offerer(beneficiary: users_models.User) -> None:
    address = geography_factories.AddressFactory(
        street="11 Avenue James Cook",
        postalCode="98800",
        city="Nouméa",
        latitude=-22.267957,
        longitude=166.433846,
        inseeCode="98818",
        banId="98818_w65mkd_00011",
        timezone="Pacific/Noumea",
    )
    offerer = offerers_factories.CaledonianOffererFactory(
        name="Structure calédonienne à Nouméa",
        street=address.street,
        postalCode=address.postalCode,
        city=address.city,
        siren=siren_utils.rid7_to_siren("1230001"),
    )
    venue = offerers_factories.CaledonianVenueFactory(
        managingOfferer=offerer,
        pricing_point="self",
        name="Lieu avec RIDET à Nouméa",
        siret=siren_utils.ridet_to_siret("1230001001"),
        latitude=address.latitude,
        longitude=address.longitude,
        bookingEmail="venue.nc@example.com",
        street=address.street,
        postalCode=address.postalCode,
        city=address.city,
        banId=address.banId,
        timezone=address.timezone,
        venueTypeCode=offerers_models.VenueTypeCode.MUSEUM,
        description="Lieu de test en Nouvelle-Calédonie",
        contact__email="noumea.nc@example.com",
        contact__website="https://nc.example.com/noumea",
        contact__phone_number="+687263443",
        contact__social_medias={"instagram": "https://instagram.com/@noumea.nc"},
        offererAddress__address=address,
    )
    second_venue = offerers_factories.CaledonianVenueFactory(
        managingOfferer=offerer,
        pricing_point="self",
        name="Lieu avec RIDET à Dumbéa",
        siret=siren_utils.ridet_to_siret("1230001002"),
        latitude=-22.204793,
        longitude=166.452108,
        bookingEmail="venue.nc@example.com",
        street="285 Boulevard du Rail Caledonien",
        postalCode="98835",
        city="Dumbéa",
        banId="98805_l2xcs6_00285",
        timezone="Pacific/Noumea",
        venueTypeCode=offerers_models.VenueTypeCode.BOOKSTORE,
        description="Lieu de test en Nouvelle-Calédonie",
        contact__email="dumbea.nc@example.com",
        contact__website="https://nc.example.com/dumbea",
        contact__phone_number="+687263443",
        contact__social_medias={"instagram": "https://instagram.com/@dumbea.nc"},
    )

    offerers_factories.UserOffererFactory(
        offerer=offerer,
        user__firstName="Mâ",
        user__lastName="Néo-Calédonien",
        user__email="pro1.nc@example.com",
        user__phoneNumber="+687263443",
        user__postalCode="98800",
        user__departementCode="988",
    )

    bank_account = finance_factories.CaledonianBankAccountFactory(
        label="Compte courant Banque de Nouvelle-Calédonie",
        offerer=offerer,
        dsApplicationId="988001",
    )
    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue, bankAccount=bank_account, timespan=(datetime.datetime.utcnow(),)
    )
    offerers_factories.VenueBankAccountLinkFactory(
        venue=second_venue, bankAccount=bank_account, timespan=(datetime.datetime.utcnow(),)
    )

    event_offer = offers_factories.EventOfferFactory(name="Offre d'événement en Nouvelle-Calédonie", venue=venue)
    # 22:00 UTC = 11:00 Noumea time on the day after
    ref_date = datetime.datetime.utcnow().replace(hour=22, minute=0, second=0, microsecond=0)
    event_stocks = [
        offers_factories.EventStockFactory(
            offer=event_offer,
            beginningDatetime=ref_date + datetime.timedelta(days=days),
            bookingLimitDatetime=ref_date + datetime.timedelta(days=days - 2),
            price=decimal.Decimal("15"),
            quantity=50,
        )
        for days in range(8, 15)
    ]

    bookings_factories.BookingFactory(stock=event_stocks[0], user=beneficiary)

    thing_stock = offers_factories.ThingStockFactory(
        offer__name="Offre physique en Nouvelle-Calédonie",
        offer__venue=venue,
        price=decimal.Decimal("100"),
        quantity=10,
    )

    bookings_factories.UsedBookingFactory(stock=thing_stock, user=beneficiary)


def _create_nc_new_offerer() -> None:
    # No address referenced in Thio, in Base d'Adresses Nationale
    address = geography_factories.AddressFactory(
        street="Village de Thio Rue rapadzi",
        postalCode="98829",
        city="Thio",
        latitude=-21.612984,
        longitude=166.214720,
        inseeCode="98829",
        banId=None,
        timezone="Pacific/Noumea",
    )
    offerer = offerers_factories.NotValidatedCaledonianOffererFactory(
        name="Structure calédonienne à Thio",
        street=address.street,
        postalCode=address.postalCode,
        city=address.city,
        siren=siren_utils.rid7_to_siren("1230002"),
    )
    offerers_factories.CaledonianVenueFactory(
        managingOfferer=offerer,
        pricing_point="self",
        name="Lieu avec RIDET à Thio",
        siret=siren_utils.ridet_to_siret("1230002001"),
        latitude=address.latitude,
        longitude=address.longitude,
        bookingEmail="thio.nc@example.com",
        street=address.street,
        postalCode=address.postalCode,
        city=address.city,
        banId=address.banId,
        timezone=address.timezone,
        isPermanent=False,
        venueTypeCode=offerers_models.VenueTypeCode.MUSEUM,
        description="Lieu de test en Nouvelle-Calédonie, adresse inconnue de la BAN",
        contact__email="thio.nc@example.com",
        contact__website="https://nc.example.com/thio",
        contact__phone_number="+687442504",
        contact__social_medias={"instagram": "https://instagram.com/@thio.nc"},
        offererAddress__address=address,
    )
    offerers_factories.UserOffererFactory(
        offerer=offerer,
        user__firstName="Méréï",
        user__lastName="Néo-Calédonien",
        user__email="pro3.nc@example.com",
        user__phoneNumber="+687749362",
        user__postalCode="98829",
        user__departementCode="988",
    )


def _create_nc_cinema() -> None:
    address = geography_factories.AddressFactory(
        street="27 Avenue de la VICTOIRE-HENRI LAFLEUR",
        postalCode="98818",
        city="Nouméa",
        latitude=-22.2734285,
        longitude=166.4430499,
        inseeCode="98818",
        banId="98818_18etss_00027",
        timezone="Pacific/Noumea",
    )
    offerer = offerers_factories.CaledonianOffererFactory(
        name="Le Rex calédonien",
        street=address.street,
        postalCode=address.postalCode,
        city=address.city,
        siren=siren_utils.rid7_to_siren("1230003"),
    )
    venue = offerers_factories.CaledonianVenueFactory(
        managingOfferer=offerer,
        pricing_point="self",
        name=offerer.name,
        siret=siren_utils.ridet_to_siret("1230003003"),
        latitude=address.latitude,
        longitude=address.longitude,
        bookingEmail="cinema.nc@example.com",
        street=address.street,
        postalCode=address.postalCode,
        city=address.city,
        banId=address.banId,
        timezone=address.timezone,
        venueTypeCode=offerers_models.VenueTypeCode.MOVIE,
        description="Cinéma de test en Nouvelle-Calédonie",
        contact__email="cinema.nc@example.com",
        contact__website="https://nc.example.com/noumea",
        contact__phone_number="+687263443",
        contact__social_medias={"instagram": "https://instagram.com/@noumea.nc"},
        offererAddress__address=address,
    )
    movie_products = create_movie_products()
    create_offer_and_stocks_for_cinemas([venue], movie_products)


def _create_nc_invoice() -> None:
    logger.info("_create_nc_invoice")
    offerer = offerers_factories.CaledonianOffererFactory(name="Structure Néo-calédonienne avec remboursement")
    bank_account = finance_factories.CaledonianBankAccountFactory(offerer=offerer)
    offerers_factories.UserOffererFactory(
        offerer=offerer,
        user__firstName="Jean-Michel",
        user__lastName="Nouvelle-Calédonie",
        user__email="pro2.nc@example.com",
        user__postalCode="98800",
        user__departementCode="988",
    )
    venue = offerers_factories.CaledonianVenueFactory(
        name="Lieu calédonien avec justificatif",
        managingOfferer=offerer,
        pricing_point="self",
        bank_account=bank_account,
    )
    virtual_venue = offerers_factories.VirtualVenueFactory(
        managingOfferer=offerer,
        name=f"{venue.name} (Offre numérique)",
        pricing_point=venue,
        bank_account=bank_account,
    )

    thing_offer1 = offers_factories.ThingOfferFactory(name="Offre calédonienne remboursée 1", venue=venue)
    thing_offer2 = offers_factories.ThingOfferFactory(name="Offre calédonienne remboursée 2", venue=venue)
    book_offer1 = offers_factories.OfferFactory(
        name="Livre calédonien remboursé 1", venue=venue, subcategoryId=subcategories.LIVRE_PAPIER.id
    )
    book_offer2 = offers_factories.OfferFactory(
        name="Livre calédonien remboursé 2", venue=venue, subcategoryId=subcategories.LIVRE_PAPIER.id
    )
    digital_offer1 = offers_factories.DigitalOfferFactory(name="Calédonien numérique remboursé 1", venue=virtual_venue)
    digital_offer2 = offers_factories.DigitalOfferFactory(name="Calédonien numérique remboursé 2", venue=virtual_venue)
    custom_rule_offer = offers_factories.ThingOfferFactory(name="Calédonien dérogatoire remboursé", venue=venue)
    finance_factories.CustomReimbursementRuleFactory(rate=0.94, offer=custom_rule_offer)

    stocks = [
        offers_factories.StockFactory(offer=thing_offer1, price=30),
        offers_factories.StockFactory(offer=thing_offer2, price=83.8),
        offers_factories.StockFactory(offer=book_offer1, price=20),
        offers_factories.StockFactory(offer=book_offer2, price=40),
        offers_factories.StockFactory(offer=digital_offer1, price=27),
        offers_factories.StockFactory(offer=digital_offer2, price=31),
        offers_factories.StockFactory(offer=custom_rule_offer, price=20),
    ]
    # This is a quick way to have a Venue reach the revenue threshold to reach the next ReimbursementRule,
    # without generating 60+ Bookings in bulk
    special_stock = offers_factories.StockFactory(offer=thing_offer2, price=19_950)
    special_user = users_factories.BeneficiaryGrant18Factory(
        firstName="This caledonian User has voluntarily a large deposit",
        deposit__source="_create_nc_invoice() in industrial sandbox",
    )
    special_user.deposit.amount = 20000
    db.session.add(special_user)
    db.session.commit()

    # Add finance incidents to invoice
    booking_with_total_incident = bookings_factories.ReimbursedBookingFactory(
        stock=offers_factories.StockFactory(offer=thing_offer1, price=30),
        quantity=1,
        amount=30,
        user__deposit__source="_create_nc_invoice() in industrial sandbox",
    )
    booking_with_partial_incident = bookings_factories.ReimbursedBookingFactory(
        stock=offers_factories.StockFactory(offer=book_offer1, price=30),
        quantity=1,
        amount=30,
        user__deposit__source="_create_nc_invoice() in industrial sandbox",
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
            booking_finance_incident, incident_validation_date=datetime.datetime.utcnow()
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
            user__deposit__source="_create_nc_invoice() in industrial sandbox",
        )
        bookings.append(booking)
    for booking in bookings:
        finance_factories.UsedBookingFinanceEventFactory(booking=booking)
    for booking in bookings:
        event = finance_models.FinanceEvent.query.filter_by(booking=booking).one()
        finance_api.price_event(event)

    finance_api.generate_cashflows_and_payment_files(cutoff=datetime.datetime.utcnow())
    cashflows = finance_models.Cashflow.query.filter_by(bankAccount=bank_account).all()
    cashflow_ids = [c.id for c in cashflows]

    finance_api.generate_and_store_invoice(
        bank_account_id=bank_account.id,
        cashflow_ids=cashflow_ids,
    )
    logger.info("Created caledonian Invoice")


def _create_one_nc_individual_incident() -> None:
    offerer = offerers_factories.CaledonianOffererFactory(name="Structure Néo-calédonienne avec note de débit")
    pro = offerers_factories.UserOffererFactory(offerer=offerer).user
    bank_account = finance_factories.CaledonianBankAccountFactory(offerer=offerer)
    venue = offerers_factories.CaledonianVenueFactory(
        name="Lieu calédonien avec note de débit",
        managingOfferer=offerer,
        pricing_point="self",
        bank_account=bank_account,
    )

    incident_booking = bookings_factories.BookingFactory(
        stock__offer__venue=venue,
        stock__price=decimal.Decimal("30"),
        user__deposit__source="_create_one_nc_individual_incident() in industrial sandbox",
    )
    bookings_api.mark_as_used(
        booking=incident_booking,
        validation_author_type=bookings_models.BookingValidationAuthorType.OFFERER,
    )
    finance_api.price_event(incident_booking.finance_events[0])
    batch = finance_api.generate_cashflows_and_payment_files(cutoff=datetime.datetime.utcnow())
    finance_api.generate_invoices(batch)

    assert incident_booking.status == bookings_models.BookingStatus.REIMBURSED

    amount = decimal.Decimal("10")
    check_bookings = validation.check_incident_bookings([incident_booking])
    check_amount = validation.check_total_amount(amount, [incident_booking])
    if not (check_bookings and check_amount):
        raise ValueError("Couldn't create overpayment incident, invalid parameters")

    # Create the overpayment incident and validate it
    finance_incident = finance_api.create_overpayment_finance_incident(
        bookings=[incident_booking],
        author=pro,
        origin="Incident de Nouvelle-Calédonie",
        amount=amount,
    )
    finance_api.validate_finance_overpayment_incident(
        finance_incident=finance_incident,
        force_debit_note=True,
        author=pro,
    )
    for booking_finance_incident in finance_incident.booking_finance_incidents:
        for finance_event in booking_finance_incident.finance_events:
            finance_api.price_event(finance_event)

    batch = finance_api.generate_cashflows_and_payment_files(cutoff=datetime.datetime.utcnow())
    finance_api.generate_debit_notes(batch)
