import datetime
import typing

from flask_sqlalchemy import BaseQuery
import sqlalchemy as sa
from sqlalchemy import and_
from sqlalchemy import or_

from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import models as finance_models
from pcapi.core.offers import models as offers_models
from pcapi.core.users import models as users_models
from pcapi.routes.backoffice.bookings.forms import BaseBookingListForm
from pcapi.routes.backoffice.bookings.forms import BookingStatus
from pcapi.utils import date as date_utils
from pcapi.utils import email as email_utils


def get_bookings(
    base_query: BaseQuery,
    form: BaseBookingListForm,
    stock_class: type[educational_models.CollectiveStock | offers_models.Stock],
    booking_class: type[educational_models.CollectiveBooking | bookings_models.Booking],
    offer_class: type[educational_models.CollectiveOffer | offers_models.Offer],
    search_by_email: bool = False,
    id_filters: typing.Iterable[sa.sql.elements.ColumnElement] = (),
    name_filters: typing.Iterable[sa.sql.elements.ColumnElement] = (),
    or_filters: list | None = None,
) -> list[bookings_models.Booking] | list[educational_models.CollectiveBooking]:
    if or_filters is None:
        or_filters = []

    if form.from_to_date.data:
        from_datetime = date_utils.date_to_localized_datetime(form.from_to_date.from_date, datetime.datetime.min.time())
        if from_datetime:
            base_query = base_query.filter(booking_class.dateCreated >= from_datetime)

        to_datetime = date_utils.date_to_localized_datetime(form.from_to_date.to_date, datetime.datetime.max.time())
        if to_datetime:
            base_query = base_query.filter(booking_class.dateCreated <= to_datetime)

    event_from_datetime = date_utils.date_to_localized_datetime(form.event_from_date.data, datetime.datetime.min.time())
    if event_from_datetime and stock_class.beginningDatetime:
        base_query = base_query.filter(stock_class.beginningDatetime >= event_from_datetime)

    event_to_datetime = date_utils.date_to_localized_datetime(form.event_to_date.data, datetime.datetime.max.time())
    if event_to_datetime and stock_class.beginningDatetime:
        base_query = base_query.filter(stock_class.beginningDatetime <= event_to_datetime)

    if form.offerer.data:
        base_query = base_query.filter(booking_class.offererId.in_(form.offerer.data))

    if form.venue.data:
        base_query = base_query.filter(booking_class.venueId.in_(form.venue.data))

    if getattr(offer_class, "subcategoryId", None) and hasattr(form, "category") and form.category.data:
        base_query = base_query.filter(
            offer_class.subcategoryId.in_(
                subcategory.id
                for subcategory in subcategories.ALL_SUBCATEGORIES
                if subcategory.category.id in form.category.data
            )
        )
    elif hasattr(offer_class, "formats") and hasattr(form, "formats") and form.formats.data:
        base_query = base_query.filter(
            offer_class.formats.overlap(sa.dialects.postgresql.array((fmt for fmt in form.formats.data)))
        )

    if getattr(offer_class, "institution", None) and hasattr(form, "institution") and form.institution.data:
        base_query = base_query.filter(booking_class.educationalInstitutionId.in_(form.institution.data))

    if form.status.data:
        if booking_class is bookings_models.Booking:
            status_filters = []
            status_in = []
            for status in form.status.data:
                if status == BookingStatus.CONFIRMED.name:
                    status_filters.append(
                        and_(  # type: ignore[type-var]
                            booking_class.isConfirmed,
                            booking_class.status == BookingStatus.CONFIRMED.name,
                        )
                    )
                elif status == BookingStatus.BOOKED.name:
                    status_filters.append(
                        and_(
                            ~booking_class.isConfirmed,  # type: ignore[operator]
                            booking_class.status == BookingStatus.CONFIRMED.name,
                        )
                    )
                else:
                    status_in.append(status)

            if status_in:
                status_filters.append(booking_class.status.in_(status_in))  # type: ignore[arg-type]

            if len(status_filters) > 1:
                base_query = base_query.filter(or_(*status_filters))
            else:
                base_query = base_query.filter(status_filters[0])
        else:
            base_query = base_query.filter(booking_class.status.in_(form.status.data))

    if form.cashflow_batches.data:
        base_query = (
            base_query.join(finance_models.Pricing).join(finance_models.CashflowPricing).join(finance_models.Cashflow)
        )
        base_query = base_query.filter(finance_models.Cashflow.batchId.in_(form.cashflow_batches.data))

    if hasattr(form, "cancellation_reason") and form.cancellation_reason.data:
        base_query = base_query.filter(booking_class.cancellationReason.in_(form.cancellation_reason.data))

    if form.q.data:
        search_query = form.q.data

        if search_query.isnumeric() and id_filters:
            for id_filter in id_filters:
                or_filters.append(id_filter == int(search_query))
        elif search_by_email:
            sanitized_email = email_utils.sanitize_email(search_query)
            if email_utils.is_valid_email(sanitized_email):
                or_filters.append(users_models.User.email == sanitized_email)

        if not or_filters and name_filters:
            for name_filter in name_filters:
                or_filters.append(name_filter.ilike(f"%{search_query}%"))

        query = base_query.filter(or_filters[0])

        if len(or_filters) > 1:
            # Performance is really better than .filter(sa.or_(...)) when searching for an id in different tables
            query = query.union(*(base_query.filter(f) for f in or_filters[1:]))
    else:
        query = base_query

    return query.limit(form.limit.data + 1).all()
