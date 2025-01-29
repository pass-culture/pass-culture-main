import datetime
import logging

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.history import factories as history_factories
from pcapi.core.history import models as history_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.users import factories as users_factories


logger = logging.getLogger(__name__)


def create_closed_offerers() -> None:
    logger.info("create_closed_offerers")

    now = datetime.datetime.utcnow()
    siren_caduc_tag = offerers_models.OffererTag.query.filter_by(name="siren-caduc").one()

    offerer = offerers_factories.ClosedOffererFactory(
        name="STRUCTURE FERMÉE", tags=[siren_caduc_tag], allowedOnAdage=True
    )
    history_factories.ActionHistoryFactory(
        actionType=history_models.ActionType.OFFERER_CLOSED,
        actionDate=now - datetime.timedelta(days=2),
        authorUser=None,
        offerer=offerer,
        comment="L'entité juridique est détectée comme inactive via l'API Sirene (INSEE)",
        extraData={"modified_info": {"tags": {"new_info": siren_caduc_tag.label}}},
    )

    venue = offerers_factories.VenueFactory(
        managingOfferer=offerer,
        name=offerer.name,
        publicName="Structure fermée",
        bookingEmail="structure.fermee@example.com",
        adageId=offerer.siren,
        contact=None,
        pricing_point="self",
    )

    offerers_factories.UserOffererFactory(
        user=users_factories.NonAttachedProFactory(
            firstName="Acteur",
            lastName="Structure-Fermée",
            email="pro.structure.fermee@example.com",
        ),
        offerer=offerer,
    )

    beneficiary = users_factories.BeneficiaryGrant18Factory(
        firstName="Jeune",
        lastName="Réservant sur structure fermée",
        email="jeune.structure.fermee@example.com",
    )

    thing_stock = offers_factories.ThingStockFactory(
        offer__venue=venue,
        offer__name="Offre physique d'une structure fermée",
        offer__subcategoryId=subcategories.MATERIEL_ART_CREATIF.id,
        price=30,
        quantity=50,
    )
    bookings_factories.UsedBookingFactory(
        user=beneficiary,
        stock=thing_stock,
        dateCreated=now - datetime.timedelta(days=8),  # booked before closure date
        dateUsed=now - datetime.timedelta(days=1),  # validated after closure date
    )
    bookings_factories.BookingFactory(
        user=beneficiary,
        stock=thing_stock,
        dateCreated=now - datetime.timedelta(days=3),  # booked before closure date, not used yet
    )

    event_offer = offers_factories.EventOfferFactory(
        venue=venue,
        name="Offre d'événement d'une structure fermée",
        subcategoryId=subcategories.ATELIER_PRATIQUE_ART.id,
    )
    bookings_factories.UsedBookingFactory(
        user=beneficiary,
        stock__offer=event_offer,
        stock__price=7.50,
        stock__quantity=50,
        stock__beginningDatetime=now - datetime.timedelta(days=4),  # event happened before closure date
        dateCreated=now - datetime.timedelta(days=7),  # booked before closure date
        dateUsed=now - datetime.timedelta(days=1),  # validated after closure date
    )
    bookings_factories.BookingFactory(
        user=beneficiary,
        stock__offer=event_offer,
        stock__price=8,
        stock__quantity=50,
        stock__beginningDatetime=now + datetime.timedelta(days=7),  # future event, after closure date
        dateCreated=now - datetime.timedelta(days=6),  # booked before closure date
    )

    logger.info("created closed offerer")
