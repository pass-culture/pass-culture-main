import datetime

import pydantic.v1 as pydantic_v1
from pydantic.v1.class_validators import validator

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
        return pydantic_v1.datetime_parse.parse_datetime(date)
    except pydantic_v1.DateTimeError:
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
        return pydantic_v1.datetime_parse.parse_datetime(date)
    except pydantic_v1.DateTimeError:
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
    activity: str | None
    address: str | None
    birthDateTxt: datetime.datetime | None
    birthLocationCtrl: str | None
    bodyBirthDateCtrl: str | None
    bodyBirthDateLevel: int | None
    bodyFirstnameCtrl: str | None
    bodyFirstnameLevel: int | None
    bodyNameCtrl: str | None
    bodyNameLevel: int | None
    bodyPieceNumber: str | None
    bodyPieceNumberCtrl: str | None
    bodyPieceNumberLevel: int | None
    city: str | None
    creatorCtrl: str | None
    email: str | None
    firstName: str | None
    gender: str | None
    id: int
    initialNumberCtrl: str | None
    initialSizeCtrl: str | None
    lastName: str | None
    phoneNumber: str | None
    postalCode: str | None
    posteCodeCtrl: str | None
    registrationDate: datetime.datetime | None
    serviceCodeCtrl: str | None

    _parse_birth_date = validator("birthDateTxt", pre=True, allow_reuse=True)(_parse_jouve_date)
    _parse_body_birth_date_level = validator("bodyBirthDateLevel", pre=True, allow_reuse=True)(_parse_level)
    _parse_body_first_name_level = validator("bodyFirstnameLevel", pre=True, allow_reuse=True)(_parse_level)
    _parse_body_name_level = validator("bodyNameLevel", pre=True, allow_reuse=True)(_parse_level)
    _parse_body_piece_number_level = validator("bodyPieceNumberLevel", pre=True, allow_reuse=True)(_parse_level)
    _parse_registration_date = validator("registrationDate", pre=True, allow_reuse=True)(_parse_jouve_datetime)

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
