from wtforms.validators import ValidationError

from pcapi.core.subscription.phone_validation import exceptions as phone_validation_exceptions
from pcapi.utils import phone_number


class PhoneNumberValidator:
    def __call__(self, form, field):  # type: ignore [no-untyped-def]
        value = field.data
        if value:
            try:
                phone_number.parse_phone_number(value, "FR")
            except phone_validation_exceptions.InvalidPhoneNumber:
                raise ValidationError("Numéro de téléphone invalide")
