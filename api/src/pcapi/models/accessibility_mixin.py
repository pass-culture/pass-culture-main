import sqlalchemy as sa
from sqlalchemy.orm import declarative_mixin


@declarative_mixin
class AccessibilityMixin:
    audioDisabilityCompliant = sa.orm.mapped_column(sa.Boolean, nullable=True)

    mentalDisabilityCompliant = sa.orm.mapped_column(sa.Boolean, nullable=True)

    motorDisabilityCompliant = sa.orm.mapped_column(sa.Boolean, nullable=True)

    visualDisabilityCompliant = sa.orm.mapped_column(sa.Boolean, nullable=True)
