import datetime
import typing

from flask_wtf import FlaskForm
import wtforms

from pcapi.core.bookings import models as bookings_models
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories import categories
from pcapi.core.educational import models as educational_models
from pcapi.routes.backoffice import filters
from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import utils
from pcapi.routes.backoffice.forms.empty import BatchForm


class BaseBookingListForm(FlaskForm):
    class Meta:
        csrf = False

    q = fields.PCOptSearchField()
    from_to_date = fields.PCDateRangeField(
        "Créées entre",
        validators=(wtforms.validators.Optional(),),
        max_date=datetime.date.today(),
        reset_to_blank=True,
    )
    event_from_date = fields.PCDateField("Événement du", validators=(wtforms.validators.Optional(),))
    event_to_date = fields.PCDateField("Événement jusqu'au", validators=(wtforms.validators.Optional(),))
    limit = fields.PCSelectField(
        "Nombre maximum",
        choices=((20, "20"), (100, "100"), (500, "500"), (1000, "1000")),
        default="100",
        coerce=int,
        validators=(wtforms.validators.Optional(),),
    )
    offerer = fields.PCTomSelectField(
        "Structures",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_offerers",
    )
    venue = fields.PCTomSelectField(
        "Lieux", multiple=True, choices=[], validate_choice=False, endpoint="backoffice_web.autocomplete_venues"
    )
    category = fields.PCSelectMultipleField(
        "Catégories", choices=utils.choices_from_enum(categories.CategoryIdLabelEnum)
    )
    status = fields.PCSelectMultipleField("États")
    cashflow_batches = fields.PCTomSelectField(
        "Virements",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_cashflow_batches",
    )

    def is_empty(self) -> bool:
        return not any(
            (
                self.q.data,
                self.offerer.data,
                self.venue.data,
                self.category.data,
                self.status.data,
                self.from_to_date.data,
                self.event_from_date.data,
                self.event_to_date.data,
                self.cashflow_batches.data,
            )
        )

    @property
    def pro_view_args(self) -> str:
        output = ""
        if len(self.venue.data) == 1 and not any(
            (
                self.q.data,
                self.offerer.data,
                self.category.data,
                self.status.data,
                self.event_from_date.data,
                self.event_to_date.data,
                self.cashflow_batches.data,
            )
        ):
            from_date = self.from_to_date.data[0].date() if self.from_to_date.data else datetime.date.today()
            to_date = (
                self.from_to_date.data[1].date() if self.from_to_date.data else from_date - datetime.timedelta(days=30)
            )
            output = (
                f"?page=1&bookingBeginningDate={str(from_date)}&bookingEndingDate={str(to_date)}&bookingStatusFilter=booked"
                f"&offerType=all&offerVenueId={self.venue.data[0]}"
            )
        return output


class GetDownloadBookingsForm(FlaskForm):
    class Meta:
        csrf = False

    venue = fields.PCIntegerField("Lieux")
    from_to_date = fields.PCDateRangeField(
        "Créées entre",
        validators=(wtforms.validators.Optional(),),
        max_date=datetime.date.today(),
        reset_to_blank=True,
    )


class GetCollectiveBookingListForm(BaseBookingListForm):
    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self.q.label.text = "ID réservation collective, ID offre, Nom ou ID de l'établissement"
        self.status.choices = utils.choices_from_enum(
            educational_models.CollectiveBookingStatus, formatter=filters.format_booking_status
        )


class GetIndividualBookingListForm(BaseBookingListForm):
    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self.q.label.text = "Code contremarque ou liste, Nom, email ou ID (offre, bénéficiaire ou résa)"
        self.status.choices = utils.choices_from_enum(BookingStatus, formatter=filters.format_booking_status)


class CancelCollectiveBookingForm(FlaskForm):
    reason = fields.PCSelectWithPlaceholderValueField(
        "Raison",
        choices=utils.choices_from_enum(
            educational_models.CollectiveBookingCancellationReasons,
            formatter=filters.format_booking_cancellation_reason,
        ),
    )


class CancelIndividualBookingForm(FlaskForm):
    reason = fields.PCSelectWithPlaceholderValueField(
        "Raison",
        choices=utils.choices_from_enum(
            bookings_models.BookingCancellationReasons, formatter=filters.format_booking_cancellation_reason
        ),
    )


class BatchCancelIndividualBookingsForm(BatchForm, CancelIndividualBookingForm):
    pass
