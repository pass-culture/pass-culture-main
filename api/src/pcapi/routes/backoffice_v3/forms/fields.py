from functools import partial
import typing

from flask import render_template
import wtforms
from wtforms import validators


def widget(field: wtforms.Field, template: str, *args: typing.Any, **kwargs: typing.Any) -> str:
    return render_template(template, field=field)


class PCOptStringField(wtforms.StringField):
    widget = partial(widget, template="components/forms/string_field.html")
    validators = [
        validators.Optional(""),
        validators.Length(min=3, max=64, message="doit contenir entre %(min)d et %(max)d caractères"),
    ]


class PCStringField(PCOptStringField):
    validators = [
        validators.InputRequired("Information obligatoire"),
        validators.Length(min=3, max=64, message="doit contenir entre %(min)d et %(max)d caractères"),
    ]


class PCPostalCodeField(PCStringField):
    validators = [
        validators.Optional(""),
        validators.Length(min=5, max=5, message="Le code postal doit contenir %(max)d caractères"),
    ]


class PCCommentField(PCOptStringField):
    validators = [
        validators.InputRequired("Information obligatoire"),
        validators.Length(min=2, max=1024, message="doit contenir entre %(min)d et %(max)d caractères"),
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


class PCSearchField(wtforms.StringField):
    widget = partial(widget, template="components/forms/search_field.html")
    validators = [validators.InputRequired("Information obligatoire")]
