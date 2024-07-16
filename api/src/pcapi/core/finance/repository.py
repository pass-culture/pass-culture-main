import datetime
import logging

from flask_sqlalchemy import BaseQuery
import pytz
import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm
import sqlalchemy.sql.functions as sqla_func
import sqlalchemy.sql.sqltypes as sqla_sqltypes

import pcapi.core.bookings.models as bookings_models
import pcapi.core.educational.models as educational_models
from pcapi.core.geography import models as geography_models
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
import pcapi.core.users.models as users_models
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
import pcapi.utils.date as date_utils
import pcapi.utils.db as db_utils

from . import models
from . import utils


logger = logging.getLogger(__name__)


def deposit_exists_for_beneficiary_and_type(beneficiary: users_models.User, deposit_type: models.DepositType) -> bool:
    return db.session.query(
        models.Deposit.query.filter_by(
            userId=beneficiary.id,
            type=deposit_type.value,
        ).exists()
    ).scalar()


def has_reimbursement(booking: bookings_models.Booking | educational_models.CollectiveBooking) -> bool:
    """Return whether the requested booking has been reimbursed."""
    if booking.status in (
        bookings_models.BookingStatus.REIMBURSED,
        educational_models.CollectiveBookingStatus.REIMBURSED,
    ):
        return True
    # A booking could have been cancelled after its reimbursement. In
    # that case, its status ("cancelled") cannot be trusted and we
    # must look at the status of its pricing (which do not change when
    # the booking is cancelled).
    if isinstance(booking, bookings_models.Booking):
        pricing_field = models.Pricing.bookingId
    else:
        pricing_field = models.Pricing.collectiveBookingId
    paid_pricings = models.Pricing.query.filter(
        pricing_field == booking.id,
        models.Pricing.status.in_(
            (
                models.PricingStatus.PROCESSED,
                models.PricingStatus.INVOICED,
            )
        ),
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


def get_invoices_by_references(references: list[str]) -> list[models.Invoice]:
    return models.Invoice.query.filter(models.Invoice.reference.in_(references)).order_by(models.Invoice.date).all()


def find_offerer_payments(
    offerer_id: int | None = None,
    reimbursement_period: tuple[datetime.date, datetime.date] | None = None,
    bank_account_id: int | None = None,
    invoices_references: list[str] | None = None,
) -> list[tuple]:
    results = []

    results.extend(
        _get_sent_pricings_for_individual_bookings(
            offerer_id, reimbursement_period, bank_account_id, invoices_references
        )
    )
    results.extend(
        _get_sent_pricings_for_collective_bookings(
            offerer_id, reimbursement_period, bank_account_id, invoices_references
        )
    )
    return results


def find_all_invoices_finance_details(invoice_ids: list[int]) -> list[tuple]:
    results = []
    results.extend(_get_collective_reimbursement_details_from_invoices(invoice_ids))
    results.extend(_get_individual_reimbursement_details_from_invoices(invoice_ids))
    # There are no legacy payments on BO (yet)
    return results


def _truncate_milliseconds(
    column: sqla_orm.InstrumentedAttribute,
) -> sqla_func.Function[sqla_sqltypes.NullType]:
    """Remove milliseconds from the value of a timestamp column."""
    return sqla.func.date_trunc("second", column)


def _get_sent_pricings_for_collective_bookings(
    offerer_id: int | None = None,
    reimbursement_period: tuple[datetime.date, datetime.date] | None = None,
    bank_account_id: int | None = None,
    invoices_references: list[str] | None = None,
) -> list[tuple]:
    query = (
        models.Pricing.query.join(educational_models.CollectiveBooking, models.Pricing.collectiveBooking)
        .join(educational_models.CollectiveStock, educational_models.CollectiveBooking.collectiveStock)
        .join(educational_models.CollectiveOffer, educational_models.CollectiveStock.collectiveOffer)
        .join(offerers_models.Venue, educational_models.CollectiveOffer.venue)
        .join(offerers_models.Offerer, offerers_models.Venue.managingOfferer)
        .join(models.Pricing.cashflows)
        .join(models.Cashflow.bankAccount)
    )

    columns: tuple[sqla.sql.elements.Label, ...] = (
        educational_models.EducationalRedactor.firstName.label("redactor_firstname"),
        educational_models.EducationalRedactor.lastName.label("redactor_lastname"),
        educational_models.EducationalInstitution.name.label("institution_name"),
        _truncate_milliseconds(educational_models.CollectiveBooking.dateUsed).label("booking_used_date"),
        educational_models.CollectiveStock.price.label("booking_amount"),
        educational_models.CollectiveStock.beginningDatetime.label("event_date"),
        educational_models.CollectiveOffer.name.label("offer_name"),
        sqla.true().label("offer_is_educational"),
        offerers_models.Venue.name.label("venue_name"),
        offerers_models.Venue.common_name.label("venue_common_name"),  # type: ignore[attr-defined]
        sqla_func.coalesce(
            offerers_models.Venue.street,
            offerers_models.Offerer.street,
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
        # See note about `amount` in `core/finance/models.py`.
        (-models.Pricing.amount).label("amount"),
        models.Pricing.standardRule.label("rule_name"),
        models.Pricing.customRuleId.label("rule_id"),
        models.Pricing.collectiveBookingId.label("collective_booking_id"),
        sqla.cast(models.Invoice.date, sqla.Date).label("invoice_date"),
        models.Invoice.reference.label("invoice_reference"),
        models.CashflowBatch.cutoff.label("cashflow_batch_cutoff"),
        models.CashflowBatch.label.label("cashflow_batch_label"),
        models.BankAccount.label.label("bank_account_label"),
        models.BankAccount.iban.label("iban"),
    )

    return (
        query.join(models.Cashflow.batch)
        .join(models.Cashflow.invoices)
        .outerjoin(models.Pricing.customRule)
        .filter(
            models.Pricing.status == models.PricingStatus.INVOICED,
            (
                (
                    sqla.cast(models.Cashflow.creationDate, sqla.Date).between(
                        *reimbursement_period,
                        symmetric=True,
                    )
                )
                if reimbursement_period
                else sqla.true()
            ),
            (educational_models.CollectiveBooking.offererId == offerer_id) if offerer_id else sqla.true(),
            (models.Cashflow.bankAccountId == bank_account_id) if bank_account_id else sqla.true(),
            (models.Invoice.reference.in_(invoices_references)) if invoices_references else sqla.true(),
            # Complementary invoices (that end with ".2") are linked
            # to the same bookings as the original invoices they
            # complement. We don't want these bookings to be listed
            # twice.
            models.Invoice.reference.not_like("%.2"),
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
        .with_entities(*columns)
    ).all()


def _get_sent_pricings_for_individual_bookings(
    offerer_id: int | None,
    reimbursement_period: tuple[datetime.date, datetime.date] | None = None,
    bank_account_id: int | None = None,
    invoices_references: list[str] | None = None,
) -> list[tuple]:
    query = (
        models.Pricing.query.join(models.Pricing.booking)
        .join(models.Pricing.cashflows)
        .join(models.Cashflow.batch)
        .join(models.Cashflow.invoices)
        .join(models.Cashflow.bankAccount)
    )

    columns: list[sqla.sql.elements.Label] = [
        bookings_models.Booking.token.label("booking_token"),
        _truncate_milliseconds(bookings_models.Booking.dateUsed).label("booking_used_date"),
        bookings_models.Booking.quantity.label("booking_quantity"),
        bookings_models.Booking.priceCategoryLabel.label("booking_price_category_label"),
        bookings_models.Booking.amount.label("booking_amount"),
        offers_models.Offer.name.label("offer_name"),
        offerers_models.Venue.name.label("venue_name"),
        offerers_models.Venue.common_name.label("venue_common_name"),  # type: ignore[attr-defined]
        sqla_func.coalesce(
            offerers_models.Venue.street,
            offerers_models.Offerer.street,
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
        # See note about `amount` in `core/finance/models.py`.
        (-models.Pricing.amount).label("amount"),
        models.Pricing.standardRule.label("rule_name"),
        models.Pricing.customRuleId.label("rule_id"),
        models.Pricing.collectiveBookingId.label("collective_booking_id"),
        sqla.cast(models.Invoice.date, sqla.Date).label("invoice_date"),
        models.Invoice.reference.label("invoice_reference"),
        models.CashflowBatch.cutoff.label("cashflow_batch_cutoff"),
        models.CashflowBatch.label.label("cashflow_batch_label"),
        models.BankAccount.label.label("bank_account_label"),
        models.BankAccount.iban.label("iban"),
    ]

    query = (
        query.outerjoin(models.Pricing.customRule)
        .filter(
            models.Pricing.status == models.PricingStatus.INVOICED,
            (
                (
                    sqla.cast(models.Cashflow.creationDate, sqla.Date).between(
                        *reimbursement_period,
                        symmetric=True,
                    )
                )
                if reimbursement_period
                else sqla.true()
            ),
            (bookings_models.Booking.offererId == offerer_id) if offerer_id else sqla.true(),
            (models.Cashflow.bankAccountId == bank_account_id) if bank_account_id else sqla.true(),
            (models.Invoice.reference.in_(invoices_references)) if invoices_references else sqla.true(),
            # Complementary invoices (that end with ".2") are linked
            # to the same bookings as the original invoices they
            # complement. We don't want these bookings to be listed
            # twice.
            models.Invoice.reference.not_like("%.2"),
        )
        .join(bookings_models.Booking.offerer)
        .join(bookings_models.Booking.stock)
        .join(offers_models.Stock.offer)
        .join(bookings_models.Booking.venue)
    )

    if FeatureToggle.WIP_ENABLE_OFFER_ADDRESS.is_active():
        sub = sqla.select(
            offerers_models.OffererAddress.id,
            geography_models.Address.street,
            geography_models.Address.postalCode,
            geography_models.Address.city,
        ).join_from(
            offerers_models.OffererAddress,
            geography_models.Address,
            offerers_models.OffererAddress.addressId == geography_models.Address.id,
        )
        sub_venue = sub.subquery("addresses_venue")
        sub_offer = sub.subquery("addresses_offer")
        columns.extend(
            [
                sqla_func.coalesce(sub_offer.c.street, sub_venue.c.street).label("address_street"),
                sqla_func.coalesce(sub_offer.c.postalCode, sub_venue.c.postalCode).label("address_postal_code"),
                sqla_func.coalesce(sub_offer.c.city, sub_venue.c.city).label("address_city"),
            ]
        )
        query = query.join(sub_venue, sub_venue.c.id == offerers_models.Venue.offererAddressId, isouter=True).join(
            sub_offer, sub_offer.c.id == offers_models.Offer.offererAddressId, isouter=True
        )

    return (
        query.order_by(bookings_models.Booking.dateUsed.desc(), bookings_models.Booking.id.desc()).with_entities(
            *columns
        )
    ).all()


def _get_reimbursement_details_from_invoices_base_query(invoice_ids: list[int]) -> BaseQuery:
    return (
        models.Invoice.query.filter(
            models.Invoice.id.in_(invoice_ids),
            # Complementary invoices (that end with ".2") are linked
            # to the same bookings as the original invoices they
            # complement. We don't want these bookings to be listed
            # twice.
            models.Invoice.reference.not_like("%.2"),
        )
        .join(models.InvoiceCashflow, models.InvoiceCashflow.invoiceId == models.Invoice.id)
        .join(models.Cashflow, models.Cashflow.id == models.InvoiceCashflow.cashflowId)
        .join(models.CashflowPricing, models.CashflowPricing.cashflowId == models.Cashflow.id)
        .join(
            models.Pricing,
            sqla.and_(
                models.Pricing.id == models.CashflowPricing.pricingId,
                models.Pricing.status == models.PricingStatus.INVOICED,
            ),
        )
        .join(models.Cashflow.bankAccount)
        .join(models.Cashflow.batch)
        .outerjoin(models.Pricing.customRule)
    )


def _get_collective_booking_reimbursement_data(query: BaseQuery) -> list[tuple]:
    return (
        query.join(models.Pricing.event)
        .join(educational_models.CollectiveStock, educational_models.CollectiveBooking.collectiveStock)
        .join(educational_models.CollectiveOffer, educational_models.CollectiveStock.collectiveOffer)
        .join(offerers_models.Venue, educational_models.CollectiveOffer.venue)
        .join(offerers_models.Offerer, offerers_models.Venue.managingOfferer)
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
            offerers_models.Venue.name.label("venue_name"),
            offerers_models.Venue.common_name.label("venue_common_name"),  # type: ignore[attr-defined]
            # Sometimes, a venue has a postal code and a city, but no address, and the offerer's address
            # is in another city. Now, we only check the postal code to keep either the venue's full address
            # or the offerer's one
            sqla.case(
                (offerers_models.Venue.postalCode.is_not(None), offerers_models.Venue.street),
                else_=offerers_models.Offerer.street,
            ).label("venue_address"),
            sqla.case(
                (offerers_models.Venue.postalCode.is_not(None), offerers_models.Venue.postalCode),
                else_=offerers_models.Offerer.postalCode,
            ).label("venue_postal_code"),
            sqla.case(
                (offerers_models.Venue.postalCode.is_not(None), offerers_models.Venue.city),
                else_=offerers_models.Offerer.city,
            ).label("venue_city"),
            offerers_models.Venue.siret.label("venue_siret"),
            offerers_models.Venue.departementCode.label("venue_departement_code"),
            # See note about `amount` in `core/finance/models.py`.
            (-models.Pricing.amount).label("amount"),
            models.Pricing.standardRule.label("rule_name"),
            models.Pricing.customRuleId.label("rule_id"),
            models.Pricing.collectiveBookingId.label("collective_booking_id"),
            sqla.cast(models.Invoice.date, sqla.Date).label("invoice_date"),
            models.Invoice.reference.label("invoice_reference"),
            models.CashflowBatch.cutoff.label("cashflow_batch_cutoff"),
            models.CashflowBatch.label.label("cashflow_batch_label"),
            models.BankAccount.label.label("bank_account_label"),
            models.BankAccount.iban.label("iban"),
            sqla.case((models.FinanceEvent.bookingFinanceIncidentId.is_(None), False), else_=True).label("is_incident"),
        )
    ).all()


def _get_collective_reimbursement_details_from_invoices(invoice_ids: list[int]) -> list[tuple]:
    collective_details = _get_collective_booking_reimbursement_data(
        _get_reimbursement_details_from_invoices_base_query(invoice_ids).join(
            educational_models.CollectiveBooking, models.Pricing.collectiveBooking
        )
    )
    collective_details.extend(
        _get_collective_booking_reimbursement_data(
            _get_reimbursement_details_from_invoices_base_query(invoice_ids)
            .join(models.Pricing.event)
            .join(models.FinanceEvent.bookingFinanceIncident)
            .join(models.BookingFinanceIncident.collectiveBooking)
        )
    )

    return collective_details


def _get_individual_booking_reimbursement_data(query: BaseQuery) -> list[tuple]:
    return (
        query.join(models.Pricing.event)
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
            offerers_models.Venue.common_name.label("venue_common_name"),  # type: ignore[attr-defined]
            # Sometimes, a venue has a postal code and a city, but no address, and the offerer's address
            # is in another city. Now, we only check the postal code to keep either the venue's full address
            # or the offerer's one
            sqla.case(
                (offerers_models.Venue.postalCode.is_not(None), offerers_models.Venue.street),
                else_=offerers_models.Offerer.street,
            ).label("venue_address"),
            sqla.case(
                (offerers_models.Venue.postalCode.is_not(None), offerers_models.Venue.postalCode),
                else_=offerers_models.Offerer.postalCode,
            ).label("venue_postal_code"),
            sqla.case(
                (offerers_models.Venue.postalCode.is_not(None), offerers_models.Venue.city),
                else_=offerers_models.Offerer.city,
            ).label("venue_city"),
            offerers_models.Venue.siret.label("venue_siret"),
            # See note about `amount` in `core/finance/models.py`.
            (-models.Pricing.amount).label("amount"),
            models.Pricing.standardRule.label("rule_name"),
            models.Pricing.customRuleId.label("rule_id"),
            models.Pricing.collectiveBookingId.label("collective_booking_id"),
            sqla.cast(models.Invoice.date, sqla.Date).label("invoice_date"),
            models.Invoice.reference.label("invoice_reference"),
            models.CashflowBatch.cutoff.label("cashflow_batch_cutoff"),
            models.CashflowBatch.label.label("cashflow_batch_label"),
            models.BankAccount.iban.label("iban"),
            models.BankAccount.label.label("bank_account_label"),
            sqla.case((models.FinanceEvent.bookingFinanceIncidentId.is_(None), False), else_=True).label("is_incident"),
        )
    ).all()


def _get_individual_reimbursement_details_from_invoices(invoice_ids: list[int]) -> list[tuple]:
    individual_details = _get_individual_booking_reimbursement_data(
        _get_reimbursement_details_from_invoices_base_query(invoice_ids).join(models.Pricing.booking)
    )
    # Finance incident data
    individual_details.extend(
        _get_individual_booking_reimbursement_data(
            _get_reimbursement_details_from_invoices_base_query(invoice_ids)
            .join(models.Pricing.event)
            .join(models.FinanceEvent.bookingFinanceIncident)
            .join(models.BookingFinanceIncident.booking)
        )
    )

    return individual_details


def get_bank_account_with_current_venues_links(offerer_id: int, bank_account_id: int) -> models.BankAccount | None:
    return (
        models.BankAccount.query.filter(
            models.BankAccount.id == bank_account_id,
            models.BankAccount.offererId == offerer_id,
            models.BankAccount.status == models.BankAccountApplicationStatus.ACCEPTED,
        )
        .join(offerers_models.Offerer)
        .outerjoin(offerers_models.Venue, offerers_models.Venue.managingOffererId == offerers_models.Offerer.id)
        .outerjoin(
            offerers_models.VenuePricingPointLink,
            sqla.and_(
                offerers_models.VenuePricingPointLink.venueId == offerers_models.Venue.id,
                offerers_models.VenuePricingPointLink.timespan.contains(datetime.datetime.utcnow()),
            ),
        )
        .outerjoin(
            offerers_models.VenueBankAccountLink,
            sqla.and_(
                offerers_models.VenueBankAccountLink.venueId == offerers_models.Venue.id,
                offerers_models.VenueBankAccountLink.timespan.contains(datetime.datetime.utcnow()),
            ),
        )
        .options(
            sqla_orm.contains_eager(models.BankAccount.offerer)
            .contains_eager(offerers_models.Offerer.managedVenues)
            .load_only(
                offerers_models.Venue.id,
                offerers_models.Venue.name,
                offerers_models.Venue.publicName,
                offerers_models.Venue.bookingEmail,
            )
            .contains_eager(offerers_models.Venue.pricing_point_links)
            .load_only(offerers_models.VenuePricingPointLink.timespan)
        )
        .options(
            sqla_orm.contains_eager(models.BankAccount.offerer)
            .contains_eager(offerers_models.Offerer.managedVenues)
            .contains_eager(offerers_models.Venue.bankAccountLinks)
        )
        .one_or_none()
    )


def get_bank_accounts_query(user: users_models.User) -> sqla_orm.Query:
    query = models.BankAccount.query.filter(models.BankAccount.status == models.BankAccountApplicationStatus.ACCEPTED)

    if not user.has_admin_role:
        query = query.join(
            offerers_models.UserOfferer, models.BankAccount.offererId == offerers_models.UserOfferer.offererId
        ).filter(offerers_models.UserOfferer.user == user, offerers_models.UserOfferer.isValidated)
    query = query.with_entities(models.BankAccount.id, models.BankAccount.label)
    return query


def get_invoices_query(
    user: users_models.User,
    bank_account_id: int | None = None,
    offerer_id: int | None = None,
    date_from: datetime.date | None = None,
    date_until: datetime.date | None = None,
) -> sqla_orm.Query:
    """Return invoices for the requested offerer.

    If given, ``date_from`` is **inclusive**, ``date_until`` is
    **exclusive**.
    """
    bank_account_subquery = models.BankAccount.query

    if not user.has_admin_role:
        bank_account_subquery = bank_account_subquery.join(
            offerers_models.UserOfferer,
            offerers_models.UserOfferer.offererId == models.BankAccount.offererId,
        ).filter(offerers_models.UserOfferer.user == user, offerers_models.UserOfferer.isValidated)
    elif user.has_admin_role and not offerer_id and not bank_account_id:
        # The following intentionally returns nothing for admin users,
        # so that we do NOT return all invoices of all bank accounts
        # for them. Admin users must select a bank account, or at least an offererId must be provided.
        bank_account_subquery = bank_account_subquery.filter(False)

    if bank_account_id:
        bank_account_subquery = bank_account_subquery.filter(models.BankAccount.id == bank_account_id)
    elif offerer_id:
        bank_account_subquery = bank_account_subquery.filter(models.BankAccount.offererId == offerer_id)

    invoices = models.Invoice.query.filter(
        models.Invoice.bankAccountId.in_(bank_account_subquery.with_entities(models.BankAccount.id))
    )

    convert_to_datetime = lambda date: date_utils.get_day_start(date, utils.ACCOUNTING_TIMEZONE).astimezone(pytz.utc)
    if date_from:
        datetime_from = convert_to_datetime(date_from)
        invoices = invoices.filter(models.Invoice.date >= datetime_from)
    if date_until:
        datetime_until = convert_to_datetime(date_until)
        invoices = invoices.filter(models.Invoice.date < datetime_until)

    return invoices


def has_invoice(offerer_id: int) -> bool:
    return db.session.query(
        models.Invoice.query.join(models.Invoice.bankAccount)
        .filter(models.BankAccount.offererId == offerer_id)
        .exists()
    ).scalar()
