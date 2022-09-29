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
        validators.Optional("Information obligatoire"),
        validators.Length(min=3, max=64, message="doit contenir entre %(min)d et %(max)d caractères"),
    ]


class PCStringField(PCOptStringField):
    validators = [
        validators.InputRequired("Information obligatoire"),
        validators.Length(min=3, max=64, message="doit contenir entre %(min)d et %(max)d caractères"),
    ]


class PCEmailField(wtforms.EmailField):
    widget = partial(widget, template="components/forms/string_field.html")
    validators = [
        validators.Email("Email obligatoire"),
        validators.Length(min=3, max=128, message="doit contenir entre %(min)d et %(max)d caractères"),
    ]


class PCSelectField(wtforms.SelectField):
    widget = partial(widget, template="components/forms/select_field.html")
    validators = [validators.InputRequired("Information obligatoire")]


class PCSearchField(wtforms.StringField):
    widget = partial(widget, template="components/forms/search_field.html")
    validators = [validators.InputRequired("Information obligatoire")]
