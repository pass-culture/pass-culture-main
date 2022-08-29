from wtforms.fields import Field
from wtforms.form import Form
from wtforms.validators import ValidationError

from pcapi.core.subscription.phone_validation import exceptions as phone_validation_exceptions
from pcapi.utils import phone_number


class PhoneNumberValidator:
    def __call__(self, form: Form, field: Field) -> None:
        value = field.data
        if value:
            try:
                phone_number.parse_phone_number(value)
            except phone_validation_exceptions.InvalidPhoneNumber:
                raise ValidationError("Numéro de téléphone invalide")
