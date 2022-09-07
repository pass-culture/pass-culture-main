from __future__ import annotations

import dataclasses
from datetime import datetime
from decimal import Decimal
import enum
import typing

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.sql.elements import False_
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import Index
from sqlalchemy.sql.selectable import Exists
from sqlalchemy.sql.sqltypes import Boolean
from sqlalchemy.sql.sqltypes import Numeric

from pcapi.core.bookings import exceptions as booking_exceptions
from pcapi.core.categories import subcategories
from pcapi.core.educational import exceptions
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models import offer_mixin
from pcapi.models.accessibility_mixin import AccessibilityMixin
from pcapi.models.pc_object import PcObject


if typing.TYPE_CHECKING:
    from sqlalchemy.orm import Mapped

    from pcapi.core.bookings.models import Booking
    from pcapi.core.offerers.models import Offerer
    from pcapi.core.offerers.models import Venue


class StudentLevels(enum.Enum):
    COLLEGE4 = "Collège - 4e"
    COLLEGE3 = "Collège - 3e"
    CAP1 = "CAP - 1re année"
    CAP2 = "CAP - 2e année"
    GENERAL2 = "Lycée - Seconde"
    GENERAL1 = "Lycée - Première"
    GENERAL0 = "Lycée - Terminale"


ADAGE_STUDENT_LEVEL_MAPPING = {
    "Collège - 4e": StudentLevels.COLLEGE4,
    "Collège - 3e": StudentLevels.COLLEGE3,
    "CAP - 1re année": StudentLevels.CAP1,
    "CAP - 2e année": StudentLevels.CAP2,
    "Lycée - Seconde": StudentLevels.GENERAL2,
    "Lycée - Première": StudentLevels.GENERAL1,
    "Lycée - Terminale": StudentLevels.GENERAL0,
}


class CollectiveBookingCancellationReasons(enum.Enum):
    OFFERER = "OFFERER"
    BENEFICIARY = "BENEFICIARY"
    EXPIRED = "EXPIRED"
    FRAUD = "FRAUD"
    REFUSED_BY_INSTITUTE = "REFUSED_BY_INSTITUTE"


class Ministry(enum.Enum):
    EDUCATION_NATIONALE = "MENjs"
    MER = "MMe"
    AGRICULTURE = "MAg"
    ARMEES = "MAr"


class CollectiveBookingStatus(enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    USED = "USED"
    CANCELLED = "CANCELLED"
    REIMBURSED = "REIMBURSED"


class EducationalBookingStatus(enum.Enum):
    REFUSED = "REFUSED"


class CollectiveBookingStatusFilter(enum.Enum):
    BOOKED = "booked"
    VALIDATED = "validated"
    REIMBURSED = "reimbursed"


class CollectiveOffer(PcObject, Base, offer_mixin.ValidationMixin, AccessibilityMixin, offer_mixin.StatusMixin, Model):  # type: ignore[valid-type, misc]
    __tablename__ = "collective_offer"

    offerId = sa.Column(sa.BigInteger, nullable=True)

    isActive: bool = sa.Column(sa.Boolean, nullable=False, server_default=sa.sql.expression.true(), default=True)

    venueId: int = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id"), nullable=False, index=True)

    venue: RelationshipProperty["Venue"] = sa.orm.relationship(
        "Venue", foreign_keys=[venueId], back_populates="collectiveOffers"
    )

    name: str = sa.Column(sa.String(140), nullable=False)

    bookingEmail = sa.Column(sa.String(120), nullable=True)

    description = sa.Column(sa.Text, nullable=True)

    durationMinutes = sa.Column(sa.Integer, nullable=True)

    dateCreated: datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)

    subcategoryId: str = sa.Column(sa.Text, nullable=False, index=True)

    dateUpdated: datetime = sa.Column(sa.DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)

    students: list[StudentLevels] = sa.Column(
        MutableList.as_mutable(postgresql.ARRAY(sa.Enum(StudentLevels))),
        nullable=False,
        server_default="{}",
    )

    collectiveStock: "CollectiveStock" = relationship(
        "CollectiveStock", back_populates="collectiveOffer", uselist=False
    )

    contactEmail: str = sa.Column(sa.String(120), nullable=False)

    contactPhone: str = sa.Column(sa.Text, nullable=False)

    offerVenue: dict = sa.Column(MutableDict.as_mutable(postgresql.json.JSONB), nullable=False)

    interventionArea: list[str] = sa.Column(
        MutableList.as_mutable(postgresql.ARRAY(sa.Text())), nullable=False, server_default="{}"
    )

    domains: list["EducationalDomain"] = relationship(
        "EducationalDomain", secondary="collective_offer_domain", back_populates="collectiveOffers"
    )

    institutionId = sa.Column(sa.BigInteger, sa.ForeignKey("educational_institution.id"), index=True, nullable=True)

    institution: Mapped["EducationalInstitution"] = relationship(
        "EducationalInstitution", foreign_keys=[institutionId], back_populates="collectiveOffers"
    )

    @property
    def isEducational(self) -> bool:
        # FIXME (rpaoloni, 2022-03-7): Remove legacy support layer
        return True

    @property
    def isEditable(self) -> bool:
        return self.status not in [offer_mixin.OfferStatus.PENDING, offer_mixin.OfferStatus.REJECTED]

    @property
    def isVisibilityEditable(self) -> bool:
        is_editable = self.isEditable
        if self.collectiveStock:
            is_editable = is_editable and not self.collectiveStock.isSoldOut

        return is_editable

    @sa.ext.hybrid.hybrid_property
    def isSoldOut(self) -> bool:
        if self.collectiveStock:
            return self.collectiveStock.isSoldOut
        return True

    @isSoldOut.expression  # type: ignore[no-redef]
    def isSoldOut(cls) -> Exists:  # pylint: disable=no-self-argument
        return (
            sa.exists()
            .where(CollectiveStock.collectiveOfferId == cls.id)
            .where(CollectiveBooking.collectiveStockId == CollectiveStock.id)
            .where(CollectiveBooking.status != CollectiveBookingStatus.CANCELLED)
        )

    @property
    def isBookable(self) -> bool:
        if self.collectiveStock:
            return self.collectiveStock.isBookable
        return False

    is_eligible_for_search = isBookable

    @property
    def isReleased(self) -> bool:
        return (
            self.isActive
            and self.validation == offer_mixin.OfferValidationStatus.APPROVED
            and self.venue.isValidated
            and self.venue.managingOfferer.isActive
            and self.venue.managingOfferer.isValidated
        )

    @property
    def hasBookingLimitDatetimePassed(self) -> bool:
        if self.collectiveStock:
            return self.collectiveStock.hasBookingLimitDatetimePassed  # type: ignore[return-value]
        return False

    @sa.ext.hybrid.hybrid_property
    def hasBookingLimitDatetimesPassed(self) -> bool:
        if not self.collectiveStock:
            return False
        return self.collectiveStock.hasBookingLimitDatetimePassed

    @hasBookingLimitDatetimesPassed.expression  # type: ignore[no-redef]
    def hasBookingLimitDatetimesPassed(cls) -> Exists:  # pylint: disable=no-self-argument
        return (
            sa.exists()
            .where(CollectiveStock.collectiveOfferId == cls.id)
            .where(CollectiveStock.hasBookingLimitDatetimePassed.is_(True))
        )

    @property
    def subcategory(self) -> subcategories.Subcategory:
        if self.subcategoryId not in subcategories.ALL_SUBCATEGORIES_DICT:
            raise ValueError(f"Unexpected subcategoryId '{self.subcategoryId}' for collective offer {self.id}")
        return subcategories.ALL_SUBCATEGORIES_DICT[self.subcategoryId]

    @classmethod
    def create_from_collective_offer_template(
        cls, collective_offer_template: CollectiveOfferTemplate
    ) -> CollectiveOffer:
        list_of_common_attributes = [
            "isActive",
            "venue",
            "name",
            "description",
            "durationMinutes",
            "dateCreated",
            "domains",
            "subcategoryId",
            "dateUpdated",
            "bookingEmail",
            "lastValidationDate",
            "validation",
            "audioDisabilityCompliant",
            "mentalDisabilityCompliant",
            "motorDisabilityCompliant",
            "visualDisabilityCompliant",
            "contactEmail",
            "contactPhone",
            "offerVenue",
            "students",
            "interventionArea",
        ]
        offer_mapping = {x: getattr(collective_offer_template, x) for x in list_of_common_attributes}
        return cls(
            **offer_mapping,
            offerId=collective_offer_template.offerId,
        )


class CollectiveOfferTemplate(PcObject, offer_mixin.ValidationMixin, AccessibilityMixin, offer_mixin.StatusMixin, Base, Model):  # type: ignore[valid-type, misc]
    __tablename__ = "collective_offer_template"

    offerId = sa.Column(sa.BigInteger, nullable=True)

    isActive: bool = sa.Column(sa.Boolean, nullable=False, server_default=sa.sql.expression.true(), default=True)

    venueId: int = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id"), nullable=False, index=True)

    venue: RelationshipProperty["Venue"] = sa.orm.relationship(
        "Venue", foreign_keys=[venueId], back_populates="collectiveOfferTemplates"
    )

    name: str = sa.Column(sa.String(140), nullable=False)

    description = sa.Column(sa.Text, nullable=True)

    durationMinutes = sa.Column(sa.Integer, nullable=True)

    dateCreated: datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)

    subcategoryId: str = sa.Column(sa.Text, nullable=False, index=True)

    dateUpdated: datetime = sa.Column(sa.DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)

    students: list[StudentLevels] = sa.Column(
        MutableList.as_mutable(postgresql.ARRAY(sa.Enum(StudentLevels))),
        nullable=False,
        server_default="{}",
    )

    priceDetail = sa.Column(sa.Text, nullable=True)

    bookingEmail = sa.Column(sa.String(120), nullable=True)

    contactEmail: str = sa.Column(sa.String(120), nullable=False)

    contactPhone: str = sa.Column(sa.Text, nullable=False)

    offerVenue: dict = sa.Column(MutableDict.as_mutable(postgresql.json.JSONB), nullable=False)

    interventionArea: list[str] = sa.Column(
        MutableList.as_mutable(postgresql.ARRAY(sa.Text())), nullable=False, server_default="{}"
    )

    domains: list["EducationalDomain"] = relationship(
        "EducationalDomain", secondary="collective_offer_template_domain", back_populates="collectiveOfferTemplates"
    )

    @property
    def isEducational(self) -> bool:
        # FIXME (rpaoloni, 2022-05-09): Remove legacy support layer
        return True

    @property
    def isEditable(self) -> bool:
        return self.status not in [offer_mixin.OfferStatus.PENDING, offer_mixin.OfferStatus.REJECTED]

    @sa.ext.hybrid.hybrid_property
    def hasBookingLimitDatetimesPassed(self) -> bool:
        # this property is here for compatibility reasons
        return False

    @hasBookingLimitDatetimesPassed.expression  # type: ignore[no-redef]
    def hasBookingLimitDatetimesPassed(cls) -> False_:  # pylint: disable=no-self-argument
        # this property is here for compatibility reasons
        return sa.sql.expression.false()

    @sa.ext.hybrid.hybrid_property
    def isSoldOut(self) -> bool:
        # this property is here for compatibility reasons
        return False

    @isSoldOut.expression  # type: ignore[no-redef]
    def isSoldOut(cls) -> False_:  # pylint: disable=no-self-argument
        # this property is here for compatibility reasons
        return sa.sql.expression.false()

    @property
    def isReleased(self) -> bool:
        return (
            self.isActive
            and self.validation == offer_mixin.OfferValidationStatus.APPROVED
            and self.venue.isValidated
            and self.venue.managingOfferer.isActive
            and self.venue.managingOfferer.isValidated
        )

    is_eligible_for_search = isReleased

    @property
    def subcategory(self) -> subcategories.Subcategory:
        if self.subcategoryId not in subcategories.ALL_SUBCATEGORIES_DICT:
            raise ValueError(f"Unexpected subcategoryId '{self.subcategoryId}' for collective offer template {self.id}")
        return subcategories.ALL_SUBCATEGORIES_DICT[self.subcategoryId]

    @classmethod
    def create_from_collective_offer(
        cls, collective_offer: CollectiveOffer, price_detail: str = None
    ) -> CollectiveOfferTemplate:
        list_of_common_attributes = [
            "isActive",
            "venue",
            "name",
            "description",
            "durationMinutes",
            "dateCreated",
            "domains",
            "subcategoryId",
            "dateUpdated",
            "bookingEmail",
            "lastValidationDate",
            "validation",
            "audioDisabilityCompliant",
            "mentalDisabilityCompliant",
            "motorDisabilityCompliant",
            "visualDisabilityCompliant",
            "contactEmail",
            "contactPhone",
            "offerVenue",
            "students",
            "interventionArea",
        ]
        collective_offer_mapping = {x: getattr(collective_offer, x) for x in list_of_common_attributes}
        return cls(
            **collective_offer_mapping,
            offerId=collective_offer.offerId,
            priceDetail=price_detail,
        )


class CollectiveStock(PcObject, Base, Model):  # type: ignore [valid-type, misc]
    __tablename__ = "collective_stock"

    stockId = sa.Column(sa.BigInteger, nullable=True)

    dateCreated: datetime = sa.Column(
        sa.DateTime, nullable=False, default=datetime.utcnow, server_default=sa.func.now()
    )

    dateModified: datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    beginningDatetime: datetime = sa.Column(sa.DateTime, index=True, nullable=False)

    collectiveOfferId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("collective_offer.id"), index=True, nullable=False, unique=True
    )

    collectiveOffer: RelationshipProperty["CollectiveOffer"] = sa.orm.relationship(
        "CollectiveOffer", foreign_keys=[collectiveOfferId], uselist=False, back_populates="collectiveStock"
    )

    collectiveBookings: RelationshipProperty[list["CollectiveBooking"]] = relationship(
        "CollectiveBooking", back_populates="collectiveStock"
    )

    price: float = sa.Column(
        sa.Numeric(10, 2), sa.CheckConstraint("price >= 0", name="check_price_is_not_negative"), nullable=False
    )

    bookingLimitDatetime: datetime = sa.Column(sa.DateTime, nullable=False)

    numberOfTickets: int = sa.Column(sa.Integer, nullable=False)

    priceDetail = sa.Column(sa.Text, nullable=True)

    @property
    def isBookable(self) -> bool:
        return not self.isExpired and self.collectiveOffer.isReleased and not self.isSoldOut

    @property
    def isEditable(self) -> bool:
        """this rule has nothing to do with the isEditable from pcapi.core.offers.models.Booking
        a collectiveStock is editable if there is no booking with status REIMBURSED, USED, CONFIRMED
        and its offer is editable.
        """
        bookable = (CollectiveBookingStatus.PENDING, CollectiveBookingStatus.CANCELLED)
        for booking in self.collectiveBookings:  # type: ignore [attr-defined]
            if booking.status not in bookable:
                return False
        return self.collectiveOffer.isEditable

    @sa.ext.hybrid.hybrid_property
    def hasBookingLimitDatetimePassed(self) -> bool:
        return self.bookingLimitDatetime <= datetime.utcnow()

    @hasBookingLimitDatetimePassed.expression  # type: ignore[no-redef]
    def hasBookingLimitDatetimePassed(cls) -> BinaryExpression:  # pylint: disable=no-self-argument
        return cls.bookingLimitDatetime <= sa.func.now()

    @sa.ext.hybrid.hybrid_property
    def isEventExpired(self) -> bool:  # todo rewrite
        return self.beginningDatetime <= datetime.utcnow()

    @isEventExpired.expression  # type: ignore[no-redef]
    def isEventExpired(cls):  # pylint: disable=no-self-argument
        return cls.beginningDatetime <= sa.func.now()

    @property
    def isExpired(self) -> bool:
        return self.isEventExpired or self.hasBookingLimitDatetimePassed  # type: ignore[return-value]

    @property
    def isEventDeletable(self) -> bool:
        return self.beginningDatetime >= datetime.utcnow()

    @property
    def isSoldOut(self) -> bool:
        for booking in self.collectiveBookings:  # type: ignore [attr-defined]
            if booking.status != CollectiveBookingStatus.CANCELLED:
                return True
        return False


class EducationalInstitution(PcObject, Base, Model):  # type: ignore [valid-type, misc]
    __tablename__ = "educational_institution"

    institutionId: str = sa.Column(sa.String(30), nullable=False, unique=True, index=True)

    institutionType = sa.Column(sa.String(80), nullable=True)

    name: str = sa.Column(sa.Text(), nullable=False)

    city: str = sa.Column(sa.Text(), nullable=False)

    postalCode: str = sa.Column(sa.String(10), nullable=False)

    email = sa.Column(sa.Text(), nullable=True)

    phoneNumber: str = sa.Column(sa.String(30), nullable=False)

    collectiveOffers: RelationshipProperty[list["CollectiveOffer"]] = relationship(
        "CollectiveOffer", back_populates="institution"
    )


class EducationalYear(PcObject, Base, Model):  # type: ignore [valid-type, misc]
    __tablename__ = "educational_year"

    adageId: str = sa.Column(sa.String(30), unique=True, nullable=False)

    beginningDate: datetime = sa.Column(sa.DateTime, nullable=False)

    expirationDate: datetime = sa.Column(sa.DateTime, nullable=False)


class EducationalDeposit(PcObject, Base, Model):  # type: ignore [valid-type, misc]
    __tablename__ = "educational_deposit"

    TEMPORARY_FUND_AVAILABLE_RATIO = 0.8

    educationalInstitutionId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("educational_institution.id"), index=True, nullable=False
    )

    educationalInstitution: EducationalInstitution = relationship(
        EducationalInstitution, foreign_keys=[educationalInstitutionId], backref="deposits"
    )

    educationalYearId: str = sa.Column(
        sa.String(30), sa.ForeignKey("educational_year.adageId"), index=True, nullable=False
    )

    educationalYear: RelationshipProperty["EducationalYear"] = relationship(  # type: ignore [misc]
        EducationalYear, foreign_keys=[educationalYearId], backref="deposits"
    )

    amount: Decimal = sa.Column(Numeric(10, 2), nullable=False)

    dateCreated: datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow, server_default=func.now())

    isFinal: bool = sa.Column(Boolean, nullable=False, default=True)

    ministry = sa.Column(
        sa.Enum(Ministry),
        nullable=True,
    )

    def get_amount(self) -> Decimal:
        return round(self.amount * Decimal(self.TEMPORARY_FUND_AVAILABLE_RATIO), 2) if not self.isFinal else self.amount

    def check_has_enough_fund(self, total_amount_after_booking: Decimal) -> None:
        if self.amount < total_amount_after_booking:
            raise exceptions.InsufficientFund()

        if self.get_amount() < total_amount_after_booking and not self.isFinal:
            raise exceptions.InsufficientTemporaryFund()

        return


class EducationalRedactor(PcObject, Base, Model):  # type: ignore [valid-type, misc]

    __tablename__ = "educational_redactor"

    email: str = sa.Column(sa.String(120), nullable=False, unique=True, index=True)

    firstName = sa.Column(sa.String(128), nullable=True)

    lastName = sa.Column(sa.String(128), nullable=True)

    civility: str = sa.Column(sa.String(20), nullable=True)

    collectiveBookings: RelationshipProperty[list["CollectiveBooking"]] = relationship(
        "CollectiveBooking", back_populates="educationalRedactor"
    )


class CollectiveBooking(PcObject, Base, Model):  # type: ignore [valid-type, misc]
    __tablename__ = "collective_booking"

    bookingId = sa.Column(sa.BigInteger)

    dateCreated: datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)
    Index("ix_collective_booking_date_created", dateCreated)

    dateUsed = sa.Column(sa.DateTime, nullable=True, index=True)

    collectiveStockId: int = sa.Column(sa.BigInteger, sa.ForeignKey("collective_stock.id"), index=True, nullable=False)

    collectiveStock: RelationshipProperty["CollectiveStock"] = relationship(
        "CollectiveStock", foreign_keys=[collectiveStockId], back_populates="collectiveBookings"
    )

    venueId: int = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id"), index=True, nullable=False)

    venue: RelationshipProperty["Venue"] = relationship("Venue", foreign_keys=[venueId], backref="collectiveBookings")

    offererId: int = sa.Column(sa.BigInteger, sa.ForeignKey("offerer.id"), index=True, nullable=False)

    offerer: RelationshipProperty["Offerer"] = relationship(
        "Offerer", foreign_keys=[offererId], backref="collectiveBookings"
    )

    cancellationDate = sa.Column(sa.DateTime, nullable=True)

    cancellationLimitDate: datetime = sa.Column(sa.DateTime, nullable=False)

    cancellationReason = sa.Column(
        "cancellationReason",
        sa.Enum(
            CollectiveBookingCancellationReasons,
            values_callable=lambda x: [reason.value for reason in CollectiveBookingCancellationReasons],
        ),
        nullable=True,
    )

    status: CollectiveBookingStatus = sa.Column(
        sa.Enum(CollectiveBookingStatus), nullable=False, default=CollectiveBookingStatus.CONFIRMED
    )

    Index("ix_collective_booking_status", status)

    reimbursementDate = sa.Column(sa.DateTime, nullable=True)

    educationalInstitutionId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("educational_institution.id"), nullable=False
    )
    educationalInstitution: Mapped["EducationalInstitution"] = relationship(
        EducationalInstitution, foreign_keys=[educationalInstitutionId], backref="collectiveBookings"
    )

    educationalYearId: str = sa.Column(sa.String(30), sa.ForeignKey("educational_year.adageId"), nullable=False)
    educationalYear: Mapped["EducationalYear"] = relationship(EducationalYear, foreign_keys=[educationalYearId])

    Index("ix_collective_booking_educationalYear_and_institution", educationalYearId, educationalInstitutionId)

    confirmationDate = sa.Column(sa.DateTime, nullable=True)
    confirmationLimitDate: datetime = sa.Column(sa.DateTime, nullable=False)

    educationalRedactorId: int = sa.Column(
        sa.BigInteger,
        sa.ForeignKey("educational_redactor.id"),
        nullable=False,
        index=True,
    )
    educationalRedactor: RelationshipProperty["EducationalRedactor"] = relationship(  # type: ignore [misc]
        EducationalRedactor,
        back_populates="collectiveBookings",
        uselist=False,
    )

    def mark_as_used(self) -> None:
        if self.is_used_or_reimbursed:
            raise booking_exceptions.BookingHasAlreadyBeenUsed()
        if self.status is CollectiveBookingStatus.CANCELLED:
            raise booking_exceptions.BookingIsCancelled()
        if self.status is CollectiveBookingStatus.PENDING:
            raise booking_exceptions.BookingNotConfirmed()
        self.dateUsed = datetime.utcnow()
        self.status = CollectiveBookingStatus.USED

    def mark_as_unused_set_confirmed(self) -> None:
        self.dateUsed = None
        self.status = CollectiveBookingStatus.CONFIRMED

    def cancel_booking(self, cancel_even_if_used: bool = False) -> None:
        if self.status is CollectiveBookingStatus.CANCELLED:
            raise booking_exceptions.BookingIsAlreadyCancelled()
        if self.status is CollectiveBookingStatus.REIMBURSED:
            raise booking_exceptions.BookingIsAlreadyUsed()
        if self.status is CollectiveBookingStatus.USED and not cancel_even_if_used:
            raise booking_exceptions.BookingIsAlreadyUsed()
        self.status = CollectiveBookingStatus.CANCELLED
        self.cancellationDate = datetime.utcnow()

    def uncancel_booking_set_used(self) -> None:
        if not (self.status is CollectiveBookingStatus.CANCELLED):
            raise booking_exceptions.BookingIsNotCancelledCannotBeUncancelled()
        self.cancellationDate = None
        self.cancellationReason = None
        self.status = CollectiveBookingStatus.USED
        self.dateUsed = datetime.utcnow()

    def mark_as_confirmed(self) -> None:
        if self.has_confirmation_limit_date_passed():
            raise booking_exceptions.ConfirmationLimitDateHasPassed()

        self.status = CollectiveBookingStatus.CONFIRMED
        self.confirmationDate = datetime.utcnow()

    @hybrid_property
    def isConfirmed(self) -> BinaryExpression:
        return self.cancellationLimitDate <= datetime.utcnow()

    @isConfirmed.expression  # type: ignore[no-redef]
    def isConfirmed(cls) -> BinaryExpression:  # pylint: disable=no-self-argument
        return cls.cancellationLimitDate <= datetime.utcnow()

    @hybrid_property
    def is_used_or_reimbursed(self) -> bool:
        return self.status in [CollectiveBookingStatus.USED, CollectiveBookingStatus.REIMBURSED]

    @is_used_or_reimbursed.expression  # type: ignore[no-redef]
    def is_used_or_reimbursed(cls) -> bool:  # pylint: disable=no-self-argument
        return cls.status.in_([CollectiveBookingStatus.USED, CollectiveBookingStatus.REIMBURSED])

    @property
    def userName(self) -> str | None:
        return f"{self.educationalRedactor.firstName} {self.educationalRedactor.lastName}"

    def has_confirmation_limit_date_passed(self) -> bool:
        return self.confirmationLimitDate <= datetime.utcnow()

    def mark_as_refused(self) -> None:

        if self.status != CollectiveBookingStatus.PENDING and self.cancellationLimitDate <= datetime.utcnow():
            raise exceptions.EducationalBookingNotRefusable()

        try:
            self.cancel_booking()
            self.cancellationReason = CollectiveBookingCancellationReasons.REFUSED_BY_INSTITUTE
        except booking_exceptions.BookingIsAlreadyUsed:
            raise exceptions.EducationalBookingNotRefusable()
        except booking_exceptions.BookingIsAlreadyCancelled:
            raise exceptions.EducationalBookingAlreadyCancelled()

        self.status = CollectiveBookingStatus.CANCELLED


class CollectiveOfferTemplateDomain(Base, Model):  # type: ignore [valid-type, misc]
    """An association table between CollectiveOfferTemplate and
    EducationalDomain for their many-to-many relationship.
    """

    __tablename__ = "collective_offer_template_domain"

    collectiveOfferTemplateId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("collective_offer_template.id", ondelete="CASCADE"), index=True, primary_key=True
    )
    educationalDomainId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("educational_domain.id", ondelete="CASCADE"), index=True, primary_key=True
    )


class CollectiveOfferDomain(Base, Model):  # type: ignore [valid-type, misc]
    """An association table between CollectiveOffer and
    EducationalDomain for their many-to-many relationship.
    """

    __tablename__ = "collective_offer_domain"

    collectiveOfferId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("collective_offer.id", ondelete="CASCADE"), index=True, primary_key=True
    )
    educationalDomainId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("educational_domain.id", ondelete="CASCADE"), index=True, primary_key=True
    )


class EducationalDomainVenue(Base, Model):  # type: ignore[valid-type, misc]
    __tablename__ = "educational_domain_venue"
    id: int = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    educationalDomainId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("educational_domain.id", ondelete="CASCADE"), index=True, nullable=False
    )
    venueId: int = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        sa.UniqueConstraint(
            "educationalDomainId",
            "venueId",
            name="unique_educational_domain_venue",
        ),
    )


class EducationalDomain(PcObject, Base, Model):  # type: ignore [valid-type, misc]
    __tablename__ = "educational_domain"

    name: str = sa.Column(sa.Text, nullable=False)
    venues: "Mapped[list[Venue]]" = sa.orm.relationship(
        "Venue", back_populates="collectiveDomains", secondary="educational_domain_venue"
    )
    collectiveOffers: RelationshipProperty[list["CollectiveOffer"]] = relationship(
        "CollectiveOffer", secondary="collective_offer_domain", back_populates="domains"
    )

    collectiveOfferTemplates: RelationshipProperty[list["CollectiveOfferTemplate"]] = relationship(
        "CollectiveOfferTemplate", secondary="collective_offer_template_domain", back_populates="domains"
    )


CollectiveBooking.trig_update_cancellationDate_on_isCancelled_ddl = f"""
    CREATE OR REPLACE FUNCTION save_collective_booking_cancellation_date()
    RETURNS TRIGGER AS $$
    BEGIN
        IF NEW.status = '{CollectiveBookingStatus.CANCELLED.value}' AND OLD."cancellationDate" IS NULL AND NEW."cancellationDate" THEN
            NEW."cancellationDate" = NOW();
        ELSIF NEW.status != '{CollectiveBookingStatus.CANCELLED.value}' THEN
            NEW."cancellationDate" = NULL;
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS stock_update_collective_booking_cancellation_date ON collective_booking;

    CREATE TRIGGER stock_update_collective_booking_cancellation_date
    BEFORE INSERT OR UPDATE OF status ON collective_booking
    FOR EACH ROW
    EXECUTE PROCEDURE save_collective_booking_cancellation_date()
    """

sa.event.listen(
    CollectiveBooking.__table__,
    "after_create",
    sa.DDL(CollectiveBooking.trig_update_cancellationDate_on_isCancelled_ddl),
)


@dataclasses.dataclass
class AdageApiResult:
    sent_data: dict
    response: dict
    success: bool
