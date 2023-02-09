from functools import partial
import typing

from flask import render_template
from flask import url_for
import wtforms
from wtforms import validators
import wtforms_sqlalchemy.fields

from pcapi.admin.validators import PhoneNumberValidator


def widget(field: wtforms.Field, template: str, *args: typing.Any, **kwargs: typing.Any) -> str:
    return render_template(template, field=field)


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


class PCStringField(wtforms.StringField):
    widget = partial(widget, template="components/forms/string_field.html")
    validators = [
        validators.InputRequired("Information obligatoire"),
        validators.Length(min=1, max=64, message="doit contenir entre %(min)d et %(max)d caractères"),
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


class PCOptCommentField(PCOptStringField):
    validators = [
        validators.Optional(""),
        validators.Length(min=1, max=1024, message="doit contenir entre %(min)d et %(max)d caractères"),
    ]


class PCCommentField(PCStringField):
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


class PCAutocompleteSelectMultipleField(PCSelectMultipleField):
    widget = partial(widget, template="components/forms/select_multiple_field_autocomplete.html")

    def __init__(self, label: str, endpoint: str, **kwargs: typing.Any):
        super().__init__(label, **kwargs)
        self.autocomplete_url = url_for(endpoint)


class PCQuerySelectMultipleField(wtforms_sqlalchemy.fields.QuerySelectMultipleField):
    widget = partial(widget, template="components/forms/select_multiple_field.html")
    validators = [validators.Optional()]

    # Method 'iter_groups' is abstract in class 'SelectFieldBase' and must be overridden
    def iter_groups(self) -> None:
        raise NotImplementedError()


class PCOptSearchField(wtforms.StringField):
    widget = partial(widget, template="components/forms/search_field.html")
    validators = [validators.Optional()]


class PCSearchField(PCOptSearchField):
    validators = [validators.InputRequired("Information obligatoire")]


class PCSwitchBooleanField(wtforms.BooleanField):
    widget = partial(widget, template="components/forms/switch_boolean_field.html")
    false_values = (False, "False", "false", "")
