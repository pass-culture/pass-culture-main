import sqlalchemy as sa
from sqlalchemy import orm as sa_orm
from sqlalchemy.orm import declarative_mixin


@declarative_mixin
class AccessibilityMixin:
    audioDisabilityCompliant = sa_orm.mapped_column(sa.Boolean, nullable=True)

    mentalDisabilityCompliant = sa_orm.mapped_column(sa.Boolean, nullable=True)

    motorDisabilityCompliant = sa_orm.mapped_column(sa.Boolean, nullable=True)

    visualDisabilityCompliant = sa_orm.mapped_column(sa.Boolean, nullable=True)
