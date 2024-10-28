import datetime
import decimal
import logging

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.geography import factories as geography_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories as offers_factories
from pcapi.utils import siren as siren_utils


logger = logging.getLogger(__name__)


def create_new_caledonia_offerers() -> None:
    logger.info("create_new_caledonia_offerers")

    _create_nc_active_offerer()
    _create_nc_minimal_offerer()

    logger.info("created New Caledonia offerers")

    _create_nc_invoice()


def _create_nc_active_offerer() -> None:
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
    for days in range(8, 15):
        offers_factories.EventStockFactory(
            offer=event_offer,
            beginningDatetime=ref_date + datetime.timedelta(days=days),
            bookingLimitDatetime=ref_date + datetime.timedelta(days=days - 2),
            price=decimal.Decimal("15"),
            quantity=50,
        )

    offers_factories.ThingStockFactory(
        offer__name="Offre physique en Nouvelle-Calédonie",
        offer__venue=venue,
        price=decimal.Decimal("100"),
        quantity=10,
    )


def _create_nc_minimal_offerer() -> None:
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

    offer1 = offers_factories.ThingOfferFactory(name="Offre calédonienne remboursée 1", venue=venue)
    offer2 = offers_factories.ThingOfferFactory(name="Offre calédonienne remboursée 2", venue=venue)

    stocks = [
        offers_factories.StockFactory(offer=offer1, price=30),
        offers_factories.StockFactory(offer=offer2, price=83.8),
    ]

    bookings = []
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
