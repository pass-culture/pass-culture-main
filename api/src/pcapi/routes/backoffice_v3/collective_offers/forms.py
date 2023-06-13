import decimal

from flask_wtf import FlaskForm
import wtforms

from pcapi.routes.backoffice_v3.forms import fields


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
