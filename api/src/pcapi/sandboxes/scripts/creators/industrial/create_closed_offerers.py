import datetime
import logging

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.history import factories as history_factories
from pcapi.core.history import models as history_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models


logger = logging.getLogger(__name__)


def create_closed_offerers() -> None:
    logger.info("create_closed_offerers")

    beneficiary = users_factories.BeneficiaryGrant18Factory(
        firstName="Jeune",
        lastName="Réservant sur structure fermée",
        email="jeune.structure.fermee@example.com",
    )

    _create_closed_offerer("Structure fermée", "structure.fermee@example.com", beneficiary)
    _create_closed_offerer(
        "Structure fermée avec CB et justificatif",
        "structure.fermee.avec.justificatif@example.com",
        beneficiary,
        with_bank_account=True,
    )

    logger.info("created closed offerer")


def _create_closed_offerer(
    name: str, email: str, beneficiary: users_models.User, with_bank_account: bool = False
) -> None:

    now = datetime.datetime.utcnow()
    siren_caduc_tag = offerers_models.OffererTag.query.filter_by(name="siren-caduc").one()

    offerer = offerers_factories.ClosedOffererFactory(name=name.upper(), tags=[siren_caduc_tag], allowedOnAdage=True)
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
        publicName=name,
        bookingEmail=email,
        adageId=offerer.siren,
        contact=None,
        pricing_point="self",
    )

    offerers_factories.UserOffererFactory(
        user=users_factories.NonAttachedProFactory(
            firstName="Acteur",
            lastName="Structure-Fermée",
            email=f"pro.{email}",
        ),
        offerer=offerer,
    )

    thing_stock = offers_factories.ThingStockFactory(
        offer__venue=venue,
        offer__name="Offre physique d'une structure fermée",
        offer__subcategoryId=subcategories.MATERIEL_ART_CREATIF.id,
        price=30,
        quantity=50,
    )
    used_1 = bookings_factories.UsedBookingFactory(
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
    used_2 = bookings_factories.UsedBookingFactory(
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

    if with_bank_account:
        bank_account = finance_factories.BankAccountFactory(offerer=offerer, label=f"Compte de {name}")
        offerers_factories.VenueBankAccountLinkFactory(venue=venue, bankAccount=bank_account)

        for booking in (used_1, used_2):
            finance_factories.UsedBookingFinanceEventFactory(booking=booking)
            event = finance_models.FinanceEvent.query.filter_by(booking=booking).one()
            finance_api.price_event(event)
        finance_api.generate_cashflows_and_payment_files(cutoff=now)
        cashflows = finance_models.Cashflow.query.filter_by(bankAccount=bank_account).all()
        cashflow_ids = [c.id for c in cashflows]
        finance_api.generate_and_store_invoice_legacy(bank_account_id=bank_account.id, cashflow_ids=cashflow_ids)
