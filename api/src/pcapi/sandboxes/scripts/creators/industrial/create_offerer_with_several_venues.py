import datetime
import logging

from pcapi.core.bookings import factories as booking_factories
from pcapi.core.finance import factories as finance_factories
from pcapi.core.geography import factories as geography_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories as offers_factories
from pcapi.sandboxes.scripts.utils.helpers import log_func_duration
from pcapi.utils import date as date_utils


logger = logging.getLogger(__name__)


@log_func_duration
def create_offerer_with_several_venues() -> offerers_models.Offerer:
    user_offerer = offerers_factories.UserOffererFactory.create(offerer__name="Structure avec plusieurs lieux")
    address1 = geography_factories.AddressFactory(
        banId="75101_2184_00012",
        inseeCode="75101",
        street="12 Place Colette",
        departmentCode="75",
        postalCode="75001",
        city="Paris",
        latitude=48.863356,
        longitude=2.336069,
    )
    venue1 = offerers_factories.VenueFactory.create(
        name="Compagnie de théâtre",
        managingOfferer=user_offerer.offerer,
        pricing_point="self",
        venueTypeCode=offerers_models.VenueTypeCode.PERFORMING_ARTS,
        offererAddress__address=address1,
    )
    bank_account1 = finance_factories.BankAccountFactory.create(offerer=venue1.managingOfferer)
    offerers_factories.VenueBankAccountLinkFactory.create(bankAccount=bank_account1, venue=venue1)
    address2 = geography_factories.AddressFactory(
        banId="75107_1257_00037",
        inseeCode="75107",
        street="37 Quai Branly",
        departmentCode="75",
        postalCode="75007",
        city="Paris",
        latitude=48.861500,
        longitude=2.297744,
    )
    venue2 = offerers_factories.VenueFactory.create(
        name="Musée",
        managingOfferer=user_offerer.offerer,
        pricing_point="self",
        venueTypeCode=offerers_models.VenueTypeCode.MUSEUM,
        offererAddress__address=address2,
    )
    bank_account2 = finance_factories.BankAccountFactory.create(offerer=venue2.managingOfferer)
    offerers_factories.VenueBankAccountLinkFactory.create(bankAccount=bank_account2, venue=venue2)
    address3 = geography_factories.AddressFactory(
        banId="06029_0880_00001",
        inseeCode="06029",
        street="1 Boulevard de la Croisette",
        departmentCode="06",
        postalCode="06400",
        city="Cannes",
        latitude=43.551407,
        longitude=7.017984,
    )
    venue3 = offerers_factories.VenueFactory.create(
        name="Festival de musique",
        managingOfferer=user_offerer.offerer,
        pricing_point="self",
        venueTypeCode=offerers_models.VenueTypeCode.FESTIVAL,
        offererAddress__address=address3,
    )
    offerers_factories.VenueBankAccountLinkFactory.create(bankAccount=bank_account1, venue=venue3)
    address4 = geography_factories.AddressFactory(
        banId="13202_cis55b_00001",
        inseeCode="13202",
        street="1 Esplanade du j4 - gisele halimi",
        departmentCode="13",
        postalCode="13002",
        city="Marseille",
        latitude=43.297033,
        longitude=5.360777,
    )
    venue4 = offerers_factories.VenueWithoutSiretFactory.create(
        name="Bibliothèque sans SIRET",
        managingOfferer=user_offerer.offerer,
        pricing_point=venue1,
        venueTypeCode=offerers_models.VenueTypeCode.LIBRARY,
        offererAddress__address=address4,
    )
    offerers_factories.VenueBankAccountLinkFactory.create(bankAccount=bank_account1, venue=venue4)
    in_two_month = date_utils.get_naive_utc_now() + datetime.timedelta(days=60)
    for i in range(1, 6):
        offer = offers_factories.DigitalOfferFactory.create(name=f"Offre avec code d'activation {i}", venue=venue1)

        offers_factories.StockWithActivationCodesFactory.create(
            offer=offer,
            activationCodes__expirationDate=in_two_month,
        )

    for i, venue in enumerate([venue1, venue2], 1):
        offers_factories.EventStockFactory.create(
            offer__name=f"Évènement 1 du lieu {i} - sans réservation", offer__venue=venue
        )

        event2 = offers_factories.EventStockFactory.create(
            offer__name=f"Évènement 2 du lieu {i} - 3 réservations confirmées", offer__venue=venue
        )
        booking_factories.BookingFactory.create_batch(3, stock=event2)

        event3 = offers_factories.EventStockFactory.create(
            offer__name=f"Évènement 3 du lieu {i} - 2 réservations dont 1 annulée", offer__venue=venue
        )
        booking_factories.BookingFactory.create(stock=event3)
        booking_factories.CancelledBookingFactory.create(stock=event3)

        event4 = offers_factories.EventStockFactory.create(
            offer__name=f"Évènement 4 du lieu {i} - réservations validées", offer__venue=venue
        )
        booking_factories.UsedBookingFactory.create_batch(2, stock=event4)

        event5 = offers_factories.EventStockFactory.create(
            offer__name=f"Évènement 5 du lieu {i} - réservations remboursées", offer__venue=venue
        )
        booking_factories.ReimbursedBookingFactory.create_batch(2, stock=event5)

    logger.info("create_offerer_with_several_venues")

    return user_offerer.offerer
