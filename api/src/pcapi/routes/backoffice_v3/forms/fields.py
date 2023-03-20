from functools import partial
import json
import typing

import email_validator
from flask import render_template
from flask import url_for
import wtforms
from wtforms import validators
import wtforms_sqlalchemy.fields

from pcapi.admin.validators import PhoneNumberValidator


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


class PCStringField(PCOptStringField):
    validators = [
        validators.InputRequired("Information obligatoire"),
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
        validators.InputRequired("Information obligatoire"),
        validators.Length(min=1, max=64, message="doit contenir entre %(min)d et %(max)d caractères"),
        DomainNameValidator("doit contenir un nom de domaine valide"),
    ]

    def __init__(self, domain_name: str | None = None, **kwargs: typing.Any):
        super().__init__(domain_name, filters=(sanitize_pc_string,), **kwargs)


class PCHiddenField(PCStringField):
    widget = partial(widget, template="components/forms/string_field.html")
    validators = [
        validators.InputRequired("Information obligatoire"),
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
        validators.InputRequired("Information obligatoire"),
        PostalCodeValidator("Le code postal doit contenir 5 caractères"),
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
        validators.InputRequired("Information obligatoire"),
        PostalCodeValidator("Le code postal doit contenir 5 caractères"),
    ]


class PCPhoneNumberField(PCStringField):
    validators = [
        validators.Optional(""),
        PhoneNumberValidator(),
    ]


class PCOptCommentField(wtforms.StringField):
    widget = partial(widget, template="components/forms/textarea_field.html")
    validators = [
        validators.Optional(""),
        validators.Length(min=1, max=1024, message="doit contenir entre %(min)d et %(max)d caractères"),
    ]


class PCCommentField(wtforms.StringField):
    widget = partial(widget, template="components/forms/textarea_field.html")
    validators = [
        validators.InputRequired("Information obligatoire"),
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


class PCDateField(wtforms.DateField):
    widget = partial(widget, template="components/forms/date_field.html")

    def gettext(self, string: str) -> str:
        match string:
            case "Not a valid date value.":
                return "Date invalide"
            case _:
                return string


class PCSelectField(wtforms.SelectField):
    widget = partial(widget, template="components/forms/select_field.html")
    validators = [validators.InputRequired("Information obligatoire")]


class PCSelectWithPlaceholderValueField(wtforms.SelectField):
    widget = partial(widget, template="components/forms/select_with_placeholder_value_field.html")
    validators = [validators.InputRequired("Information obligatoire")]


class PCSelectMultipleField(wtforms.SelectMultipleField):
    widget = partial(widget, template="components/forms/select_multiple_field.html")
    validators = [validators.Optional()]


class PCTomSelectField(PCSelectMultipleField):
    widget = partial(widget, template="components/forms/tom_select_field.html")

    def __init__(self, label: str, endpoint: str, multiple: bool = False, **kwargs: typing.Any):
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
    validators = [validators.Optional()]

    def __init__(self, label: str | None = None, **kwargs: typing.Any):
        super().__init__(label, filters=(sanitize_pc_string,), **kwargs)


class PCSearchField(PCOptSearchField):
    validators = [validators.InputRequired("Information obligatoire")]


class PCSwitchBooleanField(wtforms.BooleanField):
    widget = partial(widget, template="components/forms/switch_boolean_field.html")
    false_values = (False, "False", "false", "off", "0", "")


class PcPostalAddressAutocomplete(wtforms.StringField):
    widget = partial(widget, template="components/forms/postal_address_autocomplete.html")

    def __init__(
        self,
        label: str,
        address: str | None,
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
        self.address = address
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
