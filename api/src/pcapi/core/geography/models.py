from decimal import Decimal

from geoalchemy2 import Geometry
import sqlalchemy as sa

from pcapi.core.geography.constants import WGS_SPATIAL_REFERENCE_IDENTIFIER
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.pc_object import PcObject
from pcapi.utils.date import METROPOLE_TIMEZONE


class IrisFrance(PcObject, Base, Model):
    __tablename__ = "iris_france"
    code = sa.Column(sa.String(9), nullable=False, unique=True)
    shape: str | Geometry = sa.Column("shape", Geometry(srid=WGS_SPATIAL_REFERENCE_IDENTIFIER), nullable=False)


class Address(PcObject, Base, Model):
    __tablename__ = "address"
    banId: str | None = sa.Column(sa.Text(), nullable=True)
    inseeCode: str | None = sa.Column(sa.Text(), nullable=True)
    street: str | None = sa.Column(sa.Text(), nullable=True)
    postalCode: str = sa.Column(sa.Text(), nullable=False)
    city: str = sa.Column(sa.Text(), nullable=False)
    latitude: Decimal = sa.Column(sa.Numeric(8, 5), nullable=False)
    longitude: Decimal = sa.Column(sa.Numeric(8, 5), nullable=False)
    departmentCode = sa.Column(sa.Text(), nullable=True, index=True)
    timezone: str = sa.Column(sa.Text(), nullable=False, default=METROPOLE_TIMEZONE, server_default=METROPOLE_TIMEZONE)
    # TODO(prouzet, 2024-06-25) make isManualEdition not nullable after post migration is done on all platforms
    isManualEdition: bool = sa.Column(
        sa.Boolean, nullable=True, server_default=sa.sql.expression.false(), default=False
    )

    @property
    def fullAddress(self) -> str:
        return f"{self.street} {self.postalCode} {self.city}" if self.street else f"{self.postalCode} {self.city}"

    __table_args__ = (
        sa.Index(
            "ix_partial_unique_address_per_street_and_insee_code",
            "street",
            "inseeCode",
            unique=True,
            postgresql_where=sa.and_(street.is_not(None), inseeCode.is_not(None), isManualEdition.is_not(True)),
        ),
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
