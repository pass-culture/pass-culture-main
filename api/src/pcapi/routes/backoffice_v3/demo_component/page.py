from flask import render_template

from .. import blueprint
from .. import utils
from pcapi.core.bookings import models as bookings_models


@blueprint.backoffice_v3_web.route("/demo/component", methods=["GET"])
def demo_component() -> utils.BackofficeResponse:

    bookings = bookings_models.Booking.query.limit(100).all()

    return render_template(
        "demo_component/page.html",
        bookings = bookings
    )
