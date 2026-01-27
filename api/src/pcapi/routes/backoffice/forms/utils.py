import enum
import re
import typing

from flask_wtf import FlaskForm

from pcapi.models import feature
from pcapi.utils import email as email_utils


class PCForm(FlaskForm):
    def filter_email(self, raw_email: str | None) -> str:
        if not raw_email:
            return ""
        return email_utils.sanitize_email(raw_email)

    @property
    def raw_data(self) -> dict[str, typing.Any]:
        return {field.name: field.raw_data for field in self}


def choices_from_enum(
    enum_cls: type[enum.Enum],
    formatter: typing.Callable[[typing.Any], str] | None = None,
    exclude_opts: typing.Iterable[enum.Enum] = (),
    sort: bool = False,
) -> list[tuple]:
    choices = [(opt.name, formatter(opt) if formatter else opt.value) for opt in enum_cls if opt not in exclude_opts]
    if sort:
        return sorted(choices, key=lambda x: x[1])
    return choices


def values_from_enum(enum_cls: typing.Type[enum.Enum]) -> list[tuple]:
    return [(opt.value, opt.value) for opt in enum_cls]


def is_slug(string: str) -> bool:
    pattern = r"^[a-z0-9\-]+$"
    return bool(re.match(pattern, string))


class LazyFFString:
    def __init__(self, feature_flag: feature.FeatureToggle, value_on: str, value_off: str) -> None:
        self.feature_flag = feature_flag
        self.value_off = value_off
        self.value_on = value_on

    def __str__(self) -> str:
        if self.feature_flag.is_active():
            return str(self.value_on)
        return str(self.value_off)

    def __repr__(self) -> str:
        return self.__str__()
