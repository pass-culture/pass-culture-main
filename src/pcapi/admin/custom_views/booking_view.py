from flask import redirect
from flask import request
from flask.helpers import flash
from flask.helpers import url_for
from flask_admin import expose
from flask_admin.form import SecureForm
from sqlalchemy.orm import joinedload
from wtforms import HiddenField
from wtforms import StringField
from wtforms import validators

from pcapi.admin.base_configuration import BaseCustomAdminView
import pcapi.core.bookings.api as bookings_api
from pcapi.core.bookings.models import Booking
from pcapi.core.offers.models import Stock
from pcapi.domain.client_exceptions import ClientError
from pcapi.models.api_errors import ApiErrors


class SearchForm(SecureForm):
    token = StringField(
        "Code de contremarque",
        validators=[validators.DataRequired()],
        description='Par exemple "ABC123"',
    )


class MarkAsUsedForm(SecureForm):
    booking_id = HiddenField()


class BookingView(BaseCustomAdminView):
    @expose("/", methods=["GET", "POST"])
    def search(self):
        search_form = SearchForm(request.form)
        mark_as_used_form = None

        # Get booking by token from POSTed search; or by id from GET
        # on redirect (because we'd rather not see the token in the
        # URL).
        booking = None
        if request.method == "POST":
            if search_form.validate():
                booking = (
                    Booking.query.filter_by(token=search_form.token.data)
                    .options(joinedload(Booking.user))
                    .options(joinedload(Booking.stock).joinedload(Stock.offer))
                    .first()
                )
                if not booking:
                    flash("Aucune réservation n'existe avec ce code de contremarque.", "error")
                elif booking.isCancelled:
                    mark_as_used_form = MarkAsUsedForm(booking_id=booking.id)
        elif "id" in request.args:
            booking = (
                Booking.query.filter_by(id=request.args["id"])
                .options(joinedload(Booking.user))
                .options(joinedload(Booking.stock).joinedload(Stock.offer))
                .first()
            )

        return self.render(
            "admin/booking.html", search_form=search_form, mark_as_used_form=mark_as_used_form, booking=booking
        )

    @expose("/mark-as-used", methods=["POST"])
    def uncancel_and_mark_as_used(self):
        form = MarkAsUsedForm(request.form)
        if not form.validate():
            flash(f"Une erreur est survenue : {form.errors}", "error")
            return redirect(url_for(".search"))

        booking = Booking.query.get(form.booking_id.data)
        booking_url = f"{url_for('.search')}?id={booking.id}"

        if not booking.isCancelled:
            flash("Cette réservation n'est pas annulée, elle ne peut pas être validée via ce formulaire.", "error")
            return redirect(booking_url)

        try:
            bookings_api.mark_as_used(booking, uncancel=True)
        except Exception as exc:  # pylint: disable=broad-except
            if isinstance(exc, (ClientError, ApiErrors)):
                err = list(exc.errors.values())[0][0]
            else:
                err = str(exc)
            flash(f"L'opération a échoué : {err}", "error")
        else:
            flash("La réservation a été dés-annulée et marquée comme utilisée.", "info")
        return redirect(booking_url)
