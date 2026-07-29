import datetime
from typing import Annotated

from pydantic import BeforeValidator
from pydantic import TypeAdapter
from pydantic import ValidationError

from pcapi.core.subscription import schemas as subscription_schemas


def _parse_level(level: str | None) -> int | None:
    if not level:
        return None
    try:
        return int(level)
    except ValueError:
        return None


def _parse_jouve_date(date: str | None) -> datetime.datetime | None:
    if not date:
        return None
    # this function has to support two parsings string format:
    # 1. the "classical" format such as "year/month/day" which is expressed when calling .dict()
    # 2. jouve format, when parsing incoming data
    try:
        return TypeAdapter(datetime.datetime).validate_python(date)
    except ValidationError:
        pass

    try:
        return datetime.datetime.strptime(date, "%d/%m/%Y")
    except ValueError:
        pass

    try:
        return datetime.datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return None


def _parse_jouve_datetime(date: str | None) -> datetime.datetime | None:
    if not date:
        return None
    try:
        return TypeAdapter(datetime.datetime).validate_python(date)
    except ValidationError:
        pass
    try:
        return datetime.datetime.strptime(date, "%m/%d/%Y %H:%M %p")  # production format
    except ValueError:
        pass
    try:
        return datetime.datetime.strptime(date, "%d/%m/%Y %H:%M")  # testing format
    except ValueError:
        return None


class JouveContent(subscription_schemas.IdentityCheckContent):
    activity: str | None = None
    address: str | None = None
    birthDateTxt: Annotated[datetime.datetime, BeforeValidator(_parse_jouve_date)] | None = None
    birthLocationCtrl: str | None = None
    bodyBirthDateCtrl: str | None = None
    bodyBirthDateLevel: Annotated[int, BeforeValidator(_parse_level)] | None = None
    bodyFirstnameCtrl: str | None = None
    bodyFirstnameLevel: Annotated[int, BeforeValidator(_parse_level)] | None = None
    bodyNameCtrl: str | None = None
    bodyNameLevel: Annotated[int, BeforeValidator(_parse_level)] | None = None
    bodyPieceNumber: str | None = None
    bodyPieceNumberCtrl: str | None = None
    bodyPieceNumberLevel: Annotated[int, BeforeValidator(_parse_level)] | None = None
    city: str | None = None
    creatorCtrl: str | None = None
    email: str | None = None
    firstName: str | None = None
    gender: str | None = None
    id: int
    initialNumberCtrl: str | None = None
    initialSizeCtrl: str | None = None
    lastName: str | None = None
    phoneNumber: str | None = None
    postalCode: str | None = None
    posteCodeCtrl: str | None = None
    registrationDate: Annotated[datetime.datetime, BeforeValidator(_parse_jouve_datetime)] | None = None
    serviceCodeCtrl: str | None = None

    def get_birth_date(self) -> datetime.date | None:
        return self.birthDateTxt.date() if self.birthDateTxt else None

    def get_first_name(self) -> str | None:
        return self.firstName

    def get_id_piece_number(self) -> str | None:
        return self.bodyPieceNumber

    def get_last_name(self) -> str | None:
        return self.lastName

    def get_married_name(self) -> None:
        return None

    def get_registration_datetime(self) -> datetime.datetime | None:
        return self.registrationDate
