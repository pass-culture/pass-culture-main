import enum
import typing

from flask_wtf import FlaskForm

import pcapi.utils.email as email_utils


class PCForm(FlaskForm):
    def filter_email(self, raw_email: str | None) -> str:
        if not raw_email:
            return ""
        return email_utils.sanitize_email(raw_email)


def choices_from_enum(enum_cls: typing.Type[enum.Enum]) -> list[tuple]:
    return [(opt.name, opt.value) for opt in enum_cls]


def values_from_enum(enum_cls: typing.Type[enum.Enum]) -> list[tuple]:
    return [(opt.value, opt.value) for opt in enum_cls]
