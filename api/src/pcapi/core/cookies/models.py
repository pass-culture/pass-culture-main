from dataclasses import asdict
from dataclasses import dataclass
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext import mutable
from sqlalchemy.orm import Mapped

from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.pc_object import PcObject


ListOfCookies = list[str]


@dataclass
class OptionalCookie:
    accepted: ListOfCookies
    refused: ListOfCookies


@dataclass
class Consent:
    mandatory: ListOfCookies
    optional: OptionalCookie


class CookiesHistory(PcObject, Base, Model):  # type: ignore [valid-type, misc]
    __tablename__ = "cookies_history"

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    addedDate: datetime = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now())

    deviceId: str = sa.Column(sa.String(), nullable=False)
    _consent: Mapped[Consent] = sa.Column(
        mutable.MutableDict.as_mutable(sa.dialects.postgresql.JSONB), nullable=False, name="consent"
    )
    actionDate: datetime = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now())

    userId = sa.Column(sa.BigInteger, sa.ForeignKey("user.id", ondelete="SET NULL"), index=True, nullable=True)
    user = orm.relationship("User", foreign_keys=[userId], backref=orm.backref("cookies_history", passive_deletes=True))  # type: ignore [misc]

    @sa.ext.hybrid.hybrid_property
    def consent(self) -> Consent:
        return Consent(**self._consent)

    @consent.setter  # type: ignore [no-redef]
    def consent(self, consent: Consent) -> None:
        self._consent = asdict(consent)

    @consent.expression  # type: ignore [no-redef]
    def consent(cls):  # pylint: disable=no-self-argument
        return cls._consent
