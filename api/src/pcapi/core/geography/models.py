import dataclasses
import typing
from decimal import Decimal

import sqlalchemy as sa
from geoalchemy2 import Geometry
from sqlalchemy import orm as sa_orm

from pcapi.core.geography.constants import WGS_SPATIAL_REFERENCE_IDENTIFIER
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.pc_object import PcObject
from pcapi.utils.date import METROPOLE_TIMEZONE


@dataclasses.dataclass
class Coordinates:
    latitude: Decimal
    longitude: Decimal


class IrisFrance(PcObject, Base, Model):
    __tablename__ = "iris_france"
    code = sa.Column(sa.String(9), nullable=False, unique=True)
    shape: str | Geometry = sa.Column("shape", Geometry(srid=WGS_SPATIAL_REFERENCE_IDENTIFIER), nullable=False)


class Address(PcObject, Base, Model):
    __tablename__ = "address"
    banId: str | None = sa.Column(sa.Text(), nullable=True)
    inseeCode: str | None = sa.Column(sa.Text(), nullable=True)
    street: sa_orm.Mapped[str] = sa.Column(sa.Text(), nullable=False)
    postalCode: sa_orm.Mapped[str] = sa.Column(sa.Text(), nullable=False)
    city: sa_orm.Mapped[str] = sa.Column(sa.Text(), nullable=False)
    latitude: sa_orm.Mapped[Decimal] = sa.Column(sa.Numeric(8, 5), nullable=False)
    longitude: sa_orm.Mapped[Decimal] = sa.Column(sa.Numeric(8, 5), nullable=False)
    departmentCode: sa_orm.Mapped[str] = sa.Column(sa.Text(), nullable=False, index=True)
    timezone: sa_orm.Mapped[str] = sa.Column(
        sa.Text(), nullable=False, default=METROPOLE_TIMEZONE, server_default=METROPOLE_TIMEZONE
    )
    isManualEdition: sa_orm.Mapped[bool] = sa.Column(
        sa.Boolean, nullable=False, server_default=sa.sql.expression.false(), default=False
    )

    @property
    def fullAddress(self) -> str:
        return f"{self.street} {self.postalCode} {self.city}" if self.street else f"{self.postalCode} {self.city}"

    def field_exists_and_has_changed(self, field: str, value: typing.Any) -> typing.Any:
        if field in ("latitude", "longitude"):
            # Rounding to five digits to keep consistency with the columns definitions
            # We don’t want to consider coordinates has changed if actually the rounded value is the same
            # that the one we already have
            if isinstance(value, str):
                value = Decimal(value)
            value = round(value, 5)
        if field not in type(self).__table__.columns:
            raise ValueError(f"Unknown field {field} for model {type(self)}")
        if isinstance(getattr(self, field), Decimal):
            return str(getattr(self, field)) != str(value)
        return getattr(self, field) != value

    __table_args__ = (
        sa.Index(
            # FIXME (dramelet, 14-10-2024)
            # Our current version of sqlalchemy (1.4) doesn't handle
            # the option `nulls_not_distinct` from postgresql dialect
            # Hence this declaration and the raw query in the suitable migration
            "ix_unique_complete_address_with_nulls_not_distinct",
            "banId",
            "inseeCode",
            "street",
            "postalCode",
            "city",
            "latitude",
            "longitude",
            unique=True,
        ),
        sa.CheckConstraint('length("postalCode") = 5'),
        sa.CheckConstraint('length("inseeCode") = 5'),
        sa.CheckConstraint('length("city") <= 50'),
        sa.CheckConstraint('length("departmentCode") = 2 OR length("departmentCode") = 3'),
        sa.CheckConstraint('length("timezone") <= 50'),
    )
