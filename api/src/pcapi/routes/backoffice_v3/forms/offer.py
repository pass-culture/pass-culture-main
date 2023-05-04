import enum
import re

from flask_wtf import FlaskForm
import wtforms

from pcapi.core.categories import categories
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.routes.backoffice_v3 import utils as bo_utils

from . import constants
from . import fields
from . import utils
from .. import filters


class OfferSearchColumn(enum.Enum):
    ALL = "Tout"
    ID = "ID de l'offre"
    NAME = "Nom de l'offre"
    ISBN = "ISBN"
    VISA = "Visa d'exploitation"


class GetOffersListForm(FlaskForm):
    class Meta:
        csrf = False

    q = fields.PCOptSearchField("ID de l'offre ou liste d'ID, nom, ISBN, visa d'exploitation")
    where = fields.PCSelectField(
        "Chercher dans",
        choices=utils.choices_from_enum(OfferSearchColumn),
        default=OfferSearchColumn.ALL.name,
        validators=(wtforms.validators.Optional(),),
    )
    criteria = fields.PCTomSelectField(
        "Tags", multiple=True, choices=[], validate_choice=False, endpoint="backoffice_v3_web.autocomplete_criteria"
    )
    category = fields.PCSelectMultipleField(
        "Catégories", choices=utils.choices_from_enum(categories.CategoryIdLabelEnum)
    )
    department = fields.PCSelectMultipleField("Départements", choices=constants.area_choices)
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

    def validate_q(self, q: fields.PCOptSearchField) -> fields.PCOptSearchField:
        if q.data:
            if self.where.data == OfferSearchColumn.ID.name and not re.match(r"^[\d\s,;]+$", q.data):
                raise wtforms.validators.ValidationError("La recherche ne correspond pas à un ID ou une liste d'ID")
            if self.where.data == OfferSearchColumn.ISBN.name and not bo_utils.is_isbn_valid(q.data):
                raise wtforms.validators.ValidationError("La recherche ne correspond pas au format d'un ISBN")
            if self.where.data == OfferSearchColumn.VISA.name and not bo_utils.is_visa_valid(q.data):
                raise wtforms.validators.ValidationError("La recherche ne correspond pas au format d'un visa")
        return q

    def is_empty(self) -> bool:
        # 'where', 'only_validated_offerers', 'sort' must be combined with other filters
        return not any(
            (
                self.q.data,
                self.criteria.data,
                self.category.data,
                self.department.data,
                self.venue.data,
                self.offerer.data,
                self.status.data,
                self.from_date.data,
                self.to_date.data,
            )
        )


class EditOfferForm(FlaskForm):
    criteria = fields.PCTomSelectField(
        "Tags", multiple=True, choices=[], validate_choice=False, endpoint="backoffice_v3_web.autocomplete_criteria"
    )
    rankingWeight = fields.PCOptIntegerField("Pondération")


class BatchEditOfferForm(EditOfferForm):
    object_ids = wtforms.HiddenField("Identifiants à traiter")


class BatchEmptyOfferForm(FlaskForm):
    object_ids = wtforms.HiddenField("Identifiants à traiter")
