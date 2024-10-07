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
) -> list[tuple]:
    return [(opt.name, formatter(opt) if formatter else opt.value) for opt in enum_cls if opt not in exclude_opts]


def is_slug(string: str) -> bool:
    pattern = r"^[a-z0-9\-]+$"
    return bool(re.match(pattern, string))


class VenueRenaming:
    def __init__(self, value_off: str, value_on: str) -> None:
        self.value_off = value_off
        self.value_on = value_on

    def __str__(self) -> str:
        if feature.FeatureToggle.WIP_ENABLE_OFFER_ADDRESS.is_active():
            return str(self.value_on)
        return str(self.value_off)

    def __repr__(self) -> str:
        return self.__str__()
