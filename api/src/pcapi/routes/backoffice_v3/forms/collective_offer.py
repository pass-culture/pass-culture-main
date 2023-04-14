from flask_wtf import FlaskForm
import wtforms

from pcapi.core.categories import categories
from pcapi.models.offer_mixin import OfferValidationStatus

from . import fields
from . import utils
from .. import filters


class GetCollectiveOffersListForm(FlaskForm):
    class Meta:
        csrf = False

    q = fields.PCOptSearchField("ID, nom de l'offre")
    category = fields.PCSelectMultipleField(
        "Catégories", choices=utils.choices_from_enum(categories.CategoryIdLabelEnum)
    )
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
    status = fields.PCSelectMultipleField(
        "États",
        choices=utils.choices_from_enum(OfferValidationStatus, formatter=filters.format_offer_validation_status),
    )
    from_date = fields.PCDateField("Créées à partir du", validators=(wtforms.validators.Optional(),))
    to_date = fields.PCDateField("Jusqu'au", validators=(wtforms.validators.Optional(),))
    limit = fields.PCSelectField(
        "Nombre maximum",
        choices=((100, "100"), (500, "500"), (1000, "1000"), (3000, "3000")),
        default="100",
        coerce=int,
        validators=(wtforms.validators.Optional(),),
    )
    only_validated_offerers = fields.PCSwitchBooleanField("Uniquement les offres des structures validées")
    sort = wtforms.HiddenField(
        "sort", validators=(wtforms.validators.Optional(), wtforms.validators.AnyOf(("id", "dateCreated")))
    )

    def is_empty(self) -> bool:
        # 'only_validated_offerers', 'sort' must be combined with other filters
        return not any(
            (
                self.q.data,
                self.category.data,
                self.venue.data,
                self.offerer.data,
                self.status.data,
                self.from_date.data,
                self.to_date.data,
            )
        )
