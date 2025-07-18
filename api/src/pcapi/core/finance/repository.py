import datetime
import logging

import pytz
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
import sqlalchemy.sql.functions as sa_func
import sqlalchemy.sql.sqltypes as sa_sqltypes

import pcapi.core.bookings.models as bookings_models
import pcapi.core.educational.models as educational_models
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
import pcapi.core.users.models as users_models
import pcapi.utils.date as date_utils
import pcapi.utils.db as db_utils
from pcapi.core.geography import models as geography_models
from pcapi.models import db

from . import models
from . import utils


logger = logging.getLogger(__name__)


def deposit_exists_for_beneficiary_and_type(beneficiary: users_models.User, deposit_type: models.DepositType) -> bool:
    return db.session.query(
        db.session.query(models.Deposit)
        .filter_by(
            userId=beneficiary.id,
            type=deposit_type.value,
        )
        .exists()
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
    paid_pricings = db.session.query(models.Pricing).filter(
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
    query = (
        db.session.query(models.CustomReimbursementRule)
        .filter(
            models.CustomReimbursementRule.offerId == offer.id,
            models.CustomReimbursementRule.timespan.overlaps(timespan),
        )
        .exists()
    )
    return db.session.query(query).scalar()


def get_invoices_by_references(references: list[str]) -> list[models.Invoice]:
    return (
        db.session.query(models.Invoice)
        .filter(models.Invoice.reference.in_(references))
        .order_by(models.Invoice.date)
        .all()
    )


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
    column: sa_orm.InstrumentedAttribute,
) -> sa_func.Function[sa_sqltypes.NullType]:
    """Remove milliseconds from the value of a timestamp column."""
    return sa.func.date_trunc("second", column)


def _get_sent_pricings_for_collective_bookings(
    offerer_id: int | None = None,
    reimbursement_period: tuple[datetime.date, datetime.date] | None = None,
    bank_account_id: int | None = None,
    invoices_references: list[str] | None = None,
) -> list[tuple]:
    # Querying the Pricing information before joining the
    # CollectiveBooking makes the query much more efficient
    sub_query = (
        db.session.query(
            # See note about `amount` in `core/finance/models.py`.
            (-models.Pricing.amount).label("amount"),
            models.Pricing.standardRule.label("rule_name"),
            models.Pricing.customRuleId.label("rule_id"),
            models.Pricing.collectiveBookingId.label("collective_booking_id"),
            sa.cast(models.Invoice.date, sa.Date).label("invoice_date"),
            models.Invoice.reference.label("invoice_reference"),
            models.CashflowBatch.cutoff.label("cashflow_batch_cutoff"),
            models.CashflowBatch.label.label("cashflow_batch_label"),
            models.BankAccount.label.label("bank_account_label"),
            models.BankAccount.iban.label("iban"),
        )
        .join(models.Pricing.cashflows)
        .join(models.Cashflow.bankAccount)
        .join(models.Cashflow.batch)
        .join(models.Cashflow.invoices)
        .outerjoin(models.Pricing.customRule)
        .filter(
            models.Pricing.status == models.PricingStatus.INVOICED,
            (
                (
                    sa.cast(models.Cashflow.creationDate, sa.Date).between(
                        *reimbursement_period,
                        symmetric=True,
                    )
                )
                if reimbursement_period
                else sa.true()
            ),
            (models.Cashflow.bankAccountId == bank_account_id) if bank_account_id else sa.true(),
            (models.Invoice.reference.in_(invoices_references)) if invoices_references else sa.true(),
            # Complementary invoices (that end with ".2") are linked
            # to the same bookings as the original invoices they
            # complement. We don't want these bookings to be listed
            # twice.
            models.Invoice.reference.not_like("%.2"),
        )
        .subquery("pricing_temp")
    )
    pricing_sub_query = sa_orm.aliased(sub_query)

    columns: tuple[sa.sql.elements.Label, ...] = (
        educational_models.EducationalRedactor.firstName.label("redactor_firstname"),
        educational_models.EducationalRedactor.lastName.label("redactor_lastname"),
        educational_models.EducationalInstitution.name.label("institution_name"),
        _truncate_milliseconds(educational_models.CollectiveBooking.dateUsed).label("booking_used_date"),
        educational_models.CollectiveStock.price.label("booking_amount"),
        educational_models.CollectiveStock.startDatetime.label("event_date"),
        educational_models.CollectiveOffer.name.label("offer_name"),
        sa.true().label("offer_is_educational"),
        offerers_models.Venue.name.label("venue_name"),
        offerers_models.Venue.common_name.label("venue_common_name"),  # type: ignore[attr-defined]
        geography_models.Address.street.label("venue_address"),
        geography_models.Address.postalCode.label("venue_postal_code"),
        geography_models.Address.city.label("venue_city"),
        geography_models.Address.departmentCode.label("venue_departement_code"),
        offerers_models.Venue.siret.label("venue_siret"),
        pricing_sub_query.c.amount.label("amount"),
        pricing_sub_query.c.rule_name.label("rule_name"),
        pricing_sub_query.c.rule_id.label("rule_id"),
        pricing_sub_query.c.collective_booking_id.label("collective_booking_id"),
        pricing_sub_query.c.invoice_date.label("invoice_date"),
        pricing_sub_query.c.invoice_reference.label("invoice_reference"),
        pricing_sub_query.c.cashflow_batch_cutoff.label("cashflow_batch_cutoff"),
        pricing_sub_query.c.cashflow_batch_label.label("cashflow_batch_label"),
        pricing_sub_query.c.bank_account_label.label("bank_account_label"),
        pricing_sub_query.c.iban.label("iban"),
    )

    return (
        db.session.query(educational_models.CollectiveBooking)
        .join(
            pricing_sub_query,
            pricing_sub_query.c.collective_booking_id == educational_models.CollectiveBooking.id,
        )
        .join(educational_models.CollectiveStock, educational_models.CollectiveBooking.collectiveStock)
        .join(educational_models.CollectiveOffer, educational_models.CollectiveStock.collectiveOffer)
        .join(offerers_models.Venue, educational_models.CollectiveOffer.venue)
        .join(offerers_models.OffererAddress, offerers_models.Venue.offererAddress)
        .join(geography_models.Address, offerers_models.OffererAddress.address)
        .join(offerers_models.Offerer, offerers_models.Venue.managingOfferer)
        .join(
            educational_models.EducationalRedactor,
            educational_models.CollectiveBooking.educationalRedactor,
        )
        .join(
            educational_models.EducationalInstitution,
            educational_models.CollectiveBooking.educationalInstitution,
        )
        .filter((educational_models.CollectiveBooking.offererId == offerer_id) if offerer_id else sa.true())
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
        db.session.query(models.Pricing)
        .join(models.Pricing.booking)
        .join(models.Pricing.cashflows)
        .join(models.Cashflow.batch)
        .join(models.Cashflow.invoices)
        .join(models.Cashflow.bankAccount)
    )

    columns: list[sa.sql.elements.Label] = [
        bookings_models.Booking.token.label("booking_token"),
        _truncate_milliseconds(bookings_models.Booking.dateUsed).label("booking_used_date"),
        bookings_models.Booking.quantity.label("booking_quantity"),
        bookings_models.Booking.priceCategoryLabel.label("booking_price_category_label"),
        bookings_models.Booking.amount.label("booking_amount"),
        offers_models.Offer.name.label("offer_name"),
        offerers_models.Venue.name.label("venue_name"),
        offerers_models.Venue.common_name.label("venue_common_name"),  # type: ignore[attr-defined]
        offerers_models.Venue.siret.label("venue_siret"),
        # See note about `amount` in `core/finance/models.py`.
        (-models.Pricing.amount).label("amount"),
        models.Pricing.standardRule.label("rule_name"),
        models.Pricing.customRuleId.label("rule_id"),
        models.Pricing.collectiveBookingId.label("collective_booking_id"),
        sa.cast(models.Invoice.date, sa.Date).label("invoice_date"),
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
                    sa.cast(models.Cashflow.creationDate, sa.Date).between(
                        *reimbursement_period,
                        symmetric=True,
                    )
                )
                if reimbursement_period
                else sa.true()
            ),
            (bookings_models.Booking.offererId == offerer_id) if offerer_id else sa.true(),
            (models.Cashflow.bankAccountId == bank_account_id) if bank_account_id else sa.true(),
            (models.Invoice.reference.in_(invoices_references)) if invoices_references else sa.true(),
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

    # TODO bdalbianco 06/06/2025 CLEAN_OA ne garder que venue/offer apres la regul
    sub = sa.select(
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
            sa_func.coalesce(sub_offer.c.street, sub_venue.c.street, offerers_models.Offerer.street).label(
                "address_street"
            ),
            sa_func.coalesce(sub_offer.c.postalCode, sub_venue.c.postalCode, offerers_models.Offerer.postalCode).label(
                "address_postal_code"
            ),
            sa_func.coalesce(sub_offer.c.city, sub_venue.c.city, offerers_models.Offerer.city).label("address_city"),
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


def _get_reimbursement_details_from_invoices_base_query(invoice_ids: list[int]) -> sa_orm.Query:
    return (
        db.session.query(models.Invoice)
        .filter(
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
            sa.and_(
                models.Pricing.id == models.CashflowPricing.pricingId,
                models.Pricing.status == models.PricingStatus.INVOICED,
            ),
        )
        .join(models.Cashflow.bankAccount)
        .join(models.Cashflow.batch)
        .outerjoin(models.Pricing.customRule)
    )


def _get_collective_booking_reimbursement_data(query: sa_orm.Query) -> list[tuple]:
    return (
        query.join(models.Pricing.event)
        .join(educational_models.CollectiveStock, educational_models.CollectiveBooking.collectiveStock)
        .join(educational_models.CollectiveOffer, educational_models.CollectiveStock.collectiveOffer)
        .join(offerers_models.Venue, educational_models.CollectiveOffer.venue)
        .join(offerers_models.OffererAddress, offerers_models.Venue.offererAddress)
        .join(geography_models.Address, offerers_models.OffererAddress.address)
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
            educational_models.CollectiveStock.startDatetime.label("event_date"),
            educational_models.CollectiveOffer.name.label("offer_name"),
            offerers_models.Venue.name.label("venue_name"),
            offerers_models.Venue.common_name.label("venue_common_name"),  # type: ignore[attr-defined]
            offerers_models.Venue.siret.label("venue_siret"),
            geography_models.Address.street.label("venue_address"),
            geography_models.Address.postalCode.label("venue_postal_code"),
            geography_models.Address.city.label("venue_city"),
            geography_models.Address.departmentCode.label("venue_departement_code"),
            # See note about `amount` in `core/finance/models.py`.
            (-models.Pricing.amount).label("amount"),
            models.Pricing.standardRule.label("rule_name"),
            models.Pricing.customRuleId.label("rule_id"),
            models.Pricing.collectiveBookingId.label("collective_booking_id"),
            sa.cast(models.Invoice.date, sa.Date).label("invoice_date"),
            models.Invoice.reference.label("invoice_reference"),
            models.CashflowBatch.cutoff.label("cashflow_batch_cutoff"),
            models.CashflowBatch.label.label("cashflow_batch_label"),
            models.BankAccount.label.label("bank_account_label"),
            models.BankAccount.iban.label("iban"),
            sa.case((models.FinanceEvent.bookingFinanceIncidentId.is_(None), False), else_=True).label("is_incident"),
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


def _get_individual_booking_reimbursement_data(query: sa_orm.Query) -> list[tuple]:
    columns = [
        bookings_models.Booking.token.label("booking_token"),
        _truncate_milliseconds(bookings_models.Booking.dateUsed).label("booking_used_date"),
        bookings_models.Booking.quantity.label("booking_quantity"),
        bookings_models.Booking.priceCategoryLabel.label("booking_price_category_label"),
        bookings_models.Booking.amount.label("booking_amount"),
        offers_models.Offer.name.label("offer_name"),
        offerers_models.Venue.name.label("venue_name"),
        offerers_models.Venue.common_name.label("venue_common_name"),  # type: ignore[attr-defined]
        offerers_models.Venue.siret.label("venue_siret"),
        # See note about `amount` in `core/finance/models.py`.
        (-models.Pricing.amount).label("amount"),
        models.Pricing.standardRule.label("rule_name"),
        models.Pricing.customRuleId.label("rule_id"),
        models.Pricing.collectiveBookingId.label("collective_booking_id"),
        sa.cast(models.Invoice.date, sa.Date).label("invoice_date"),
        models.Invoice.reference.label("invoice_reference"),
        models.CashflowBatch.cutoff.label("cashflow_batch_cutoff"),
        models.CashflowBatch.label.label("cashflow_batch_label"),
        models.BankAccount.iban.label("iban"),
        models.BankAccount.label.label("bank_account_label"),
        sa.case((models.FinanceEvent.bookingFinanceIncidentId.is_(None), False), else_=True).label("is_incident"),
    ]
    query = (
        query.join(models.Pricing.event)
        .join(bookings_models.Booking.offerer)
        .join(bookings_models.Booking.stock)
        .join(offers_models.Stock.offer)
        .join(bookings_models.Booking.venue)
        .order_by(bookings_models.Booking.dateUsed.desc(), bookings_models.Booking.id.desc())
    )
    # TODO bdalbianco 06/06/2025 CLEAN_OA retirer offerer après la regul
    sub = sa.select(
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
            sa_func.coalesce(sub_offer.c.street, sub_venue.c.street, offerers_models.Offerer.street).label(
                "address_street"
            ),
            sa_func.coalesce(sub_offer.c.postalCode, sub_venue.c.postalCode, offerers_models.Offerer.postalCode).label(
                "address_postal_code"
            ),
            sa_func.coalesce(sub_offer.c.city, sub_venue.c.city, offerers_models.Offerer.city).label("address_city"),
        ]
    )
    query = (
        query.join(sub_venue, sub_venue.c.id == offerers_models.Venue.offererAddressId, isouter=True)
        .join(sub_offer, sub_offer.c.id == offers_models.Offer.offererAddressId, isouter=True)
        .with_entities(*columns)
    )
    return query.all()


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
        db.session.query(models.BankAccount)
        .filter(
            models.BankAccount.id == bank_account_id,
            models.BankAccount.offererId == offerer_id,
            models.BankAccount.status == models.BankAccountApplicationStatus.ACCEPTED,
        )
        .join(offerers_models.Offerer)
        .outerjoin(offerers_models.Venue, offerers_models.Venue.managingOffererId == offerers_models.Offerer.id)
        .outerjoin(
            offerers_models.VenuePricingPointLink,
            sa.and_(
                offerers_models.VenuePricingPointLink.venueId == offerers_models.Venue.id,
                offerers_models.VenuePricingPointLink.timespan.contains(datetime.datetime.utcnow()),
            ),
        )
        .outerjoin(
            offerers_models.VenueBankAccountLink,
            sa.and_(
                offerers_models.VenueBankAccountLink.venueId == offerers_models.Venue.id,
                offerers_models.VenueBankAccountLink.timespan.contains(datetime.datetime.utcnow()),
            ),
        )
        .options(
            sa_orm.contains_eager(models.BankAccount.offerer)
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
            sa_orm.contains_eager(models.BankAccount.offerer)
            .contains_eager(offerers_models.Offerer.managedVenues)
            .contains_eager(offerers_models.Venue.bankAccountLinks)
        )
        .one_or_none()
    )


def get_bank_accounts_query(user: users_models.User) -> sa_orm.Query:
    query = db.session.query(models.BankAccount).filter(
        models.BankAccount.status == models.BankAccountApplicationStatus.ACCEPTED
    )

    if not user.has_admin_role:
        query = query.join(
            offerers_models.UserOfferer, models.BankAccount.offererId == offerers_models.UserOfferer.offererId
        ).filter(offerers_models.UserOfferer.user == user, offerers_models.UserOfferer.isValidated)
    query = query.with_entities(models.BankAccount.id, models.BankAccount.label)
    return query


def convert_to_datetime(date: datetime.date) -> datetime.datetime:
    return date_utils.get_day_start(date, utils.ACCOUNTING_TIMEZONE).astimezone(pytz.utc)


def get_invoices_query(
    user: users_models.User,
    bank_account_id: int | None = None,
    offerer_id: int | None = None,
    date_from: datetime.date | None = None,
    date_until: datetime.date | None = None,
) -> sa_orm.Query:
    """Return invoices for the requested offerer.

    If given, ``date_from`` is **inclusive**, ``date_until`` is
    **exclusive**.
    """
    bank_account_subquery = db.session.query(models.BankAccount)

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

    invoices = db.session.query(models.Invoice).filter(
        models.Invoice.bankAccountId.in_(bank_account_subquery.with_entities(models.BankAccount.id))
    )

    if date_from:
        datetime_from = convert_to_datetime(date_from)
        invoices = invoices.filter(models.Invoice.date >= datetime_from)
    if date_until:
        datetime_until = convert_to_datetime(date_until)
        invoices = invoices.filter(models.Invoice.date < datetime_until)

    return invoices


def has_invoice(offerer_id: int) -> bool:
    return db.session.query(
        db.session.query(models.Invoice)
        .join(models.Invoice.bankAccount)
        .filter(models.BankAccount.offererId == offerer_id)
        .exists()
    ).scalar()
