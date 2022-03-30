import enum

import sqlalchemy as sa


class OfferStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    PENDING = "PENDING"
    EXPIRED = "EXPIRED"
    REJECTED = "REJECTED"
    SOLD_OUT = "SOLD_OUT"
    INACTIVE = "INACTIVE"
    DRAFT = "DRAFT"


class OfferValidationStatus(enum.Enum):
    APPROVED = "APPROVED"
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    REJECTED = "REJECTED"


class OfferValidationType(enum.Enum):
    """
    How the last validation status was set:
    automatically by code at API call or manually from backoffice by pass Culture team.
    """

    AUTO = "AUTO"
    MANUAL = "MANUAL"


class AccessibilityMixin:
    audioDisabilityCompliant = sa.Column(sa.Boolean, nullable=True)

    mentalDisabilityCompliant = sa.Column(sa.Boolean, nullable=True)

    motorDisabilityCompliant = sa.Column(sa.Boolean, nullable=True)

    visualDisabilityCompliant = sa.Column(sa.Boolean, nullable=True)


class StatusMixin:
    @sa.ext.hybrid.hybrid_property
    def status(self) -> OfferStatus:
        if self.validation == OfferValidationStatus.REJECTED:
            return OfferStatus.REJECTED

        if self.validation == OfferValidationStatus.PENDING:
            return OfferStatus.PENDING

        if self.validation == OfferValidationStatus.DRAFT:
            return OfferStatus.DRAFT

        if not self.isActive:
            return OfferStatus.INACTIVE

        if self.validation == OfferValidationStatus.APPROVED:
            # CollectiveOfferTemplate have a status but their hasBookingLimitDatetimesPassed is always False
            if getattr(self, "hasBookingLimitDatetimesPassed", False):
                return OfferStatus.EXPIRED
            # CollectiveOfferTemplate have a status but their isSoldout is always False
            if getattr(self, "isSoldOut", False):
                return OfferStatus.SOLD_OUT

        return OfferStatus.ACTIVE

    @status.expression
    def status(cls):  # pylint: disable=no-self-argument
        return sa.case(
            [
                (cls.validation == OfferValidationStatus.REJECTED.name, OfferStatus.REJECTED.name),
                (cls.validation == OfferValidationStatus.PENDING.name, OfferStatus.PENDING.name),
                (cls.validation == OfferValidationStatus.DRAFT.name, OfferStatus.DRAFT.name),
                (cls.isActive.is_(False), OfferStatus.INACTIVE.name),
                (cls.hasBookingLimitDatetimesPassed.is_(True), OfferStatus.EXPIRED.name),
                (cls.isSoldOut.is_(True), OfferStatus.SOLD_OUT.name),
            ],
            else_=OfferStatus.ACTIVE.name,
        )


class ValidationMixin:
    lastValidationDate = sa.Column(sa.DateTime, index=True, nullable=True)

    lastValidationType = sa.Column(sa.Enum(OfferValidationType, name="validation_type"), nullable=True)

    validation = sa.Column(
        sa.Enum(OfferValidationStatus, name="validation_status"),
        nullable=False,
        default=OfferValidationStatus.APPROVED,
        server_default="APPROVED",
        index=True,
    )

    @property
    def isApproved(self):
        return self.validation == OfferValidationStatus.APPROVED
