import datetime

import pytz
import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm
import sqlalchemy.sql.functions as sqla_func

import pcapi.core.bookings.models as bookings_models
import pcapi.core.educational.models as educational_models
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
import pcapi.core.payments.models as payments_models
import pcapi.core.users.models as users_models
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
import pcapi.utils.date as date_utils
import pcapi.utils.db as db_utils

from . import models
from . import utils


def get_business_units_query(  # type: ignore [no-untyped-def]
    user: users_models.User,
    offerer_id: int = None,
):
    query = (
        models.BusinessUnit.query.join(models.BankInformation)
        .filter(models.BusinessUnit.status == models.BusinessUnitStatus.ACTIVE)
        .filter(models.BankInformation.status == models.BankInformationStatus.ACCEPTED)
        .join(offerers_models.Venue, offerers_models.Venue.businessUnitId == models.BusinessUnit.id)
    )
    venue_subquery = offerers_models.Venue.query
    if not user.has_admin_role:
        venue_subquery = venue_subquery.join(
            offerers_models.UserOfferer,
            offerers_models.Venue.managingOffererId == offerers_models.UserOfferer.offererId,
        ).filter(offerers_models.UserOfferer.user == user, offerers_models.UserOfferer.isValidated)
    if offerer_id:
        venue_subquery = venue_subquery.filter(offerers_models.Venue.managingOffererId == offerer_id)
    if venue_subquery.whereclause is not None:
        venue_subquery = venue_subquery.with_entities(offerers_models.Venue.id).subquery()
        query = query.filter(offerers_models.Venue.id.in_(venue_subquery))
    return query


def find_business_unit_by_siret(siret: str) -> models.BusinessUnit | None:
    return models.BusinessUnit.query.filter_by(siret=siret).one_or_none()


def get_invoices_query(  # type: ignore [no-untyped-def]
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
            offerers_models.UserOfferer,
            offerers_models.UserOfferer.offererId == offerers_models.Venue.managingOffererId,
        ).filter(offerers_models.UserOfferer.user == user, offerers_models.UserOfferer.isValidated)
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
    convert_to_datetime = lambda date: date_utils.get_day_start(date, utils.ACCOUNTING_TIMEZONE).astimezone(pytz.utc)
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
    timespan = db_utils.make_timerange(start=now, end=None)
    query = payments_models.CustomReimbursementRule.query.filter(
        payments_models.CustomReimbursementRule.offerId == offer.id,
        payments_models.CustomReimbursementRule.timespan.overlaps(timespan),  # type: ignore [attr-defined]
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
    payment_date = sqla.cast(models.PaymentStatus.date, sqla.Date)
    sent_payments = (
        models.Payment.query.join(models.PaymentStatus)
        .join(bookings_models.Booking)
        .filter(
            models.PaymentStatus.status == models.TransactionStatus.SENT,
            payment_date.between(*reimbursement_period, symmetric=True),
            bookings_models.Booking.offererId.in_(offerer_ids),
            (bookings_models.Booking.venueId == venue_id)
            if venue_id
            else (bookings_models.Booking.venueId is not None),
        )
        .join(offerers_models.Offerer)
        .outerjoin(educational_models.EducationalBooking)
        .outerjoin(educational_models.EducationalRedactor)
        .join(offers_models.Stock)
        .join(offers_models.Offer)
        .join(offerers_models.Venue)
        .distinct(models.Payment.id)
        .order_by(models.Payment.id.desc(), models.PaymentStatus.date.desc())
        .with_entities(
            educational_models.EducationalRedactor.firstName.label("redactor_firstname"),
            educational_models.EducationalRedactor.lastName.label("redactor_lastname"),
            bookings_models.Booking.token.label("booking_token"),
            bookings_models.Booking.dateUsed.label("booking_used_date"),
            bookings_models.Booking.quantity.label("booking_quantity"),
            bookings_models.Booking.amount.label("booking_amount"),
            offers_models.Offer.name.label("offer_name"),
            offers_models.Offer.isEducational.label("offer_is_educational"),
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
        )
    )
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
        results.extend(sent_payments.all())

    return results


def _get_sent_pricings_for_collective_bookings(
    offerer_ids: list[int],
    reimbursement_period: tuple[datetime.date, datetime.date],
    venue_id: int | None = None,
) -> list[tuple]:
    BusinessUnitVenue = sqla_orm.aliased(offerers_models.Venue)
    return (
        models.Pricing.query.join(educational_models.CollectiveBooking, models.Pricing.collectiveBooking)
        .join(educational_models.CollectiveStock, educational_models.CollectiveBooking.collectiveStock)
        .join(educational_models.CollectiveOffer, educational_models.CollectiveStock.collectiveOffer)
        .join(offerers_models.Venue, educational_models.CollectiveOffer.venue)
        .join(offerers_models.Offerer, offerers_models.Venue.managingOfferer)
        .join(offerers_models.Venue.businessUnit)
        .join(models.Pricing.cashflows)
        .join(models.Cashflow.bankAccount)
        .join(models.Cashflow.batch)
        .join(models.Cashflow.invoices)
        .outerjoin(models.Pricing.customRule)
        .filter(
            models.Pricing.status == models.PricingStatus.INVOICED,
            sqla.cast(models.Cashflow.creationDate, sqla.Date).between(
                *reimbursement_period,
                symmetric=True,
            ),
            educational_models.CollectiveBooking.offererId.in_(offerer_ids),
            (offerers_models.Venue.id == venue_id) if venue_id else sqla.true(),
        )
        .join(
            educational_models.EducationalRedactor,
            educational_models.CollectiveBooking.educationalRedactor,
        )
        .join(
            educational_models.EducationalInstitution,
            educational_models.CollectiveBooking.educationalInstitution,
        )
        # There should be a Venue with the same SIRET as the business
        # unit... but edition has been sloppy and there are
        # inconsistencies. See also similar outer joins in `finance/api.py`.
        # FIXME (dbaty, 2022-05-18): if the BusinessUnit model stays,
        # revisit this issue. This is barely acceptable.
        .outerjoin(BusinessUnitVenue, BusinessUnitVenue.siret == models.BusinessUnit.siret)
        .order_by(
            educational_models.CollectiveBooking.dateUsed.desc(),
            educational_models.CollectiveBooking.id.desc(),
        )
        .with_entities(
            educational_models.EducationalRedactor.firstName.label("redactor_firstname"),
            educational_models.EducationalRedactor.lastName.label("redactor_lastname"),
            educational_models.EducationalInstitution.name.label("institution_name"),
            educational_models.CollectiveBooking.dateUsed.label("booking_used_date"),
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
            BusinessUnitVenue.name.label("business_unit_name"),
            sqla_func.coalesce(
                BusinessUnitVenue.address,
                offerers_models.Offerer.address,
            ).label("business_unit_address"),
            sqla_func.coalesce(
                BusinessUnitVenue.postalCode,
                offerers_models.Offerer.postalCode,
            ).label("business_unit_postal_code"),
            sqla_func.coalesce(
                BusinessUnitVenue.city,
                offerers_models.Offerer.city,
            ).label("business_unit_city"),
            BusinessUnitVenue.siret.label("business_unit_siret"),
            # See note about `amount` in `core/finance/models.py`.
            (-models.Pricing.amount).label("amount"),
            models.Pricing.standardRule.label("rule_name"),
            models.Pricing.customRuleId.label("rule_id"),
            models.Invoice.date.label("invoice_date"),
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
    BusinessUnitVenue = sqla_orm.aliased(offerers_models.Venue)
    return (
        models.Pricing.query.join(models.Pricing.booking)
        .join(models.Pricing.cashflows)
        .join(models.Cashflow.bankAccount)
        .join(models.Cashflow.batch)
        .join(models.Cashflow.invoices)
        .outerjoin(models.Pricing.customRule)
        .filter(
            models.Pricing.status == models.PricingStatus.INVOICED,
            sqla.cast(models.Cashflow.creationDate, sqla.Date).between(
                *reimbursement_period,
                symmetric=True,
            ),
            bookings_models.Booking.offererId.in_(offerer_ids),
            (bookings_models.Booking.venueId == venue_id) if venue_id else sqla.true(),
        )
        .join(bookings_models.Booking.offerer)
        .join(bookings_models.Booking.stock)
        .join(offers_models.Stock.offer)
        .join(bookings_models.Booking.venue)
        .join(offerers_models.Venue.businessUnit)
        # There should be a Venue with the same SIRET as the business
        # unit... but edition has been sloppy and there are
        # inconsistencies. See also similar outer joins in `finance/api.py`.
        # FIXME (dbaty, 2022-05-18): if the BusinessUnit model stays,
        # revisit this issue. This is barely acceptable.
        .outerjoin(BusinessUnitVenue, BusinessUnitVenue.siret == models.BusinessUnit.siret)
        .order_by(bookings_models.Booking.dateUsed.desc(), bookings_models.Booking.id.desc())
        .with_entities(
            bookings_models.Booking.token.label("booking_token"),
            bookings_models.Booking.dateUsed.label("booking_used_date"),
            bookings_models.Booking.quantity.label("booking_quantity"),
            bookings_models.Booking.amount.label("booking_amount"),
            offers_models.Offer.name.label("offer_name"),
            offers_models.Offer.isEducational.label("offer_is_educational"),
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
            BusinessUnitVenue.name.label("business_unit_name"),
            sqla_func.coalesce(
                BusinessUnitVenue.address,
                offerers_models.Offerer.address,
            ).label("business_unit_address"),
            sqla_func.coalesce(
                BusinessUnitVenue.postalCode,
                offerers_models.Offerer.postalCode,
            ).label("business_unit_postal_code"),
            sqla_func.coalesce(
                BusinessUnitVenue.city,
                offerers_models.Offerer.city,
            ).label("business_unit_city"),
            BusinessUnitVenue.siret.label("business_unit_siret"),
            # See note about `amount` in `core/finance/models.py`.
            (-models.Pricing.amount).label("amount"),
            models.Pricing.standardRule.label("rule_name"),
            models.Pricing.customRuleId.label("rule_id"),
            models.Invoice.date.label("invoice_date"),
            models.Invoice.reference.label("invoice_reference"),
            models.CashflowBatch.cutoff.label("cashflow_batch_cutoff"),
            models.CashflowBatch.label.label("cashflow_batch_label"),
            models.BankInformation.iban.label("iban"),
        )
    ).all()
