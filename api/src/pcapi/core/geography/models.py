import dataclasses
import typing
from decimal import Decimal

import sqlalchemy as sa
from geoalchemy2 import Geometry
from sqlalchemy import orm as sa_orm

from pcapi.core.geography.constants import WGS_SPATIAL_REFERENCE_IDENTIFIER
from pcapi.core.geography.utils import format_coordinate
from pcapi.models import Model
from pcapi.models.pc_object import PcObject
from pcapi.utils.date import METROPOLE_TIMEZONE


@dataclasses.dataclass
class Coordinates:
    latitude: Decimal
    longitude: Decimal


class IrisFrance(PcObject, Model):
    __tablename__ = "iris_france"
    code: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(9), nullable=False, unique=True)
    shape: sa_orm.Mapped[str | Geometry] = sa_orm.mapped_column(
        "shape", Geometry(srid=WGS_SPATIAL_REFERENCE_IDENTIFIER), nullable=False
    )


class Address(PcObject, Model):
    __tablename__ = "address"
    banId: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text(), nullable=True)
    inseeCode: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text(), nullable=True)
    street: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text(), nullable=False)
    postalCode: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text(), nullable=False, index=True)
    city: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text(), nullable=False)
    latitude: sa_orm.Mapped[Decimal] = sa_orm.mapped_column(sa.Numeric(8, 5), nullable=False)
    longitude: sa_orm.Mapped[Decimal] = sa_orm.mapped_column(sa.Numeric(8, 5), nullable=False)
    departmentCode: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text(), nullable=False, index=True)
    timezone: sa_orm.Mapped[str] = sa_orm.mapped_column(
        sa.Text(), nullable=False, default=METROPOLE_TIMEZONE, server_default=METROPOLE_TIMEZONE
    )
    isManualEdition: sa_orm.Mapped[bool] = sa_orm.mapped_column(
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
            value = format_coordinate(value)
        if field not in type(self).__table__.columns:
            raise ValueError(f"Unknown field {field} for model {type(self)}")
        if isinstance(getattr(self, field), Decimal):
            return str(getattr(self, field)) != str(value)
        return getattr(self, field) != value

    __table_args__ = (
        sa.Index(
            "ix_unique_complete_address_with_nulls_not_distinct",
            "banId",
            "inseeCode",
            "street",
            "postalCode",
            "city",
            "latitude",
            "longitude",
            postgresql_nulls_not_distinct=True,
            unique=True,
        ),
        sa.Index(
            "ix_address_trgm_unaccent_city",
            sa.func.immutable_unaccent("city"),
            postgresql_using="gin",
            postgresql_ops={
                "description": "gin_trgm_ops",
            },
        ),
        sa.CheckConstraint('length("postalCode") = 5'),
        sa.CheckConstraint('length("inseeCode") = 5'),
        sa.CheckConstraint('length("city") <= 50'),
        sa.CheckConstraint('length("departmentCode") = 2 OR length("departmentCode") = 3'),
        sa.CheckConstraint('length("timezone") <= 50'),
    )
