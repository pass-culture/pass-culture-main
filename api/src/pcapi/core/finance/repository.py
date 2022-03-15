import datetime
import typing

import pytz

import pcapi.core.bookings.models as bookings_models
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
import pcapi.core.payments.models as payments_models
import pcapi.core.payments.utils as payments_utils
import pcapi.core.users.models as users_models
from pcapi.models import db
from pcapi.models.bank_information import BankInformation
from pcapi.models.bank_information import BankInformationStatus
from pcapi.models.user_offerer import UserOfferer
import pcapi.utils.date as date_utils

from . import models


def get_business_units_query(
    user: users_models.User,
    offerer_id: int = None,
):
    query = (
        models.BusinessUnit.query.join(BankInformation)
        .filter(models.BusinessUnit.status == models.BusinessUnitStatus.ACTIVE)
        .filter(BankInformation.status == BankInformationStatus.ACCEPTED)
        .join(offerers_models.Venue, offerers_models.Venue.businessUnitId == models.BusinessUnit.id)
    )
    venue_subquery = offerers_models.Venue.query
    if not user.has_admin_role:
        venue_subquery = venue_subquery.join(
            UserOfferer, offerers_models.Venue.managingOffererId == UserOfferer.offererId
        ).filter(UserOfferer.user == user)
    if offerer_id:
        venue_subquery = venue_subquery.filter(offerers_models.Venue.managingOffererId == offerer_id)
    if venue_subquery.whereclause is not None:
        venue_subquery = venue_subquery.with_entities(offerers_models.Venue.id).subquery()
        query = query.filter(offerers_models.Venue.id.in_(venue_subquery))
    return query


def find_business_unit_by_siret(siret: str) -> typing.Optional[models.BusinessUnit]:
    return models.BusinessUnit.query.filter_by(siret=siret).one_or_none()


def get_invoices_query(
    user: users_models.User,
    business_unit_id: int = None,
    date_from: datetime.date = None,
    date_until: datetime.date = None,
):
    """Return invoices for the requested offerer.

    If given, ``date_from`` is **inclusive**, ``date_until`` is
    **exclusive**.
    """
    business_units_subquery = offerers_models.Venue.query
    if not user.has_admin_role:
        business_units_subquery = business_units_subquery.join(
            UserOfferer, UserOfferer.offererId == offerers_models.Venue.managingOffererId
        ).filter(UserOfferer.user == user)
    if business_unit_id:
        # Filtering like this makes sure that the requested business
        # unit id is accessible by the requesting user.
        business_units_subquery = business_units_subquery.filter(
            offerers_models.Venue.businessUnitId == business_unit_id
        )
    elif user.has_admin_role:
        # The following intentionally returns nothing for admin users,
        # so that we do NOT return all invoices of all business units
        # for them. Admin users must select a business unit.
        business_units_subquery = business_units_subquery.filter(False)
    invoices = models.Invoice.query.filter(
        models.Invoice.businessUnitId.in_(
            business_units_subquery.with_entities(offerers_models.Venue.businessUnitId).subquery()
        )
    )
    convert_to_datetime = lambda date: date_utils.get_day_start(date, payments_utils.ACCOUNTING_TIMEZONE).astimezone(
        pytz.utc
    )
    if date_from:
        datetime_from = convert_to_datetime(date_from)
        invoices = invoices.filter(models.Invoice.date >= datetime_from)
    if date_until:
        datetime_until = convert_to_datetime(date_until)
        invoices = invoices.filter(models.Invoice.date < datetime_until)

    return invoices


def has_reimbursement(booking: bookings_models.Booking) -> bool:
    """Return whether the requested booking has been reimbursed."""
    if db.session.query(models.Payment.query.filter_by(bookingId=booking.id).exists()).scalar():
        return True
    paid_pricings = models.Pricing.query.filter(
        models.Pricing.bookingId == booking.id,
        models.Pricing.status.in_((models.PricingStatus.PROCESSED, models.PricingStatus.INVOICED)),
    )
    return db.session.query(paid_pricings.exists()).scalar()


def has_active_or_future_custom_reimbursement_rule(offer: offers_models.Offer) -> bool:
    """Return whether the offer is linked to a custom reimbursement rule
    that is either active or future (but not past).

    Only reimbursement rules that are linked to this *specific* offer
    are looked at (because these rules define an *amount*). Rules that
    apply to subcategories of an offerer are ignored (because they
    define a *rate*).
    """
    now = datetime.datetime.utcnow()
    timespan = payments_models.CustomReimbursementRule._make_timespan(start=now, end=None)
    query = payments_models.CustomReimbursementRule.query.filter(
        payments_models.CustomReimbursementRule.offerId == offer.id,
        payments_models.CustomReimbursementRule.timespan.overlaps(timespan),
    ).exists()
    return db.session.query(query).scalar()
