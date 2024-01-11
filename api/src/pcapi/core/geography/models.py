from typing import TYPE_CHECKING

from geoalchemy2 import Geometry
import sqlalchemy as sa

from pcapi.core.geography.constants import WGS_SPATIAL_REFERENCE_IDENTIFIER
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.accessibility_mixin import AccessibilityMixin
from pcapi.models.pc_object import PcObject


if TYPE_CHECKING:
    from pcapi.core.offerers.models import Offerer


class IrisFrance(PcObject, Base, Model):
    __tablename__ = "iris_france"
    code = sa.Column(sa.String(9), nullable=False, unique=True)
    shape: str | Geometry = sa.Column("shape", Geometry(srid=WGS_SPATIAL_REFERENCE_IDENTIFIER), nullable=False)


class Address(PcObject, Base, Model):
    __tablename__ = "address"
    banId: str | None = sa.Column(sa.Text(), nullable=True, unique=True)
    street: str = sa.Column(sa.Text(), nullable=False)
    postalCode: str = sa.Column(sa.String(10), nullable=False)
    city: str = sa.Column(sa.String(50), nullable=False)
    country: str = sa.Column(sa.String(50), nullable=False)
    latitude: float = sa.Column(sa.Numeric(8, 5), nullable=False)
    longitude: float = sa.Column(sa.Numeric(8, 5), nullable=False)

    __table_args__ = (
        sa.Index("ix_unique_address_per_banid", "banId", unique=True, postgresql_where=banId.isnot(None)),
        sa.Index(
            "ix_unique_address_per_street_and_postalcode",
            "street",
            "postalCode",
            unique=True,
            postgresql_where=banId.is_(None),
        ),
    )


class PointOfInterest(PcObject, Base, Model, AccessibilityMixin):
    __tablename__ = "point_of_interest"
    extraAddress: str | None = sa.Column(sa.Text(), nullable=True)
    addressId: int = sa.Column(sa.Integer, sa.ForeignKey("address.id"))
    address: sa.orm.Mapped["Address"] = sa.orm.relationship("Address", foreign_keys=[addressId])

    __table_args__ = (
        sa.Index(
            "ix_unique_poi_per_address_and_extra_address",
            "extraAddress",
            "addressId",
            unique=True,
            postgresql_where=extraAddress.isnot(None),
        ),
    )


class OffererPointOfInterest(PcObject, Base, Model):
    __tablename__ = "offerer_point_of_interest"
    label: str = sa.Column(sa.Text(), nullable=False)
    pointOfInterestId = sa.Column(sa.Integer, sa.ForeignKey("point_of_interest.id"))
    pointOfInterest: sa.orm.Mapped["PointOfInterest"] = sa.orm.relationship(
        "PointOfInterest", foreign_keys=[pointOfInterestId]
    )
