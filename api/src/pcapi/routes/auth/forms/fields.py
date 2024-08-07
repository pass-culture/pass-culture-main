from functools import partial
import typing

from flask import render_template
import wtforms
from wtforms import validators


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
        validators.DataRequired("Information obligatoire"),
        validators.Length(min=1, max=64, message="doit contenir entre %(min)d et %(max)d caractères"),
    ]


class PCOptPasswordField(wtforms.PasswordField):
    widget = partial(widget, template="components/forms/string_field.html")
    validators = [
        validators.Optional(""),
        validators.Length(max=64, message="doit contenir au maximum %(max)d caractères"),
    ]

    def __init__(self, label: str | None = None, **kwargs: typing.Any):
        super().__init__(label, filters=(sanitize_pc_string,), **kwargs)


class PCPasswordField(PCOptPasswordField):
    validators = [
        validators.DataRequired("Information obligatoire"),
        validators.Length(min=1, max=64, message="doit contenir entre %(min)d et %(max)d caractères"),
    ]


class PCHiddenField(PCStringField):
    widget = partial(widget, template="components/forms/string_field.html")
    validators = [
        validators.DataRequired("Information obligatoire"),
        validators.Length(max=64, message="doit contenir au maximum %(max)d caractères"),
    ]


class PCLongHiddenField(PCHiddenField):
    validators = [
        validators.DataRequired("Information obligatoire"),
        validators.Length(max=256, message="doit contenir au maximum %(max)d caractères"),
    ]


class PCEmailField(wtforms.EmailField):
    widget = partial(widget, template="components/forms/string_field.html")
    validators = [
        validators.Email("Email obligatoire"),
        validators.Length(min=3, max=128, message="doit contenir entre %(min)d et %(max)d caractères"),
    ]
