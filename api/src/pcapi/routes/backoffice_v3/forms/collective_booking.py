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
    category = fields.PCSelectMultipleField(
        "Catégories", choices=utils.choices_from_enum(categories.CategoryIdLabelEnum)
    )
    status = fields.PCSelectMultipleField(
        "États", choices=utils.choices_from_enum(CollectiveBookingStatus, formatter=filters.format_booking_status)
    )
    from_date = fields.PCDateField("À partir du", validators=(wtforms.validators.Optional(),))
    to_date = fields.PCDateField("Jusqu'au", validators=(wtforms.validators.Optional(),))
    page = wtforms.HiddenField("page", default="1", validators=(wtforms.validators.Optional(),))
    per_page = fields.PCSelectField(
        "Par page",
        choices=(("10", "10"), ("25", "25"), ("50", "50"), ("100", "100")),
        default="100",
        validators=(wtforms.validators.Optional(),),
    )

    def validate_q(self, q: fields.PCOptSearchField) -> fields.PCOptSearchField:
        if q.data:
            q.data = q.data.strip()
        return q
