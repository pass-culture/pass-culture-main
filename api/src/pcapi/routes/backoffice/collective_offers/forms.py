import decimal
import typing

from flask_wtf import FlaskForm
import wtforms

from pcapi.core.categories import categories
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.routes.backoffice import filters
from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import utils
from pcapi.routes.backoffice.offers.forms import GetOffersBaseFields


class EditCollectiveOfferPrice(FlaskForm):
    class Meta:
        locales = ["fr_FR", "fr"]

    price = fields.PCDecimalField(
        "Prix",
        use_locale=True,
        validators=[
            wtforms.validators.InputRequired("Information obligatoire"),
            wtforms.validators.NumberRange(min=0, message="Doit contenir un nombre positif"),
        ],
    )

    numberOfTickets = fields.PCIntegerField(
        "Places",
        validators=[
            wtforms.validators.InputRequired("Information obligatoire"),
            wtforms.validators.NumberRange(min=0, message="Doit contenir un nombre positif"),
        ],
    )

    def validate_price(self, price: fields.PCOptSearchField) -> fields.PCOptSearchField:
        price.data = price.data.quantize(decimal.Decimal("1.00"))
        return price


class GetCollectiveOffersListForm(GetOffersBaseFields):
    class Meta:
        csrf = False

    from_date = fields.PCDateField("Créées à partir du", validators=(wtforms.validators.Optional(),))
    to_date = fields.PCDateField("Jusqu'au", validators=(wtforms.validators.Optional(),))
    only_validated_offerers = fields.PCSwitchBooleanField("Uniquement les offres des structures validées")
    q = fields.PCOptSearchField("ID, nom de l'offre")
    category = fields.PCSelectMultipleField(
        "Catégories", choices=utils.choices_from_enum(categories.CategoryIdLabelEnum)
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
    status = fields.PCSelectMultipleField(
        "États",
        choices=utils.choices_from_enum(OfferValidationStatus, formatter=filters.format_offer_validation_status),
    )
    limit = fields.PCSelectField(
        "Nombre maximum",
        choices=((100, "100"), (500, "500"), (1000, "1000"), (3000, "3000")),
        default="100",
        coerce=int,
        validators=(wtforms.validators.Optional(),),
    )

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self._fields.move_to_end("q", last=False)

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
                self.q.data,
            )
        )
