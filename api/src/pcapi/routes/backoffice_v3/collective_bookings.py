from functools import partial

from flask import render_template
from flask import request
from flask import url_for

from pcapi.core.educational import models as educational_models
from pcapi.core.permissions import models as perm_models

from . import search_utils
from . import utils
from .forms import collective_booking as collective_booking_forms


collective_bookings_blueprint = utils.child_backoffice_blueprint(
    "collective_bookings",
    __name__,
    url_prefix="/collective_bookings",
    permission=perm_models.Permissions.MANAGE_BOOKINGS,
)


@collective_bookings_blueprint.route("", methods=["GET"])
def list_collective_bookings() -> utils.BackofficeResponse:
    form = collective_booking_forms.GetCollectiveBookingListForm(request.args)
    if not form.validate():
        return render_template("collective_bookings/list.html", isEAC=True, rows=[], form=form), 400

    # This query only returns a single row, but will receive other possible criteria in the near future
    bookings = educational_models.CollectiveBooking.query.filter(
        educational_models.CollectiveBooking.id == form.q.data
    ).order_by(educational_models.CollectiveBooking.dateCreated.desc())

    paginated_bookings = bookings.paginate(
        page=int(form.data["page"]),
        per_page=int(form.data["per_page"]),
    )

    next_page = partial(url_for, ".list_collective_bookings", **form.data)
    next_pages_urls = search_utils.pagination_links(next_page, int(form.data["page"]), paginated_bookings.pages)

    form.page.data = 1  # Reset to first page when form is submitted ("Appliquer" clicked)

    return render_template(
        "collective_bookings/list.html",
        rows=paginated_bookings,
        form=form,
        next_pages_urls=next_pages_urls,
    )
