from flask_wtf import FlaskForm
import wtforms

from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories import categories

from . import fields
from . import utils
from .. import filters


class GetIndividualBookingListForm(FlaskForm):
    class Meta:
        csrf = False

    q = fields.PCOptSearchField("Code contremarque, ID offre, Nom, email ou ID du bénéficiaire")
    offerer = fields.PCTomSelectField(
        "Structures",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_v3_web.autocomplete_offerers",
    )
    venue = fields.PCTomSelectField(
        "Lieux", multiple=True, choices=[], validate_choice=False, endpoint="backoffice_v3_web.autocomplete_venues"
    )
    category = fields.PCSelectMultipleField(
        "Catégories", choices=utils.choices_from_enum(categories.CategoryIdLabelEnum)
    )
    status = fields.PCSelectMultipleField(
        "États", choices=utils.choices_from_enum(BookingStatus, formatter=filters.format_booking_status)
    )
    cashflow_batches = fields.PCTomSelectField(
        "Virements",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_v3_web.autocomplete_cashflow_batches",
    )
    from_date = fields.PCDateField("Créées à partir du", validators=(wtforms.validators.Optional(),))
    to_date = fields.PCDateField("Créées jusqu'au", validators=(wtforms.validators.Optional(),))
    event_from_date = fields.PCDateField("Événement du", validators=(wtforms.validators.Optional(),))
    event_to_date = fields.PCDateField("Événement jusqu'au", validators=(wtforms.validators.Optional(),))
    limit = fields.PCSelectField(
        "Nombre maximum",
        choices=((20, "20"), (100, "100"), (500, "500"), (1000, "1000")),
        default="100",
        coerce=int,
        validators=(wtforms.validators.Optional(),),
    )

    def is_empty(self) -> bool:
        return not any(
            (
                self.q.data,
                self.offerer.data,
                self.venue.data,
                self.category.data,
                self.status.data,
                self.from_date.data,
                self.to_date.data,
                self.event_from_date.data,
                self.event_to_date.data,
                self.cashflow_batches.data,
            )
        )
