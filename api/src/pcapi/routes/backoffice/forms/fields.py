import datetime
from functools import partial
import json
import re
import typing

import email_validator
from flask import render_template
from flask import url_for
import wtforms
from wtforms import validators
import wtforms_sqlalchemy.fields

from pcapi.core.subscription.phone_validation import exceptions as phone_validation_exceptions
from pcapi.utils import phone_number


class PhoneNumberValidator:
    def __call__(self, form: wtforms.Form, field: wtforms.Field) -> None:
        value = field.data
        if value:
            try:
                phone_number.parse_phone_number(value)
            except phone_validation_exceptions.InvalidPhoneNumber:
                raise validators.ValidationError("Numéro de téléphone invalide")


class SiretValidator:
    def __init__(self) -> None:
        self.field_flags = {
            "required": True,
            "minlength": 14,
            "maxlength": 14,
            "pattern": r"\d{14}",
        }

    def __call__(self, form: wtforms.Form, field: wtforms.Field) -> None:
        value = field.data
        if not re.match(r"^\d{14}$", value):
            raise validators.ValidationError("Le SIRET doit contenir exactement 14 chiffres")


def widget(field: wtforms.Field, template: str, *args: typing.Any, **kwargs: typing.Any) -> str:
    return render_template(template, field=field)


def sanitize_pc_string(value: str | None) -> str | None:
    """
    Strips leading whitespaces and avoids empty strings in database.
    """
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
    return value


class PostalCodeValidator:
    def __init__(self, message: str) -> None:
        self.message = message

    def __call__(self, form: wtforms.Form, postal_code: wtforms.Field) -> None:
        if not postal_code.data.isnumeric() or len(postal_code.data) != 5:
            raise validators.ValidationError(self.message)


class PCOptStringField(wtforms.StringField):
    widget = partial(widget, template="components/forms/string_field.html")
    validators = [
        validators.Optional(""),
        validators.Length(max=64, message="doit contenir au maximum %(max)d caractères"),
    ]

    def __init__(self, label: str | None = None, **kwargs: typing.Any):
        super().__init__(label, filters=(sanitize_pc_string,), **kwargs)


class PCOptPasswordField(wtforms.PasswordField):
    widget = partial(widget, template="components/forms/string_field.html")
    validators = [
        validators.Optional(""),
        validators.Length(max=64, message="doit contenir au maximum %(max)d caractères"),
    ]

    def __init__(self, label: str | None = None, **kwargs: typing.Any):
        super().__init__(label, filters=(sanitize_pc_string,), **kwargs)


class PCStringField(PCOptStringField):
    validators = [
        validators.DataRequired("Information obligatoire"),
        validators.Length(min=1, max=64, message="doit contenir entre %(min)d et %(max)d caractères"),
    ]


class PCPasswordField(PCOptPasswordField):
    validators = [
        validators.DataRequired("Information obligatoire"),
        validators.Length(min=1, max=64, message="doit contenir entre %(min)d et %(max)d caractères"),
    ]


class DomainNameValidator:
    def __init__(self, message: str) -> None:
        self.message = message

    def __call__(self, form: wtforms.Form, field: wtforms.Field) -> None:
        content = field.data
        if not content:
            return

        content = content.strip()

        try:
            email_validator.syntax.validate_email_domain_name(content)
        except email_validator.EmailSyntaxError:
            raise wtforms.validators.ValidationError(self.message)


class PCDomainName(wtforms.StringField):
    widget = partial(widget, template="components/forms/inline_form_field.html")
    validators = [
        validators.DataRequired("Information obligatoire"),
        validators.Length(min=1, max=64, message="doit contenir entre %(min)d et %(max)d caractères"),
        DomainNameValidator("doit contenir un nom de domaine valide"),
    ]

    def __init__(self, domain_name: str | None = None, **kwargs: typing.Any):
        super().__init__(domain_name, filters=(sanitize_pc_string,), **kwargs)


class PCHiddenField(PCStringField):
    widget = partial(widget, template="components/forms/string_field.html")
    validators = [
        validators.DataRequired("Information obligatoire"),
        validators.Length(max=64, message="doit contenir au maximum %(max)d caractères"),
    ]


class PCOptHiddenField(PCStringField):
    widget = partial(widget, template="components/forms/string_field.html")
    validators = [
        validators.Optional(""),
        validators.Length(max=64, message="doit contenir au maximum %(max)d caractères"),
    ]


class PCPostalCodeHiddenField(PCOptHiddenField):
    validators = [
        validators.DataRequired("Information obligatoire"),
        PostalCodeValidator("Le code postal doit contenir 5 caractères"),
    ]


class PCBanIdHiddenField(PCHiddenField):
    validators = [
        validators.Optional(""),
        validators.Length(max=20, message="doit contenir au maximum %(max)d caractères"),
    ]


class PCOptPostalCodeHiddenField(PCOptHiddenField):
    validators = [
        validators.Optional(""),
        PostalCodeValidator("Le code postal doit contenir 5 caractères"),
    ]


class PCOptPostalCodeField(PCStringField):
    validators = [
        validators.Optional(""),
        PostalCodeValidator("Le code postal doit contenir 5 caractères"),
    ]


class PCPostalCodeField(PCStringField):
    validators = [
        validators.DataRequired("Information obligatoire"),
        PostalCodeValidator("Le code postal doit contenir 5 caractères"),
    ]


class PCPhoneNumberField(PCStringField):
    validators = [
        validators.Optional(""),
        PhoneNumberValidator(),
    ]


class PCSiretField(PCStringField):
    validators = [SiretValidator()]


class PCTextareaField(wtforms.StringField):
    widget = partial(widget, template="components/forms/textarea_field.html")

    def __init__(self, label: str, rows: int = 3, **kwargs: typing.Any):
        super().__init__(label, **kwargs)
        self.rows = rows


class PCOptCommentField(PCTextareaField):
    validators = [
        validators.Optional(""),
        validators.Length(min=1, max=1024, message="doit contenir entre %(min)d et %(max)d caractères"),
    ]


class PCCommentField(PCTextareaField):
    validators = [
        validators.DataRequired("Information obligatoire"),
        validators.Length(min=1, max=1024, message="doit contenir entre %(min)d et %(max)d caractères"),
    ]


class PCEmailField(wtforms.EmailField):
    widget = partial(widget, template="components/forms/string_field.html")
    validators = [
        validators.Email("Email obligatoire"),
        validators.Length(min=3, max=128, message="doit contenir entre %(min)d et %(max)d caractères"),
    ]


class PCOptIntegerField(wtforms.IntegerField):
    widget = partial(widget, template="components/forms/string_field.html")
    validators = [
        validators.Optional(""),
    ]


class PCIntegerField(wtforms.IntegerField):
    widget = partial(widget, template="components/forms/string_field.html")
    validators = [
        validators.InputRequired("Information obligatoire"),
    ]


class PCOptHiddenIntegerField(wtforms.IntegerField):
    widget = partial(widget, template="components/forms/string_field.html")
    validators = [
        validators.Optional(""),
    ]

    def gettext(self, string: str) -> str:
        match string:
            case "Not a valid integer value.":
                return f"Le paramètre {self.name} devrait être un entier"
            case _:
                return string


class PCDateTimeField(wtforms.DateTimeField):
    widget = partial(widget, template="components/forms/date_field.html")
    input_type = "datetime-local"

    def gettext(self, string: str) -> str:
        match string:
            case "Not a valid date value.":
                return "Date invalide"
            case _:
                return string


class PCOptDateTimeField(PCDateTimeField):
    validators = [
        validators.Optional(""),
    ]


class PCDateField(wtforms.DateField):
    widget = partial(widget, template="components/forms/date_field.html")
    input_type = "date"

    def gettext(self, string: str) -> str:
        match string:
            case "Not a valid date value.":
                return "Date invalide"
            case _:
                return string


class PCOptDateField(PCDateField):
    validators = [
        validators.Optional(""),
    ]


class PCDateRangeField(wtforms.StringField):
    separator = " - "
    date_range_dateformat = "%d/%m/%Y"
    widget = partial(widget, template="components/forms/date_range_field.html")

    def process_formdata(self, valuelist: list) -> None:
        if valuelist:
            from_to_date_split = valuelist[0].split(self.separator)
            from_date = datetime.datetime.strptime(from_to_date_split[0], self.date_range_dateformat)
            to_date = datetime.datetime.strptime(from_to_date_split[1], self.date_range_dateformat)
            self.data = [from_date, to_date]
        else:
            self.data = []

    @property
    def from_date(self) -> datetime.date | None:
        return self.data[0]

    @property
    def to_date(self) -> datetime.date | None:
        return self.data[1]

    def __init__(
        self,
        label: str,
        max_date: datetime.date | None = None,
        reset_to_blank: bool = False,
        calendar_start_date: datetime.date | None = None,
        calendar_end_date: datetime.date | None = None,
        **kwargs: typing.Any,
    ):
        super().__init__(label, **kwargs)
        self.max_date = max_date
        self.reset_to_blank = reset_to_blank
        self.calendar_start_date = calendar_start_date
        self.calendar_end_date = calendar_end_date


class PCSelectField(wtforms.SelectField):
    widget = partial(widget, template="components/forms/select_field.html")
    validators = [validators.InputRequired("Information obligatoire")]

    def __init__(self, label: str | None = None, *, default_text: str = "", **kwargs: typing.Any):
        super().__init__(label, **kwargs)
        self.default_text = default_text


class PCSelectWithPlaceholderValueField(wtforms.SelectField):
    widget = partial(widget, template="components/forms/select_with_placeholder_value_field.html")
    validators = [validators.InputRequired("Information obligatoire")]


class PCSelectMultipleField(wtforms.SelectMultipleField):
    widget = partial(widget, template="components/forms/select_multiple_field.html")
    validators = [validators.Optional()]

    def __init__(
        self,
        label: str,
        *,
        search_inline: bool = False,
        full_row: bool = False,
        field_list_compatibility: bool = False,
        **kwargs: typing.Any,
    ):
        super().__init__(label, **kwargs)
        self.search_inline = search_inline  # not higher than other form fields
        self.full_row = full_row  # new line in the form with a full-width dropdown
        self.field_list_compatibility = field_list_compatibility


class PCTomSelectField(PCSelectMultipleField):
    widget = partial(widget, template="components/forms/tom_select_field.html")

    def __init__(self, label: str, *, endpoint: str, multiple: bool = False, **kwargs: typing.Any):
        super().__init__(label, **kwargs)
        self.tomselect_autocomplete_url = url_for(endpoint)
        self.multiple = multiple

    @property
    def tomselect_options(self) -> str:
        return json.dumps(
            [{"id": str(choice_value), "text": choice_label} for choice_value, choice_label in self.choices]
        )

    @property
    def tomselect_items(self) -> str:
        return json.dumps([str(choice_value) for choice_value, _ in self.choices])


class PCQuerySelectMultipleField(wtforms_sqlalchemy.fields.QuerySelectMultipleField):
    widget = partial(widget, template="components/forms/select_multiple_field.html")
    validators = [validators.Optional()]

    # Method 'iter_groups' is abstract in class 'SelectFieldBase' and must be overridden
    def iter_groups(self) -> None:
        raise NotImplementedError()


class PCOptSearchField(wtforms.StringField):
    widget = partial(widget, template="components/forms/search_field.html")
    validators = [validators.Optional(strip_whitespace=True)]

    def __init__(self, label: str | None = None, **kwargs: typing.Any):
        super().__init__(label, filters=(sanitize_pc_string,), **kwargs)


class PCSearchField(PCOptSearchField):
    validators = [validators.DataRequired("Information obligatoire")]


class PCSwitchBooleanField(wtforms.BooleanField):
    widget = partial(widget, template="components/forms/switch_boolean_field.html")
    false_values = (False, "False", "false", "off", "0", "")

    def __init__(self, label: str, full_row: bool = False, full_opacity: bool = False, **kwargs: typing.Any):
        super().__init__(label, **kwargs)
        self.full_row = full_row
        self.full_opacity = full_opacity  # set to True so that input is not greyed out when read-only


class PCCheckboxField(wtforms.BooleanField):
    widget = partial(widget, template="components/forms/checkbox_field.html")
    false_values = (False, "False", "false", "off", "0", "")


class PcPostalAddressAutocomplete(wtforms.StringField):
    widget = partial(widget, template="components/forms/postal_address_autocomplete.html")

    def __init__(
        self,
        label: str,
        street: str | None,
        ban_id: str | None,
        city: str | None,
        postal_code: str | None,
        latitude: str | None,
        longitude: str | None,
        required: bool = False,
        has_reset: bool = False,
        has_manual_editing: bool = False,
        limit: int = 10,
        **kwargs: typing.Any,
    ):
        super().__init__(label, **kwargs)
        self.street = street
        self.ban_id = ban_id
        self.city = city
        self.postal_code = postal_code
        self.latitude = latitude
        self.longitude = longitude
        self.required = required
        self.has_reset = has_reset
        self.has_manual_editing = has_manual_editing
        self.limit = limit


class PCDecimalField(wtforms.DecimalField):
    widget = partial(widget, template="components/forms/string_field.html")


class PCFieldListField(wtforms.FieldList):
    widget = partial(widget, template="components/forms/field_list_field.html")


class PCFormField(wtforms.FormField):
    widget = partial(widget, template="components/forms/form_field.html")
