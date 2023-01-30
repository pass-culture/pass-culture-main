import datetime
from functools import partial

from flask import render_template
from flask import request
from flask import url_for
import sqlalchemy as sa

from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import subcategories_v2
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import models as users_models
from pcapi.utils import date as date_utils
from pcapi.utils.clean_accents import clean_accents

from . import search_utils
from . import utils
from .forms import individual_booking as individual_booking_forms


individual_bookings_blueprint = utils.child_backoffice_blueprint(
    "individual_bookings",
    __name__,
    url_prefix="/individual-bookings",
    permission=perm_models.Permissions.MANAGE_BOOKINGS,
)


def _get_individual_bookings(form: individual_booking_forms.GetIndividualBookingListForm) -> sa.orm.Query:
    query = (
        bookings_models.Booking.query.outerjoin(offers_models.Stock)
        .outerjoin(offers_models.Offer)
        .outerjoin(users_models.User, bookings_models.Booking.user)
        .options(
            sa.orm.joinedload(bookings_models.Booking.stock)
            .load_only(offers_models.Stock.quantity, offers_models.Stock.offerId)
            .joinedload(offers_models.Stock.offer)
            .load_only(
                offers_models.Offer.id,
                offers_models.Offer.name,
                offers_models.Offer.subcategoryId,
            ),
            sa.orm.joinedload(bookings_models.Booking.user).load_only(
                users_models.User.id, users_models.User.firstName, users_models.User.lastName
            ),
        )
    )

    if form.q.data:
        search_query = form.q.data

        if search_query.isnumeric():
            query = query.filter(
                sa.or_(
                    bookings_models.Booking.token == search_query,
                    offers_models.Offer.id == search_query,
                    users_models.User.id == search_query,
                )
            )
        elif len(search_query) == 6:
            query = query.filter(bookings_models.Booking.token == search_query)
        else:
            name = search_query.replace(" ", "%").replace("-", "%")
            name = clean_accents(name)
            query = query.filter(
                sa.func.unaccent(sa.func.concat(users_models.User.firstName, " ", users_models.User.lastName)).ilike(
                    f"%{name}%"
                ),
            )

    if form.from_date.data:
        from_datetime = date_utils.date_to_localized_datetime(form.from_date.data, datetime.datetime.min.time())
        query = query.filter(bookings_models.Booking.dateCreated >= from_datetime)

    if form.to_date.data:
        to_datetime = date_utils.date_to_localized_datetime(form.to_date.data, datetime.datetime.max.time())
        query = query.filter(bookings_models.Booking.dateCreated <= to_datetime)

    if form.category.data:
        query = query.filter(
            offers_models.Offer.subcategoryId.in_(
                subcategory.id
                for subcategory in subcategories_v2.ALL_SUBCATEGORIES
                if subcategory.category.id in form.category.data
            )
        )

    if form.status.data:
        query = query.filter(bookings_models.Booking.status.in_(form.status.data))

    return query.order_by(bookings_models.Booking.dateCreated.desc())


@individual_bookings_blueprint.route("", methods=["GET"])
def list_individual_bookings() -> utils.BackofficeResponse:
    form = individual_booking_forms.GetIndividualBookingListForm(request.args)
    if not form.validate():
        return render_template("individual_bookings/list.html", rows=[], form=form), 400

    if (
        not form.q.data
        and not form.category.data
        and not form.status.data
        and not form.from_date.data
        and not form.to_date.data
    ):
        # Empty results when no filter is set
        return render_template("individual_bookings/list.html", rows=[], form=form)

    bookings = _get_individual_bookings(form)

    paginated_bookings = bookings.paginate(  # type: ignore [attr-defined]
        page=int(form.data["page"]),
        per_page=int(form.data["per_page"]),
    )

    next_page = partial(url_for, ".list_individual_bookings", **form.data)
    next_pages_urls = search_utils.pagination_links(next_page, int(form.data["page"]), paginated_bookings.pages)

    form.page.data = 1  # Reset to first page when form is submitted ("Appliquer" clicked)

    return render_template(
        "individual_bookings/list.html",
        rows=paginated_bookings,
        form=form,
        next_pages_urls=next_pages_urls,
    )
