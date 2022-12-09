from datetime import datetime
from decimal import Decimal
import enum
import random
import typing

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.ext.mutable import MutableList
import sqlalchemy.orm as sa_orm
from sqlalchemy.orm import relationship
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.sql.elements import False_
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import Index
from sqlalchemy.sql.selectable import Exists
from sqlalchemy.sql.sqltypes import Boolean
from sqlalchemy.sql.sqltypes import Numeric

from pcapi import settings
from pcapi.core.bookings import exceptions as booking_exceptions
from pcapi.core.categories import subcategories
from pcapi.core.object_storage import delete_public_object
from pcapi.core.object_storage import store_public_object
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models import offer_mixin
from pcapi.models.accessibility_mixin import AccessibilityMixin
from pcapi.models.pc_object import PcObject
from pcapi.utils.image_conversion import CropParams
from pcapi.utils.image_conversion import ImageRatio
from pcapi.utils.image_conversion import process_original_image
from pcapi.utils.image_conversion import standardize_image


if typing.TYPE_CHECKING:
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


class CollectiveBookingCancellationReasons(enum.Enum):
    OFFERER = "OFFERER"
    BENEFICIARY = "BENEFICIARY"
    EXPIRED = "EXPIRED"
    FRAUD = "FRAUD"
    REFUSED_BY_INSTITUTE = "REFUSED_BY_INSTITUTE"
    REFUSED_BY_HEADMASTER = "REFUSED_BY_HEADMASTER"


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


@sa.orm.declarative_mixin
class HasImageMixin:
    BASE_URL = f"{settings.OBJECT_STORAGE_URL}/{settings.THUMBS_FOLDER_NAME}"
    FOLDER = settings.THUMBS_FOLDER_NAME

    id: sa.orm.Mapped[int]
    imageId = sa.Column(sa.Text, nullable=True)
    imageCrop: dict | None = sa.Column(MutableDict.as_mutable(postgresql.json.JSONB), nullable=True)
    imageCredit = sa.Column(sa.Text, nullable=True)
    # Whether or not we also stored the original image in the storage bucket.
    imageHasOriginal = sa.Column(sa.Boolean, nullable=True)

    @sa.ext.hybrid.hybrid_property
    def hasImage(self) -> bool:
        return self.imageId is not None

    @hasImage.expression  # type: ignore[no-redef]
    def hasImage(cls) -> bool:  # pylint: disable=no-self-argument
        return cls.imageId != None

    def _get_image_storage_id(self, original: bool = False) -> str:
        original_suffix = "_original" if original else ""
        if self.id is None:
            raise ValueError("Trying to get image_storage_id for an unsaved object")
        return f"{type(self).__name__.lower()}/{self.imageId}{original_suffix}.jpg"

    def _generate_new_image_id(self, old_id: str | None) -> str:
        """Generate a unique id for the image. The generated id is a string like:
        "xxxxxxxxxxyyyyyyy" where "xxxxxxxxxx" part is the 10 digit, zero paded, object id and the "yyyyyyy" part is a
        7 digit random number.

        The object id part is there to simplify imageId collision avoidance.
        The method avoid collision on random number.
        """
        new_id = old_id
        while new_id == old_id:
            new_id = str(self.id).zfill(10) + str(random.randrange(1_000_000, 10_000_000))
        return typing.cast(str, new_id)

    @property
    def imageUrl(self) -> str | None:
        return self._image_url(original=False)

    @property
    def imageOriginalUrl(self) -> str | None:
        return self._image_url(original=True)

    def _image_url(self, original: bool = False) -> str | None:
        if not self.hasImage or (self.hasImage and original and not self.imageHasOriginal):
            return None
        return f"{self.BASE_URL}/{self._get_image_storage_id(original=original)}"

    def set_image(
        self,
        image: bytes,
        credit: str,
        crop_params: CropParams,
        ratio: ImageRatio = ImageRatio.PORTRAIT,
        keep_original: bool = False,
    ) -> None:
        old_id = self.imageId
        if self.hasImage:  # pylint: disable=using-constant-test
            self.delete_image()

        self.imageId = self._generate_new_image_id(old_id)
        self.imageCrop = crop_params.__dict__ if keep_original else None
        self.imageCredit = credit
        self.imageHasOriginal = keep_original

        store_public_object(
            folder=self.FOLDER,
            object_id=self._get_image_storage_id(),
            blob=standardize_image(content=image, ratio=ratio, crop_params=crop_params),
            content_type="image/jpeg",
        )
        if keep_original:
            store_public_object(
                folder=self.FOLDER,
                object_id=self._get_image_storage_id(original=True),
                blob=process_original_image(content=image, resize=False),
                content_type="image/jpeg",
            )

    def delete_image(self) -> None:
        delete_public_object(
            folder=self.FOLDER,
            object_id=self._get_image_storage_id(),
        )
        if self.imageHasOriginal:
            delete_public_object(
                folder=self.FOLDER,
                object_id=self._get_image_storage_id(original=True),
            )
        self.imageCrop = None
        self.imageCredit = None
        self.imageHasOriginal = None
        self.imageId = None


class CollectiveOffer(
    PcObject, Base, offer_mixin.ValidationMixin, AccessibilityMixin, offer_mixin.StatusMixin, HasImageMixin, Model
):
    __tablename__ = "collective_offer"

    offerId = sa.Column(sa.BigInteger, nullable=True)

    isActive: bool = sa.Column(sa.Boolean, nullable=False, server_default=sa.sql.expression.true(), default=True)

    venueId: int = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id"), nullable=False, index=True)

    venue: sa_orm.Mapped["Venue"] = sa.orm.relationship(
        "Venue", foreign_keys=[venueId], back_populates="collectiveOffers"
    )

    name: str = sa.Column(sa.String(140), nullable=False)

    bookingEmails: list[str] = sa.Column(
        MutableList.as_mutable(postgresql.ARRAY(sa.String)),
        nullable=False,
        server_default="{}",
    )

    description = sa.Column(sa.Text, nullable=False, server_default="", default="")

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

    institution: sa_orm.Mapped["EducationalInstitution | None"] = relationship(
        "EducationalInstitution", foreign_keys=[institutionId], back_populates="collectiveOffers"
    )

    templateId: int | None = sa.Column(
        sa.BigInteger, sa.ForeignKey("collective_offer_template.id"), index=True, nullable=True
    )

    template: sa_orm.Mapped["CollectiveOfferTemplate | None"] = sa.orm.relationship(
        "CollectiveOfferTemplate", foreign_keys=[templateId], back_populates="collectiveOffers"
    )

    isPublicApi: bool = sa.Column(sa.Boolean, nullable=False, server_default=sa.sql.expression.false(), default=False)

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

    @sa.ext.hybrid.hybrid_property
    def isEvent(self) -> bool:
        return self.subcategory.is_event

    @isEvent.expression  # type: ignore [no-redef]
    def isEvent(cls) -> bool:  # pylint: disable=no-self-argument
        return cls.subcategoryId.in_(subcategories.EVENT_SUBCATEGORIES)

    @property
    def is_cancellable_from_offerer(self) -> bool:
        if self.collectiveStock is None:
            return False
        return self.collectiveStock.is_cancellable_from_offerer


class CollectiveOfferTemplate(
    PcObject, offer_mixin.ValidationMixin, AccessibilityMixin, offer_mixin.StatusMixin, HasImageMixin, Base, Model
):
    __tablename__ = "collective_offer_template"

    offerId = sa.Column(sa.BigInteger, nullable=True)

    isActive: bool = sa.Column(sa.Boolean, nullable=False, server_default=sa.sql.expression.true(), default=True)

    venueId: int = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id"), nullable=False, index=True)

    venue: sa_orm.Mapped["Venue"] = sa.orm.relationship(
        "Venue", foreign_keys=[venueId], back_populates="collectiveOfferTemplates"
    )

    name: str = sa.Column(sa.String(140), nullable=False)

    description = sa.Column(sa.Text, nullable=False, server_default="", default="")

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

    bookingEmails: list[str] = sa.Column(
        MutableList.as_mutable(postgresql.ARRAY(sa.String)),
        nullable=False,
        server_default="{}",
    )

    contactEmail: str = sa.Column(sa.String(120), nullable=False)

    contactPhone: str = sa.Column(sa.Text, nullable=False)

    offerVenue: dict = sa.Column(MutableDict.as_mutable(postgresql.json.JSONB), nullable=False)

    interventionArea: list[str] = sa.Column(
        MutableList.as_mutable(postgresql.ARRAY(sa.Text())), nullable=False, server_default="{}"
    )

    domains: list["EducationalDomain"] = relationship(
        "EducationalDomain", secondary="collective_offer_template_domain", back_populates="collectiveOfferTemplates"
    )

    collectiveOffers: sa_orm.Mapped["CollectiveOffer"] = relationship("CollectiveOffer", back_populates="template")

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
            and self.venue.managingOfferer.isActive
            and self.venue.managingOfferer.isValidated
        )

    is_eligible_for_search = isReleased

    @property
    def subcategory(self) -> subcategories.Subcategory:
        if self.subcategoryId not in subcategories.ALL_SUBCATEGORIES_DICT:
            raise ValueError(f"Unexpected subcategoryId '{self.subcategoryId}' for collective offer template {self.id}")
        return subcategories.ALL_SUBCATEGORIES_DICT[self.subcategoryId]

    @sa.ext.hybrid.hybrid_property
    def isEvent(self) -> bool:
        return self.subcategory.is_event

    @isEvent.expression  # type: ignore [no-redef]
    def isEvent(cls) -> bool:  # pylint: disable=no-self-argument
        return cls.subcategoryId.in_(subcategories.EVENT_SUBCATEGORIES)

    @property
    def is_cancellable_from_offerer(self) -> bool:
        return False

    @classmethod
    def create_from_collective_offer(
        cls, collective_offer: CollectiveOffer, price_detail: str | None = None
    ) -> "CollectiveOfferTemplate":
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
            "bookingEmails",
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


class CollectiveStock(PcObject, Base, Model):
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

    collectiveOffer: sa_orm.Mapped["CollectiveOffer"] = sa.orm.relationship(
        "CollectiveOffer", foreign_keys=[collectiveOfferId], uselist=False, back_populates="collectiveStock"
    )

    collectiveBookings: list["CollectiveBooking"] = relationship("CollectiveBooking", back_populates="collectiveStock")

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
        for booking in self.collectiveBookings:
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
        for booking in self.collectiveBookings:
            if booking.status != CollectiveBookingStatus.CANCELLED:
                return True
        return False

    @property
    def is_cancellable_from_offerer(self) -> bool:
        if any(booking.is_cancellable_from_offerer for booking in self.collectiveBookings):
            return True

        return False


class EducationalInstitution(PcObject, Base, Model):
    __tablename__ = "educational_institution"

    institutionId: str = sa.Column(sa.String(30), nullable=False, unique=True, index=True)

    institutionType = sa.Column(sa.String(80), nullable=False)

    name: str = sa.Column(sa.Text(), nullable=False)

    city: str = sa.Column(sa.Text(), nullable=False)

    postalCode: str = sa.Column(sa.String(10), nullable=False)

    email = sa.Column(sa.Text(), nullable=True)

    phoneNumber: str = sa.Column(sa.String(30), nullable=False)

    collectiveOffers: list["CollectiveOffer"] = relationship("CollectiveOffer", back_populates="institution")

    isActive: bool = sa.Column(sa.Boolean, nullable=False, default=True)


class EducationalYear(PcObject, Base, Model):
    __tablename__ = "educational_year"

    adageId: str = sa.Column(sa.String(30), unique=True, nullable=False)

    beginningDate: datetime = sa.Column(sa.DateTime, nullable=False)

    expirationDate: datetime = sa.Column(sa.DateTime, nullable=False)


class EducationalDeposit(PcObject, Base, Model):
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

    educationalYear: sa_orm.Mapped["EducationalYear"] = relationship(
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
        from pcapi.core.educational import exceptions

        if self.amount < total_amount_after_booking:
            raise exceptions.InsufficientFund()

        if self.get_amount() < total_amount_after_booking and not self.isFinal:
            raise exceptions.InsufficientTemporaryFund()

        return


class EducationalRedactor(PcObject, Base, Model):

    __tablename__ = "educational_redactor"

    email: str = sa.Column(sa.String(120), nullable=False, unique=True, index=True)

    firstName = sa.Column(sa.String(128), nullable=True)

    lastName = sa.Column(sa.String(128), nullable=True)

    civility = sa.Column(sa.String(20), nullable=True)

    collectiveBookings: list["CollectiveBooking"] = relationship(
        "CollectiveBooking", back_populates="educationalRedactor"
    )


class CollectiveBooking(PcObject, Base, Model):
    __tablename__ = "collective_booking"

    bookingId = sa.Column(sa.BigInteger)

    dateCreated: datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)
    Index("ix_collective_booking_date_created", dateCreated)

    dateUsed = sa.Column(sa.DateTime, nullable=True, index=True)

    collectiveStockId: int = sa.Column(sa.BigInteger, sa.ForeignKey("collective_stock.id"), index=True, nullable=False)

    collectiveStock: sa_orm.Mapped["CollectiveStock"] = relationship(
        "CollectiveStock", foreign_keys=[collectiveStockId], back_populates="collectiveBookings"
    )

    venueId: int = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id"), index=True, nullable=False)

    venue: sa_orm.Mapped["Venue"] = relationship("Venue", foreign_keys=[venueId], backref="collectiveBookings")

    offererId: int = sa.Column(sa.BigInteger, sa.ForeignKey("offerer.id"), index=True, nullable=False)

    offerer: sa_orm.Mapped["Offerer"] = relationship("Offerer", foreign_keys=[offererId], backref="collectiveBookings")

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
    educationalInstitution: sa_orm.Mapped["EducationalInstitution"] = relationship(
        EducationalInstitution, foreign_keys=[educationalInstitutionId], backref="collectiveBookings"
    )

    educationalYearId: str = sa.Column(sa.String(30), sa.ForeignKey("educational_year.adageId"), nullable=False)
    educationalYear: sa_orm.Mapped["EducationalYear"] = relationship(EducationalYear, foreign_keys=[educationalYearId])

    Index("ix_collective_booking_educationalYear_and_institution", educationalYearId, educationalInstitutionId)

    confirmationDate = sa.Column(sa.DateTime, nullable=True)
    confirmationLimitDate: datetime = sa.Column(sa.DateTime, nullable=False)

    educationalRedactorId: int = sa.Column(
        sa.BigInteger,
        sa.ForeignKey("educational_redactor.id"),
        nullable=False,
        index=True,
    )
    educationalRedactor: sa_orm.Mapped["EducationalRedactor"] = relationship(
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

    def cancel_booking(
        self,
        reason: CollectiveBookingCancellationReasons,
        cancel_even_if_used: bool = False,
    ) -> None:
        from pcapi.core.educational import exceptions

        if self.status is CollectiveBookingStatus.CANCELLED:
            raise exceptions.CollectiveBookingAlreadyCancelled()
        if self.status is CollectiveBookingStatus.REIMBURSED:
            raise exceptions.CollectiveBookingIsAlreadyUsed
        if self.status is CollectiveBookingStatus.USED and not cancel_even_if_used:
            raise exceptions.CollectiveBookingIsAlreadyUsed
        self.status = CollectiveBookingStatus.CANCELLED
        self.cancellationDate = datetime.utcnow()
        self.cancellationReason = reason
        self.dateUsed = None

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
        from pcapi.core.educational import exceptions

        if self.status != CollectiveBookingStatus.PENDING and self.cancellationLimitDate <= datetime.utcnow():
            raise exceptions.EducationalBookingNotRefusable()
        cancellation_reason = (
            CollectiveBookingCancellationReasons.REFUSED_BY_INSTITUTE
            if self.status == CollectiveBookingStatus.PENDING
            else CollectiveBookingCancellationReasons.REFUSED_BY_HEADMASTER
        )
        try:
            self.cancel_booking(cancellation_reason)
        except exceptions.CollectiveBookingIsAlreadyUsed:
            raise exceptions.EducationalBookingNotRefusable()

        self.status = CollectiveBookingStatus.CANCELLED

    @property
    def is_cancellable_from_offerer(self) -> bool:
        return self.status not in (
            CollectiveBookingStatus.USED,
            CollectiveBookingStatus.REIMBURSED,
            CollectiveBookingStatus.CANCELLED,
        )


class CollectiveOfferTemplateDomain(Base, Model):
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


class CollectiveOfferDomain(Base, Model):
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


class EducationalDomainVenue(Base, Model):
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


class EducationalDomain(PcObject, Base, Model):
    __tablename__ = "educational_domain"

    name: str = sa.Column(sa.Text, nullable=False)
    venues: sa_orm.Mapped[list["Venue"]] = sa.orm.relationship(
        "Venue", back_populates="collectiveDomains", secondary="educational_domain_venue"
    )
    collectiveOffers: list["CollectiveOffer"] = relationship(
        "CollectiveOffer", secondary="collective_offer_domain", back_populates="domains"
    )

    collectiveOfferTemplates: list["CollectiveOfferTemplate"] = relationship(
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
