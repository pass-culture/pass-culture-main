import datetime
import logging
import uuid

import factory

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db


logger = logging.getLogger(__name__)


INDIVIDUAL_INCIDENT_PARAMS = [
    {
        "with_other_venue": True,
        "with_over_revenue_threshold_booking": True,
        "multiple_bookings": False,
        "force_debit_note": False,
        "is_partial": True,
        "comment": "Incident individuel partiel avec plusieurs barêmes",
    },
    {
        "with_other_venue": False,
        "with_over_revenue_threshold_booking": False,
        "multiple_bookings": False,
        "force_debit_note": False,
        "is_partial": False,
        "comment": "Incident individuel total",
    },
    {
        "with_other_venue": False,
        "with_over_revenue_threshold_booking": False,
        "multiple_bookings": True,
        "force_debit_note": False,
        "is_partial": False,
        "comment": "Incident individuel total sur plusieurs réservations",
    },
    {
        "with_other_venue": False,
        "with_over_revenue_threshold_booking": False,
        "multiple_bookings": False,
        "force_debit_note": True,
        "is_partial": True,
        "comment": "Incident individuel partiel avec note de débit",
    },
    {
        "with_other_venue": True,
        "with_over_revenue_threshold_booking": True,
        "multiple_bookings": False,
        "force_debit_note": True,
        "is_partial": False,
        "comment": "Incident individuel total avec plusieurs barêmes et note de débit",
    },
    {
        "with_other_venue": False,
        "with_over_revenue_threshold_booking": True,
        "multiple_bookings": True,
        "force_debit_note": True,
        "is_partial": False,
        "comment": "Incident individuel total sur plusieurs réservations, avec plusieurs barêmes et note de débit",
    },
]


def _check_individual_incident_params() -> None:
    for params in INDIVIDUAL_INCIDENT_PARAMS:
        if params["is_partial"] and params["multiple_bookings"]:
            raise ValueError("Incident not created: an incident can't be partial and have multiple bookings")


_check_individual_incident_params()

COLLECTIVE_INCIDENT_PARAMS = [
    {
        "with_other_venue": False,
        "with_over_revenue_threshold_booking": True,
        "multiple_bookings": False,
        "force_debit_note": False,
        "comment": "Incident collectif total avec plusieurs barêmes",
    },
    {
        "with_other_venue": False,
        "with_over_revenue_threshold_booking": False,
        "multiple_bookings": False,
        "force_debit_note": True,
        "comment": "Incident collectif total avec note de débit",
    },
]


def _add_nearly_over_revenue_threshold_booking(
    venue: offerers_models.Venue, is_collective: bool = False
) -> bookings_models.Booking:
    special_user = users_factories.BeneficiaryGrant18Factory(
        firstName=factory.LazyFunction(lambda: f"martin.cident_{uuid.uuid4()}@example.com"),
        deposit__source="create_industrial_incidents() in industrial sandbox",
    )
    special_user.deposit.amount = 20300
    db.session.add(special_user)
    db.session.commit()

    if is_collective:
        # TODO(jeremieb): find a better solution to avoid institution creation
        # from UsedCollectiveBookingFactory
        institution = educational_models.EducationalInstitution.query.first()

        special_stock = educational_factories.CollectiveStockFactory(collectiveOffer__venue=venue, price=19990)
        special_booking = educational_factories.UsedCollectiveBookingFactory(
            collectiveStock=special_stock, educationalInstitution=institution
        )
    else:
        special_stock = offers_factories.StockFactory(offer__venue=venue, price=19990)
        special_booking = bookings_factories.UsedBookingFactory(
            stock=special_stock,
            user=special_user,
        )
    return special_booking


def _create_one_individual_incident(
    offerer: offerers_models.Offerer,
    pro: users_models.User,
    iteration: int,
    with_other_venue: bool,
    with_over_revenue_threshold_booking: bool,
    multiple_bookings: bool,
    force_debit_note: bool,
    is_partial: bool,
    comment: str,
) -> None:
    venue = offerers_factories.VenueFactory(
        name=f"{iteration} - Lieu avec beaucoup d'incidents",
        managingOfferer=offerer,
        pricing_point="self",
    )
    bank_account = finance_factories.BankAccountFactory(offerer=venue.managingOfferer)
    offerers_factories.VenueBankAccountLinkFactory(bankAccount=bank_account, venue=venue)

    # This is a quick way to have a Venue reach the revenue threshold to reach the next ReimbursementRule
    special_bookings = (
        [_add_nearly_over_revenue_threshold_booking(venue)] if with_over_revenue_threshold_booking else []
    )

    if with_other_venue:
        venue = offerers_factories.VenueFactory(
            name=f"{iteration} - Autre lieu avec beaucoup d'incidents", managingOfferer=offerer, pricing_point=venue
        )
    stocks = offers_factories.StockFactory.create_batch(
        2 if multiple_bookings else 1,
        offer__venue=venue,
        price=30,
    )
    incident_bookings = []
    for stock in stocks:
        booking = bookings_factories.UsedBookingFactory(
            stock=stock,
            user__deposit__source="create_industrial_incidents() in industrial sandbox",
        )
        incident_bookings.append(booking)

    bookings = special_bookings + incident_bookings
    for booking in bookings:
        finance_factories.UsedBookingFinanceEventFactory(booking=booking)
    for booking in bookings:
        event = finance_models.FinanceEvent.query.filter_by(booking=booking).one()
        finance_api.price_event(event)
    finance_api.generate_cashflows_and_payment_files(cutoff=datetime.datetime.utcnow())

    finance_incident = finance_factories.FinanceIncidentFactory(venue=venue, forceDebitNote=force_debit_note)
    if is_partial and not multiple_bookings:
        new_total_amount = (incident_bookings[0].amount * incident_bookings[0].quantity) * 100 - 1000
    else:
        new_total_amount = 0

    for booking in incident_bookings:
        finance_factories.IndividualBookingFinanceIncidentFactory(
            booking=booking, incident=finance_incident, newTotalAmount=new_total_amount
        )

    history_api.add_action(
        history_models.ActionType.FINANCE_INCIDENT_CREATED,
        author=pro,
        finance_incident=finance_incident,
        comment=comment,
    )


def _create_one_collective_incident(
    offerer: offerers_models.Offerer,
    pro: users_models.User,
    iteration: int,
    with_other_venue: bool,
    with_over_revenue_threshold_booking: bool,
    multiple_bookings: bool,
    force_debit_note: bool,
    comment: str,
) -> None:
    venue = offerers_factories.VenueFactory(
        name=f"{iteration} - Lieu avec beaucoup d'incidents collectifs",
        managingOfferer=offerer,
        pricing_point="self",
    )
    bank_account = finance_factories.BankAccountFactory(offerer=venue.managingOfferer)
    offerers_factories.VenueBankAccountLinkFactory(bankAccount=bank_account, venue=venue)

    # This is a quick way to have a Venue reach the revenue threshold to reach the next ReimbursementRule
    special_bookings = (
        [_add_nearly_over_revenue_threshold_booking(venue, True)] if with_over_revenue_threshold_booking else []
    )

    if with_other_venue:
        venue = offerers_factories.VenueFactory(
            name=f"{iteration} - Autre lieu avec beaucoup d'incidents collectifs",
            managingOfferer=offerer,
            pricing_point=venue,
        )
    stocks = educational_factories.CollectiveStockFactory.create_batch(
        2 if multiple_bookings else 1,
        collectiveOffer__venue=venue,
        price=30,
    )

    # TODO(jeremieb): find a better solution to avoid institution creation
    # from UsedCollectiveBookingFactory
    institution = educational_models.EducationalInstitution.query.first()

    incident_bookings = []
    for stock in stocks:
        booking = educational_factories.UsedCollectiveBookingFactory(
            collectiveStock=stock, educationalInstitution=institution
        )
        incident_bookings.append(booking)

    bookings = special_bookings + incident_bookings
    for booking in bookings:
        finance_factories.UsedCollectiveBookingFinanceEventFactory(collectiveBooking=booking)
    for booking in bookings:
        event = finance_models.FinanceEvent.query.filter_by(collectiveBooking=booking).one()
        finance_api.price_event(event)
    finance_api.generate_cashflows_and_payment_files(cutoff=datetime.datetime.utcnow())

    finance_incident = finance_factories.FinanceIncidentFactory(venue=venue, forceDebitNote=force_debit_note)
    for booking in incident_bookings:
        finance_factories.CollectiveBookingFinanceIncidentFactory(
            collectiveBooking=booking, incident=finance_incident, newTotalAmount=0
        )

    history_api.add_action(
        history_models.ActionType.FINANCE_INCIDENT_CREATED,
        author=pro,
        finance_incident=finance_incident,
        comment="comment",
    )


def create_industrial_incidents() -> None:
    offerer = offerers_factories.OffererFactory(name="Structure avec beaucoup d'incidents")
    pro = users_factories.ProFactory(email="pctest.pro.incidents@example.com")
    offerers_factories.UserOffererFactory(offerer=offerer, user=pro)

    for i, params in enumerate(INDIVIDUAL_INCIDENT_PARAMS):
        _create_one_individual_incident(
            offerer,
            pro,
            i,
            bool(params["with_other_venue"]),
            bool(params["with_over_revenue_threshold_booking"]),
            bool(params["multiple_bookings"]),
            bool(params["force_debit_note"]),
            bool(params["is_partial"]),
            str(params["comment"]),
        )
        logger.info("Created individual incident")

    for i, params in enumerate(COLLECTIVE_INCIDENT_PARAMS):
        _create_one_collective_incident(
            offerer,
            pro,
            i,
            bool(params["with_other_venue"]),
            bool(params["with_over_revenue_threshold_booking"]),
            bool(params["multiple_bookings"]),
            bool(params["force_debit_note"]),
            str(params["comment"]),
        )
        logger.info("Created collective incident")
