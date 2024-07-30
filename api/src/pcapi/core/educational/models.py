from datetime import date
from datetime import datetime
import decimal
from decimal import Decimal
import enum
import random
import typing

import psycopg2.extras
import sqlalchemy as sa
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.ext.mutable import MutableList
import sqlalchemy.orm as sa_orm
from sqlalchemy.orm import declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.sql.elements import False_
from sqlalchemy.sql.elements import UnaryExpression
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import Index
from sqlalchemy.sql.selectable import Exists
from sqlalchemy.sql.sqltypes import Boolean
from sqlalchemy.sql.sqltypes import Numeric

from pcapi import settings
from pcapi.core.bookings import exceptions as booking_exceptions
from pcapi.core.categories import categories
from pcapi.core.categories import subcategories_v2 as subcategories
import pcapi.core.finance.models as finance_models
from pcapi.core.object_storage import delete_public_object
from pcapi.core.object_storage import store_public_object
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models import db
from pcapi.models import offer_mixin
from pcapi.models.accessibility_mixin import AccessibilityMixin
from pcapi.models.pc_object import PcObject
from pcapi.utils.db import MagicEnum
from pcapi.utils.image_conversion import CropParams
from pcapi.utils.image_conversion import ImageRatio
from pcapi.utils.image_conversion import process_original_image
from pcapi.utils.image_conversion import standardize_image
from pcapi.utils.phone_number import ParsedPhoneNumber


BIG_NUMBER_FOR_SORTING_ORDERS = 9999


if typing.TYPE_CHECKING:
    from pcapi.core.offerers.models import Offerer
    from pcapi.core.offerers.models import OffererAddress
    from pcapi.core.offerers.models import Venue
    from pcapi.core.offers.models import OfferValidationRule
    from pcapi.core.providers.models import Provider
    from pcapi.core.users.models import User


class StudentLevels(enum.Enum):
    ECOLES_MARSEILLE_MATERNELLE = "Écoles Marseille - Maternelle"
    ECOLES_MARSEILLE_CP_CE1_CE2 = "Écoles Marseille - CP, CE1, CE2"
    ECOLES_MARSEILLE_CM1_CM2 = "Écoles Marseille - CM1, CM2"
    COLLEGE6 = "Collège - 6e"
    COLLEGE5 = "Collège - 5e"
    COLLEGE4 = "Collège - 4e"
    COLLEGE3 = "Collège - 3e"
    CAP1 = "CAP - 1re année"
    CAP2 = "CAP - 2e année"
    GENERAL2 = "Lycée - Seconde"
    GENERAL1 = "Lycée - Première"
    GENERAL0 = "Lycée - Terminale"

    @classmethod
    def primary_levels(cls) -> set:
        return {
            cls.ECOLES_MARSEILLE_MATERNELLE,
            cls.ECOLES_MARSEILLE_CP_CE1_CE2,
            cls.ECOLES_MARSEILLE_CM1_CM2,
        }


class CollectiveBookingCancellationReasons(enum.Enum):
    OFFERER = "OFFERER"
    BENEFICIARY = "BENEFICIARY"
    EXPIRED = "EXPIRED"
    FRAUD = "FRAUD"
    REFUSED_BY_INSTITUTE = "REFUSED_BY_INSTITUTE"
    REFUSED_BY_HEADMASTER = "REFUSED_BY_HEADMASTER"
    PUBLIC_API = "PUBLIC_API"
    FINANCE_INCIDENT = "FINANCE_INCIDENT"
    BACKOFFICE = "BACKOFFICE"


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


class CollectiveOfferDisplayedStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    PENDING = "PENDING"
    REJECTED = "REJECTED"
    PREBOOKED = "PREBOOKED"
    BOOKED = "BOOKED"
    INACTIVE = "INACTIVE"
    EXPIRED = "EXPIRED"
    ENDED = "ENDED"
    CANCELLED = "CANCELLED"
    ARCHIVED = "ARCHIVED"


class EducationalBookingStatus(enum.Enum):
    REFUSED = "REFUSED"


class CollectiveBookingStatusFilter(enum.Enum):
    BOOKED = "booked"
    VALIDATED = "validated"
    REIMBURSED = "reimbursed"


class InstitutionRuralLevel(enum.Enum):
    URBAIN_DENSITE_INTERMEDIAIRE = "urbain densité intermédiaire"
    RURAL_SOUS_FORTE_INFLUENCE_D_UN_POLE = "rural sous forte influence d'un pôle"
    URBAIN_DENSE = "urbain dense"
    RURAL_SOUS_FAIBLE_INFLUENCE_D_UN_POLE = "rural sous faible influence d'un pôle"
    RURAL_AUTONOME_TRES_PEU_DENSE = "rural autonome très peu dense"
    RURAL_AUTONOME_PEU_DENSE = "rural autonome peu dense"


# Mapping from rurality level to distance in km
PLAYLIST_RURALITY_MAX_DISTANCE_MAPPING = {
    InstitutionRuralLevel.URBAIN_DENSE: 3,
    InstitutionRuralLevel.URBAIN_DENSITE_INTERMEDIAIRE: 10,
    InstitutionRuralLevel.RURAL_SOUS_FORTE_INFLUENCE_D_UN_POLE: 15,
    InstitutionRuralLevel.RURAL_SOUS_FAIBLE_INFLUENCE_D_UN_POLE: 60,
    InstitutionRuralLevel.RURAL_AUTONOME_PEU_DENSE: 60,
    InstitutionRuralLevel.RURAL_AUTONOME_TRES_PEU_DENSE: 60,
}


class PlaylistType(enum.Enum):
    CLASSROOM = "Dans votre classe"
    LOCAL_OFFERER = "À proximité de l'établissement"
    NEW_OFFER = "Nouvelles offres"
    NEW_OFFERER = "Nouveaux partenaires culturels"


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

    @hybrid_property
    def hasImage(self) -> bool:
        return self.imageId is not None

    @hasImage.expression  # type: ignore[no-redef]
    def hasImage(cls) -> BinaryExpression:  # pylint: disable=no-self-argument
        return cls.imageId is not None

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


@sa.orm.declarative_mixin
class CollectiveStatusMixin:
    @hybrid_property
    def status(self) -> offer_mixin.CollectiveOfferStatus:
        if self.isArchived:
            return offer_mixin.CollectiveOfferStatus.ARCHIVED

        if self.validation == offer_mixin.OfferValidationStatus.REJECTED:
            return offer_mixin.CollectiveOfferStatus.REJECTED

        if self.validation == offer_mixin.OfferValidationStatus.PENDING:
            return offer_mixin.CollectiveOfferStatus.PENDING

        if self.validation == offer_mixin.OfferValidationStatus.DRAFT:
            return offer_mixin.CollectiveOfferStatus.DRAFT

        if not self.isActive:
            return offer_mixin.CollectiveOfferStatus.INACTIVE

        if self.validation == offer_mixin.OfferValidationStatus.APPROVED:
            if self.hasBeginningDatetimePassed:
                return offer_mixin.CollectiveOfferStatus.EXPIRED
            if self.isSoldOut:
                return offer_mixin.CollectiveOfferStatus.SOLD_OUT
            if self.hasBookingLimitDatetimesPassed:
                return offer_mixin.CollectiveOfferStatus.INACTIVE
            if self.hasEndDatePassed:
                return offer_mixin.CollectiveOfferStatus.INACTIVE

        return offer_mixin.CollectiveOfferStatus.ACTIVE

    @status.expression  # type: ignore[no-redef]
    def status(cls) -> sa.sql.elements.Case:  # pylint: disable=no-self-argument
        return sa.case(
            (
                cls.isArchived.is_(True),
                offer_mixin.CollectiveOfferStatus.ARCHIVED,
            ),
            (
                cls.validation == offer_mixin.OfferValidationStatus.REJECTED.name,
                offer_mixin.CollectiveOfferStatus.REJECTED.name,
            ),
            (
                cls.validation == offer_mixin.OfferValidationStatus.PENDING.name,
                offer_mixin.CollectiveOfferStatus.PENDING.name,
            ),
            (
                cls.validation == offer_mixin.OfferValidationStatus.DRAFT.name,
                offer_mixin.CollectiveOfferStatus.DRAFT.name,
            ),
            (cls.isActive.is_(False), offer_mixin.CollectiveOfferStatus.INACTIVE.name),
            (cls.hasBeginningDatetimePassed, offer_mixin.CollectiveOfferStatus.EXPIRED.name),
            (cls.isSoldOut, offer_mixin.CollectiveOfferStatus.SOLD_OUT.name),
            (cls.hasBookingLimitDatetimesPassed, offer_mixin.CollectiveOfferStatus.INACTIVE.name),
            (cls.hasEndDatePassed, offer_mixin.CollectiveOfferStatus.INACTIVE.name),
            else_=offer_mixin.CollectiveOfferStatus.ACTIVE.name,
        )


class OfferContactFormEnum(enum.Enum):
    FORM = "form"


class CollectiveOffer(
    PcObject, Base, offer_mixin.ValidationMixin, AccessibilityMixin, CollectiveStatusMixin, HasImageMixin, Model
):
    __tablename__ = "collective_offer"

    offerId = sa.Column(sa.BigInteger, nullable=True)

    isActive: bool = sa.Column(sa.Boolean, nullable=False, server_default=sa.sql.expression.true(), default=True)

    authorId = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), nullable=True)

    author: sa_orm.Mapped["User"] | None = relationship("User", foreign_keys=[authorId], uselist=False)

    # the venueId is the billing address.
    # To find where the offer takes place, check offerVenue.
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

    description: str = sa.Column(sa.Text, nullable=False, server_default="", default="")

    durationMinutes = sa.Column(sa.Integer, nullable=True)

    dateCreated: datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)

    dateArchived: datetime | None = sa.Column(sa.DateTime, nullable=True)

    subcategoryId: str | None = sa.Column(sa.Text, nullable=True)

    dateUpdated: datetime = sa.Column(sa.DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)

    students: list[StudentLevels] = sa.Column(
        MutableList.as_mutable(postgresql.ARRAY(sa.Enum(StudentLevels))),
        nullable=False,
        server_default="{}",
    )

    collectiveStock: "CollectiveStock" = relationship(
        "CollectiveStock", back_populates="collectiveOffer", uselist=False
    )

    contactEmail: str | None = sa.Column(sa.String(120), nullable=True)

    contactPhone: str | None = sa.Column(sa.Text, nullable=True)

    # Where the offer takes place
    # There are three types:
    #   1. within an educational institution;
    #   2. within the offerer's place;
    #   3. in some random place.
    # Each object should have the same three keys: one for the venue
    # type, one for the venueId (filled when 1.) and one for the random
    # place (filled when 3.)
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

    teacherId: int | None = sa.Column(
        sa.BigInteger,
        sa.ForeignKey("educational_redactor.id"),
        nullable=True,
        index=True,
    )

    teacher: sa_orm.Mapped["EducationalRedactor"] = relationship(
        "EducationalRedactor",
        back_populates="collectiveOffers",
        uselist=False,
    )

    providerId: int | None = sa.Column(
        sa.BigInteger,
        sa.ForeignKey("provider.id"),
        nullable=True,
        index=True,
    )

    provider: sa_orm.Mapped["Provider"] = relationship(
        "Provider", foreign_keys=providerId, back_populates="collectiveOffers"
    )

    flaggingValidationRules: list["OfferValidationRule"] = sa.orm.relationship(
        "OfferValidationRule", secondary="validation_rule_collective_offer_link", back_populates="collectiveOffers"
    )

    educationalRedactorsFavorite: sa.orm.Mapped["EducationalRedactor"] = relationship(
        "EducationalRedactor",
        secondary="collective_offer_educational_redactor",
        back_populates="favoriteCollectiveOffers",
    )

    formats: list[subcategories.EacFormat] | None = sa.Column(
        postgresql.ARRAY(sa.Enum(subcategories.EacFormat, create_constraint=False, native_enum=False)), nullable=True
    )

    isNonFreeOffer: sa_orm.Mapped["bool | None"] = sa.orm.query_expression()

    offererAddressId: int = sa.Column(sa.BigInteger, sa.ForeignKey("offerer_address.id"), nullable=True, index=True)
    offererAddress: sa_orm.Mapped["OffererAddress"] = relationship(
        "OffererAddress", foreign_keys=offererAddressId, uselist=False
    )

    # TODO(jeremieb): remove this property once the front end client
    # does not need this field anymore.
    @property
    def isPublicApi(self) -> bool:
        return self.providerId is not None

    # does the collective offer belongs to a national program
    nationalProgramId: int | None = sa.Column(
        sa.BigInteger,
        sa.ForeignKey("national_program.id"),
        nullable=True,
        index=True,
    )

    nationalProgram: sa_orm.Mapped["NationalProgram"] = relationship("NationalProgram", foreign_keys=nationalProgramId)

    @property
    def isEditable(self) -> bool:
        return self.status not in [
            offer_mixin.CollectiveOfferStatus.PENDING,
            offer_mixin.CollectiveOfferStatus.REJECTED,
        ]

    @property
    def isEditableByPcPro(self) -> bool:
        return self.isEditable and not self.isPublicApi

    @property
    def isVisibilityEditable(self) -> bool:
        is_editable = self.isEditable
        if self.collectiveStock:
            is_editable = is_editable and not self.collectiveStock.isSoldOut

        return is_editable

    @hybrid_property
    def hasEndDatePassed(self) -> bool:
        return False

    @hasEndDatePassed.expression  # type: ignore[no-redef]
    def hasEndDatePassed(cls) -> False_:  # pylint: disable=no-self-argument
        return sa.sql.expression.false()

    @hybrid_property
    def isSoldOut(self) -> bool:
        if self.collectiveStock:
            return self.collectiveStock.isSoldOut
        return True

    @isSoldOut.expression  # type: ignore[no-redef]
    def isSoldOut(cls) -> Exists:  # pylint: disable=no-self-argument
        aliased_collective_stock = sa.orm.aliased(CollectiveStock)
        aliased_collective_booking = sa.orm.aliased(CollectiveBooking)
        return (
            sa.exists()
            .where(aliased_collective_stock.collectiveOfferId == cls.id)
            .where(aliased_collective_booking.collectiveStockId == aliased_collective_stock.id)
            .where(aliased_collective_booking.status != CollectiveBookingStatus.CANCELLED)
        )

    @hybrid_property
    def isArchived(self) -> bool:
        return self.dateArchived is not None

    @isArchived.expression  # type: ignore[no-redef]
    def isArchived(cls) -> Boolean:  # pylint: disable=no-self-argument
        return cls.dateArchived.is_not(sa.null())

    @property
    def isBookable(self) -> bool:
        if self.collectiveStock:
            return self.collectiveStock.isBookable
        return False

    @property
    def isReleased(self) -> bool:
        return (
            self.isActive
            and self.validation == offer_mixin.OfferValidationStatus.APPROVED
            and self.venue.managingOfferer.isActive
            and self.venue.managingOfferer.isValidated
        )

    @property
    def start(self) -> datetime | None:
        if not self.collectiveStock:
            return None

        return self.collectiveStock.startDatetime

    @property
    def end(self) -> datetime | None:
        if not self.collectiveStock:
            return None

        return self.collectiveStock.endDatetime

    @property
    def dates(self) -> dict | None:
        if not self.start or not self.end:
            return None
        return {"start": self.start, "end": self.end}

    @property
    def hasBookingLimitDatetimePassed(self) -> bool:
        if self.collectiveStock:
            return self.collectiveStock.hasBookingLimitDatetimePassed
        return False

    @hybrid_property
    def hasBookingLimitDatetimesPassed(self) -> bool:
        if not self.collectiveStock:
            return False
        return self.collectiveStock.hasBookingLimitDatetimePassed

    @hasBookingLimitDatetimesPassed.expression  # type: ignore[no-redef]
    def hasBookingLimitDatetimesPassed(cls) -> Exists:  # pylint: disable=no-self-argument
        aliased_collective_stock = sa.orm.aliased(CollectiveStock)
        return (
            sa.exists()
            .where(aliased_collective_stock.collectiveOfferId == cls.id)
            .where(aliased_collective_stock.hasBookingLimitDatetimePassed.is_(True))
        )

    @hybrid_property
    def hasBeginningDatetimePassed(self) -> bool:
        if not self.collectiveStock:
            return False
        return self.collectiveStock.hasBeginningDatetimePassed

    @hasBeginningDatetimePassed.expression  # type: ignore[no-redef]
    def hasBeginningDatetimePassed(cls) -> Exists:  # pylint: disable=no-self-argument
        aliased_collective_stock = sa.orm.aliased(CollectiveStock)
        return (
            sa.exists()
            .where(aliased_collective_stock.collectiveOfferId == cls.id)
            .where(aliased_collective_stock.hasBeginningDatetimePassed.is_(True))
        )

    @property
    def days_until_booking_limit(self) -> int | None:
        if not self.collectiveStock:
            return None

        delta = self.collectiveStock.bookingLimitDatetime - datetime.utcnow()
        return delta.days

    @property
    def requires_attention(self) -> bool:
        if self.days_until_booking_limit is not None and self.status == offer_mixin.CollectiveOfferStatus.SOLD_OUT:
            return self.days_until_booking_limit < 7

        return False

    @property
    def sort_criterion(self) -> typing.Tuple[bool, int, datetime]:
        """
        This is used to sort orders with the following criterium.

        1. Archived order are not relevant
        2. Orders with a booking limit in a near future (ie < 7 days) are relevant
        3. DateCreated is to be used as a default rule. Older -> less relevant that younger
        """
        if self.requires_attention and self.days_until_booking_limit is not None:
            date_limit_score = self.days_until_booking_limit
        else:
            date_limit_score = BIG_NUMBER_FOR_SORTING_ORDERS

        # pylint: disable=invalid-unary-operand-type
        return not self.isArchived, -date_limit_score, self.dateCreated

    def get_formats(self) -> typing.Sequence[subcategories.EacFormat] | None:
        if self.formats:
            return self.formats
        if self.subcategory:
            return self.subcategory.formats
        return None

    @property
    def subcategory(self) -> subcategories.Subcategory | None:
        if self.subcategoryId not in subcategories.ALL_SUBCATEGORIES_DICT:
            return None
        return subcategories.ALL_SUBCATEGORIES_DICT[self.subcategoryId]

    @property
    def category(self) -> categories.Category | None:
        if not self.subcategory:
            return None
        return self.subcategory.category

    @property
    def categoryId(self) -> str:  # used in validation rule, do not remove
        if not self.subcategory:
            return ""
        return self.subcategory.category.id

    @property
    def visibleText(self) -> str:  # used in validation rule, do not remove
        text_data: list[str] = [self.name, self.description]
        if self.collectiveStock and self.collectiveStock.priceDetail:
            text_data.append(self.collectiveStock.priceDetail)
        return " ".join(text_data)

    @hybrid_property
    def isEvent(self) -> bool:
        return self.subcategory.is_event

    @isEvent.expression  # type: ignore[no-redef]
    def isEvent(cls) -> BinaryExpression:  # pylint: disable=no-self-argument
        return cls.subcategoryId.in_(subcategories.EVENT_SUBCATEGORIES)

    @property
    def is_cancellable_from_offerer(self) -> bool:
        if self.collectiveStock is None:
            return False
        return self.collectiveStock.is_cancellable_from_offerer

    @property
    def lastBookingId(self) -> int | None:
        query = db.session.query(func.max(CollectiveBooking.id))
        query = query.join(CollectiveStock, CollectiveBooking.collectiveStock)
        query = query.filter(CollectiveStock.collectiveOfferId == self.id)
        return query.scalar()

    @property
    def lastBookingStatus(self) -> CollectiveBookingStatus | None:
        subquery = db.session.query(func.max(CollectiveBooking.id))
        subquery = subquery.join(CollectiveStock, CollectiveBooking.collectiveStock)
        subquery = subquery.filter(CollectiveStock.collectiveOfferId == self.id)

        query = db.session.query(CollectiveBooking.status)
        query = query.join(CollectiveStock, CollectiveBooking.collectiveStock)
        query = query.filter(CollectiveStock.collectiveOfferId == self.id, CollectiveBooking.id.in_(subquery))
        result = query.one_or_none()
        return result[0] if result else None

    @hybrid_property
    def is_expired(self) -> bool:
        return self.hasBeginningDatetimePassed

    @is_expired.expression  # type: ignore[no-redef]
    def is_expired(cls) -> UnaryExpression:  # pylint: disable=no-self-argument
        return cls.hasBeginningDatetimePassed


class CollectiveOfferTemplate(
    PcObject, offer_mixin.ValidationMixin, AccessibilityMixin, CollectiveStatusMixin, HasImageMixin, Base, Model
):
    __tablename__ = "collective_offer_template"

    offerId = sa.Column(sa.BigInteger, nullable=True)

    isActive: bool = sa.Column(sa.Boolean, nullable=False, server_default=sa.sql.expression.true(), default=True)

    authorId = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), nullable=True)

    author: sa_orm.Mapped["User"] | None = relationship("User", foreign_keys=[authorId], uselist=False)

    venueId: int = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id"), nullable=False, index=True)

    venue: sa_orm.Mapped["Venue"] = sa.orm.relationship(
        "Venue", foreign_keys=[venueId], back_populates="collectiveOfferTemplates"
    )

    name: str = sa.Column(sa.String(140), nullable=False)

    description: str = sa.Column(sa.Text, nullable=False, server_default="", default="")

    durationMinutes = sa.Column(sa.Integer, nullable=True)

    dateCreated: datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)

    subcategoryId: str | None = sa.Column(sa.Text, nullable=True)

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

    offerVenue: dict = sa.Column(MutableDict.as_mutable(postgresql.json.JSONB), nullable=False)

    interventionArea: list[str] = sa.Column(
        MutableList.as_mutable(postgresql.ARRAY(sa.Text())), nullable=False, server_default="{}"
    )

    domains: list["EducationalDomain"] = relationship(
        "EducationalDomain", secondary="collective_offer_template_domain", back_populates="collectiveOfferTemplates"
    )

    collectiveOffers: sa_orm.Mapped["CollectiveOffer"] = relationship("CollectiveOffer", back_populates="template")

    providerId: int | None = sa.Column(
        sa.BigInteger,
        sa.ForeignKey("provider.id"),
        nullable=True,
        index=True,
    )

    provider: sa_orm.Mapped["Provider"] = relationship(
        "Provider", foreign_keys=providerId, back_populates="collectiveOfferTemplates"
    )

    collectiveOfferRequest: sa_orm.Mapped["CollectiveOfferRequest"] = relationship(
        "CollectiveOfferRequest", back_populates="collectiveOfferTemplate"
    )

    flaggingValidationRules: list["OfferValidationRule"] = sa.orm.relationship(
        "OfferValidationRule",
        secondary="validation_rule_collective_offer_template_link",
        back_populates="collectiveOfferTemplates",
    )

    # does the collective offer belongs to a national program
    nationalProgramId: int | None = sa.Column(
        sa.BigInteger,
        sa.ForeignKey("national_program.id"),
        nullable=True,
        index=True,
    )

    nationalProgram: sa_orm.Mapped["NationalProgram"] = relationship("NationalProgram", foreign_keys=nationalProgramId)

    educationalRedactorsFavorite: sa.orm.Mapped["EducationalRedactor"] = relationship(
        "EducationalRedactor",
        secondary="collective_offer_template_educational_redactor",
        back_populates="favoriteCollectiveOfferTemplates",
    )

    dateRange: psycopg2.extras.DateTimeRange = sa.Column(postgresql.TSRANGE)

    formats: list[subcategories.EacFormat] | None = sa.Column(
        postgresql.ARRAY(sa.Enum(subcategories.EacFormat, create_constraint=False, native_enum=False)), nullable=True
    )

    collective_playlists: list[sa_orm.Mapped["CollectivePlaylist"]] = relationship(
        "CollectivePlaylist", back_populates="collective_offer_template"
    )

    contactEmail: str | None = sa.Column(sa.String(120), nullable=True)
    contactPhone: str | None = sa.Column(sa.Text, nullable=True)
    contactUrl: str | None = sa.Column(sa.Text, nullable=True)
    contactForm: OfferContactFormEnum | None = sa.Column(
        MagicEnum(OfferContactFormEnum),
        nullable=True,
        server_default=None,
        default=None,
    )
    offererAddressId: int = sa.Column(sa.BigInteger, sa.ForeignKey("offerer_address.id"), nullable=True, index=True)
    offererAddress: sa_orm.Mapped["OffererAddress | None"] = relationship(
        "OffererAddress", foreign_keys=[offererAddressId], uselist=False
    )

    dateArchived: datetime | None = sa.Column(sa.DateTime, nullable=True)

    @declared_attr
    def __table_args__(self):
        parent_args = []
        # Retrieves indexes from parent mixins defined in __table_args__
        for base_class in self.__mro__:
            try:
                parent_args += super(base_class, self).__table_args__
            except (AttributeError, TypeError):
                pass
        parent_args += [
            sa.UniqueConstraint("dateRange", "id", name="collective_offer_template_unique_daterange"),
            sa.CheckConstraint(
                '"dateRange" is NULL OR ('
                'NOT isempty("dateRange") '
                'AND lower("dateRange") is NOT NULL '
                'AND upper("dateRange") IS NOT NULL '
                'AND lower("dateRange")::date >= "dateCreated"::date)',
                name="template_dates_non_empty_daterange",
            ),
            sa.CheckConstraint(
                '("contactEmail" is not null) or ("contactPhone" is not null) or ("contactUrl" is not null) or ("contactForm" is not null)',
                name="collective_offer_tmpl_contact_request_form_data_constraint",
            ),
            sa.CheckConstraint(
                '("contactUrl" IS NULL OR "contactForm" IS NULL)',
                name="collective_offer_tmpl_contact_form_switch_constraint",
            ),
        ]

        return tuple(parent_args)

    @property
    def start(self) -> datetime | None:
        if not self.dateRange:
            return None
        return self.dateRange.lower

    @property
    def end(self) -> datetime | None:
        if not self.dateRange:
            return None
        return self.dateRange.upper

    @property
    def dates(self) -> dict | None:
        if not self.dateRange:
            return None
        return {"start": self.start, "end": self.end}

    @property
    def isEditable(self) -> bool:
        return self.status not in [
            offer_mixin.CollectiveOfferStatus.PENDING,
            offer_mixin.CollectiveOfferStatus.REJECTED,
        ]

    @property
    def isEditableByPcPro(self) -> bool:
        return self.isEditable

    @hybrid_property
    def hasEndDatePassed(self) -> bool:
        if not self.end:
            return False
        return self.end < datetime.utcnow()

    @hasEndDatePassed.expression  # type: ignore[no-redef]
    def hasEndDatePassed(cls) -> Exists:  # pylint: disable=no-self-argument
        return cls.dateRange.contained_by(psycopg2.extras.DateTimeRange(upper=datetime.utcnow()))

    @hybrid_property
    def hasBookingLimitDatetimesPassed(self) -> bool:
        # this property is here for compatibility reasons
        return False

    @hasBookingLimitDatetimesPassed.expression  # type: ignore[no-redef]
    def hasBookingLimitDatetimesPassed(cls) -> False_:  # pylint: disable=no-self-argument
        # this property is here for compatibility reasons
        return sa.sql.expression.false()

    @hybrid_property
    def hasBeginningDatetimePassed(self) -> bool:
        # this property is here for compatibility reasons
        return False

    @hasBeginningDatetimePassed.expression  # type: ignore[no-redef]
    def hasBeginningDatetimePassed(cls) -> False_:  # pylint: disable=no-self-argument
        # this property is here for compatibility reasons
        return sa.sql.expression.false()

    @hybrid_property
    def isArchived(self) -> bool:
        return self.dateArchived is not None

    @isArchived.expression  # type: ignore[no-redef]
    def isArchived(cls) -> Boolean:  # pylint: disable=no-self-argument
        return cls.dateArchived.is_not(sa.null())

    @hybrid_property
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

    @property
    def is_eligible_for_search(self) -> bool:
        return bool(self.isReleased and not self.venue.isVirtual)

    @property
    def sort_criterion(self) -> typing.Tuple[bool, int, datetime]:
        """
        This is is used to compoare orders.

        For template orders there is no booking_limit criterium. Thats is why we define the second value of the tuple
        to the constant.
        """
        return (not self.isArchived, -BIG_NUMBER_FOR_SORTING_ORDERS, self.dateCreated)

    def get_formats(self) -> typing.Sequence[subcategories.EacFormat] | None:
        if self.formats:
            return self.formats
        if self.subcategory:
            return self.subcategory.formats
        return None

    @property
    def subcategory(self) -> subcategories.Subcategory | None:
        if self.subcategoryId not in subcategories.ALL_SUBCATEGORIES_DICT:
            return None
        return subcategories.ALL_SUBCATEGORIES_DICT[self.subcategoryId]

    @property
    def categoryId(self) -> str:  # used in validation rule, do not remove
        if not self.subcategory:
            return ""
        return self.subcategory.category.id

    @property
    def visibleText(self) -> str:  # used in validation rule, do not remove
        return f"{self.name} {self.description} {self.priceDetail}"

    @hybrid_property
    def isEvent(self) -> bool:
        return self.subcategory.is_event

    @isEvent.expression  # type: ignore[no-redef]
    def isEvent(cls) -> BinaryExpression:  # pylint: disable=no-self-argument
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
            "nationalProgramId",
            "formats",
            "author",
        ]
        collective_offer_mapping = {x: getattr(collective_offer, x) for x in list_of_common_attributes}
        return cls(
            **collective_offer_mapping,
            offerId=collective_offer.offerId,
            priceDetail=price_detail,
        )

    @hybrid_property
    def is_expired(self) -> bool:
        return self.hasBeginningDatetimePassed

    @is_expired.expression  # type: ignore[no-redef]
    def is_expired(cls) -> UnaryExpression:  # pylint: disable=no-self-argument
        return cls.hasBeginningDatetimePassed


class CollectiveStock(PcObject, Base, Model):
    __tablename__ = "collective_stock"

    stockId = sa.Column(sa.BigInteger, nullable=True)

    dateCreated: datetime = sa.Column(
        sa.DateTime, nullable=False, default=datetime.utcnow, server_default=sa.func.now()
    )

    dateModified: datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    beginningDatetime: datetime = sa.Column(sa.DateTime, index=True, nullable=False)

    startDatetime: datetime = sa.Column(sa.DateTime, nullable=True)
    endDatetime: datetime = sa.Column(sa.DateTime, nullable=True)

    collectiveOfferId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("collective_offer.id"), index=True, nullable=False, unique=True
    )

    collectiveOffer: sa_orm.Mapped["CollectiveOffer"] = sa.orm.relationship(
        "CollectiveOffer", foreign_keys=[collectiveOfferId], uselist=False, back_populates="collectiveStock"
    )

    collectiveBookings: list["CollectiveBooking"] = relationship("CollectiveBooking", back_populates="collectiveStock")

    price: decimal.Decimal = sa.Column(
        sa.Numeric(10, 2),
        sa.CheckConstraint("price >= 0", name="check_price_is_not_negative"),
        index=True,
        nullable=False,
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

    @hybrid_property
    def hasBookingLimitDatetimePassed(self) -> bool:
        return self.bookingLimitDatetime <= datetime.utcnow()

    @hasBookingLimitDatetimePassed.expression  # type: ignore[no-redef]
    def hasBookingLimitDatetimePassed(cls) -> BinaryExpression:  # pylint: disable=no-self-argument
        return cls.bookingLimitDatetime <= sa.func.now()

    @hybrid_property
    def hasBeginningDatetimePassed(self) -> bool:
        return self.beginningDatetime <= datetime.utcnow()

    @hasBeginningDatetimePassed.expression  # type: ignore[no-redef]
    def hasBeginningDatetimePassed(cls) -> BinaryExpression:  # pylint: disable=no-self-argument
        return cls.beginningDatetime <= sa.func.now()

    @hybrid_property
    def isEventExpired(self) -> bool:  # todo rewrite
        return self.beginningDatetime <= datetime.utcnow()

    @isEventExpired.expression  # type: ignore[no-redef]
    def isEventExpired(cls):  # pylint: disable=no-self-argument
        return cls.beginningDatetime <= sa.func.now()

    @property
    def isExpired(self) -> bool:
        return self.isEventExpired or self.hasBookingLimitDatetimePassed

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

    id: sa_orm.Mapped[int] = sa.Column(sa.Integer, primary_key=True, autoincrement=True)

    # this institutionId corresponds to the UAI ("Unité Administrative Immatriculée") code
    institutionId: str = sa.Column(sa.String(30), nullable=False, unique=True, index=True)

    institutionType: str = sa.Column(sa.String(80), nullable=False)

    name: str = sa.Column(sa.Text(), nullable=False)

    city: str = sa.Column(sa.Text(), nullable=False)

    postalCode: str = sa.Column(sa.String(10), nullable=False)

    email = sa.Column(sa.Text(), nullable=True)

    phoneNumber: str = sa.Column(sa.String(30), nullable=False)

    collectiveOffers: list["CollectiveOffer"] = relationship("CollectiveOffer", back_populates="institution")

    isActive: bool = sa.Column(sa.Boolean, nullable=False, server_default=sa.sql.expression.true(), default=True)

    collectiveOfferRequest: sa_orm.Mapped["CollectiveOfferRequest"] = relationship(
        "CollectiveOfferRequest", back_populates="educationalInstitution"
    )

    programs: list["EducationalInstitutionProgram"] = relationship(
        "EducationalInstitutionProgram",
        secondary="educational_institution_program_association",
        back_populates="institutions",
    )

    ruralLevel: InstitutionRuralLevel = sa.Column(MagicEnum(InstitutionRuralLevel), nullable=True, default=None)

    collective_playlists: list[sa_orm.Mapped["CollectivePlaylist"]] = relationship(
        "CollectivePlaylist", back_populates="institution"
    )

    __table_args__ = (sa.Index("ix_educational_institution_type_name_city", institutionType + " " + name + " " + city),)

    @property
    def full_name(self) -> str:
        return f"{self.institutionType} {self.name}".strip()


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

    def check_has_enough_fund(self, total_amount_after_booking: Decimal) -> None:
        """Check that the total amount of bookings won't exceed the
        deposit's amount.

        Note:
          if the deposit is not the final one, only a part of it can
          be consumed (eg. only 80% can be used).
        """
        from pcapi.core.educational import exceptions

        if self.isFinal:
            if self.amount < total_amount_after_booking:
                raise exceptions.InsufficientFund()
        else:
            ratio = Decimal(self.TEMPORARY_FUND_AVAILABLE_RATIO)
            temporary_fund = round(self.amount * ratio, 2)

            if temporary_fund < total_amount_after_booking:
                raise exceptions.InsufficientTemporaryFund()


class EducationalRedactor(PcObject, Base, Model):
    __tablename__ = "educational_redactor"

    email: str = sa.Column(sa.String(120), nullable=False, unique=True, index=True)

    firstName = sa.Column(sa.String(128), nullable=True)

    lastName = sa.Column(sa.String(128), nullable=True)

    civility = sa.Column(sa.String(20), nullable=True)

    preferences: sa.orm.Mapped[dict] = sa.Column(
        sa.dialects.postgresql.JSONB(), server_default="{}", default={}, nullable=False
    )

    collectiveBookings: list["CollectiveBooking"] = relationship(
        "CollectiveBooking", back_populates="educationalRedactor"
    )

    collectiveOffers: list["CollectiveOffer"] = relationship("CollectiveOffer", back_populates="teacher")

    collectiveOfferRequest: sa_orm.Mapped["CollectiveOfferRequest"] = relationship(
        "CollectiveOfferRequest", back_populates="educationalRedactor"
    )

    favoriteCollectiveOffers: sa.orm.Mapped["CollectiveOffer"] = relationship(
        "CollectiveOffer",
        secondary="collective_offer_educational_redactor",
        back_populates="educationalRedactorsFavorite",
    )

    favoriteCollectiveOfferTemplates: sa.orm.Mapped["CollectiveOfferTemplate"] = relationship(
        "CollectiveOfferTemplate",
        secondary="collective_offer_template_educational_redactor",
        back_populates="educationalRedactorsFavorite",
    )

    @property
    def full_name(self) -> str:
        # full_name is used for display and should never be empty, which would be confused with no user.
        # We use the email as a fallback because it is the most human-readable way to identify a single user
        return (f"{self.firstName or ''} {self.lastName or ''}".strip()) or self.email


class CollectiveBooking(PcObject, Base, Model):
    __tablename__ = "collective_booking"

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

    def cancel_booking(
        self,
        reason: CollectiveBookingCancellationReasons,
        cancel_even_if_used: bool = False,
        cancel_even_if_reimbursed: bool = False,
    ) -> None:
        from pcapi.core.educational import exceptions

        if self.status is CollectiveBookingStatus.CANCELLED:
            raise exceptions.CollectiveBookingAlreadyCancelled()
        if self.status is CollectiveBookingStatus.REIMBURSED and not cancel_even_if_reimbursed:
            raise exceptions.CollectiveBookingIsAlreadyUsed
        if self.status is CollectiveBookingStatus.USED and not cancel_even_if_used:
            raise exceptions.CollectiveBookingIsAlreadyUsed
        self.status = CollectiveBookingStatus.CANCELLED
        self.cancellationDate = datetime.utcnow()
        self.cancellationReason = reason
        self.dateUsed = None

    def uncancel_booking(self) -> None:
        if not (self.status is CollectiveBookingStatus.CANCELLED):
            raise booking_exceptions.BookingIsNotCancelledCannotBeUncancelled()
        self.cancellationDate = None
        self.cancellationReason = None
        if self.confirmationDate:
            if self.collectiveStock.beginningDatetime < datetime.utcnow():
                self.status = CollectiveBookingStatus.USED
                self.dateUsed = datetime.utcnow()
            else:
                self.status = CollectiveBookingStatus.CONFIRMED
        else:
            self.status = CollectiveBookingStatus.PENDING

    def mark_as_confirmed(self) -> None:
        if self.has_confirmation_limit_date_passed():
            raise booking_exceptions.ConfirmationLimitDateHasPassed()

        self.status = CollectiveBookingStatus.CONFIRMED
        self.confirmationDate = datetime.utcnow()

    @hybrid_property
    def isConfirmed(self) -> bool:
        return self.cancellationLimitDate <= datetime.utcnow()

    @isConfirmed.expression  # type: ignore[no-redef]
    def isConfirmed(cls) -> BinaryExpression:  # pylint: disable=no-self-argument
        return cls.cancellationLimitDate <= datetime.utcnow()

    @hybrid_property
    def is_used_or_reimbursed(self) -> bool:
        return self.status in [CollectiveBookingStatus.USED, CollectiveBookingStatus.REIMBURSED]

    @is_used_or_reimbursed.expression  # type: ignore[no-redef]
    def is_used_or_reimbursed(cls) -> BinaryExpression:  # pylint: disable=no-self-argument
        return cls.status.in_([CollectiveBookingStatus.USED, CollectiveBookingStatus.REIMBURSED])

    @hybrid_property
    def isReimbursed(self) -> bool:
        return self.status == CollectiveBookingStatus.REIMBURSED

    @isReimbursed.expression  # type: ignore[no-redef]
    def isReimbursed(cls) -> BinaryExpression:  # pylint: disable=no-self-argument
        return cls.status == CollectiveBookingStatus.REIMBURSED

    @hybrid_property
    def isCancelled(self) -> bool:
        return self.status == CollectiveBookingStatus.CANCELLED

    @isCancelled.expression  # type: ignore[no-redef]
    def isCancelled(cls) -> BinaryExpression:  # pylint: disable=no-self-argument
        return cls.status == CollectiveBookingStatus.CANCELLED

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

    @property
    def reimbursement_pricing(self) -> finance_models.Pricing | None:
        """Return related pricing if this booking has been reimbursed."""
        pricings = [
            pricing
            for pricing in self.pricings
            if pricing.status
            in (
                finance_models.PricingStatus.PROCESSED,
                finance_models.PricingStatus.INVOICED,
            )
        ]

        pricings = sorted(pricings, key=lambda x: x.creationDate, reverse=True)
        if pricings:
            return pricings[0]

        return None

    @property
    def invoiced_pricing(self) -> finance_models.Pricing | None:
        pricings = [pricing for pricing in self.pricings if pricing.status == finance_models.PricingStatus.INVOICED]
        pricings = sorted(pricings, key=lambda pricing: pricing.creationDate, reverse=True)
        if pricings:
            return pricings[0]
        return None

    @property
    def cashflow_batch(self) -> finance_models.CashflowBatch | None:
        """Return cashflow batch in which this booking has been
        reimbursed (if any).
        """
        if not self.reimbursement_pricing:
            return None

        cashflow = self.reimbursement_pricing.cashflow
        if not cashflow:
            return None

        return cashflow.batch

    @property
    def reimbursement_rate(self) -> float | None:
        if not self.reimbursement_pricing:
            return None

        try:
            # pricing.amount is in cents, amount in euros
            # -> the result is a percentage
            return float("{:.2f}".format((-self.reimbursement_pricing.amount / self.total_amount)))
        except (decimal.DivisionByZero, decimal.InvalidOperation):  # raised when both values are 0
            return None

    @property
    def total_amount(self) -> Decimal:
        return self.collectiveStock.price


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
    nationalPrograms: sa_orm.Mapped[list["NationalProgram"]] = sa.orm.relationship(
        "NationalProgram", back_populates="domains", secondary="domain_to_national_program"
    )


class CollectiveDmsApplication(PcObject, Base, Model):
    __tablename__ = "collective_dms_application"
    state: str = sa.Column(sa.String(30), nullable=False)
    procedure: int = sa.Column(sa.BigInteger, nullable=False)
    application: int = sa.Column(sa.BigInteger, nullable=False, index=True)
    siret: str = sa.Column(sa.String(14), nullable=False, index=True)
    lastChangeDate: datetime = sa.Column(sa.DateTime, nullable=False)
    depositDate = sa.Column(sa.DateTime, nullable=False)
    expirationDate = sa.Column(sa.DateTime, nullable=True)
    buildDate = sa.Column(sa.DateTime, nullable=True)
    instructionDate = sa.Column(sa.DateTime, nullable=True)
    processingDate = sa.Column(sa.DateTime, nullable=True)
    userDeletionDate = sa.Column(sa.DateTime, nullable=True)


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


class CollectiveOfferRequest(PcObject, Base, Model):
    _phoneNumber: str | None = sa.Column(sa.String(30), nullable=True, name="phoneNumber")

    requestedDate: date | None = sa.Column(sa.Date, nullable=True)

    totalStudents: int | None = sa.Column(sa.Integer, nullable=True)

    totalTeachers: int | None = sa.Column(sa.Integer, nullable=True)

    comment: str = sa.Column(sa.Text, nullable=False)

    dateCreated: date = sa.Column(sa.Date, nullable=False, server_default=sa.func.current_date())

    educationalRedactorId: int = sa.Column(sa.BigInteger, sa.ForeignKey("educational_redactor.id"), nullable=False)

    educationalRedactor: sa_orm.Mapped["EducationalRedactor"] = relationship(
        "EducationalRedactor", foreign_keys=educationalRedactorId, back_populates="collectiveOfferRequest"
    )

    collectiveOfferTemplateId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("collective_offer_template.id"), index=True, nullable=False
    )

    collectiveOfferTemplate: sa_orm.Mapped["CollectiveOfferTemplate"] = relationship(
        "CollectiveOfferTemplate", foreign_keys=collectiveOfferTemplateId, back_populates="collectiveOfferRequest"
    )

    educationalInstitutionId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("educational_institution.id"), index=True, nullable=False
    )

    educationalInstitution: sa_orm.Mapped["EducationalInstitution"] = relationship(
        "EducationalInstitution", foreign_keys=educationalInstitutionId, back_populates="collectiveOfferRequest"
    )

    @hybrid_property
    def phoneNumber(self) -> str | None:
        return self._phoneNumber

    @phoneNumber.setter  # type: ignore[no-redef]
    def phoneNumber(self, value: str | None) -> None:
        if not value:
            self._phoneNumber = None
        else:
            self._phoneNumber = ParsedPhoneNumber(value).phone_number

    @phoneNumber.expression  # type: ignore[no-redef]
    def phoneNumber(cls) -> str | None:  # pylint: disable=no-self-argument
        return cls._phoneNumber


class ValidationRuleCollectiveOfferLink(PcObject, Base, Model):
    __tablename__ = "validation_rule_collective_offer_link"
    ruleId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("offer_validation_rule.id", ondelete="CASCADE"), nullable=False
    )
    collectiveOfferId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("collective_offer.id", ondelete="CASCADE"), nullable=False
    )


class ValidationRuleCollectiveOfferTemplateLink(PcObject, Base, Model):
    __tablename__ = "validation_rule_collective_offer_template_link"
    ruleId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("offer_validation_rule.id", ondelete="CASCADE"), nullable=False
    )
    collectiveOfferTemplateId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("collective_offer_template.id", ondelete="CASCADE"), nullable=False
    )


class NationalProgram(PcObject, Base, Model):
    """
    Keep a track of existing national program that are used to highlight
    collective offers (templates) within a coherent frame.
    """

    name: str = sa.Column(sa.Text, unique=True)
    dateCreated: datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)
    domains: sa_orm.Mapped[list["EducationalDomain"]] = sa.orm.relationship(
        "EducationalDomain", back_populates="nationalPrograms", secondary="domain_to_national_program"
    )


class NationalProgramOfferLinkHistory(PcObject, Base, Model):
    """
    Keep a track on national program and collective offer links.
    It might be useful to find if an offer has been part of a given
    program or not.
    """

    dateCreated: datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)
    collectiveOfferId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("collective_offer.id", ondelete="CASCADE"), nullable=False
    )
    nationalProgramId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("national_program.id", ondelete="CASCADE"), nullable=False
    )


class NationalProgramOfferTemplateLinkHistory(PcObject, Base, Model):
    """
    Keep a track on national program and collective offer template links.
    It might be useful to find if an offer has been part of a given
    program or not.
    """

    dateCreated: datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)
    collectiveOfferTemplateId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("collective_offer_template.id", ondelete="CASCADE"), nullable=False
    )
    nationalProgramId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("national_program.id", ondelete="CASCADE"), nullable=False
    )


class CollectiveOfferEducationalRedactor(PcObject, Base, Model):
    """Allow adding to favorite the collective offer for adage user"""

    __tablename__ = "collective_offer_educational_redactor"

    educationalRedactorId: int = sa.Column(sa.BigInteger, sa.ForeignKey("educational_redactor.id"), nullable=False)
    collectiveOfferId: int = sa.Column(sa.BigInteger, sa.ForeignKey("collective_offer.id"), nullable=False)
    collectiveOffer: sa_orm.Mapped["CollectiveOffer"] = sa.orm.relationship(
        "CollectiveOffer", foreign_keys=[collectiveOfferId], viewonly=True
    )
    __table_args__ = (UniqueConstraint("educationalRedactorId", "collectiveOfferId", name="unique_redactorId_offer"),)


class CollectiveOfferTemplateEducationalRedactor(PcObject, Base, Model):
    """Allow adding to favorite the offer template for adage user"""

    __tablename__ = "collective_offer_template_educational_redactor"

    educationalRedactorId: int = sa.Column(sa.BigInteger, sa.ForeignKey("educational_redactor.id"), nullable=False)
    collectiveOfferTemplateId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("collective_offer_template.id"), nullable=False
    )
    collectiveOfferTemplate: sa_orm.Mapped["CollectiveOfferTemplate"] = sa.orm.relationship(
        "CollectiveOfferTemplate", foreign_keys=[collectiveOfferTemplateId], viewonly=True
    )
    __table_args__ = (
        UniqueConstraint("educationalRedactorId", "collectiveOfferTemplateId", name="unique_redactorId_template"),
    )


class EducationalInstitutionProgramAssociation(Base, Model):
    """Association model between EducationalInstitution and
    EducationalInstitutionProgram (many-to-many)
    """

    institutionId: int = sa.Column(
        sa.BigInteger,
        sa.ForeignKey("educational_institution.id", ondelete="CASCADE"),
        index=True,
        primary_key=True,
        # Unique constraint has been added to ensure that an institution is not associated with more than one program.
        # This is because of invoices generation in finance/api.py: there is no other way to guess that a collective
        # booking relates to a program.
        # If you wish to remove this constraint, please ensure that a relationship can be made between a collective
        # booking and a program, then fix generate_invoice_file().
        unique=True,
    )
    programId: int = sa.Column(
        sa.BigInteger,
        sa.ForeignKey("educational_institution_program.id", ondelete="CASCADE"),
        index=True,
        primary_key=True,
    )


class EducationalInstitutionProgram(PcObject, Base, Model):
    # technical name
    name: str = sa.Column(sa.Text, nullable=False, unique=True)
    # public (printable) name - if something different from name is needed
    label: str | None = sa.Column(sa.Text, nullable=True)
    description: str | None = sa.Column(sa.Text, nullable=True)

    institutions: list["EducationalInstitution"] = relationship(
        "EducationalInstitution", secondary="educational_institution_program_association", back_populates="programs"
    )


class CollectivePlaylist(PcObject, Base, Model):
    type: str = sa.Column(MagicEnum(PlaylistType), nullable=False)
    distanceInKm: float = sa.Column(sa.Float, nullable=True)

    institutionId = sa.Column(sa.BigInteger, sa.ForeignKey("educational_institution.id"), index=True, nullable=False)
    institution: sa_orm.Mapped["EducationalInstitution"] = relationship(
        "EducationalInstitution", foreign_keys=[institutionId], back_populates="collective_playlists"
    )

    venueId: int = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id"), index=True, nullable=True)
    venue: sa_orm.Mapped["Venue"] = relationship("Venue", foreign_keys=[venueId], back_populates="collective_playlists")

    collectiveOfferTemplateId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("collective_offer_template.id"), index=True, nullable=True
    )
    collective_offer_template: sa_orm.Mapped["CollectiveOfferTemplate"] = relationship(
        "CollectiveOfferTemplate", foreign_keys=[collectiveOfferTemplateId], back_populates="collective_playlists"
    )

    Index("ix_collective_playlist_type_institutionId", type, institutionId)


class AdageVenueAddress(PcObject, Base, Model):
    adageId: str | None = sa.Column(sa.Text, nullable=True, unique=True)
    adageInscriptionDate: datetime | None = sa.Column(sa.DateTime, nullable=True)
    venueId: int | None = sa.Column(
        sa.BigInteger, sa.ForeignKey("venue.id", ondelete="CASCADE"), index=True, nullable=True
    )
    venue: sa_orm.Mapped["Venue"] = sa.orm.relationship(
        "Venue", foreign_keys=[venueId], back_populates="adage_addresses"
    )


class DomainToNationalProgram(PcObject, Base, Model):
    """Intermediate table that links `EducationalDomain`
    to `NationalProgram`. Links are unique: a domain can be linked to many
    programs but not twice the same.
    """

    domainId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("educational_domain.id", ondelete="CASCADE"), index=True, nullable=False
    )
    nationalProgramId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("national_program.id", ondelete="CASCADE"), index=True, nullable=False
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "domainId",
            "nationalProgramId",
            name="unique_domain_to_national_program",
        ),
    )
