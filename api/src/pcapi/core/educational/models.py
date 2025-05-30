import datetime
import decimal
import enum
import logging
import random
import typing

import sqlalchemy as sa
from psycopg2.extras import DateTimeRange
from sqlalchemy import orm as sa_orm
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext import mutable as sa_mutable
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import elements as sa_elements
from sqlalchemy.sql import selectable as sa_selectable

from pcapi import models
from pcapi import settings
from pcapi.core import object_storage
from pcapi.core.bookings import exceptions as booking_exceptions
from pcapi.core.categories.models import EacFormat
from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.finance import models as finance_models
from pcapi.models import offer_mixin
from pcapi.models.accessibility_mixin import AccessibilityMixin
from pcapi.models.pc_object import PcObject
from pcapi.utils import db as db_utils
from pcapi.utils import image_conversion
from pcapi.utils.phone_number import ParsedPhoneNumber
from pcapi.utils.siren import SIREN_LENGTH


logger = logging.getLogger(__name__)

BIG_NUMBER_FOR_SORTING_OFFERS = 9999

MAX_COLLECTIVE_NAME_LENGTH: typing.Final = 110
MAX_COLLECTIVE_DESCRIPTION_LENGTH: typing.Final = 1500


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
    GENERAL2 = "Lycée - Seconde"
    GENERAL1 = "Lycée - Première"
    GENERAL0 = "Lycée - Terminale"
    CAP2 = "CAP - 2e année"
    CAP1 = "CAP - 1re année"

    @classmethod
    def primary_levels(cls) -> set:
        return {
            cls.ECOLES_MARSEILLE_MATERNELLE,
            cls.ECOLES_MARSEILLE_CP_CE1_CE2,
            cls.ECOLES_MARSEILLE_CM1_CM2,
        }


class AdageFrontRoles(enum.Enum):
    REDACTOR = "redactor"
    READONLY = "readonly"


class OfferAddressType(enum.Enum):
    OFFERER_VENUE = "offererVenue"
    SCHOOL = "school"
    OTHER = "other"


class OfferVenueDict(typing.TypedDict):
    addressType: OfferAddressType
    venueId: int | None
    otherAddress: str


class OfferVenueDictStr(typing.TypedDict):
    addressType: typing.Literal["offererVenue"] | typing.Literal["school"] | typing.Literal["other"]
    venueId: int | None
    otherAddress: str


class CollectiveBookingCancellationReasons(enum.Enum):
    OFFERER = "OFFERER"
    BENEFICIARY = "BENEFICIARY"
    EXPIRED = "EXPIRED"
    FRAUD = "FRAUD"
    FRAUD_SUSPICION = "FRAUD_SUSPICION"
    FRAUD_INAPPROPRIATE = "FRAUD_INAPPROPRIATE"
    REFUSED_BY_INSTITUTE = "REFUSED_BY_INSTITUTE"
    REFUSED_BY_HEADMASTER = "REFUSED_BY_HEADMASTER"
    PUBLIC_API = "PUBLIC_API"
    FINANCE_INCIDENT = "FINANCE_INCIDENT"
    BACKOFFICE = "BACKOFFICE"
    BACKOFFICE_EVENT_CANCELLED = "BACKOFFICE_EVENT_CANCELLED"
    BACKOFFICE_OFFER_MODIFIED = "BACKOFFICE_OFFER_MODIFIED"
    BACKOFFICE_OFFER_WITH_WRONG_INFORMATION = "BACKOFFICE_OFFER_WITH_WRONG_INFORMATION"
    BACKOFFICE_OFFERER_BUSINESS_CLOSED = "BACKOFFICE_OFFERER_BUSINESS_CLOSED"
    OFFERER_CONNECT_AS = "OFFERER_CONNECT_AS"
    OFFERER_CLOSED = "OFFERER_CLOSED"


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
    PUBLISHED = "PUBLISHED"
    UNDER_REVIEW = "UNDER_REVIEW"
    REJECTED = "REJECTED"
    PREBOOKED = "PREBOOKED"
    BOOKED = "BOOKED"
    HIDDEN = "HIDDEN"
    EXPIRED = "EXPIRED"
    ENDED = "ENDED"
    CANCELLED = "CANCELLED"
    REIMBURSED = "REIMBURSED"
    ARCHIVED = "ARCHIVED"
    DRAFT = "DRAFT"


COLLECTIVE_OFFER_TEMPLATE_STATUSES: typing.Final = (
    CollectiveOfferDisplayedStatus.ARCHIVED,
    CollectiveOfferDisplayedStatus.REJECTED,
    CollectiveOfferDisplayedStatus.UNDER_REVIEW,
    CollectiveOfferDisplayedStatus.DRAFT,
    CollectiveOfferDisplayedStatus.HIDDEN,
    CollectiveOfferDisplayedStatus.PUBLISHED,
    CollectiveOfferDisplayedStatus.ENDED,
)


class CollectiveOfferAllowedAction(enum.Enum):
    CAN_EDIT_DETAILS = "CAN_EDIT_DETAILS"
    CAN_EDIT_DATES = "CAN_EDIT_DATES"
    CAN_EDIT_INSTITUTION = "CAN_EDIT_INSTITUTION"
    CAN_EDIT_DISCOUNT = "CAN_EDIT_DISCOUNT"
    CAN_DUPLICATE = "CAN_DUPLICATE"
    CAN_CANCEL = "CAN_CANCEL"
    CAN_ARCHIVE = "CAN_ARCHIVE"


class CollectiveOfferTemplateAllowedAction(enum.Enum):
    CAN_EDIT_DETAILS = "CAN_EDIT_DETAILS"
    CAN_DUPLICATE = "CAN_DUPLICATE"
    CAN_ARCHIVE = "CAN_ARCHIVE"
    CAN_CREATE_BOOKABLE_OFFER = "CAN_CREATE_BOOKABLE_OFFER"
    CAN_PUBLISH = "CAN_PUBLISH"
    CAN_HIDE = "CAN_HIDE"


ALLOWED_ACTIONS_BY_DISPLAYED_STATUS: typing.Final[
    dict[CollectiveOfferDisplayedStatus, tuple[CollectiveOfferAllowedAction, ...]]
] = {
    CollectiveOfferDisplayedStatus.DRAFT: (
        CollectiveOfferAllowedAction.CAN_EDIT_DETAILS,
        CollectiveOfferAllowedAction.CAN_EDIT_DATES,
        CollectiveOfferAllowedAction.CAN_EDIT_INSTITUTION,
        CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT,
        CollectiveOfferAllowedAction.CAN_ARCHIVE,
    ),
    CollectiveOfferDisplayedStatus.UNDER_REVIEW: (CollectiveOfferAllowedAction.CAN_DUPLICATE,),
    CollectiveOfferDisplayedStatus.PUBLISHED: (
        CollectiveOfferAllowedAction.CAN_EDIT_DETAILS,
        CollectiveOfferAllowedAction.CAN_EDIT_DATES,
        CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT,
        CollectiveOfferAllowedAction.CAN_DUPLICATE,
        CollectiveOfferAllowedAction.CAN_ARCHIVE,
    ),
    CollectiveOfferDisplayedStatus.REJECTED: (
        CollectiveOfferAllowedAction.CAN_DUPLICATE,
        CollectiveOfferAllowedAction.CAN_ARCHIVE,
    ),
    CollectiveOfferDisplayedStatus.PREBOOKED: (
        CollectiveOfferAllowedAction.CAN_EDIT_DETAILS,
        CollectiveOfferAllowedAction.CAN_EDIT_DATES,
        CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT,
        CollectiveOfferAllowedAction.CAN_DUPLICATE,
        CollectiveOfferAllowedAction.CAN_CANCEL,
    ),
    CollectiveOfferDisplayedStatus.BOOKED: (
        CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT,
        CollectiveOfferAllowedAction.CAN_DUPLICATE,
        CollectiveOfferAllowedAction.CAN_CANCEL,
    ),
    CollectiveOfferDisplayedStatus.EXPIRED: (
        CollectiveOfferAllowedAction.CAN_EDIT_DATES,
        CollectiveOfferAllowedAction.CAN_ARCHIVE,
        CollectiveOfferAllowedAction.CAN_DUPLICATE,
    ),
    CollectiveOfferDisplayedStatus.ENDED: (  # after 48h, cannot edit discount or cancel anymore
        CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT,
        CollectiveOfferAllowedAction.CAN_DUPLICATE,
        CollectiveOfferAllowedAction.CAN_CANCEL,
    ),
    CollectiveOfferDisplayedStatus.REIMBURSED: (
        CollectiveOfferAllowedAction.CAN_DUPLICATE,
        CollectiveOfferAllowedAction.CAN_ARCHIVE,
    ),
    CollectiveOfferDisplayedStatus.CANCELLED: (
        CollectiveOfferAllowedAction.CAN_DUPLICATE,
        CollectiveOfferAllowedAction.CAN_ARCHIVE,
    ),
    CollectiveOfferDisplayedStatus.ARCHIVED: (CollectiveOfferAllowedAction.CAN_DUPLICATE,),
    CollectiveOfferDisplayedStatus.HIDDEN: (),
}

TEMPLATE_ALLOWED_ACTIONS_BY_DISPLAYED_STATUS: typing.Final[
    dict[CollectiveOfferDisplayedStatus, tuple[CollectiveOfferTemplateAllowedAction, ...]]
] = {
    CollectiveOfferDisplayedStatus.DRAFT: (
        CollectiveOfferTemplateAllowedAction.CAN_EDIT_DETAILS,
        CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE,
    ),
    CollectiveOfferDisplayedStatus.UNDER_REVIEW: (),
    CollectiveOfferDisplayedStatus.PUBLISHED: (
        CollectiveOfferTemplateAllowedAction.CAN_EDIT_DETAILS,
        CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE,
        CollectiveOfferTemplateAllowedAction.CAN_CREATE_BOOKABLE_OFFER,
        CollectiveOfferTemplateAllowedAction.CAN_HIDE,
    ),
    CollectiveOfferDisplayedStatus.REJECTED: (CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE,),
    CollectiveOfferDisplayedStatus.ARCHIVED: (),
    CollectiveOfferDisplayedStatus.HIDDEN: (
        CollectiveOfferTemplateAllowedAction.CAN_EDIT_DETAILS,
        CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE,
        CollectiveOfferTemplateAllowedAction.CAN_CREATE_BOOKABLE_OFFER,
        CollectiveOfferTemplateAllowedAction.CAN_PUBLISH,
    ),
    CollectiveOfferDisplayedStatus.ENDED: (
        CollectiveOfferTemplateAllowedAction.CAN_EDIT_DETAILS,
        CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE,
        CollectiveOfferTemplateAllowedAction.CAN_CREATE_BOOKABLE_OFFER,
    ),
}


class EducationalBookingStatus(enum.Enum):
    REFUSED = "REFUSED"


class CollectiveBookingStatusFilter(enum.Enum):
    BOOKED = "booked"
    VALIDATED = "validated"
    REIMBURSED = "reimbursed"


class InstitutionRuralLevel(enum.Enum):
    GRANDS_CENTRES_URBAINS = "Grands centres urbains"  # URBAIN_DENSE
    CEINTURES_URBAINES = "Ceintures urbaines"  # URBAIN_DENSE
    CENTRES_URBAINS_INTERMEDIAIRES = "Centres urbains intermédiaires"  # URBAIN_DENSITE_INTERMEDIAIRE
    PETITES_VILLES = "Petites villes"  # RURAL_SOUS_FORTE_INFLUENCE_D_UN_POLE
    BOURGS_RURAUX = "Bourgs ruraux"  # RURAL_SOUS_FAIBLE_INFLUENCE_D_UN_POLE
    RURAL_A_HABITAT_DISPERSE = "Rural à habitat dispersé"  # RURAL_AUTONOME_PEU_DENSE
    RURAL_A_HABITAT_TRES_DISPERSE = "Rural à habitat très dispersé"  # RURAL_AUTONOME_TRES_PEU_DENSE


# Mapping from rurality level to distance in km
PLAYLIST_RURALITY_MAX_DISTANCE_MAPPING = {
    InstitutionRuralLevel.GRANDS_CENTRES_URBAINS: 3,
    InstitutionRuralLevel.CEINTURES_URBAINES: 3,
    InstitutionRuralLevel.CENTRES_URBAINS_INTERMEDIAIRES: 10,
    InstitutionRuralLevel.PETITES_VILLES: 15,
    InstitutionRuralLevel.BOURGS_RURAUX: 60,
    InstitutionRuralLevel.RURAL_A_HABITAT_DISPERSE: 60,
    InstitutionRuralLevel.RURAL_A_HABITAT_TRES_DISPERSE: 60,
}


class PlaylistType(enum.Enum):
    CLASSROOM = "Dans votre classe"
    LOCAL_OFFERER = "À proximité de l'établissement"
    NEW_OFFER = "Nouvelles offres"
    NEW_OFFERER = "Nouveaux partenaires culturels"


class CollectiveLocationType(enum.Enum):
    SCHOOL = "SCHOOL"
    ADDRESS = "ADDRESS"
    TO_BE_DEFINED = "TO_BE_DEFINED"


@sa_orm.declarative_mixin
class HasImageMixin:
    BASE_URL = f"{settings.OBJECT_STORAGE_URL}/{settings.THUMBS_FOLDER_NAME}"
    FOLDER = settings.THUMBS_FOLDER_NAME

    id: sa_orm.Mapped[int]
    imageId = sa.Column(sa.Text, nullable=True)
    imageCrop: sa_orm.Mapped[dict | None] = sa.Column(
        sa_mutable.MutableDict.as_mutable(postgresql.json.JSONB), nullable=True
    )
    imageCredit = sa.Column(sa.Text, nullable=True)
    # Whether or not we also stored the original image in the storage bucket.
    imageHasOriginal = sa.Column(sa.Boolean, nullable=True)

    @hybrid_property
    def hasImage(self) -> bool:
        return self.imageId is not None

    @hasImage.expression  # type: ignore[no-redef]
    def hasImage(cls) -> sa_elements.BinaryExpression:
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
        *,
        image: bytes,
        credit: str,
        crop_params: image_conversion.CropParams,
        ratio: image_conversion.ImageRatio = image_conversion.ImageRatio.PORTRAIT,
        keep_original: bool = False,
    ) -> None:
        old_id = self.imageId
        if self.hasImage:
            self.delete_image()

        self.imageId = self._generate_new_image_id(old_id)
        self.imageCrop = crop_params.__dict__ if keep_original else None
        self.imageCredit = credit
        self.imageHasOriginal = keep_original

        object_storage.store_public_object(
            folder=self.FOLDER,
            object_id=self._get_image_storage_id(),
            blob=image_conversion.standardize_image(content=image, ratio=ratio, crop_params=crop_params),
            content_type="image/jpeg",
        )
        if keep_original:
            object_storage.store_public_object(
                folder=self.FOLDER,
                object_id=self._get_image_storage_id(original=True),
                blob=image_conversion.process_original_image(content=image, resize=False),
                content_type="image/jpeg",
            )

    def delete_image(self) -> None:
        object_storage.delete_public_object(
            folder=self.FOLDER,
            object_id=self._get_image_storage_id(),
        )
        if self.imageHasOriginal:
            object_storage.delete_public_object(
                folder=self.FOLDER,
                object_id=self._get_image_storage_id(original=True),
            )
        self.imageCrop = None
        self.imageCredit = None
        self.imageHasOriginal = None
        self.imageId = None


@sa_orm.declarative_mixin
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
            if self.hasStartDatetimePassed:
                return offer_mixin.CollectiveOfferStatus.EXPIRED
            if self.isSoldOut:
                return offer_mixin.CollectiveOfferStatus.SOLD_OUT
            if self.hasBookingLimitDatetimesPassed:
                return offer_mixin.CollectiveOfferStatus.INACTIVE
            if self.hasEndDatePassed:
                return offer_mixin.CollectiveOfferStatus.INACTIVE

        return offer_mixin.CollectiveOfferStatus.ACTIVE

    @status.expression  # type: ignore[no-redef]
    def status(cls) -> sa.sql.elements.Case:
        return sa.case(
            (
                cls.isArchived.is_(True),
                offer_mixin.CollectiveOfferStatus.ARCHIVED.name,
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
            (cls.hasStartDatetimePassed, offer_mixin.CollectiveOfferStatus.EXPIRED.name),
            (cls.isSoldOut, offer_mixin.CollectiveOfferStatus.SOLD_OUT.name),
            (cls.hasBookingLimitDatetimesPassed, offer_mixin.CollectiveOfferStatus.INACTIVE.name),
            (cls.hasEndDatePassed, offer_mixin.CollectiveOfferStatus.INACTIVE.name),
            else_=offer_mixin.CollectiveOfferStatus.ACTIVE.name,
        )


class OfferContactFormEnum(enum.Enum):
    FORM = "form"


class CollectiveOfferRejectionReason(enum.Enum):
    CO_FUNDING = "CO_FUNDING"
    CSTI_IRRELEVANT = "CSTI_IRRELEVANT"
    EXAMS_PREPARATION = "EXAMS_PREPARATION"
    HOUSING_CATERING_TRANSPORT = "HOUSING_CATERING_TRANSPORT"
    INELIGIBLE_OFFER = "INELIGIBLE_OFFER"
    INELIGIBLE_SERVICE = "INELIGIBLE_SERVICE"
    MAX_BUDGET_REACHED = "MAX_BUDGET_REACHED"
    MISSING_DESCRIPTION = "MISSING_DESCRIPTION"
    MISSING_DESCRIPTION_AND_DATE = "MISSING_DESCRIPTION_AND_DATE"
    MISSING_MEDIATION = "MISSING_MEDIATION"
    MISSING_PRICE = "MISSING_PRICE"
    OTHER = "OTHER"
    PAST_DATE_OFFER = "PAST_DATE_OFFER"
    PRIMARY_ELEMENTARY_SCHOOL = "PRIMARY_ELEMENTARY_SCHOOL"
    WRONG_DATE = "WRONG_DATE"
    WRONG_PRICE = "WRONG_PRICE"


class ValidationRuleCollectiveOfferLink(PcObject, models.Base, models.Model):
    __tablename__ = "validation_rule_collective_offer_link"
    ruleId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("offer_validation_rule.id", ondelete="CASCADE"), nullable=False
    )
    collectiveOfferId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("collective_offer.id", ondelete="CASCADE"), nullable=False
    )


class ValidationRuleCollectiveOfferTemplateLink(PcObject, models.Base, models.Model):
    __tablename__ = "validation_rule_collective_offer_template_link"
    ruleId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("offer_validation_rule.id", ondelete="CASCADE"), nullable=False
    )
    collectiveOfferTemplateId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("collective_offer_template.id", ondelete="CASCADE"), nullable=False
    )


class CollectiveOfferTemplateDomain(models.Base, models.Model):
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


class CollectiveOfferDomain(models.Base, models.Model):
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


class CollectiveOffer(
    PcObject,
    models.Base,
    offer_mixin.ValidationMixin,
    AccessibilityMixin,
    CollectiveStatusMixin,
    HasImageMixin,
    models.Model,
):
    __tablename__ = "collective_offer"

    isActive: bool = sa.Column(sa.Boolean, nullable=False, server_default=sa.sql.expression.true(), default=True)

    authorId = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), nullable=True)

    author: sa_orm.Mapped["User | None"] = sa_orm.relationship("User", foreign_keys=[authorId], uselist=False)

    # the venueId is the billing address.
    # To find where the offer takes place, check offerVenue.
    venueId: int = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id"), nullable=False, index=True)

    venue: sa_orm.Mapped["Venue"] = sa_orm.relationship(
        "Venue", foreign_keys=[venueId], back_populates="collectiveOffers"
    )

    name: str = sa.Column(sa.String(140), nullable=False)

    bookingEmails: list[str] = sa.Column(
        sa_mutable.MutableList.as_mutable(postgresql.ARRAY(sa.String)),
        nullable=False,
        server_default="{}",
    )

    description: str = sa.Column(sa.Text, nullable=False, server_default="", default="")

    durationMinutes = sa.Column(sa.Integer, nullable=True)

    dateCreated: datetime.datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)

    dateArchived: datetime.datetime | None = sa.Column(sa.DateTime, nullable=True)

    dateUpdated: datetime.datetime = sa.Column(
        sa.DateTime, nullable=True, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    students: list[StudentLevels] = sa.Column(
        sa_mutable.MutableList.as_mutable(postgresql.ARRAY(sa.Enum(StudentLevels))),
        nullable=False,
        server_default="{}",
    )

    collectiveStock: sa_orm.Mapped["CollectiveStock"] = sa_orm.relationship(
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
    offerVenue: sa_orm.Mapped[OfferVenueDictStr] = sa.Column(
        sa_mutable.MutableDict.as_mutable(postgresql.json.JSONB), nullable=False
    )

    interventionArea: list[str] = sa.Column(
        sa_mutable.MutableList.as_mutable(postgresql.ARRAY(sa.Text())), nullable=False, server_default="{}"
    )

    domains: sa_orm.Mapped[list["EducationalDomain"]] = sa_orm.relationship(
        "EducationalDomain", secondary=CollectiveOfferDomain.__table__, back_populates="collectiveOffers"
    )

    institutionId = sa.Column(sa.BigInteger, sa.ForeignKey("educational_institution.id"), index=True, nullable=True)

    institution: sa_orm.Mapped["EducationalInstitution | None"] = sa_orm.relationship(
        "EducationalInstitution", foreign_keys=[institutionId], back_populates="collectiveOffers"
    )

    templateId: int | None = sa.Column(
        sa.BigInteger, sa.ForeignKey("collective_offer_template.id"), index=True, nullable=True
    )

    template: sa_orm.Mapped["CollectiveOfferTemplate | None"] = sa_orm.relationship(
        "CollectiveOfferTemplate", foreign_keys=[templateId], back_populates="collectiveOffers"
    )

    teacherId: int | None = sa.Column(
        sa.BigInteger,
        sa.ForeignKey("educational_redactor.id"),
        nullable=True,
        index=True,
    )

    teacher: sa_orm.Mapped["EducationalRedactor"] = sa_orm.relationship(
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

    provider: sa_orm.Mapped["Provider"] = sa_orm.relationship(
        "Provider", foreign_keys=providerId, back_populates="collectiveOffers"
    )

    flaggingValidationRules: sa_orm.Mapped[list["OfferValidationRule"]] = sa_orm.relationship(
        "OfferValidationRule", secondary=ValidationRuleCollectiveOfferLink.__table__, back_populates="collectiveOffers"
    )

    formats: list[EacFormat] = sa.Column(
        postgresql.ARRAY(sa.Enum(EacFormat, create_constraint=False, native_enum=False)), nullable=False
    )

    rejectionReason: CollectiveOfferRejectionReason | None = sa.Column(
        db_utils.MagicEnum(CollectiveOfferRejectionReason), default=None
    )

    isNonFreeOffer: sa_orm.Mapped["bool | None"] = sa_orm.query_expression()

    offererAddressId: sa_orm.Mapped[int | None] = sa.Column(
        sa.BigInteger, sa.ForeignKey("offerer_address.id"), nullable=True, index=True
    )
    offererAddress: sa_orm.Mapped["OffererAddress | None"] = sa_orm.relationship(
        "OffererAddress", foreign_keys=offererAddressId, uselist=False
    )

    locationType: sa_orm.Mapped[CollectiveLocationType | None] = sa.Column(
        db_utils.MagicEnum(CollectiveLocationType), nullable=True, server_default=None, default=None
    )
    locationComment: sa_orm.Mapped[str | None] = sa.Column(sa.Text(), nullable=True)

    @sa_orm.declared_attr
    def __table_args__(self):
        parent_args = []
        # Retrieves indexes from parent mixins defined in __table_args__
        for base_class in self.__mro__:
            try:
                parent_args += super(base_class, self).__table_args__
            except (AttributeError, TypeError):
                pass

        parent_args += [
            sa.CheckConstraint(
                f"length(description) <= {MAX_COLLECTIVE_DESCRIPTION_LENGTH}",
                name="collective_offer_description_constraint",
            ),
            sa.CheckConstraint(
                '"locationComment" IS NULL OR length("locationComment") <= 200',
                name="collective_offer_location_comment_constraint",
            ),
        ]

        return tuple(parent_args)

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

    nationalProgram: sa_orm.Mapped["NationalProgram"] = sa_orm.relationship(
        "NationalProgram", foreign_keys=nationalProgramId
    )

    @property
    def isEditable(self) -> bool:
        return self.status not in [
            offer_mixin.CollectiveOfferStatus.PENDING,
            offer_mixin.CollectiveOfferStatus.REJECTED,
        ]

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
    def hasEndDatePassed(cls) -> sa_elements.False_:
        return sa.sql.expression.false()

    @hybrid_property
    def isSoldOut(self) -> bool:
        if self.collectiveStock:
            return self.collectiveStock.isSoldOut
        return True

    @isSoldOut.expression  # type: ignore[no-redef]
    def isSoldOut(cls) -> sa_selectable.Exists:
        aliased_collective_stock = sa_orm.aliased(CollectiveStock)
        aliased_collective_booking = sa_orm.aliased(CollectiveBooking)
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
    def isArchived(cls) -> sa.Boolean:
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
    def start(self) -> datetime.datetime | None:
        if not self.collectiveStock:
            return None

        return self.collectiveStock.startDatetime

    @property
    def end(self) -> datetime.datetime | None:
        if not self.collectiveStock:
            return None

        return self.collectiveStock.endDatetime

    @property
    def dates(self) -> dict | None:
        if not self.start or not self.end:
            return None
        return {"start": self.start, "end": self.end}

    @hybrid_property
    def hasStartDatetimePassed(self) -> bool:
        if not self.collectiveStock:
            return False
        return self.collectiveStock.hasStartDatetimePassed

    @hasStartDatetimePassed.expression  # type: ignore[no-redef]
    def hasStartDatetimePassed(cls) -> sa_selectable.Exists:
        aliased_collective_stock = sa_orm.aliased(CollectiveStock)
        return (
            sa.exists()
            .where(aliased_collective_stock.collectiveOfferId == cls.id)
            .where(aliased_collective_stock.hasStartDatetimePassed.is_(True))
        )

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
    def hasBookingLimitDatetimesPassed(cls) -> sa_selectable.Exists:
        aliased_collective_stock = sa_orm.aliased(CollectiveStock)
        return (
            sa.exists()
            .where(aliased_collective_stock.collectiveOfferId == cls.id)
            .where(aliased_collective_stock.hasBookingLimitDatetimePassed.is_(True))
        )

    @hybrid_property
    def hasEndDatetimePassed(self) -> bool:
        if not self.collectiveStock:
            return False
        return self.collectiveStock.hasEndDatetimePassed

    @hasEndDatetimePassed.expression  # type: ignore[no-redef]
    def hasEndDatetimePassed(cls) -> sa_selectable.Exists:
        aliased_collective_stock = sa_orm.aliased(CollectiveStock)
        return (
            sa.exists()
            .where(aliased_collective_stock.collectiveOfferId == cls.id)
            .where(aliased_collective_stock.hasEndDatetimePassed.is_(True))
        )

    @property
    def days_until_booking_limit(self) -> int | None:
        if not self.collectiveStock:
            return None

        delta = self.collectiveStock.bookingLimitDatetime - datetime.datetime.utcnow()
        return delta.days

    @property
    def requires_attention(self) -> bool:
        is_prebooked = (
            False
            if not self.collectiveStock
            else any(
                booking.status == CollectiveBookingStatus.PENDING for booking in self.collectiveStock.collectiveBookings
            )
        )
        is_published = self.status == offer_mixin.CollectiveOfferStatus.ACTIVE
        if self.days_until_booking_limit is not None:
            return self.days_until_booking_limit < 7 and (is_prebooked or is_published)

        return False

    @property
    def sort_criterion(self) -> typing.Tuple[bool, int, datetime.datetime]:
        """
        This is used to sort offers with the following criterium.

        1. Archived offers are not relevant
        2. Published or prebooked offers with a booking limit in a near future (ie < 7 days) are relevant
        3. DateCreated is to be used as a default rule. Older -> less relevant that younger
        """
        if self.requires_attention and self.days_until_booking_limit is not None:
            date_limit_score = self.days_until_booking_limit
        else:
            date_limit_score = BIG_NUMBER_FOR_SORTING_OFFERS

        return not self.isArchived, -date_limit_score, self.dateCreated

    @property
    def displayedStatus(self) -> CollectiveOfferDisplayedStatus:
        if self.isArchived:
            return CollectiveOfferDisplayedStatus.ARCHIVED

        match self.validation:
            case offer_mixin.OfferValidationStatus.DRAFT:
                return CollectiveOfferDisplayedStatus.DRAFT
            case offer_mixin.OfferValidationStatus.PENDING:
                return CollectiveOfferDisplayedStatus.UNDER_REVIEW
            case offer_mixin.OfferValidationStatus.REJECTED:
                return CollectiveOfferDisplayedStatus.REJECTED
            case offer_mixin.OfferValidationStatus.APPROVED:
                if not self.isActive:
                    return CollectiveOfferDisplayedStatus.HIDDEN

                last_booking_status = self.lastBookingStatus
                has_booking_limit_passed = self.hasBookingLimitDatetimesPassed
                has_started = self.hasStartDatetimePassed
                has_ended = self.hasEndDatetimePassed

                match last_booking_status:
                    case None:
                        if has_started:
                            return CollectiveOfferDisplayedStatus.CANCELLED

                        if has_booking_limit_passed:
                            return CollectiveOfferDisplayedStatus.EXPIRED

                        return CollectiveOfferDisplayedStatus.PUBLISHED

                    case CollectiveBookingStatus.PENDING:
                        if has_booking_limit_passed:
                            return CollectiveOfferDisplayedStatus.EXPIRED
                        return CollectiveOfferDisplayedStatus.PREBOOKED

                    case CollectiveBookingStatus.CONFIRMED:
                        if has_ended:
                            return CollectiveOfferDisplayedStatus.ENDED
                        return CollectiveOfferDisplayedStatus.BOOKED

                    case CollectiveBookingStatus.USED:
                        return CollectiveOfferDisplayedStatus.ENDED

                    case CollectiveBookingStatus.REIMBURSED:
                        return CollectiveOfferDisplayedStatus.REIMBURSED

                    case CollectiveBookingStatus.CANCELLED:
                        if (
                            self.lastBookingCancellationReason == CollectiveBookingCancellationReasons.EXPIRED
                            and not has_started
                        ):
                            # There is a script that set the booking status to CANCELLED with cancellation reason EXPIRED when the booking is expired.
                            # We need to distinguish between an expired booking and a cancelled booking.
                            return CollectiveOfferDisplayedStatus.EXPIRED

                        return CollectiveOfferDisplayedStatus.CANCELLED

        logger.error("Incorrect status: %s %s", self.validation, last_booking_status)
        return CollectiveOfferDisplayedStatus.PUBLISHED

    def _get_allowed_actions(self) -> tuple[CollectiveOfferAllowedAction, ...]:
        displayed_status = self.displayedStatus
        allowed_actions = ALLOWED_ACTIONS_BY_DISPLAYED_STATUS[displayed_status]

        # an offer that has ended more than 48 hours ago cannot have its price edited or be canceled
        if displayed_status == CollectiveOfferDisplayedStatus.ENDED and self.is_two_days_past_end():
            not_allowed = {
                CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT,
                CollectiveOfferAllowedAction.CAN_CANCEL,
            }
            return tuple(action for action in allowed_actions if action not in not_allowed)

        return allowed_actions

    @property
    def allowedActionsForPublicApi(self) -> list[CollectiveOfferAllowedAction]:
        """The list of allowed actions in the context of public API"""

        # an offer created in PC Pro cannot be edited with the public API
        if not self.isPublicApi:
            return []

        return list(self._get_allowed_actions())

    @property
    def allowedActions(self) -> list[CollectiveOfferAllowedAction]:
        """The list of allowed actions in the context of PC Pro"""

        allowed_actions = self._get_allowed_actions()

        # an offer created with the public API cannot be edited in PC Pro
        if self.isPublicApi:
            not_allowed = {
                CollectiveOfferAllowedAction.CAN_EDIT_DETAILS,
                CollectiveOfferAllowedAction.CAN_EDIT_DATES,
                CollectiveOfferAllowedAction.CAN_EDIT_INSTITUTION,
                CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT,
            }

            return [action for action in allowed_actions if action not in not_allowed]

        return list(allowed_actions)

    @property
    def visibleText(self) -> str:  # used in validation rule, do not remove
        text_data: list[str] = [self.name, self.description]
        if self.collectiveStock and self.collectiveStock.priceDetail:
            text_data.append(self.collectiveStock.priceDetail)
        return " ".join(text_data)

    @property
    def is_cancellable_from_offerer(self) -> bool:
        if self.collectiveStock is None:
            return False
        return self.collectiveStock.is_cancellable_from_offerer

    @property
    def lastBooking(self) -> "CollectiveBooking | None":
        stock = self.collectiveStock
        if stock is None:
            return None

        return stock.lastBooking

    @property
    def lastBookingId(self) -> int | None:
        booking = self.lastBooking
        return booking.id if booking else None

    @property
    def lastBookingStatus(self) -> CollectiveBookingStatus | None:
        booking = self.lastBooking
        return booking.status if booking else None

    @property
    def lastBookingCancellationReason(self) -> CollectiveBookingCancellationReasons | None:
        booking = self.lastBooking
        return booking.cancellationReason if booking else None

    @hybrid_property
    def is_expired(self) -> bool:
        return self.hasStartDatetimePassed

    @is_expired.expression  # type: ignore[no-redef]
    def is_expired(cls) -> sa_elements.UnaryExpression:
        return cls.hasStartDatetimePassed

    def is_two_days_past_end(self) -> bool:
        if self.collectiveStock is None:
            return False

        return self.collectiveStock.is_two_days_past_end()


class CollectiveOfferTemplateEducationalRedactor(PcObject, models.Base, models.Model):
    """Allow adding to favorite the offer template for adage user"""

    __tablename__ = "collective_offer_template_educational_redactor"

    educationalRedactorId: int = sa.Column(sa.BigInteger, sa.ForeignKey("educational_redactor.id"), nullable=False)
    collectiveOfferTemplateId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("collective_offer_template.id"), nullable=False
    )
    collectiveOfferTemplate: sa_orm.Mapped["CollectiveOfferTemplate"] = sa_orm.relationship(
        "CollectiveOfferTemplate", foreign_keys=[collectiveOfferTemplateId], viewonly=True
    )
    __table_args__ = (
        sa.UniqueConstraint("educationalRedactorId", "collectiveOfferTemplateId", name="unique_redactorId_template"),
    )


class CollectiveOfferTemplate(
    PcObject,
    offer_mixin.ValidationMixin,
    AccessibilityMixin,
    CollectiveStatusMixin,
    HasImageMixin,
    models.Base,
    models.Model,
):
    __tablename__ = "collective_offer_template"

    isActive: bool = sa.Column(sa.Boolean, nullable=False, server_default=sa.sql.expression.true(), default=True)

    authorId = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), nullable=True)

    author: sa_orm.Mapped["User | None"] = sa_orm.relationship("User", foreign_keys=[authorId], uselist=False)

    venueId: int = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id"), nullable=False, index=True)

    venue: sa_orm.Mapped["Venue"] = sa_orm.relationship(
        "Venue", foreign_keys=[venueId], back_populates="collectiveOfferTemplates"
    )

    name: str = sa.Column(sa.String(140), nullable=False)

    description: str = sa.Column(sa.Text, nullable=False, server_default="", default="")

    durationMinutes = sa.Column(sa.Integer, nullable=True)

    dateCreated: datetime.datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)

    dateUpdated: datetime.datetime = sa.Column(
        sa.DateTime, nullable=True, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    students: list[StudentLevels] = sa.Column(
        sa_mutable.MutableList.as_mutable(postgresql.ARRAY(sa.Enum(StudentLevels))),
        nullable=False,
        server_default="{}",
    )

    priceDetail = sa.Column(sa.Text, nullable=True)

    bookingEmails: list[str] = sa.Column(
        sa_mutable.MutableList.as_mutable(postgresql.ARRAY(sa.String)),
        nullable=False,
        server_default="{}",
    )

    offerVenue: sa_orm.Mapped[OfferVenueDictStr] = sa.Column(
        sa_mutable.MutableDict.as_mutable(postgresql.json.JSONB), nullable=False
    )

    interventionArea: list[str] = sa.Column(
        sa_mutable.MutableList.as_mutable(postgresql.ARRAY(sa.Text())), nullable=False, server_default="{}"
    )

    domains: sa_orm.Mapped[list["EducationalDomain"]] = sa_orm.relationship(
        "EducationalDomain",
        secondary=CollectiveOfferTemplateDomain.__table__,
        back_populates="collectiveOfferTemplates",
    )

    collectiveOffers: sa_orm.Mapped[list["CollectiveOffer"]] = sa_orm.relationship(
        "CollectiveOffer", back_populates="template"
    )

    flaggingValidationRules: sa_orm.Mapped[list["OfferValidationRule"]] = sa_orm.relationship(
        "OfferValidationRule",
        secondary=ValidationRuleCollectiveOfferTemplateLink.__table__,
        back_populates="collectiveOfferTemplates",
    )

    # does the collective offer belongs to a national program
    nationalProgramId: int | None = sa.Column(
        sa.BigInteger,
        sa.ForeignKey("national_program.id"),
        nullable=True,
        index=True,
    )

    nationalProgram: sa_orm.Mapped["NationalProgram"] = sa_orm.relationship(
        "NationalProgram", foreign_keys=nationalProgramId
    )

    educationalRedactorsFavorite: sa_orm.Mapped[list["EducationalRedactor"]] = sa_orm.relationship(
        "EducationalRedactor",
        secondary=CollectiveOfferTemplateEducationalRedactor.__table__,
        back_populates="favoriteCollectiveOfferTemplates",
    )

    dateRange: DateTimeRange = sa.Column(postgresql.TSRANGE)

    formats: list[EacFormat] = sa.Column(
        postgresql.ARRAY(sa.Enum(EacFormat, create_constraint=False, native_enum=False)), nullable=False
    )

    collective_playlists: sa_orm.Mapped[list["CollectivePlaylist"]] = sa_orm.relationship(
        "CollectivePlaylist", back_populates="collective_offer_template"
    )

    contactEmail: str | None = sa.Column(sa.String(120), nullable=True)
    contactPhone: str | None = sa.Column(sa.Text, nullable=True)
    contactUrl: str | None = sa.Column(sa.Text, nullable=True)
    contactForm: OfferContactFormEnum | None = sa.Column(
        db_utils.MagicEnum(OfferContactFormEnum),
        nullable=True,
        server_default=None,
        default=None,
    )

    rejectionReason: CollectiveOfferRejectionReason | None = sa.Column(
        db_utils.MagicEnum(CollectiveOfferRejectionReason), default=None
    )

    offererAddressId: sa_orm.Mapped[int | None] = sa.Column(
        sa.BigInteger, sa.ForeignKey("offerer_address.id"), nullable=True, index=True
    )
    offererAddress: sa_orm.Mapped["OffererAddress | None"] = sa_orm.relationship(
        "OffererAddress", foreign_keys=[offererAddressId], uselist=False
    )

    locationType: sa_orm.Mapped[CollectiveLocationType | None] = sa.Column(
        db_utils.MagicEnum(CollectiveLocationType), nullable=True, server_default=None, default=None
    )
    locationComment: sa_orm.Mapped[str | None] = sa.Column(sa.Text(), nullable=True)

    dateArchived: datetime.datetime | None = sa.Column(sa.DateTime, nullable=True)

    @sa_orm.declared_attr
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
            sa.CheckConstraint(
                f"length(description) <= {MAX_COLLECTIVE_DESCRIPTION_LENGTH}",
                name="collective_offer_tmpl_description_constraint",
            ),
            sa.CheckConstraint(
                '"locationComment" IS NULL OR length("locationComment") <= 200',
                name="collective_offer_tmpl_location_comment_constraint",
            ),
        ]

        return tuple(parent_args)

    @hybrid_property
    def displayedStatus(self) -> CollectiveOfferDisplayedStatus:
        if self.isArchived:
            return CollectiveOfferDisplayedStatus.ARCHIVED

        if self.validation == offer_mixin.OfferValidationStatus.REJECTED:
            return CollectiveOfferDisplayedStatus.REJECTED

        if self.validation == offer_mixin.OfferValidationStatus.PENDING:
            return CollectiveOfferDisplayedStatus.UNDER_REVIEW

        if self.validation == offer_mixin.OfferValidationStatus.DRAFT:
            return CollectiveOfferDisplayedStatus.DRAFT

        if self.hasEndDatePassed:
            return CollectiveOfferDisplayedStatus.ENDED

        if not self.isActive:
            return CollectiveOfferDisplayedStatus.HIDDEN

        return CollectiveOfferDisplayedStatus.PUBLISHED

    @displayedStatus.expression  # type: ignore[no-redef]
    def displayedStatus(cls) -> sa.sql.elements.Case:
        return sa.case(
            (
                cls.isArchived.is_(True),
                CollectiveOfferDisplayedStatus.ARCHIVED.name,
            ),
            (
                cls.validation == offer_mixin.OfferValidationStatus.REJECTED.name,
                CollectiveOfferDisplayedStatus.REJECTED.name,
            ),
            (
                cls.validation == offer_mixin.OfferValidationStatus.PENDING.name,
                CollectiveOfferDisplayedStatus.UNDER_REVIEW.name,
            ),
            (
                cls.validation == offer_mixin.OfferValidationStatus.DRAFT.name,
                CollectiveOfferDisplayedStatus.DRAFT.name,
            ),
            (cls.hasEndDatePassed, CollectiveOfferDisplayedStatus.ENDED.name),
            (cls.isActive.is_(False), CollectiveOfferDisplayedStatus.HIDDEN.name),
            else_=CollectiveOfferDisplayedStatus.PUBLISHED.name,
        )

    @property
    def allowedActions(self) -> list[CollectiveOfferTemplateAllowedAction]:
        return list(TEMPLATE_ALLOWED_ACTIONS_BY_DISPLAYED_STATUS[self.displayedStatus])

    @property
    def start(self) -> datetime.datetime | None:
        if not self.dateRange:
            return None
        return self.dateRange.lower

    @property
    def end(self) -> datetime.datetime | None:
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

    @hybrid_property
    def hasEndDatePassed(self) -> bool:
        if not self.end:
            return False
        return self.end < datetime.datetime.utcnow()

    @hasEndDatePassed.expression  # type: ignore[no-redef]
    def hasEndDatePassed(cls) -> sa_elements.BooleanClauseList:
        return sa.and_(
            cls.dateRange.is_not(None),
            sa.func.upper(cls.dateRange) < sa.func.now(),
        )

    @hybrid_property
    def hasBookingLimitDatetimesPassed(self) -> bool:
        # this property is here for compatibility reasons
        return False

    @hasBookingLimitDatetimesPassed.expression  # type: ignore[no-redef]
    def hasBookingLimitDatetimesPassed(cls) -> sa_elements.False_:
        # this property is here for compatibility reasons
        return sa.sql.expression.false()

    @hybrid_property
    def hasStartDatetimePassed(self) -> bool:
        # this property is here for compatibility reasons
        return False

    @hasStartDatetimePassed.expression  # type: ignore[no-redef]
    def hasStartDatetimePassed(cls) -> sa_elements.False_:
        # this property is here for compatibility reasons
        return sa.sql.expression.false()

    @hybrid_property
    def hasEndDatetimePassed(self) -> bool:
        # this property is here for compatibility reasons
        return False

    @hasEndDatetimePassed.expression  # type: ignore[no-redef]
    def hasEndDatetimePassed(cls) -> sa_elements.False_:
        # this property is here for compatibility reasons
        return sa.sql.expression.false()

    @hybrid_property
    def isArchived(self) -> bool:
        return self.dateArchived is not None

    @isArchived.expression  # type: ignore[no-redef]
    def isArchived(cls) -> sa.Boolean:
        return cls.dateArchived.is_not(sa.null())

    @hybrid_property
    def isSoldOut(self) -> bool:
        # this property is here for compatibility reasons
        return False

    @isSoldOut.expression  # type: ignore[no-redef]
    def isSoldOut(cls) -> sa_elements.False_:
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
    def sort_criterion(self) -> typing.Tuple[bool, int, datetime.datetime]:
        """
        This is is used to compare offers.

        For template offers there is no booking_limit criterium. Thats is why we define the second value of the tuple
        to the constant.
        """
        return (not self.isArchived, -BIG_NUMBER_FOR_SORTING_OFFERS, self.dateCreated)

    @property
    def visibleText(self) -> str:  # used in validation rule, do not remove
        return f"{self.name} {self.description} {self.priceDetail}"

    @property
    def is_cancellable_from_offerer(self) -> bool:
        return False

    @hybrid_property
    def is_expired(self) -> bool:
        return self.hasStartDatetimePassed

    @is_expired.expression  # type: ignore[no-redef]
    def is_expired(cls) -> sa_elements.UnaryExpression:
        return cls.hasStartDatetimePassed


class CollectiveStock(PcObject, models.Base, models.Model):
    __tablename__ = "collective_stock"

    dateCreated: datetime.datetime = sa.Column(
        sa.DateTime, nullable=False, default=datetime.datetime.utcnow, server_default=sa.func.now()
    )

    dateModified: datetime.datetime = sa.Column(
        sa.DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    startDatetime: datetime.datetime = sa.Column(sa.DateTime, nullable=False)
    endDatetime: datetime.datetime = sa.Column(sa.DateTime, nullable=False)
    sa.Index("ix_collective_stock_startDatetime_endDatetime", startDatetime, endDatetime)

    collectiveOfferId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("collective_offer.id"), index=True, nullable=False, unique=True
    )

    collectiveOffer: sa_orm.Mapped["CollectiveOffer"] = sa_orm.relationship(
        "CollectiveOffer", foreign_keys=[collectiveOfferId], uselist=False, back_populates="collectiveStock"
    )

    collectiveBookings: sa_orm.Mapped[list["CollectiveBooking"]] = sa_orm.relationship(
        "CollectiveBooking", back_populates="collectiveStock"
    )

    price: decimal.Decimal = sa.Column(
        sa.Numeric(10, 2),
        sa.CheckConstraint("price >= 0", name="check_price_is_not_negative"),
        index=True,
        nullable=False,
    )

    bookingLimitDatetime: datetime.datetime = sa.Column(sa.DateTime, nullable=False)

    numberOfTickets: int = sa.Column(sa.Integer, nullable=False)

    priceDetail = sa.Column(sa.Text, nullable=True)

    @property
    def lastBooking(self) -> "CollectiveBooking | None":
        bookings = sorted(self.collectiveBookings, key=lambda booking: booking.dateCreated)
        return bookings[-1] if bookings else None

    @property
    def lastBookingStatus(self) -> CollectiveBookingStatus | None:
        booking = self.lastBooking
        return booking.status if booking else None

    @property
    def isBookable(self) -> bool:
        if self.lastBookingStatus == CollectiveBookingStatus.CANCELLED:
            return False

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
        return self.bookingLimitDatetime <= datetime.datetime.utcnow()

    @hasBookingLimitDatetimePassed.expression  # type: ignore[no-redef]
    def hasBookingLimitDatetimePassed(cls) -> sa_elements.BinaryExpression:
        return cls.bookingLimitDatetime <= sa.func.now()

    @hybrid_property
    def hasStartDatetimePassed(self) -> bool:
        return self.startDatetime <= datetime.datetime.utcnow()

    @hasStartDatetimePassed.expression  # type: ignore[no-redef]
    def hasStartDatetimePassed(cls) -> sa_elements.BinaryExpression:
        return cls.startDatetime <= sa.func.now()

    @hybrid_property
    def hasEndDatetimePassed(self) -> bool:
        return self.endDatetime <= datetime.datetime.utcnow()

    @hasEndDatetimePassed.expression  # type: ignore[no-redef]
    def hasEndDatetimePassed(cls) -> sa_elements.BinaryExpression:
        return cls.endDatetime <= sa.func.now()

    @hybrid_property
    def isEventExpired(self) -> bool:
        return self.startDatetime <= datetime.datetime.utcnow()

    @isEventExpired.expression  # type: ignore[no-redef]
    def isEventExpired(cls):
        return cls.startDatetime <= sa.func.now()

    @property
    def isExpired(self) -> bool:
        return self.isEventExpired or self.hasBookingLimitDatetimePassed

    def get_non_cancelled_bookings(self) -> list["CollectiveBooking"]:
        return [booking for booking in self.collectiveBookings if booking.status != CollectiveBookingStatus.CANCELLED]

    def get_unique_non_cancelled_booking(self) -> "CollectiveBooking | None":
        non_cancelled_bookings = self.get_non_cancelled_bookings()
        if len(non_cancelled_bookings) > 1:
            raise educational_exceptions.MultipleCollectiveBookingFound()
        return non_cancelled_bookings[0] if non_cancelled_bookings else None

    def is_two_days_past_end(self) -> bool:
        return self.endDatetime + datetime.timedelta(days=2) < datetime.datetime.utcnow()

    @property
    def isSoldOut(self) -> bool:
        non_cancelled_bookings = self.get_non_cancelled_bookings()
        return len(non_cancelled_bookings) > 0

    @property
    def is_cancellable_from_offerer(self) -> bool:
        if any(booking.is_cancellable_from_offerer for booking in self.collectiveBookings):
            return True

        return False


class EducationalInstitution(PcObject, models.Base, models.Model):
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

    collectiveOffers: sa_orm.Mapped[list["CollectiveOffer"]] = sa_orm.relationship(
        "CollectiveOffer", back_populates="institution"
    )

    isActive: bool = sa.Column(sa.Boolean, nullable=False, server_default=sa.sql.expression.true(), default=True)

    programAssociations: sa_orm.Mapped[list["EducationalInstitutionProgramAssociation"]] = sa_orm.relationship(
        "EducationalInstitutionProgramAssociation", back_populates="institution"
    )

    ruralLevel: InstitutionRuralLevel = sa.Column(
        db_utils.MagicEnum(InstitutionRuralLevel), nullable=True, default=None
    )

    collective_playlists: sa_orm.Mapped[list["CollectivePlaylist"]] = sa_orm.relationship(
        "CollectivePlaylist", back_populates="institution"
    )

    latitude: decimal.Decimal | None = sa.Column(sa.Numeric(8, 5), nullable=True)

    longitude: decimal.Decimal | None = sa.Column(sa.Numeric(8, 5), nullable=True)

    __table_args__ = (
        sa.Index("ix_educational_institution_type_name_city", institutionType + " " + name + " " + city),
        sa.Index(
            "ix_educational_institution_department_code",
            sa.func.postal_code_to_department_code(postalCode),
            "id",
        ),
    )

    @property
    def full_name(self) -> str:
        return f"{self.institutionType} {self.name}".strip()

    def programs_at_date(self, date: datetime.datetime) -> list["EducationalInstitutionProgram"]:
        return [association.program for association in self.programAssociations if date in association.timespan]


class EducationalYear(PcObject, models.Base, models.Model):
    __tablename__ = "educational_year"

    adageId: str = sa.Column(sa.String(30), unique=True, nullable=False)

    beginningDate: datetime.datetime = sa.Column(sa.DateTime, nullable=False)

    expirationDate: datetime.datetime = sa.Column(sa.DateTime, nullable=False)


class EducationalDeposit(PcObject, models.Base, models.Model):
    __tablename__ = "educational_deposit"

    TEMPORARY_FUND_AVAILABLE_RATIO = 0.8

    educationalInstitutionId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("educational_institution.id"), index=True, nullable=False
    )

    educationalInstitution: sa_orm.Mapped[EducationalInstitution] = sa_orm.relationship(
        EducationalInstitution, foreign_keys=[educationalInstitutionId], backref="deposits"
    )

    educationalYearId: str = sa.Column(
        sa.String(30), sa.ForeignKey("educational_year.adageId"), index=True, nullable=False
    )

    educationalYear: sa_orm.Mapped["EducationalYear"] = sa_orm.relationship(
        EducationalYear, foreign_keys=[educationalYearId], backref="deposits"
    )

    amount: decimal.Decimal = sa.Column(sa.Numeric(10, 2), nullable=False)

    dateCreated: datetime.datetime = sa.Column(
        sa.DateTime, nullable=False, default=datetime.datetime.utcnow, server_default=sa.func.now()
    )

    isFinal: bool = sa.Column(sa.Boolean, nullable=False, default=True)

    ministry = sa.Column(
        sa.Enum(Ministry),
        nullable=True,
    )

    def check_has_enough_fund(self, total_amount_after_booking: decimal.Decimal) -> None:
        """Check that the total amount of bookings won't exceed the
        deposit's amount.

        Note:
          if the deposit is not the final one, only a part of it can
          be consumed (eg. only 80% can be used).
        """
        if self.isFinal:
            if self.amount < total_amount_after_booking:
                raise educational_exceptions.InsufficientFund()
        else:
            ratio = decimal.Decimal(self.TEMPORARY_FUND_AVAILABLE_RATIO)
            temporary_fund = round(self.amount * ratio, 2)

            if temporary_fund < total_amount_after_booking:
                raise educational_exceptions.InsufficientTemporaryFund()


class EducationalRedactor(PcObject, models.Base, models.Model):
    __tablename__ = "educational_redactor"

    email: str = sa.Column(sa.String(120), nullable=False, unique=True, index=True)

    firstName = sa.Column(sa.String(128), nullable=True)

    lastName = sa.Column(sa.String(128), nullable=True)

    civility = sa.Column(sa.String(20), nullable=True)

    preferences: sa_orm.Mapped[dict] = sa.Column(postgresql.JSONB(), server_default="{}", default={}, nullable=False)

    collectiveBookings: sa_orm.Mapped[list["CollectiveBooking"]] = sa_orm.relationship(
        "CollectiveBooking", back_populates="educationalRedactor"
    )

    collectiveOffers: sa_orm.Mapped[list["CollectiveOffer"]] = sa_orm.relationship(
        "CollectiveOffer", back_populates="teacher"
    )

    favoriteCollectiveOfferTemplates: sa_orm.Mapped[list["CollectiveOfferTemplate"]] = sa_orm.relationship(
        "CollectiveOfferTemplate",
        secondary=CollectiveOfferTemplateEducationalRedactor.__table__,
        back_populates="educationalRedactorsFavorite",
    )

    @property
    def full_name(self) -> str:
        # full_name is used for display and should never be empty, which would be confused with no user.
        # We use the email as a fallback because it is the most human-readable way to identify a single user
        return (f"{self.firstName or ''} {self.lastName or ''}".strip()) or self.email


class CollectiveBooking(PcObject, models.Base, models.Model):
    __tablename__ = "collective_booking"

    dateCreated: datetime.datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)
    sa.Index("ix_collective_booking_date_created", dateCreated)

    dateUsed = sa.Column(sa.DateTime, nullable=True, index=True)

    collectiveStockId: int = sa.Column(sa.BigInteger, sa.ForeignKey("collective_stock.id"), index=True, nullable=False)

    collectiveStock: sa_orm.Mapped["CollectiveStock"] = sa_orm.relationship(
        "CollectiveStock", foreign_keys=[collectiveStockId], back_populates="collectiveBookings"
    )

    venueId: int = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id"), index=True, nullable=False)

    venue: sa_orm.Mapped["Venue"] = sa_orm.relationship("Venue", foreign_keys=[venueId], backref="collectiveBookings")

    offererId: int = sa.Column(sa.BigInteger, sa.ForeignKey("offerer.id"), index=True, nullable=False)

    offerer: sa_orm.Mapped["Offerer"] = sa_orm.relationship(
        "Offerer", foreign_keys=[offererId], backref="collectiveBookings"
    )

    cancellationDate = sa.Column(sa.DateTime, nullable=True)

    cancellationUserId: int | None = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), nullable=True)

    cancellationUser: sa_orm.Mapped["User | None"] = sa_orm.relationship("User", foreign_keys=[cancellationUserId])

    cancellationLimitDate: datetime.datetime = sa.Column(sa.DateTime, nullable=False)

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

    sa.Index("ix_collective_booking_status", status)

    reimbursementDate = sa.Column(sa.DateTime, nullable=True)

    educationalInstitutionId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("educational_institution.id"), nullable=False
    )
    educationalInstitution: sa_orm.Mapped["EducationalInstitution"] = sa_orm.relationship(
        EducationalInstitution, foreign_keys=[educationalInstitutionId], backref="collectiveBookings"
    )

    educationalYearId: str = sa.Column(sa.String(30), sa.ForeignKey("educational_year.adageId"), nullable=False)
    educationalYear: sa_orm.Mapped["EducationalYear"] = sa_orm.relationship(
        EducationalYear, foreign_keys=[educationalYearId]
    )

    sa.Index("ix_collective_booking_educationalYear_and_institution", educationalYearId, educationalInstitutionId)

    confirmationDate = sa.Column(sa.DateTime, nullable=True)
    confirmationLimitDate: datetime.datetime = sa.Column(sa.DateTime, nullable=False)

    educationalRedactorId: int = sa.Column(
        sa.BigInteger,
        sa.ForeignKey("educational_redactor.id"),
        nullable=False,
        index=True,
    )
    educationalRedactor: sa_orm.Mapped["EducationalRedactor"] = sa_orm.relationship(
        EducationalRedactor,
        back_populates="collectiveBookings",
        uselist=False,
    )

    def cancel_booking(
        self,
        reason: CollectiveBookingCancellationReasons,
        cancel_even_if_used: bool = False,
        cancel_even_if_reimbursed: bool = False,
        author_id: int | None = None,
    ) -> None:
        if self.status is CollectiveBookingStatus.CANCELLED:
            raise educational_exceptions.CollectiveBookingAlreadyCancelled()
        if self.status is CollectiveBookingStatus.REIMBURSED and not cancel_even_if_reimbursed:
            raise educational_exceptions.CollectiveBookingIsAlreadyUsed
        if self.status is CollectiveBookingStatus.USED and not cancel_even_if_used:
            raise educational_exceptions.CollectiveBookingIsAlreadyUsed
        self.status = CollectiveBookingStatus.CANCELLED
        self.cancellationDate = datetime.datetime.utcnow()
        self.cancellationReason = reason
        self.cancellationUserId = author_id
        self.dateUsed = None

    def uncancel_booking(self) -> None:
        if self.status is not CollectiveBookingStatus.CANCELLED:
            raise booking_exceptions.BookingIsNotCancelledCannotBeUncancelled()

        self.cancellationDate = None
        self.cancellationReason = None
        self.cancellationUserId = None

        if self.confirmationDate:
            if self.collectiveStock.is_two_days_past_end():
                self.status = CollectiveBookingStatus.USED
                self.dateUsed = datetime.datetime.utcnow()
            else:
                self.status = CollectiveBookingStatus.CONFIRMED
        else:
            self.status = CollectiveBookingStatus.PENDING

    def mark_as_confirmed(self) -> None:
        if self.has_confirmation_limit_date_passed():
            raise booking_exceptions.ConfirmationLimitDateHasPassed()

        self.status = CollectiveBookingStatus.CONFIRMED
        self.confirmationDate = datetime.datetime.utcnow()

    @hybrid_property
    def isConfirmed(self) -> bool:
        return self.cancellationLimitDate <= datetime.datetime.utcnow()

    @isConfirmed.expression  # type: ignore[no-redef]
    def isConfirmed(cls) -> sa_elements.BinaryExpression:
        return cls.cancellationLimitDate <= datetime.datetime.utcnow()

    @hybrid_property
    def is_used_or_reimbursed(self) -> bool:
        return self.status in [CollectiveBookingStatus.USED, CollectiveBookingStatus.REIMBURSED]

    @is_used_or_reimbursed.expression  # type: ignore[no-redef]
    def is_used_or_reimbursed(cls) -> sa_elements.BinaryExpression:
        return cls.status.in_([CollectiveBookingStatus.USED, CollectiveBookingStatus.REIMBURSED])

    @hybrid_property
    def isReimbursed(self) -> bool:
        return self.status == CollectiveBookingStatus.REIMBURSED

    @isReimbursed.expression  # type: ignore[no-redef]
    def isReimbursed(cls) -> sa_elements.BinaryExpression:
        return cls.status == CollectiveBookingStatus.REIMBURSED

    @hybrid_property
    def isCancelled(self) -> bool:
        return self.status == CollectiveBookingStatus.CANCELLED

    @isCancelled.expression  # type: ignore[no-redef]
    def isCancelled(cls) -> sa_elements.BinaryExpression:
        return cls.status == CollectiveBookingStatus.CANCELLED

    @property
    def is_expired(self) -> bool:
        return self.isCancelled and self.cancellationReason == CollectiveBookingCancellationReasons.EXPIRED

    @property
    def userName(self) -> str | None:
        return f"{self.educationalRedactor.firstName} {self.educationalRedactor.lastName}"

    def has_confirmation_limit_date_passed(self) -> bool:
        return self.confirmationLimitDate <= datetime.datetime.utcnow()

    def mark_as_refused(self) -> None:
        if self.status != CollectiveBookingStatus.PENDING and self.cancellationLimitDate <= datetime.datetime.utcnow():
            raise educational_exceptions.EducationalBookingNotRefusable()
        cancellation_reason = (
            CollectiveBookingCancellationReasons.REFUSED_BY_INSTITUTE
            if self.status == CollectiveBookingStatus.PENDING
            else CollectiveBookingCancellationReasons.REFUSED_BY_HEADMASTER
        )
        try:
            self.cancel_booking(cancellation_reason)
        except educational_exceptions.CollectiveBookingIsAlreadyUsed:
            raise educational_exceptions.EducationalBookingNotRefusable()

        self.status = CollectiveBookingStatus.CANCELLED

    @property
    def is_cancellable_from_offerer(self) -> bool:
        return self.status not in (
            CollectiveBookingStatus.USED,
            CollectiveBookingStatus.REIMBURSED,
            CollectiveBookingStatus.CANCELLED,
        )

    @hybrid_property
    def validated_incident_id(self) -> int | None:
        for booking_incident in self.incidents:
            if booking_incident.incident.status == finance_models.IncidentStatus.VALIDATED:
                return booking_incident.incident.id
        return None

    @validated_incident_id.expression  # type: ignore[no-redef]
    def validated_incident_id(cls) -> int | None:
        return (
            sa.select(finance_models.FinanceIncident.id)
            .select_from(finance_models.FinanceIncident)
            .join(finance_models.BookingFinanceIncident)
            .where(
                sa.and_(
                    finance_models.BookingFinanceIncident.collectiveBookingId == CollectiveBooking.id,
                    finance_models.FinanceIncident.status == finance_models.IncidentStatus.VALIDATED,
                )
            )
            .limit(1)
            .correlate(CollectiveBooking)
            .scalar_subquery()
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
    def total_amount(self) -> decimal.Decimal:
        return self.collectiveStock.price


class EducationalDomainVenue(models.Base, models.Model):
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


class DomainToNationalProgram(PcObject, models.Base, models.Model):
    """Intermediate table that links `EducationalDomain`
    to `NationalProgram`. Links are unique: a domain can be linked to many
    programs but not twice the same.
    """

    __tablename__ = "domain_to_national_program"
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


class EducationalDomain(PcObject, models.Base, models.Model):
    __tablename__ = "educational_domain"

    name: str = sa.Column(sa.Text, nullable=False)
    venues: sa_orm.Mapped[list["Venue"]] = sa_orm.relationship(
        "Venue", back_populates="collectiveDomains", secondary=EducationalDomainVenue.__table__
    )
    collectiveOffers: sa_orm.Mapped[list["CollectiveOffer"]] = sa_orm.relationship(
        "CollectiveOffer", secondary=CollectiveOfferDomain.__table__, back_populates="domains"
    )

    collectiveOfferTemplates: sa_orm.Mapped[list["CollectiveOfferTemplate"]] = sa_orm.relationship(
        "CollectiveOfferTemplate", secondary=CollectiveOfferTemplateDomain.__table__, back_populates="domains"
    )
    nationalPrograms: sa_orm.Mapped[list["NationalProgram"]] = sa_orm.relationship(
        "NationalProgram",
        back_populates="domains",
        secondary=DomainToNationalProgram.__table__,
        order_by="NationalProgram.name",
    )


class CollectiveDmsApplication(PcObject, models.Base, models.Model):
    __tablename__ = "collective_dms_application"
    state: str = sa.Column(sa.String(30), nullable=False)
    procedure: int = sa.Column(sa.BigInteger, nullable=False)
    application: int = sa.Column(sa.BigInteger, nullable=False, index=True)
    siret: str = sa.Column(sa.String(14), nullable=False, index=True)
    lastChangeDate: datetime.datetime = sa.Column(sa.DateTime, nullable=False)
    depositDate = sa.Column(sa.DateTime, nullable=False)
    expirationDate = sa.Column(sa.DateTime, nullable=True)
    buildDate = sa.Column(sa.DateTime, nullable=True)
    instructionDate = sa.Column(sa.DateTime, nullable=True)
    processingDate = sa.Column(sa.DateTime, nullable=True)
    userDeletionDate = sa.Column(sa.DateTime, nullable=True)

    @hybrid_property
    def siren(self):
        return self.siret[:SIREN_LENGTH]

    @siren.expression  # type: ignore[no-redef]
    def siren(cls) -> str:
        return sa.func.substr(cls.siret, 1, SIREN_LENGTH)

    # Search application related to an offerer should use siren expression to use take benefit from the index
    # instead of "LIKE '123456782%'" which causes a sequential scan.
    sa.Index("ix_collective_dms_application_siren", sa.func.substr(siret, 1, SIREN_LENGTH))


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


class CollectiveOfferRequest(PcObject, models.Base, models.Model):
    __tablename__ = "collective_offer_request"
    _phoneNumber: str | None = sa.Column(sa.String(30), nullable=True, name="phoneNumber")

    requestedDate: datetime.date | None = sa.Column(sa.Date, nullable=True)

    totalStudents: int | None = sa.Column(sa.Integer, nullable=True)

    totalTeachers: int | None = sa.Column(sa.Integer, nullable=True)

    comment: str = sa.Column(sa.Text, nullable=False)

    dateCreated: datetime.date = sa.Column(sa.Date, nullable=False, server_default=sa.func.current_date())

    educationalRedactorId: int = sa.Column(sa.BigInteger, sa.ForeignKey("educational_redactor.id"), nullable=False)

    educationalRedactor: sa_orm.Mapped["EducationalRedactor"] = sa_orm.relationship(
        "EducationalRedactor", foreign_keys=educationalRedactorId
    )

    collectiveOfferTemplateId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("collective_offer_template.id"), index=True, nullable=False
    )

    collectiveOfferTemplate: sa_orm.Mapped["CollectiveOfferTemplate"] = sa_orm.relationship(
        "CollectiveOfferTemplate", foreign_keys=collectiveOfferTemplateId
    )

    educationalInstitutionId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("educational_institution.id"), index=True, nullable=False
    )

    educationalInstitution: sa_orm.Mapped["EducationalInstitution"] = sa_orm.relationship(
        "EducationalInstitution", foreign_keys=educationalInstitutionId
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
    def phoneNumber(cls) -> str | None:
        return cls._phoneNumber


class NationalProgram(PcObject, models.Base, models.Model):
    """
    Keep a track of existing national program that are used to highlight
    collective offers (templates) within a coherent frame.
    """

    __tablename__ = "national_program"
    name: str = sa.Column(sa.Text, unique=True)
    dateCreated: datetime.datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)
    domains: sa_orm.Mapped[list["EducationalDomain"]] = sa_orm.relationship(
        "EducationalDomain",
        back_populates="nationalPrograms",
        secondary=DomainToNationalProgram.__table__,
    )
    isActive: sa_orm.Mapped[bool] = sa.Column(
        sa.Boolean, nullable=False, server_default=sa.sql.expression.true(), default=True
    )


PROGRAM_MARSEILLE_EN_GRAND = "marseille_en_grand"


class EducationalInstitutionProgramAssociation(models.Base, models.Model):
    """Association model between EducationalInstitution and
    EducationalInstitutionProgram (many-to-many)
    """

    __tablename__ = "educational_institution_program_association"
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
    institution: sa_orm.Mapped["EducationalInstitution"] = sa_orm.relationship(
        "EducationalInstitution", foreign_keys=[institutionId]
    )
    programId: int = sa.Column(
        sa.BigInteger,
        sa.ForeignKey("educational_institution_program.id", ondelete="CASCADE"),
        index=True,
        primary_key=True,
    )
    program: sa_orm.Mapped["EducationalInstitutionProgram"] = sa_orm.relationship(
        "EducationalInstitutionProgram", foreign_keys=[programId]
    )
    timespan: sa_orm.Mapped[DateTimeRange] = sa.Column(
        # the date 2023-09-01 is the beginning of the MEG program. This will need to evolve if other programs are added
        "timespan",
        postgresql.TSRANGE(),
        server_default=sa.text("'[\"2023-09-01 00:00:00\",)'::tsrange"),
        nullable=False,
    )


class EducationalInstitutionProgram(PcObject, models.Base, models.Model):
    __tablename__ = "educational_institution_program"
    # technical name
    name: str = sa.Column(sa.Text, nullable=False, unique=True)
    # public (printable) name - if something different from name is needed
    label: str | None = sa.Column(sa.Text, nullable=True)
    description: str | None = sa.Column(sa.Text, nullable=True)


class CollectivePlaylist(PcObject, models.Base, models.Model):
    __tablename__ = "collective_playlist"
    type: str = sa.Column(db_utils.MagicEnum(PlaylistType), nullable=False)
    distanceInKm: float = sa.Column(sa.Float, nullable=True)

    institutionId = sa.Column(sa.BigInteger, sa.ForeignKey("educational_institution.id"), index=True, nullable=False)
    institution: sa_orm.Mapped["EducationalInstitution"] = sa_orm.relationship(
        "EducationalInstitution", foreign_keys=[institutionId], back_populates="collective_playlists"
    )

    venueId: int = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id"), index=True, nullable=True)
    venue: sa_orm.Mapped["Venue"] = sa_orm.relationship(
        "Venue", foreign_keys=[venueId], back_populates="collective_playlists"
    )

    collectiveOfferTemplateId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("collective_offer_template.id"), index=True, nullable=True
    )
    collective_offer_template: sa_orm.Mapped["CollectiveOfferTemplate"] = sa_orm.relationship(
        "CollectiveOfferTemplate", foreign_keys=[collectiveOfferTemplateId], back_populates="collective_playlists"
    )

    sa.Index("ix_collective_playlist_type_institutionId", type, institutionId)


class AdageVenueAddress(PcObject, models.Base, models.Model):
    __tablename__ = "adage_venue_address"
    adageId: str | None = sa.Column(sa.Text, nullable=True, unique=True)
    adageInscriptionDate: datetime.datetime | None = sa.Column(sa.DateTime, nullable=True)
    venueId: int | None = sa.Column(
        sa.BigInteger, sa.ForeignKey("venue.id", ondelete="CASCADE"), index=True, nullable=True
    )
    venue: sa_orm.Mapped["Venue"] = sa_orm.relationship(
        "Venue", foreign_keys=[venueId], back_populates="adage_addresses"
    )
