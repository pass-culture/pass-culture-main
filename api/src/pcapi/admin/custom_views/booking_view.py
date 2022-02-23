from flask import redirect
from flask import request
from flask.helpers import flash
from flask.helpers import url_for
from flask_admin import expose
from flask_admin.form import SecureForm
from sqlalchemy.orm import joinedload
import werkzeug
from wtforms import StringField
from wtforms import validators

from pcapi.admin.base_configuration import BaseCustomAdminView
from pcapi.core.bookings import models as booking_models
import pcapi.core.bookings.api as bookings_api
from pcapi.core.educational.models import EducationalBooking
import pcapi.core.finance.repository as finance_repository
from pcapi.core.offers.models import Stock
from pcapi.domain.client_exceptions import ClientError
from pcapi.models.api_errors import ApiErrors


def _get_exception_message(exc: Exception) -> str:
    if isinstance(exc, (ClientError, ApiErrors)):
        return list(exc.errors.values())[0][0]
    return str(exc)


class SearchForm(SecureForm):
    token = StringField(
        "Code de contremarque",
        validators=[validators.DataRequired()],
        description='Par exemple "ABC123"',
    )


class MarkAsUsedForm(SecureForm):
    pass


class CancelForm(SecureForm):
    pass


class BookingView(BaseCustomAdminView):
    @expose("/", methods=["GET", "POST"])
    def search(self) -> werkzeug.Response:
        search_form = SearchForm(request.form)
        mark_as_used_form = None
        cancel_form = None

        # Get booking by token from POSTed search; or by id from GET
        # on redirect (because we'd rather not see the token in the
        # URL).
        booking = None
        if request.method == "POST":
            if search_form.validate():
                token = search_form.token.data.strip().upper()
                booking = (
                    booking_models.Booking.query.filter_by(token=token)
                    .options(
                        joinedload(booking_models.Booking.individualBooking).joinedload(
                            booking_models.IndividualBooking.user
                        )
                    )
                    .options(
                        joinedload(booking_models.Booking.educationalBooking).joinedload(
                            EducationalBooking.educationalRedactor
                        )
                    )
                    .options(joinedload(booking_models.Booking.stock).joinedload(Stock.offer))
                    .one_or_none()
                )
                if not booking:
                    flash("Aucune réservation n'existe avec ce code de contremarque.", "error")
                elif booking.status == booking_models.BookingStatus.CANCELLED:
                    mark_as_used_form = MarkAsUsedForm(booking_id=booking.id)
                elif (
                    booking.educationalBookingId is not None
                    and booking.status != booking_models.BookingStatus.CANCELLED
                ):
                    flash("Vous ne pouvez pas annuler une réservation associée à une offre collective")
                elif not finance_repository.has_reimbursement(booking):
                    cancel_form = CancelForm(booking_id=booking.id)
        elif "id" in request.args:
            booking = (
                booking_models.Booking.query.options(
                    joinedload(booking_models.Booking.individualBooking).joinedload(
                        booking_models.IndividualBooking.user
                    )
                )
                .options(joinedload(booking_models.Booking.stock).joinedload(Stock.offer))
                .get(request.args["id"])
            )

        return self.render(
            "admin/booking.html",
            search_form=search_form,
            mark_as_used_form=mark_as_used_form,
            booking=booking,
            cancel_form=cancel_form,
        )

    @expose("/mark-as-used/<int:booking_id>", methods=["POST"])
    def uncancel_and_mark_as_used(self, booking_id: int) -> werkzeug.Response:
        booking = booking_models.Booking.query.get_or_404(booking_id)
        booking_url = url_for(".search", id=booking.id)

        if booking.status != booking_models.BookingStatus.CANCELLED:
            flash("Cette réservation n'est pas annulée, elle ne peut pas être validée via ce formulaire.", "error")
            return redirect(booking_url)

        try:
            bookings_api.mark_as_used_with_uncancelling(booking)
        except Exception as exc:  # pylint: disable=broad-except
            flash(f"L'opération a échoué : {_get_exception_message(exc)}", "error")
        else:
            flash("La réservation a été dés-annulée et marquée comme utilisée.", "info")
        return redirect(booking_url)

    @expose("/cancel/<int:booking_id>", methods=["POST"])
    def cancel(self, booking_id: int) -> werkzeug.Response:
        """
        Parse form, cancel booking and then send and email to the booking's
        offerer
        """
        booking = booking_models.Booking.query.get_or_404(booking_id)
        booking_url = url_for(".search", id=booking.id)

        try:
            bookings_api.mark_as_cancelled(booking)
        except Exception as exc:  # pylint: disable=broad-except
            flash(f"L'opération a échoué : {_get_exception_message(exc)}", "error")
        else:
            flash("La réservation a été marquée comme annulée", "info")
        return redirect(booking_url)
