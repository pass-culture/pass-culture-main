import datetime
import logging
import typing
from collections import defaultdict

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from flask_login import current_user

from pcapi.core.bookings import models as bookings_models
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import models as finance_models
from pcapi.core.mails.transactional.pro.fraudulent_booking_suspicion import send_fraudulent_booking_suspicion_email
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.routes.backoffice.bookings.forms import BaseBookingListForm
from pcapi.routes.backoffice.bookings.forms import BookingStatus
from pcapi.utils import date as date_utils
from pcapi.utils import email as email_utils
from pcapi.utils import string as string_utils


logger = logging.getLogger(__name__)


def get_filtered_booking_query(
    *,
    base_query: sa_orm.Query,
    form: BaseBookingListForm,
    stock_class: type[educational_models.CollectiveStock | offers_models.Stock],
    booking_class: type[educational_models.CollectiveBooking | bookings_models.Booking],
    search_by_email: bool = False,
    id_filters: typing.Iterable[sa_orm.InstrumentedAttribute] = (),
    name_filters: typing.Iterable[sa_orm.InstrumentedAttribute] = (),
    or_filters: list | None = None,
) -> sa_orm.Query:
    start_column = (
        educational_models.CollectiveStock.startDatetime
        if stock_class is educational_models.CollectiveStock
        else offers_models.Stock.beginningDatetime
    )

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
    if event_from_datetime and start_column:
        base_query = base_query.filter(start_column >= event_from_datetime)

    event_to_datetime = date_utils.date_to_localized_datetime(form.event_to_date.data, datetime.datetime.max.time())
    if event_to_datetime and start_column:
        base_query = base_query.filter(start_column <= event_to_datetime)

    if form.offerer.data:
        base_query = base_query.filter(booking_class.offererId.in_(form.offerer.data))

    if form.venue.data:
        base_query = base_query.filter(booking_class.venueId.in_(form.venue.data))

    if form.status.data:
        if booking_class is bookings_models.Booking:
            status_filters = []
            status_in = []
            for status in form.status.data:
                if status == BookingStatus.CONFIRMED.name:
                    status_filters.append(
                        sa.and_(
                            booking_class.isConfirmed,
                            booking_class.status == BookingStatus.CONFIRMED.name,
                        )
                    )
                elif status == BookingStatus.BOOKED.name:
                    status_filters.append(
                        sa.and_(
                            ~booking_class.isConfirmed,
                            booking_class.status == BookingStatus.CONFIRMED.name,
                        )
                    )
                else:
                    status_in.append(status)

            if status_in:
                status_filters.append(booking_class.status.in_(status_in))

            if len(status_filters) > 1:
                base_query = base_query.filter(sa.or_(*status_filters))
            else:
                base_query = base_query.filter(status_filters[0])
        else:
            base_query = base_query.filter(booking_class.status.in_(form.status.data))

    if form.cashflow_batches.data:
        base_query = (
            base_query.join(finance_models.Pricing).join(finance_models.CashflowPricing).join(finance_models.Cashflow)
        )
        base_query = base_query.filter(finance_models.Cashflow.batchId.in_(form.cashflow_batches.data))

    if form.has_incident.data and len(form.has_incident.data) == 1:
        if form.has_incident.data[0] == "true":
            base_query = base_query.filter(booking_class.validated_incident_id != None)
        else:
            base_query = base_query.filter(booking_class.validated_incident_id == None)

    if form.q.data:
        search_query = form.q.data

        if string_utils.is_numeric(search_query) and id_filters:
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

    return query.limit(form.limit.data + 1)


def tag_bookings_as_fraudulent(bookings_ids: list[int], send_emails: bool) -> None:
    bookings = (
        db.session.query(bookings_models.Booking)
        .options(
            sa_orm.joinedload(bookings_models.Booking.stock)
            .load_only()
            .joinedload(offers_models.Stock.offer)
            .load_only(offers_models.Offer.bookingEmail),
            sa_orm.joinedload(bookings_models.Booking.venue).load_only(offerers_models.Venue.bookingEmail),
        )
        .filter(
            bookings_models.Booking.id.in_(bookings_ids),
            bookings_models.Booking.fraudulentBookingTag == None,
        )
    )
    tokens_by_email = defaultdict(list)
    for booking in bookings:
        fraudulent_booking_tag = bookings_models.FraudulentBookingTag(booking=booking, author=current_user)
        if booking_email := booking.stock.offer.bookingEmail or booking.venue.bookingEmail:
            tokens_by_email[booking_email].append(booking.token)
        db.session.add(fraudulent_booking_tag)

    if send_emails:
        for pro_email in tokens_by_email:
            send_fraudulent_booking_suspicion_email(pro_email, tokens_by_email[pro_email])
    db.session.flush()
