from functools import partial

from flask import render_template
from flask import request
from flask import url_for

from pcapi.core.bookings import models as bookings_models
from pcapi.core.permissions import models as perm_models

from . import search_utils
from . import utils
from .forms import individual_booking as individual_booking_forms


individual_bookings_blueprint = utils.child_backoffice_blueprint(
    "individual_bookings",
    __name__,
    url_prefix="/individual_bookings",
    permission=perm_models.Permissions.MANAGE_BOOKINGS,
)


@individual_bookings_blueprint.route("", methods=["GET"])
def list_individual_bookings() -> utils.BackofficeResponse:
    form = individual_booking_forms.GetIndividualBookingListForm(request.args)
    if not form.validate():
        return render_template("individual_bookings/list.html", rows=[], form=form), 400

    bookings = bookings_models.Booking.query.filter(bookings_models.Booking.token == form.q.data).order_by(
        bookings_models.Booking.dateCreated.desc()
    )

    paginated_bookings = bookings.paginate(
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
