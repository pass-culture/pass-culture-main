from flask_wtf import FlaskForm
import wtforms

from pcapi.core.categories import categories
from pcapi.core.educational.models import CollectiveBookingStatus

from . import fields
from . import utils
from .. import filters


class GetCollectiveBookingListForm(FlaskForm):
    class Meta:
        csrf = False

    q = fields.PCOptSearchField("ID réservation collective, ID offre, Nom ou ID de l'établissement")
    offerer = fields.PCAutocompleteSelectMultipleField(
        "Structures", choices=[], validate_choice=False, endpoint="backoffice_v3_web.autocomplete_offerers"
    )
    venue = fields.PCAutocompleteSelectMultipleField(
        "Lieux", choices=[], validate_choice=False, endpoint="backoffice_v3_web.autocomplete_venues"
    )
    category = fields.PCSelectMultipleField(
        "Catégories", choices=utils.choices_from_enum(categories.CategoryIdLabelEnum)
    )
    status = fields.PCSelectMultipleField(
        "États", choices=utils.choices_from_enum(CollectiveBookingStatus, formatter=filters.format_booking_status)
    )
    from_date = fields.PCDateField("À partir du", validators=(wtforms.validators.Optional(),))
    to_date = fields.PCDateField("Jusqu'au", validators=(wtforms.validators.Optional(),))
    limit = fields.PCSelectField(
        "Nombre maximum",
        choices=((20, "20"), (100, "100"), (500, "500"), (1000, "1000")),
        default="100",
        coerce=int,
        validators=(wtforms.validators.Optional(),),
    )

    def validate_q(self, q: fields.PCOptSearchField) -> fields.PCOptSearchField:
        if q.data:
            q.data = q.data.strip()
        return q

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
            )
        )
