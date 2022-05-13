from __future__ import annotations

import dataclasses
from datetime import datetime
from decimal import Decimal
import enum
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import Index
from sqlalchemy.sql.sqltypes import Boolean
from sqlalchemy.sql.sqltypes import Numeric

from pcapi.core.bookings import exceptions as booking_exceptions
from pcapi.core.categories import subcategories
from pcapi.core.educational import exceptions
from pcapi.core.offers.models import Offer
from pcapi.models import Model
from pcapi.models.offer_mixin import AccessibilityMixin
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.models.offer_mixin import StatusMixin
from pcapi.models.offer_mixin import ValidationMixin
from pcapi.models.pc_object import PcObject


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


class CollectiveOffer(PcObject, ValidationMixin, AccessibilityMixin, StatusMixin, Model):  # type: ignore[valid-type, misc]
    __tablename__ = "collective_offer"

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)

    offerId = sa.Column(sa.BigInteger, nullable=True)

    isActive = sa.Column(sa.Boolean, nullable=False, server_default=sa.sql.expression.true(), default=True)

    venueId = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id"), nullable=False, index=True)

    venue = sa.orm.relationship("Venue", foreign_keys=[venueId], back_populates="collectiveOffers")  # type: ignore [misc]

    name = sa.Column(sa.String(140), nullable=False)

    bookingEmail = sa.Column(sa.String(120), nullable=True)

    description = sa.Column(sa.Text, nullable=True)

    durationMinutes = sa.Column(sa.Integer, nullable=True)

    dateCreated = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)

    subcategoryId = sa.Column(sa.Text, nullable=False, index=True)

    dateUpdated: datetime = sa.Column(sa.DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)  # type: ignore [assignment]

    students: list[StudentLevels] = sa.Column(  # type: ignore [assignment]
        MutableList.as_mutable(postgresql.ARRAY(sa.Enum(StudentLevels))),
        nullable=False,
        server_default="{}",
    )

    collectiveStock = relationship("CollectiveStock", back_populates="collectiveOffer", uselist=False)

    contactEmail = sa.Column(sa.String(120), nullable=False)

    contactPhone = sa.Column(sa.Text, nullable=False)

    offerVenue = sa.Column(MutableDict.as_mutable(postgresql.json.JSONB), nullable=False)  # type: ignore [attr-defined]

    @property
    def isEducational(self) -> bool:
        # FIXME (rpaoloni, 2022-03-7): Remove legacy support layer
        return True

    @sa.ext.hybrid.hybrid_property
    def isSoldOut(self):
        return self.collectiveStock.isSoldOut

    @isSoldOut.expression  # type: ignore[no-redef]
    def isSoldOut(cls):  # pylint: disable=no-self-argument
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
            and self.validation == OfferValidationStatus.APPROVED
            and self.venue.isValidated
            and self.venue.managingOfferer.isActive
            and self.venue.managingOfferer.isValidated
        )

    @property
    def hasBookingLimitDatetimePassed(self):  # type: ignore [no-untyped-def]
        if self.collectiveStock:
            return self.collectiveStock.hasBookingLimitDatetimePassed
        return False

    @sa.ext.hybrid.hybrid_property
    def hasBookingLimitDatetimesPassed(self) -> bool:
        if not self.collectiveStock:
            return False
        return self.collectiveStock.hasBookingLimitDatetimePassed

    @hasBookingLimitDatetimesPassed.expression  # type: ignore[no-redef]
    def hasBookingLimitDatetimesPassed(cls):  # pylint: disable=no-self-argument
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
    def create_from_offer(cls, offer: Offer) -> CollectiveOffer:
        list_of_common_attributes = [
            "isActive",
            "venue",
            "name",
            "description",
            "durationMinutes",
            "dateCreated",
            "subcategoryId",
            "dateUpdated",
            "bookingEmail",
            "lastValidationDate",
            "validation",
            "audioDisabilityCompliant",
            "mentalDisabilityCompliant",
            "motorDisabilityCompliant",
            "visualDisabilityCompliant",
        ]
        offer_mapping = {x: getattr(offer, x) for x in list_of_common_attributes}
        students = [StudentLevels(x).name for x in offer.extraData.get("students", [])]  # type: ignore [union-attr]
        return cls(
            **offer_mapping,
            offerId=offer.id,
            contactEmail=offer.extraData.get("contactEmail"),  # type: ignore [union-attr]
            contactPhone=offer.extraData.get("contactPhone", "").strip(),  # type: ignore [union-attr]
            offerVenue=offer.extraData.get("offerVenue"),  # type: ignore [union-attr]
            students=students,
        )

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
        ]
        offer_mapping = {x: getattr(collective_offer_template, x) for x in list_of_common_attributes}
        return cls(
            **offer_mapping,
            offerId=collective_offer_template.offerId,
        )


class CollectiveOfferTemplate(PcObject, ValidationMixin, AccessibilityMixin, StatusMixin, Model):  # type: ignore[valid-type, misc]
    __tablename__ = "collective_offer_template"

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)

    offerId = sa.Column(sa.BigInteger, nullable=True)

    isActive = sa.Column(sa.Boolean, nullable=False, server_default=sa.sql.expression.true(), default=True)

    venueId = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id"), nullable=False, index=True)

    venue = sa.orm.relationship("Venue", foreign_keys=[venueId], back_populates="collectiveOfferTemplates")  # type: ignore [misc]

    name = sa.Column(sa.String(140), nullable=False)

    description = sa.Column(sa.Text, nullable=True)

    durationMinutes = sa.Column(sa.Integer, nullable=True)

    dateCreated = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)

    subcategoryId = sa.Column(sa.Text, nullable=False, index=True)

    dateUpdated: datetime = sa.Column(sa.DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)  # type: ignore [assignment]

    students: list[StudentLevels] = sa.Column(  # type: ignore [assignment]
        MutableList.as_mutable(postgresql.ARRAY(sa.Enum(StudentLevels))),
        nullable=False,
        server_default="{}",
    )

    priceDetail = sa.Column(sa.Text, nullable=True)

    bookingEmail = sa.Column(sa.String(120), nullable=True)

    contactEmail = sa.Column(sa.String(120), nullable=False)

    contactPhone = sa.Column(sa.Text, nullable=False)

    offerVenue = sa.Column(MutableDict.as_mutable(postgresql.json.JSONB), nullable=False)  # type: ignore [attr-defined]

    @property
    def isEducational(self) -> bool:
        # FIXME (rpaoloni, 2022-05-09): Remove legacy support layer
        return True

    @sa.ext.hybrid.hybrid_property
    def hasBookingLimitDatetimesPassed(self) -> bool:
        # this property is here for compatibility reasons
        return False

    @hasBookingLimitDatetimesPassed.expression  # type: ignore[no-redef]
    def hasBookingLimitDatetimesPassed(cls):  # pylint: disable=no-self-argument
        # this property is here for compatibility reasons
        return sa.sql.expression.false()

    @sa.ext.hybrid.hybrid_property
    def isSoldOut(self):
        # this property is here for compatibility reasons
        return False

    @isSoldOut.expression  # type: ignore[no-redef]
    def isSoldOut(cls):  # pylint: disable=no-self-argument
        # this property is here for compatibility reasons
        return sa.sql.expression.false()

    @property
    def isReleased(self) -> bool:
        return (
            self.isActive
            and self.validation == OfferValidationStatus.APPROVED
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
        ]
        collective_offer_mapping = {x: getattr(collective_offer, x) for x in list_of_common_attributes}
        return cls(
            **collective_offer_mapping,
            offerId=collective_offer.offerId,
            priceDetail=price_detail,
        )

    @classmethod
    def create_from_offer(cls, offer: Offer, price_detail: str = None) -> CollectiveOfferTemplate:
        list_of_common_attributes = [
            "isActive",
            "venue",
            "name",
            "description",
            "durationMinutes",
            "dateCreated",
            "subcategoryId",
            "dateUpdated",
            "bookingEmail",
            "lastValidationDate",
            "validation",
            "audioDisabilityCompliant",
            "mentalDisabilityCompliant",
            "motorDisabilityCompliant",
            "visualDisabilityCompliant",
        ]
        offer_mapping = {x: getattr(offer, x) for x in list_of_common_attributes}
        students = [StudentLevels(x).name for x in offer.extraData.get("students", [])]  # type: ignore [union-attr]
        return cls(
            **offer_mapping,
            offerId=offer.id,
            contactEmail=offer.extraData.get("contactEmail"),  # type: ignore [union-attr]
            contactPhone=offer.extraData.get("contactPhone", "").strip(),  # type: ignore [union-attr]
            offerVenue=offer.extraData.get("offerVenue"),  # type: ignore [union-attr]
            students=students,
            priceDetail=price_detail,
        )


class CollectiveStock(PcObject, Model):  # type: ignore[valid-type, misc]
    __tablename__ = "collective_stock"

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)

    stockId = sa.Column(sa.BigInteger, nullable=True)

    dateCreated = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow, server_default=sa.func.now())

    dateModified = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    beginningDatetime = sa.Column(sa.DateTime, index=True, nullable=False)

    collectiveOfferId = sa.Column(
        sa.BigInteger, sa.ForeignKey("collective_offer.id"), index=True, nullable=False, unique=True
    )

    collectiveOffer = sa.orm.relationship(
        "CollectiveOffer", foreign_keys=[collectiveOfferId], uselist=False, back_populates="collectiveStock"
    )

    collectiveBookings = relationship("CollectiveBooking", back_populates="collectiveStock")

    price = sa.Column(
        sa.Numeric(10, 2), sa.CheckConstraint("price >= 0", name="check_price_is_not_negative"), nullable=False
    )

    bookingLimitDatetime = sa.Column(sa.DateTime, nullable=False)

    numberOfTickets = sa.Column(sa.Integer, nullable=False)

    priceDetail = sa.Column(sa.Text, nullable=True)

    @property
    def isBookable(self) -> bool:
        return not self.isExpired and self.collectiveOffer.isReleased and not self.isSoldOut

    @sa.ext.hybrid.hybrid_property
    def hasBookingLimitDatetimePassed(self):
        return self.bookingLimitDatetime <= datetime.utcnow()

    @hasBookingLimitDatetimePassed.expression  # type: ignore[no-redef]
    def hasBookingLimitDatetimePassed(cls):  # pylint: disable=no-self-argument
        return cls.bookingLimitDatetime <= sa.func.now()

    @sa.ext.hybrid.hybrid_property
    def isEventExpired(self):  # todo rewrite
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
        for booking in self.collectiveBookings:
            if booking.status != CollectiveBookingStatus.CANCELLED:
                return True
        return False


class EducationalInstitution(PcObject, Model):  # type: ignore[valid-type, misc]
    __tablename__ = "educational_institution"

    id: int = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)  # type: ignore [assignment]

    institutionId: str = sa.Column(sa.String(30), nullable=False, unique=True, index=True)  # type: ignore [assignment]

    name: str = sa.Column(sa.Text(), nullable=True)  # type: ignore [assignment]

    city: str = sa.Column(sa.Text(), nullable=True)  # type: ignore [assignment]

    postalCode: str = sa.Column(sa.String(10), nullable=True)  # type: ignore [assignment]

    email: str = sa.Column(sa.Text(), nullable=True)  # type: ignore [assignment]

    phoneNumber: str = sa.Column(sa.String(30), nullable=True)  # type: ignore [assignment]


class EducationalYear(PcObject, Model):  # type: ignore[valid-type, misc]
    __tablename__ = "educational_year"

    id: int = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)  # type: ignore [assignment]

    adageId: str = sa.Column(sa.String(30), unique=True, nullable=False)  # type: ignore [assignment]

    beginningDate: datetime = sa.Column(sa.DateTime, nullable=False)  # type: ignore [assignment]

    expirationDate: datetime = sa.Column(sa.DateTime, nullable=False)  # type: ignore [assignment]


class EducationalDeposit(PcObject, Model):  # type: ignore[valid-type, misc]
    __tablename__ = "educational_deposit"

    TEMPORARY_FUND_AVAILABLE_RATIO = 0.8

    id: int = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)  # type: ignore [assignment]

    educationalInstitutionId = sa.Column(
        sa.BigInteger, sa.ForeignKey("educational_institution.id"), index=True, nullable=False
    )

    educationalInstitution: EducationalInstitution = relationship(  # type: ignore [assignment]
        EducationalInstitution, foreign_keys=[educationalInstitutionId], backref="deposits"
    )

    educationalYearId = sa.Column(sa.String(30), sa.ForeignKey("educational_year.adageId"), index=True, nullable=False)

    educationalYear: EducationalYear = relationship(  # type: ignore [assignment]
        EducationalYear, foreign_keys=[educationalYearId], backref="deposits"
    )

    amount: Decimal = sa.Column(Numeric(10, 2), nullable=False)  # type: ignore [assignment]

    dateCreated: datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow, server_default=func.now())  # type: ignore [assignment]

    isFinal: bool = sa.Column(Boolean, nullable=False, default=True)  # type: ignore [assignment]

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


class EducationalRedactor(PcObject, Model):  # type: ignore[valid-type, misc]

    __tablename__ = "educational_redactor"

    id: int = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)  # type: ignore [assignment]

    email: str = sa.Column(sa.String(120), nullable=False, unique=True, index=True)  # type: ignore [assignment]

    firstName: str = sa.Column(sa.String(128), nullable=True)  # type: ignore [assignment]

    lastName: str = sa.Column(sa.String(128), nullable=True)  # type: ignore [assignment]

    civility: str = sa.Column(sa.String(20), nullable=True)  # type: ignore [assignment]

    educationalBookings = relationship(
        "EducationalBooking",
        back_populates="educationalRedactor",
    )

    collectiveBookings = relationship("CollectiveBooking", back_populates="educationalRedactor")


class EducationalBooking(PcObject, Model):  # type: ignore[valid-type, misc]
    __tablename__ = "educational_booking"

    id: int = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)  # type: ignore [assignment]

    educationalInstitutionId = sa.Column(sa.BigInteger, sa.ForeignKey("educational_institution.id"), nullable=False)
    educationalInstitution: EducationalInstitution = relationship(  # type: ignore [assignment]
        EducationalInstitution, foreign_keys=[educationalInstitutionId], backref="educationalBookings"
    )

    educationalYearId = sa.Column(sa.String(30), sa.ForeignKey("educational_year.adageId"), nullable=False)
    educationalYear: EducationalYear = relationship(EducationalYear, foreign_keys=[educationalYearId])  # type: ignore [assignment]

    Index("ix_educational_booking_educationalYear_and_institution", educationalYearId, educationalInstitutionId)

    status = sa.Column(
        "status",
        sa.Enum(EducationalBookingStatus),
        nullable=True,
    )

    confirmationDate: Optional[datetime] = sa.Column(sa.DateTime, nullable=True)  # type: ignore [assignment]
    confirmationLimitDate = sa.Column(sa.DateTime, nullable=True)

    booking = relationship(  # type: ignore [misc]
        "Booking",
        back_populates="educationalBooking",
        uselist=False,
        lazy="joined",
        innerjoin=True,
    )

    educationalRedactorId = sa.Column(
        sa.BigInteger,
        sa.ForeignKey("educational_redactor.id"),
        nullable=False,
        index=True,
    )
    educationalRedactor: EducationalRedactor = relationship(  # type: ignore [assignment]
        EducationalRedactor,
        back_populates="educationalBookings",
        uselist=False,
    )

    def has_confirmation_limit_date_passed(self) -> bool:
        return bool(self.confirmationLimitDate and self.confirmationLimitDate <= datetime.utcnow())

    def mark_as_refused(self) -> None:
        from pcapi.core.bookings import models as bookings_models

        if (
            self.booking.status != bookings_models.BookingStatus.PENDING
            and self.booking.cancellationLimitDate <= datetime.utcnow()
        ):
            raise exceptions.EducationalBookingNotRefusable()

        try:
            self.booking.cancel_booking()
            self.booking.cancellationReason = bookings_models.BookingCancellationReasons.REFUSED_BY_INSTITUTE
        except booking_exceptions.BookingIsAlreadyUsed:
            raise exceptions.EducationalBookingNotRefusable()
        except booking_exceptions.BookingIsAlreadyCancelled:
            raise exceptions.EducationalBookingAlreadyCancelled()

        self.status = EducationalBookingStatus.REFUSED  # type: ignore [assignment]


class CollectiveBooking(PcObject, Model):  # type: ignore[valid-type, misc]
    __tablename__ = "collective_booking"
    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)

    bookingId = sa.Column(sa.BigInteger)

    dateCreated = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)
    Index("ix_collective_booking_date_created", dateCreated)

    dateUsed = sa.Column(sa.DateTime, nullable=True, index=True)

    collectiveStockId = sa.Column(sa.BigInteger, sa.ForeignKey("collective_stock.id"), index=True, nullable=False)

    collectiveStock = relationship(
        "CollectiveStock", foreign_keys=[collectiveStockId], back_populates="collectiveBookings"
    )

    venueId = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id"), index=True, nullable=False)

    venue = relationship("Venue", foreign_keys=[venueId], backref="collectiveBookings")  # type: ignore [misc]

    offererId = sa.Column(sa.BigInteger, sa.ForeignKey("offerer.id"), index=True, nullable=False)

    offerer = relationship("Offerer", foreign_keys=[offererId], backref="collectiveBookings")  # type: ignore [misc]

    cancellationDate = sa.Column(sa.DateTime, nullable=True)

    cancellationLimitDate = sa.Column(sa.DateTime, nullable=False)

    cancellationReason = sa.Column(
        "cancellationReason",
        sa.Enum(
            CollectiveBookingCancellationReasons,
            values_callable=lambda x: [reason.value for reason in CollectiveBookingCancellationReasons],
        ),
        nullable=True,
    )

    status = sa.Column(
        "status", sa.Enum(CollectiveBookingStatus), nullable=False, default=CollectiveBookingStatus.CONFIRMED
    )

    Index("ix_collective_booking_status", status)

    reimbursementDate = sa.Column(sa.DateTime, nullable=True)

    educationalInstitutionId = sa.Column(sa.BigInteger, sa.ForeignKey("educational_institution.id"), nullable=False)
    educationalInstitution: EducationalInstitution = relationship(  # type: ignore [assignment]
        EducationalInstitution, foreign_keys=[educationalInstitutionId], backref="collectiveBookings"
    )

    educationalYearId = sa.Column(sa.String(30), sa.ForeignKey("educational_year.adageId"), nullable=False)
    educationalYear: EducationalYear = relationship(EducationalYear, foreign_keys=[educationalYearId])  # type: ignore [assignment]

    Index("ix_collective_booking_educationalYear_and_institution", educationalYearId, educationalInstitutionId)

    confirmationDate: Optional[datetime] = sa.Column(sa.DateTime, nullable=True)  # type: ignore [assignment]
    confirmationLimitDate = sa.Column(sa.DateTime, nullable=False)

    educationalRedactorId = sa.Column(
        sa.BigInteger,
        sa.ForeignKey("educational_redactor.id"),
        nullable=False,
        index=True,
    )
    educationalRedactor: EducationalRedactor = relationship(  # type: ignore [assignment]
        EducationalRedactor,
        back_populates="collectiveBookings",
        uselist=False,
    )

    def mark_as_used(self) -> None:
        if self.is_used_or_reimbursed:  # pylint: disable=using-constant-test
            raise booking_exceptions.BookingHasAlreadyBeenUsed()
        if self.status is CollectiveBookingStatus.CANCELLED:
            raise booking_exceptions.BookingIsCancelled()
        if self.status is CollectiveBookingStatus.PENDING:
            raise booking_exceptions.BookingNotConfirmed()
        self.dateUsed = datetime.utcnow()
        self.status = CollectiveBookingStatus.USED

    def mark_as_unused_set_confirmed(self) -> None:
        self.dateUsed = None
        self.status = CollectiveBookingStatus.CONFIRMED  # type: ignore [assignment]

    def cancel_booking(self, cancel_even_if_used: bool = False) -> None:
        if self.status is CollectiveBookingStatus.CANCELLED:
            raise booking_exceptions.BookingIsAlreadyCancelled()
        if self.status is CollectiveBookingStatus.REIMBURSED:
            raise booking_exceptions.BookingIsAlreadyUsed()
        if self.status is CollectiveBookingStatus.USED and not cancel_even_if_used:
            raise booking_exceptions.BookingIsAlreadyUsed()
        self.status = CollectiveBookingStatus.CANCELLED  # type: ignore [assignment]
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

        self.status = CollectiveBookingStatus.CONFIRMED  # type: ignore [assignment]
        self.confirmationDate = datetime.utcnow()

    @hybrid_property
    def isConfirmed(self):
        return self.cancellationLimitDate <= datetime.utcnow()

    @isConfirmed.expression  # type: ignore[no-redef]
    def isConfirmed(cls):  # pylint: disable=no-self-argument
        return cls.cancellationLimitDate <= datetime.utcnow()

    @hybrid_property
    def is_used_or_reimbursed(self) -> bool:
        return self.status in [CollectiveBookingStatus.USED, CollectiveBookingStatus.REIMBURSED]

    @is_used_or_reimbursed.expression  # type: ignore[no-redef]
    def is_used_or_reimbursed(cls) -> bool:  # pylint: disable=no-self-argument
        return cls.status.in_([CollectiveBookingStatus.USED, CollectiveBookingStatus.REIMBURSED])

    @property
    def userName(self) -> Optional[str]:
        return f"{self.educationalRedactor.firstName} {self.educationalRedactor.lastName}"

    def has_confirmation_limit_date_passed(self) -> bool:
        return self.confirmationLimitDate <= datetime.utcnow()

    def mark_as_refused(self) -> None:

        if self.status != CollectiveBookingStatus.PENDING and self.cancellationLimitDate <= datetime.utcnow():
            raise exceptions.EducationalBookingNotRefusable()

        try:
            self.cancel_booking()
            self.cancellationReason = CollectiveBookingCancellationReasons.REFUSED_BY_INSTITUTE  # type: ignore [assignment]
        except booking_exceptions.BookingIsAlreadyUsed:
            raise exceptions.EducationalBookingNotRefusable()
        except booking_exceptions.BookingIsAlreadyCancelled:
            raise exceptions.EducationalBookingAlreadyCancelled()

        self.status = CollectiveBookingStatus.CANCELLED  # type: ignore [assignment]


CollectiveBooking.trig_ddl = f"""
    CREATE OR REPLACE FUNCTION public.get_deposit_balance (deposit_id bigint, only_used_bookings boolean)
        RETURNS numeric
        AS $$
    DECLARE
        deposit_amount bigint := (SELECT CASE WHEN ("expirationDate" > now() OR "expirationDate" IS NULL) THEN amount ELSE 0 END amount FROM deposit WHERE id = deposit_id);
        sum_bookings numeric;
    BEGIN
        IF deposit_amount IS NULL
        THEN RAISE EXCEPTION 'the deposit was not found';
        END IF;

        SELECT
            COALESCE(SUM(amount * quantity), 0) INTO sum_bookings
        FROM
            booking
            JOIN individual_booking ON (booking."individualBookingId" = individual_booking.id)
        WHERE
            individual_booking."depositId" = deposit_id
            AND NOT booking.status = '{CollectiveBookingStatus.CANCELLED.value}'
            AND (NOT only_used_bookings OR booking.status in ('USED', 'REIMBURSED'));
        RETURN
            deposit_amount - sum_bookings;
        END;
    $$
    LANGUAGE plpgsql;

    CREATE OR REPLACE FUNCTION public.get_wallet_balance (user_id bigint, only_used_bookings boolean)
        RETURNS numeric
        AS $$
    DECLARE
        deposit_id bigint := (SELECT deposit.id FROM deposit WHERE "userId" = user_id  AND "expirationDate" > now());
    BEGIN
        RETURN
            CASE WHEN deposit_id IS NOT NULL THEN get_deposit_balance(deposit_id, only_used_bookings) ELSE 0 END;
    END;
    $$
    LANGUAGE plpgsql;

    CREATE OR REPLACE FUNCTION check_booking()
    RETURNS TRIGGER AS $$
    DECLARE
        lastStockUpdate date := (SELECT "dateModified" FROM stock WHERE id=NEW."stockId");
        deposit_id bigint := (SELECT individual_booking."depositId" FROM booking LEFT JOIN individual_booking ON individual_booking.id = booking."individualBookingId" WHERE booking.id=NEW.id);
    BEGIN
    IF EXISTS (SELECT "quantity" FROM stock WHERE id=NEW."stockId" AND "quantity" IS NOT NULL)
        AND (
            (SELECT "quantity" FROM stock WHERE id=NEW."stockId")
            <
            (SELECT SUM(quantity) FROM booking WHERE "stockId"=NEW."stockId" AND status != '{CollectiveBookingStatus.CANCELLED.value}')
            )
        THEN RAISE EXCEPTION 'tooManyBookings'
                    USING HINT = 'Number of bookings cannot exceed "stock.quantity"';
    END IF;

    IF (
        (NEW."educationalBookingId" IS NULL AND OLD."educationalBookingId" IS NULL)
        AND (NEW."individualBookingId" IS NOT NULL OR OLD."individualBookingId" IS NOT NULL)
        AND (
        -- If this is a new booking, we probably want to check the wallet.
        OLD IS NULL
        -- If we're updating an existing booking...
        OR (
            -- Check the wallet if we are changing the quantity or the amount
            -- The backend should never do that, but let's be defensive.
            (NEW."quantity" != OLD."quantity" OR NEW."amount" != OLD."amount")
            -- If amount and quantity are unchanged, we want to check the wallet
            -- only if we are UNcancelling a booking. (Users with no credits left
            -- should be able to cancel their booking. Also, their booking can
            -- be marked as used or not used.)
            OR (NEW.status != OLD.status AND OLD.status = '{CollectiveBookingStatus.CANCELLED.value}' AND NEW.status != '{CollectiveBookingStatus.CANCELLED.value}')
        )
        )
        AND (
            -- Allow to book free offers even with no credit left (or expired deposits)
            (deposit_id IS NULL AND NEW."amount" != 0)
            OR (deposit_id IS NOT NULL AND get_deposit_balance(deposit_id, false) < 0)
        )
    )
    THEN RAISE EXCEPTION 'insufficientFunds'
                USING HINT = 'The user does not have enough credit to book';
    END IF;

    RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS booking_update ON booking;
    CREATE CONSTRAINT TRIGGER booking_update
    AFTER INSERT
    OR UPDATE OF quantity, amount, status, "userId"
    ON booking
    FOR EACH ROW EXECUTE PROCEDURE check_booking()
    """
sa.event.listen(CollectiveBooking.__table__, "after_create", sa.DDL(CollectiveBooking.trig_ddl))

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
