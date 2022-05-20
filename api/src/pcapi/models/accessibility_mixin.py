import sqlalchemy as sa


class AccessibilityMixin:
    audioDisabilityCompliant = sa.Column(sa.Boolean, nullable=True)

    mentalDisabilityCompliant = sa.Column(sa.Boolean, nullable=True)

    motorDisabilityCompliant = sa.Column(sa.Boolean, nullable=True)

    visualDisabilityCompliant = sa.Column(sa.Boolean, nullable=True)
