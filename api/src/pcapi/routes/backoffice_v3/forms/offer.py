import enum
from functools import partial
import re
import typing

from flask import url_for
from flask_wtf import FlaskForm
import wtforms

from pcapi.core.categories import categories
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.routes.backoffice_v3 import utils as bo_utils

from . import constants
from . import fields
from . import utils
from .. import filters
from ..forms import empty as empty_forms


class OfferSearchColumn(enum.Enum):
    ALL = "Tout"
    ID = "ID de l'offre"
    NAME = "Nom de l'offre"
    ISBN = "ISBN"
    VISA = "Visa d'exploitation"


class OfferMixinForm(utils.PCForm):
    class Meta:
        csrf = False

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
    order = wtforms.HiddenField(
        "order", default="asc", validators=(wtforms.validators.Optional(), wtforms.validators.AnyOf(("asc", "desc")))
    )

    def is_empty(self) -> bool:
        # 'only_validated_offerers', 'sort' must be combined with other filters
        return not any(
            (
                self.category.data,
                self.venue.data,
                self.offerer.data,
                self.status.data,
                self.from_date.data,
                self.to_date.data,
            )
        )

    def get_sort_link(self, endpoint: str) -> str:
        form_url = partial(url_for, endpoint, **self.raw_data)
        return form_url(
            sort="dateCreated", order="asc" if self.sort.data == "dateCreated" and self.order.data == "desc" else "desc"
        )


class GetOffersListForm(OfferMixinForm):
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
    department = fields.PCSelectMultipleField("Départements", choices=constants.area_choices)

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self._fields.move_to_end("where", last=False)
        self._fields.move_to_end("q", last=False)
        self._fields.move_to_end("criteria")
        self._fields.move_to_end("category")
        self._fields.move_to_end("department")
        self._fields.move_to_end("offerer")
        self._fields.move_to_end("venue")
        self._fields.move_to_end("status")

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
        return super().is_empty() and not any(
            (
                self.q.data,
                self.criteria.data,
                self.department.data,
            )
        )


class GetCollectiveOffersListForm(OfferMixinForm):
    q = fields.PCOptSearchField("ID, nom de l'offre")

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self._fields.move_to_end("q", last=False)

    def is_empty(self) -> bool:
        return super().is_empty() and not self.q.data


class GetCollectiveOfferTemplatesListForm(GetCollectiveOffersListForm):
    pass


class EditOfferForm(FlaskForm):
    criteria = fields.PCTomSelectField(
        "Tags", multiple=True, choices=[], validate_choice=False, endpoint="backoffice_v3_web.autocomplete_criteria"
    )
    rankingWeight = fields.PCOptIntegerField("Pondération")


class BatchEditOfferForm(empty_forms.BatchForm, EditOfferForm):
    pass
