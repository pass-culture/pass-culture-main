import datetime
import decimal
import logging

import schwifty

from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.geography import factories as geography_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.users import factories as users_factories


logger = logging.getLogger(__name__)


def create_new_caledonia_offerers() -> None:
    logger.info("create_new_caledonia_offerers")

    _create_nc_active_offerer()
    _create_nc_minimal_offerer()

    logger.info("created New Caledonia offerers")


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
    offerer = offerers_factories.NotValidatedOffererFactory(
        name="Structure calédonienne à Nouméa",
        street=address.street,
        postalCode=address.postalCode,
        city=address.city,
        siren="NC1230001",  # NC + RID7 (experimental)
        allowedOnAdage=False,
    )
    venue = offerers_factories.VenueFactory(
        managingOfferer=offerer,
        pricing_point="self",
        name="Lieu avec RIDET à Nouméa",
        siret="NC1230001001",  # NC + RIDET (experimental)
        departementCode="988",
        latitude=address.latitude,
        longitude=address.longitude,
        bookingEmail="venue.nc@example.net",
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
        adageId=None,
        offererAddress__address=address,
    )
    pro_user = offerers_factories.UserOffererFactory(
        offerer=offerer,
        user__firstName="Mâ",
        user__lastName="Néo-Calédonien",
        user__email="pro1.nc@example.com",
        user__phoneNumber="+687263443",
    ).user
    users_factories.UserProNewNavStateFactory(user=pro_user)

    bank_account = finance_factories.BankAccountFactory(
        label="Compte courant Banque de Nouvelle-Calédonie",
        offerer=offerer,
        iban=schwifty.IBAN.generate("NC", bank_code="7528", account_code="98800000001").compact,
        bic="CEPANCNM",
        dsApplicationId="988001",
        status=finance_models.BankAccountApplicationStatus.ACCEPTED,
    )
    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue, bankAccount=bank_account, timespan=(datetime.datetime.utcnow(),)
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
    offerer = offerers_factories.NotValidatedOffererFactory(
        name="Structure calédonienne à Thio",
        street=address.street,
        postalCode=address.postalCode,
        city=address.city,
        siren="NC1230002",  # NC + RID7 (experimental)
        allowedOnAdage=False,
    )
    offerers_factories.VenueFactory(
        managingOfferer=offerer,
        pricing_point="self",
        name="Lieu avec RIDET à Thio",
        siret="NC1230002001",  # NC + RIDET (experimental)
        departementCode="988",
        latitude=address.latitude,
        longitude=address.longitude,
        bookingEmail="thio.nc@example.net",
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
        adageId=None,
        offererAddress__address=address,
    )
    pro_user = offerers_factories.UserOffererFactory(
        offerer=offerer,
        user__firstName="Méréï",
        user__lastName="Néo-Calédonien",
        user__email="pro2.nc@example.com",
        user__phoneNumber="+687442504",
    ).user
    users_factories.UserProNewNavStateFactory(user=pro_user)
