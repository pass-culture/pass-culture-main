import datetime
import enum
import typing

from flask_wtf import FlaskForm
import wtforms

from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import categories
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.educational import models as educational_models
from pcapi.routes.backoffice import filters
from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import utils
from pcapi.routes.backoffice.forms.empty import BatchForm


class BookingStatus(enum.Enum):
    BOOKED = "Réservée"
    CONFIRMED = "Confirmée"
    USED = "Validée"
    CANCELLED = "Annulée"
    REIMBURSED = "Remboursée"


# same keys as educational_models.CollectiveBookingStatus but with different values to display the status in french
class CollectiveBookingStatus(enum.Enum):
    PENDING = "Pré-réservée"
    CONFIRMED = "Confirmée"
    USED = "Validée"
    CANCELLED = "Annulée"
    REIMBURSED = "Remboursée"


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
    event_from_date = fields.PCDateField("Évènement du", validators=(wtforms.validators.Optional(),))
    event_to_date = fields.PCDateField("Évènement jusqu'au", validators=(wtforms.validators.Optional(),))
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
                self.status.data,
                self.from_to_date.data,
                self.event_from_date.data,
                self.event_to_date.data,
                self.cashflow_batches.data,
            )
        )

    @property
    def is_single_venue_with_optional_dates(self) -> bool:
        return len(self.venue.data) == 1 and not any(
            (
                self.q.data,
                self.offerer.data,
                self.status.data,
                self.event_from_date.data,
                self.event_to_date.data,
                self.cashflow_batches.data,
            )
        )

    @property
    def pro_view_args(self) -> str:
        output = ""
        if self.is_single_venue_with_optional_dates:
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

    venue = fields.PCIntegerField("Lieu")
    from_to_date = fields.PCDateRangeField(
        "Créées entre",
        validators=(wtforms.validators.Optional(),),
        max_date=datetime.date.today(),
        reset_to_blank=True,
    )


class GetCollectiveBookingListForm(BaseBookingListForm):
    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self.q.label.text = "ID réservation collective ou ID offre"
        self.status.choices = utils.choices_from_enum(CollectiveBookingStatus)

        self._fields.move_to_end("offerer")
        self._fields.move_to_end("venue")
        self._fields.move_to_end("institution")
        self._fields.move_to_end("formats")
        self._fields.move_to_end("status")
        self._fields.move_to_end("cashflow_batches")

    def is_empty(self) -> bool:
        return super().is_empty() and not self.institution.data and not self.formats.data

    @property
    def is_single_venue_with_optional_dates(self) -> bool:
        return super().is_single_venue_with_optional_dates and not self.formats.data

    institution = fields.PCTomSelectField(
        "Établissement",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_institutions",
    )
    formats = fields.PCSelectMultipleField(
        "Formats", choices=utils.choices_from_enum(subcategories.EacFormat), field_list_compatibility=True
    )


class GetIndividualBookingListForm(BaseBookingListForm):
    category = fields.PCSelectMultipleField(
        "Catégories", choices=utils.choices_from_enum(categories.CategoryIdLabelEnum)
    )
    cancellation_reason = fields.PCSelectMultipleField(
        "Raison d'annulation",
        choices=utils.choices_from_enum(
            bookings_models.BookingCancellationReasons, formatter=filters.format_booking_cancellation_reason
        ),
    )
    deposit = fields.PCSelectField(
        "État du crédit",
        choices=(("active", "Actif"), ("expired", "Expiré")),
        default=None,
        validators=(wtforms.validators.Optional(),),
    )

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self.q.label.text = "Code contremarque ou liste, nom d'offre, email ou ID (offre, jeune ou résa)"
        self.status.choices = utils.choices_from_enum(BookingStatus)

        self._fields.move_to_end("deposit")
        self._fields.move_to_end("limit")
        self._fields.move_to_end("offerer")
        self._fields.move_to_end("venue")
        self._fields.move_to_end("category")
        self._fields.move_to_end("status")
        self._fields.move_to_end("cancellation_reason")
        self._fields.move_to_end("cashflow_batches")

    def is_empty(self) -> bool:
        return (
            super().is_empty()
            and not self.category.data
            and not self.cancellation_reason.data
            and not self.deposit.data
        )

    @property
    def is_single_venue_with_optional_dates(self) -> bool:
        return (
            super().is_single_venue_with_optional_dates
            and not self.category.data
            and not self.cancellation_reason
            and not self.deposit
        )


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
