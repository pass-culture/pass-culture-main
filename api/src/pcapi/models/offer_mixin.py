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


class AccessibilityMixin:
    audioDisabilityCompliant = sa.Column(sa.Boolean, nullable=True)

    mentalDisabilityCompliant = sa.Column(sa.Boolean, nullable=True)

    motorDisabilityCompliant = sa.Column(sa.Boolean, nullable=True)

    visualDisabilityCompliant = sa.Column(sa.Boolean, nullable=True)


class StatusMixin:
    @sa.ext.hybrid.hybrid_property
    def status(self) -> OfferStatus:
        # pylint: disable=too-many-return-statements
        if self.validation == OfferValidationStatus.REJECTED:
            return OfferStatus.REJECTED

        if self.validation == OfferValidationStatus.PENDING:
            return OfferStatus.PENDING

        if self.validation == OfferValidationStatus.DRAFT:
            return OfferStatus.DRAFT

        if not self.isActive:
            return OfferStatus.INACTIVE

        if self.validation == OfferValidationStatus.APPROVED:
            if self.hasBookingLimitDatetimesPassed:
                return OfferStatus.EXPIRED

            if self.isSoldOut:
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

    validation = sa.Column(
        sa.Enum(OfferValidationStatus),
        nullable=False,
        default=OfferValidationStatus.APPROVED,
        server_default="APPROVED",
        index=True,
    )

    @property
    def isApproved(self):
        return self.validation == OfferValidationStatus.APPROVED
