import datetime
from typing import Any

import pytz
import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm
import sqlalchemy.sql.functions as sqla_func
import sqlalchemy.sql.sqltypes as sqla_sqltypes

import pcapi.core.bookings.models as bookings_models
import pcapi.core.educational.models as educational_models
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
import pcapi.core.users.models as users_models
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
import pcapi.utils.date as date_utils
import pcapi.utils.db as db_utils

from . import models
from . import utils


def deposit_exists_for_beneficiary_and_type(beneficiary: users_models.User, deposit_type: models.DepositType) -> bool:
    return db.session.query(
        models.Deposit.query.filter_by(
            userId=beneficiary.id,
            type=deposit_type.value,
        ).exists()
    ).scalar()


def get_reimbursement_points_query(user: users_models.User) -> sqla_orm.Query:
    query = offerers_models.Venue.query.join(models.BankInformation).filter(
        models.BankInformation.status == models.BankInformationStatus.ACCEPTED
    )
    venue_subquery = offerers_models.Venue.query
    if not user.has_admin_role:
        venue_subquery = venue_subquery.join(
            offerers_models.UserOfferer,
            offerers_models.Venue.managingOffererId == offerers_models.UserOfferer.offererId,
        ).filter(offerers_models.UserOfferer.user == user, offerers_models.UserOfferer.isValidated)
    if venue_subquery.whereclause is not None:
        venue_subquery = venue_subquery.with_entities(offerers_models.Venue.id).subquery()
        query = query.filter(offerers_models.Venue.id.in_(venue_subquery))
    return query


def get_invoices_query(
    user: users_models.User,
    reimbursement_point_id: int | None = None,
    date_from: datetime.date | None = None,
    date_until: datetime.date | None = None,
) -> sqla_orm.Query:
    """Return invoices for the requested offerer.

    If given, ``date_from`` is **inclusive**, ``date_until`` is
    **exclusive**.
    """
    reimbursement_point_subquery = offerers_models.Venue.query

    if not user.has_admin_role:
        reimbursement_point_subquery = reimbursement_point_subquery.join(
            offerers_models.UserOfferer,
            offerers_models.UserOfferer.offererId == offerers_models.Venue.managingOffererId,
        ).filter(offerers_models.UserOfferer.user == user, offerers_models.UserOfferer.isValidated)

    if reimbursement_point_id:
        reimbursement_point_subquery = reimbursement_point_subquery.join(
            offerers_models.Venue.reimbursement_point_links
        ).filter(offerers_models.VenueReimbursementPointLink.reimbursementPointId == reimbursement_point_id)

    elif user.has_admin_role:
        # The following intentionally returns nothing for admin users,
        # so that we do NOT return all invoices of all reimbursement points
        # for them. Admin users must select a reimbursement point.
        reimbursement_point_subquery = reimbursement_point_subquery.filter(False)

    invoices = models.Invoice.query.filter(
        models.Invoice.reimbursementPointId.in_(
            reimbursement_point_subquery.with_entities(offerers_models.Venue.id).subquery()
        )
    )

    convert_to_datetime = lambda date: date_utils.get_day_start(date, utils.ACCOUNTING_TIMEZONE).astimezone(pytz.utc)
    if date_from:
        datetime_from = convert_to_datetime(date_from)
        invoices = invoices.filter(models.Invoice.date >= datetime_from)
    if date_until:
        datetime_until = convert_to_datetime(date_until)
        invoices = invoices.filter(models.Invoice.date < datetime_until)

    return invoices


def has_reimbursement(booking: bookings_models.Booking | educational_models.CollectiveBooking) -> bool:
    """Return whether the requested booking has been reimbursed."""
    if isinstance(booking, bookings_models.Booking):
        pricing_field = models.Pricing.bookingId
        payment_field = models.Payment.bookingId
    else:
        pricing_field = models.Pricing.collectiveBookingId
        payment_field = models.Payment.collectiveBookingId
    if db.session.query(models.Payment.query.filter(payment_field == booking.id).exists()).scalar():
        return True
    paid_pricings = models.Pricing.query.filter(
        pricing_field == booking.id,
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
    timespan = db_utils.make_timerange(start=now, end=None)
    query = models.CustomReimbursementRule.query.filter(
        models.CustomReimbursementRule.offerId == offer.id,
        models.CustomReimbursementRule.timespan.overlaps(timespan),
    ).exists()
    return db.session.query(query).scalar()


def find_all_offerer_payments(
    offerer_id: int,
    reimbursement_period: tuple[datetime.date, datetime.date],
    venue_id: int | None = None,
) -> list[tuple]:
    return find_all_offerers_payments(
        offerer_ids=[offerer_id],
        reimbursement_period=reimbursement_period,
        venue_id=venue_id,
    )


def find_all_offerers_payments(
    offerer_ids: list[int],
    reimbursement_period: tuple[datetime.date, datetime.date],
    venue_id: int | None = None,
) -> list[tuple]:
    results = []

    results.extend(
        _get_sent_pricings_for_individual_bookings(
            offerer_ids,
            reimbursement_period,
            venue_id,
        )
    )
    results.extend(
        _get_sent_pricings_for_collective_bookings(
            offerer_ids,
            reimbursement_period,
            venue_id,
        )
    )

    if FeatureToggle.INCLUDE_LEGACY_PAYMENTS_FOR_REIMBURSEMENTS.is_active():
        payment_date = sqla.cast(models.PaymentStatus.date, sqla.Date)
        results.extend(
            _get_legacy_payments_for_individual_bookings(
                payment_date, offerer_ids, reimbursement_period, venue_id
            ).all()
        )
        results.extend(
            _get_legacy_payments_for_collective_bookings(
                payment_date, offerer_ids, reimbursement_period, venue_id
            ).all()
        )

    return results


def _truncate_milliseconds(
    column: sqla_orm.InstrumentedAttribute,
) -> sqla_func.Function[sqla_sqltypes.NullType]:
    """Remove milliseconds from the value of a timestamp column."""
    return sqla.func.date_trunc("second", column)


def _get_sent_pricings_for_collective_bookings(
    offerer_ids: list[int],
    reimbursement_period: tuple[datetime.date, datetime.date],
    venue_id: int | None = None,
) -> list[tuple]:
    ReimbursementPoint = sqla_orm.aliased(offerers_models.Venue)
    return (
        models.Pricing.query.join(educational_models.CollectiveBooking, models.Pricing.collectiveBooking)
        .join(educational_models.CollectiveStock, educational_models.CollectiveBooking.collectiveStock)
        .join(educational_models.CollectiveOffer, educational_models.CollectiveStock.collectiveOffer)
        .join(offerers_models.Venue, educational_models.CollectiveOffer.venue)
        .join(offerers_models.Offerer, offerers_models.Venue.managingOfferer)
        .join(models.Pricing.cashflows)
        .join(models.Cashflow.bankAccount)
        .join(models.Cashflow.batch)
        .join(models.Cashflow.invoices)
        .join(ReimbursementPoint, models.Cashflow.reimbursementPointId == ReimbursementPoint.id)
        .outerjoin(models.Pricing.customRule)
        .filter(
            models.Pricing.status == models.PricingStatus.INVOICED,
            sqla.cast(models.Cashflow.creationDate, sqla.Date).between(
                *reimbursement_period,
                symmetric=True,
            ),
            educational_models.CollectiveBooking.offererId.in_(offerer_ids),
            (offerers_models.Venue.id == venue_id) if venue_id else sqla.true(),
            # Complementary invoices (that end with ".2") are linked
            # to the same bookings as the original invoices they
            # complement. We don't want these bookings to be listed
            # twice.
            models.Invoice.reference.notlike("%.2"),
        )
        .join(
            educational_models.EducationalRedactor,
            educational_models.CollectiveBooking.educationalRedactor,
        )
        .join(
            educational_models.EducationalInstitution,
            educational_models.CollectiveBooking.educationalInstitution,
        )
        .order_by(
            educational_models.CollectiveBooking.dateUsed.desc(),
            educational_models.CollectiveBooking.id.desc(),
        )
        .with_entities(
            educational_models.EducationalRedactor.firstName.label("redactor_firstname"),
            educational_models.EducationalRedactor.lastName.label("redactor_lastname"),
            educational_models.EducationalInstitution.name.label("institution_name"),
            _truncate_milliseconds(educational_models.CollectiveBooking.dateUsed).label("booking_used_date"),
            educational_models.CollectiveStock.price.label("booking_amount"),
            educational_models.CollectiveStock.beginningDatetime.label("event_date"),
            educational_models.CollectiveOffer.name.label("offer_name"),
            sqla.true().label("offer_is_educational"),
            offerers_models.Venue.name.label("venue_name"),
            sqla_func.coalesce(
                offerers_models.Venue.address,
                offerers_models.Offerer.address,
            ).label("venue_address"),
            sqla_func.coalesce(
                offerers_models.Venue.postalCode,
                offerers_models.Offerer.postalCode,
            ).label("venue_postal_code"),
            sqla_func.coalesce(
                offerers_models.Venue.city,
                offerers_models.Offerer.city,
            ).label("venue_city"),
            offerers_models.Venue.siret.label("venue_siret"),
            offerers_models.Venue.departementCode.label("venue_departement_code"),
            ReimbursementPoint.name.label("reimbursement_point_name"),
            sqla_func.coalesce(
                ReimbursementPoint.address,
                offerers_models.Offerer.address,
            ).label("reimbursement_point_address"),
            sqla_func.coalesce(
                ReimbursementPoint.postalCode,
                offerers_models.Offerer.postalCode,
            ).label("reimbursement_point_postal_code"),
            sqla_func.coalesce(
                ReimbursementPoint.city,
                offerers_models.Offerer.city,
            ).label("reimbursement_point_city"),
            ReimbursementPoint.siret.label("reimbursement_point_siret"),
            # See note about `amount` in `core/finance/models.py`.
            (-models.Pricing.amount).label("amount"),
            models.Pricing.standardRule.label("rule_name"),
            models.Pricing.customRuleId.label("rule_id"),
            models.Pricing.collectiveBookingId.label("collective_booking_id"),
            sqla.cast(models.Invoice.date, sqla.Date).label("invoice_date"),
            models.Invoice.reference.label("invoice_reference"),
            models.CashflowBatch.cutoff.label("cashflow_batch_cutoff"),
            models.CashflowBatch.label.label("cashflow_batch_label"),
            models.BankInformation.iban.label("iban"),
        )
    ).all()


def _get_sent_pricings_for_individual_bookings(
    offerer_ids: list[int],
    reimbursement_period: tuple[datetime.date, datetime.date],
    venue_id: int | None = None,
) -> list[tuple]:
    ReimbursementPoint = sqla_orm.aliased(offerers_models.Venue)
    return (
        models.Pricing.query.join(models.Pricing.booking)
        .join(models.Pricing.cashflows)
        .join(models.Cashflow.bankAccount)
        .join(models.Cashflow.batch)
        .join(models.Cashflow.invoices)
        .join(ReimbursementPoint, models.Cashflow.reimbursementPointId == ReimbursementPoint.id)
        .outerjoin(models.Pricing.customRule)
        .filter(
            models.Pricing.status == models.PricingStatus.INVOICED,
            sqla.cast(models.Cashflow.creationDate, sqla.Date).between(
                *reimbursement_period,
                symmetric=True,
            ),
            bookings_models.Booking.offererId.in_(offerer_ids),
            (bookings_models.Booking.venueId == venue_id) if venue_id else sqla.true(),
            # Complementary invoices (that end with ".2") are linked
            # to the same bookings as the original invoices they
            # complement. We don't want these bookings to be listed
            # twice.
            models.Invoice.reference.notlike("%.2"),
        )
        .join(bookings_models.Booking.offerer)
        .join(bookings_models.Booking.stock)
        .join(offers_models.Stock.offer)
        .join(bookings_models.Booking.venue)
        .order_by(bookings_models.Booking.dateUsed.desc(), bookings_models.Booking.id.desc())
        .with_entities(
            bookings_models.Booking.token.label("booking_token"),
            _truncate_milliseconds(bookings_models.Booking.dateUsed).label("booking_used_date"),
            bookings_models.Booking.quantity.label("booking_quantity"),
            bookings_models.Booking.priceCategoryLabel.label("booking_price_category_label"),
            bookings_models.Booking.amount.label("booking_amount"),
            offers_models.Offer.name.label("offer_name"),
            offerers_models.Venue.name.label("venue_name"),
            sqla_func.coalesce(
                offerers_models.Venue.address,
                offerers_models.Offerer.address,
            ).label("venue_address"),
            sqla_func.coalesce(
                offerers_models.Venue.postalCode,
                offerers_models.Offerer.postalCode,
            ).label("venue_postal_code"),
            sqla_func.coalesce(
                offerers_models.Venue.city,
                offerers_models.Offerer.city,
            ).label("venue_city"),
            offerers_models.Venue.siret.label("venue_siret"),
            ReimbursementPoint.name.label("reimbursement_point_name"),
            sqla_func.coalesce(
                ReimbursementPoint.address,
                offerers_models.Offerer.address,
            ).label("reimbursement_point_address"),
            sqla_func.coalesce(
                ReimbursementPoint.postalCode,
                offerers_models.Offerer.postalCode,
            ).label("reimbursement_point_postal_code"),
            sqla_func.coalesce(
                ReimbursementPoint.city,
                offerers_models.Offerer.city,
            ).label("reimbursement_point_city"),
            ReimbursementPoint.siret.label("reimbursement_point_siret"),
            # See note about `amount` in `core/finance/models.py`.
            (-models.Pricing.amount).label("amount"),
            models.Pricing.standardRule.label("rule_name"),
            models.Pricing.customRuleId.label("rule_id"),
            models.Pricing.collectiveBookingId.label("collective_booking_id"),
            sqla.cast(models.Invoice.date, sqla.Date).label("invoice_date"),
            models.Invoice.reference.label("invoice_reference"),
            models.CashflowBatch.cutoff.label("cashflow_batch_cutoff"),
            models.CashflowBatch.label.label("cashflow_batch_label"),
            models.BankInformation.iban.label("iban"),
        )
    ).all()


def _get_legacy_payments_for_individual_bookings(
    payment_date_cast: Any,
    offerer_ids: list[int],
    reimbursement_period: tuple[datetime.date, datetime.date],
    venue_id: int | None = None,
) -> sqla_orm.Query:
    return (
        models.Payment.query.join(models.PaymentStatus)
        .join(bookings_models.Booking)
        .filter(
            models.PaymentStatus.status == models.TransactionStatus.SENT,
            payment_date_cast.between(*reimbursement_period, symmetric=True),
            bookings_models.Booking.offererId.in_(offerer_ids),
            (bookings_models.Booking.venueId == venue_id)
            if venue_id
            else (bookings_models.Booking.venueId is not None),
        )
        .join(offerers_models.Offerer)
        .join(offers_models.Stock)
        .join(offers_models.Offer)
        .join(offerers_models.Venue)
        .distinct(models.Payment.id)
        .order_by(models.Payment.id.desc(), models.PaymentStatus.date.desc())
        .with_entities(
            bookings_models.Booking.token.label("booking_token"),
            _truncate_milliseconds(bookings_models.Booking.dateUsed).label("booking_used_date"),
            bookings_models.Booking.priceCategoryLabel.label("booking_price_category_label"),
            bookings_models.Booking.quantity.label("booking_quantity"),
            bookings_models.Booking.amount.label("booking_amount"),
            offers_models.Offer.name.label("offer_name"),
            offerers_models.Venue.name.label("venue_name"),
            sqla_func.coalesce(
                offerers_models.Venue.address,
                offerers_models.Offerer.address,
            ).label("venue_address"),
            sqla_func.coalesce(
                offerers_models.Venue.postalCode,
                offerers_models.Offerer.postalCode,
            ).label("venue_postal_code"),
            sqla_func.coalesce(
                offerers_models.Venue.city,
                offerers_models.Offerer.city,
            ).label("venue_city"),
            offerers_models.Venue.siret.label("venue_siret"),
            models.Payment.iban.label("iban"),
            models.Payment.amount.label("amount"),
            models.Payment.reimbursementRate.label("reimbursement_rate"),
            models.Payment.transactionLabel.label("transaction_label"),
            models.Payment.collectiveBookingId.label("collective_booking_id"),
        )
    )


def _get_legacy_payments_for_collective_bookings(
    payment_date_cast: Any,
    offerer_ids: list[int],
    reimbursement_period: tuple[datetime.date, datetime.date],
    venue_id: int | None = None,
) -> sqla_orm.Query:
    return (
        models.Payment.query.join(models.PaymentStatus)
        .join(educational_models.CollectiveBooking)
        .filter(
            models.PaymentStatus.status == models.TransactionStatus.SENT,
            payment_date_cast.between(*reimbursement_period, symmetric=True),
            educational_models.CollectiveBooking.offererId.in_(offerer_ids),
            (educational_models.CollectiveBooking.venueId == venue_id)
            if venue_id
            else (educational_models.CollectiveBooking.venueId is not None),
        )
        .join(offerers_models.Venue, offerers_models.Venue.id == educational_models.CollectiveBooking.venueId)
        .join(offerers_models.Offerer, offerers_models.Offerer.id == educational_models.CollectiveBooking.offererId)
        .join(educational_models.CollectiveStock, educational_models.CollectiveBooking.collectiveStock)
        .join(educational_models.CollectiveOffer, educational_models.CollectiveStock.collectiveOffer)
        .join(educational_models.EducationalRedactor, educational_models.CollectiveBooking.educationalRedactor)
        .distinct(models.Payment.id)
        .order_by(models.Payment.id.desc(), models.PaymentStatus.date.desc())
        .with_entities(
            educational_models.EducationalRedactor.firstName.label("redactor_firstname"),
            educational_models.EducationalRedactor.lastName.label("redactor_lastname"),
            _truncate_milliseconds(educational_models.CollectiveBooking.dateUsed).label("booking_used_date"),
            educational_models.CollectiveStock.price.label("booking_amount"),
            educational_models.CollectiveOffer.name.label("offer_name"),
            offerers_models.Venue.name.label("venue_name"),
            sqla_func.coalesce(
                offerers_models.Venue.address,
                offerers_models.Offerer.address,
            ).label("venue_address"),
            sqla_func.coalesce(
                offerers_models.Venue.postalCode,
                offerers_models.Offerer.postalCode,
            ).label("venue_postal_code"),
            sqla_func.coalesce(
                offerers_models.Venue.city,
                offerers_models.Offerer.city,
            ).label("venue_city"),
            offerers_models.Venue.siret.label("venue_siret"),
            models.Payment.iban.label("iban"),
            models.Payment.amount.label("amount"),
            models.Payment.reimbursementRate.label("reimbursement_rate"),
            models.Payment.transactionLabel.label("transaction_label"),
            models.Payment.collectiveBookingId.label("collective_booking_id"),
        )
    )
