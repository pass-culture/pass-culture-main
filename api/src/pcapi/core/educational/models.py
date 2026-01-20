import datetime
import decimal
import enum
import logging
import random
import typing

import sqlalchemy as sa
import sqlalchemy.event as sa_event
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
from pcapi.core.educational import exceptions
from pcapi.core.finance import models as finance_models
from pcapi.core.geography import models as geography_models
from pcapi.models import offer_mixin
from pcapi.models.accessibility_mixin import AccessibilityMixin
from pcapi.models.pc_object import PcObject
from pcapi.utils import date as date_utils
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


class CollectiveOfferExportType(enum.Enum):
    CSV = "csv"
    EXCEL = "excel"


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
    CAN_SHARE = "CAN_SHARE"


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
        CollectiveOfferTemplateAllowedAction.CAN_SHARE,
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
    imageId = sa_orm.mapped_column(sa.Text, nullable=True)
    imageCrop: sa_orm.Mapped[dict | None] = sa_orm.mapped_column(
        sa_mutable.MutableDict.as_mutable(postgresql.json.JSONB), nullable=True
    )
    imageCredit = sa_orm.mapped_column(sa.Text, nullable=True)
    # Whether or not we also stored the original image in the storage bucket.
    imageHasOriginal = sa_orm.mapped_column(sa.Boolean, nullable=True)

    @hybrid_property
    def hasImage(self) -> bool:
        return self.imageId is not None

    @hasImage.inplace.expression
    @classmethod
    def _hasImageExpression(cls) -> sa_elements.BinaryExpression[bool]:
        return cls.imageId.is_not(sa.null())

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


class ValidationRuleCollectiveOfferLink(PcObject, models.Model):
    __tablename__ = "validation_rule_collective_offer_link"
    ruleId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offer_validation_rule.id", ondelete="CASCADE"), nullable=False
    )
    collectiveOfferId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("collective_offer.id", ondelete="CASCADE"), nullable=False, index=True
    )


class ValidationRuleCollectiveOfferTemplateLink(PcObject, models.Model):
    __tablename__ = "validation_rule_collective_offer_template_link"
    ruleId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offer_validation_rule.id", ondelete="CASCADE"), nullable=False
    )
    collectiveOfferTemplateId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("collective_offer_template.id", ondelete="CASCADE"), nullable=False, index=True
    )


class CollectiveOfferTemplateDomain(models.Model):
    """An association table between CollectiveOfferTemplate and
    EducationalDomain for their many-to-many relationship.
    """

    __tablename__ = "collective_offer_template_domain"

    collectiveOfferTemplateId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("collective_offer_template.id", ondelete="CASCADE"), index=True, primary_key=True
    )
    educationalDomainId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("educational_domain.id", ondelete="CASCADE"), index=True, primary_key=True
    )


class CollectiveOfferDomain(models.Model):
    """An association table between CollectiveOffer and
    EducationalDomain for their many-to-many relationship.
    """

    __tablename__ = "collective_offer_domain"

    collectiveOfferId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("collective_offer.id", ondelete="CASCADE"), index=True, primary_key=True
    )
    educationalDomainId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("educational_domain.id", ondelete="CASCADE"), index=True, primary_key=True
    )


class CollectiveOffer(
    PcObject,
    models.Model,
    offer_mixin.ValidationMixin,
    AccessibilityMixin,
    HasImageMixin,
):
    __tablename__ = "collective_offer"

    isActive: sa_orm.Mapped[bool] = sa_orm.mapped_column(
        sa.Boolean, nullable=False, server_default=sa.sql.expression.true(), default=True
    )

    authorId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(sa.BigInteger, sa.ForeignKey("user.id"), nullable=True)
    author: sa_orm.Mapped["User | None"] = sa_orm.relationship(
        "User", foreign_keys=[authorId], back_populates="collectiveOffers", uselist=False
    )

    # the venueId is the billing address.
    # To find where the offer takes place, check locationType / offererAddress
    venueId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("venue.id"), nullable=False, index=True
    )
    venue: sa_orm.Mapped["Venue"] = sa_orm.relationship(
        "Venue", foreign_keys=[venueId], back_populates="collectiveOffers"
    )

    name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(140), nullable=False)

    bookingEmails: sa_orm.Mapped[list[str]] = sa_orm.mapped_column(
        sa_mutable.MutableList.as_mutable(postgresql.ARRAY(sa.String)),
        nullable=False,
        server_default="{}",
    )
    description: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False, server_default="", default="")

    durationMinutes: sa_orm.Mapped[int | None] = sa_orm.mapped_column(sa.Integer, nullable=True)

    dateCreated: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, default=date_utils.get_naive_utc_now
    )
    dateArchived: sa_orm.Mapped[datetime.datetime | None] = sa_orm.mapped_column(sa.DateTime, nullable=True)

    dateUpdated: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=True, default=date_utils.get_naive_utc_now, onupdate=date_utils.get_naive_utc_now
    )

    students: sa_orm.Mapped[list[StudentLevels]] = sa_orm.mapped_column(
        sa_mutable.MutableList.as_mutable(postgresql.ARRAY(sa.Enum(StudentLevels))),
        nullable=False,
        server_default="{}",
    )

    collectiveStock: sa_orm.Mapped["CollectiveStock"] = sa_orm.relationship(
        "CollectiveStock",
        foreign_keys="CollectiveStock.collectiveOfferId",
        back_populates="collectiveOffer",
        uselist=False,
    )

    contactEmail: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.String(120), nullable=True)

    contactPhone: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)

    interventionArea: sa_orm.Mapped[list[str]] = sa_orm.mapped_column(
        sa_mutable.MutableList.as_mutable(postgresql.ARRAY(sa.Text())), nullable=False, server_default="{}"
    )

    domains: sa_orm.Mapped[list["EducationalDomain"]] = sa_orm.relationship(
        "EducationalDomain", secondary=CollectiveOfferDomain.__table__, back_populates="collectiveOffers"
    )

    institutionId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("educational_institution.id"), index=True, nullable=True
    )
    institution: sa_orm.Mapped["EducationalInstitution | None"] = sa_orm.relationship(
        "EducationalInstitution", foreign_keys=[institutionId], back_populates="collectiveOffers"
    )

    templateId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("collective_offer_template.id"), index=True, nullable=True
    )
    template: sa_orm.Mapped["CollectiveOfferTemplate | None"] = sa_orm.relationship(
        "CollectiveOfferTemplate", foreign_keys=[templateId], back_populates="collectiveOffers"
    )

    teacherId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger,
        sa.ForeignKey("educational_redactor.id"),
        nullable=True,
        index=True,
    )
    teacher: sa_orm.Mapped["EducationalRedactor | None"] = sa_orm.relationship(
        "EducationalRedactor",
        foreign_keys=[teacherId],
        back_populates="collectiveOffers",
        uselist=False,
    )

    providerId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger,
        sa.ForeignKey("provider.id"),
        nullable=True,
        index=True,
    )
    provider: sa_orm.Mapped["Provider | None"] = sa_orm.relationship(
        "Provider", foreign_keys=[providerId], back_populates="collectiveOffers"
    )

    flaggingValidationRules: sa_orm.Mapped[list["OfferValidationRule"]] = sa_orm.relationship(
        "OfferValidationRule", secondary=ValidationRuleCollectiveOfferLink.__table__, back_populates="collectiveOffers"
    )

    formats: sa_orm.Mapped[list[EacFormat]] = sa_orm.mapped_column(
        postgresql.ARRAY(sa.Enum(EacFormat, create_constraint=False, native_enum=False)), nullable=False
    )

    rejectionReason: sa_orm.Mapped[CollectiveOfferRejectionReason | None] = sa_orm.mapped_column(
        db_utils.MagicEnum(CollectiveOfferRejectionReason), default=None, nullable=True
    )

    isNonFreeOffer: sa_orm.Mapped["bool | None"] = sa_orm.query_expression()

    offererAddressId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offerer_address.id"), nullable=True, index=True
    )
    offererAddress: sa_orm.Mapped["OffererAddress | None"] = sa_orm.relationship(
        "OffererAddress", foreign_keys=[offererAddressId], uselist=False
    )

    # locationType = SCHOOL -> the offer is located at school - offererAddressId and locationComment are None
    # locationType = ADDRESS -> the offer is located at a specific address - offererAddressId is filled and locationComment is None
    # locationType = TO_BE_DEFINED -> the offer location is not precisely defined - offererAddressId is None and locationComment may be filled
    locationType: sa_orm.Mapped[CollectiveLocationType] = sa_orm.mapped_column(
        db_utils.MagicEnum(CollectiveLocationType), nullable=False
    )

    locationComment: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text(), nullable=True)

    # does the collective offer belongs to a national program
    nationalProgramId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger,
        sa.ForeignKey("national_program.id"),
        nullable=True,
        index=True,
    )
    nationalProgram: sa_orm.Mapped["NationalProgram | None"] = sa_orm.relationship(
        "NationalProgram", foreign_keys=[nationalProgramId], back_populates="collectiveOffers"
    )

    @sa_orm.declared_attr.directive
    def __table_args__(cls) -> tuple:
        parent_args: list = []
        # Retrieves indexes from parent mixins defined in __table_args__
        for base_class in cls.__mro__:
            try:
                parent_args += super(base_class, cls).__table_args__
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
            sa.CheckConstraint(
                '("locationType" = \'ADDRESS\' AND "offererAddressId" IS NOT NULL) OR ("locationType" != \'ADDRESS\' AND "offererAddressId" IS NULL)',
                name="collective_offer_location_type_and_address_constraint",
            ),
            sa.CheckConstraint(
                '"locationType" = \'TO_BE_DEFINED\' OR "locationComment" IS NULL',
                name="collective_offer_location_type_and_comment_constraint",
            ),
            sa.Index("ix_collective_offer_locationType_offererAddressId", "locationType", "offererAddressId"),
        ]

        return tuple(parent_args)

    @property
    def isPublicApi(self) -> bool:
        return self.providerId is not None

    @hybrid_property
    def isArchived(self) -> bool:
        return self.dateArchived is not None

    @isArchived.inplace.expression
    @classmethod
    def _isArchivedExpression(cls) -> sa.BinaryExpression[bool]:
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

    @hasStartDatetimePassed.inplace.expression
    def _hasStartDatetimePassedExpression(cls) -> sa_selectable.Exists:
        aliased_collective_stock = sa_orm.aliased(CollectiveStock)
        return (
            sa.exists()
            .where(aliased_collective_stock.collectiveOfferId == cls.id)
            .where(aliased_collective_stock.hasStartDatetimePassed.is_(True))
        )

    @property
    def hasBookingLimitDatetimesPassed(self) -> bool:
        if not self.collectiveStock:
            return False
        return self.collectiveStock.hasBookingLimitDatetimePassed

    @property
    def hasEndDatetimePassed(self) -> bool:
        if not self.collectiveStock:
            return False
        return self.collectiveStock.hasEndDatetimePassed

    def get_days_until_booking_limit(self) -> int | None:
        if not self.collectiveStock:
            return None

        delta = self.collectiveStock.bookingLimitDatetime - date_utils.get_naive_utc_now()
        return delta.days

    def get_sort_criterion(self) -> tuple[bool, int, datetime.datetime]:
        """
        This is used to sort offers with the following criterium.

        1. Archived offers are not relevant
        2. Published or prebooked offers with a booking limit in a near future (ie < 7 days) are relevant
        3. DateCreated is to be used as a default rule. Older -> less relevant that younger
        """
        days_until_booking_limit = self.get_days_until_booking_limit()
        statuses_requiring_attention = {
            CollectiveOfferDisplayedStatus.PREBOOKED,
            CollectiveOfferDisplayedStatus.PUBLISHED,
        }

        if (
            days_until_booking_limit is not None
            and days_until_booking_limit < 7
            and self.displayedStatus in statuses_requiring_attention
        ):
            date_limit_score = days_until_booking_limit
        else:
            date_limit_score = BIG_NUMBER_FOR_SORTING_OFFERS

        return not self.isArchived, -date_limit_score, self.dateCreated

    @property
    def displayedStatus(self) -> CollectiveOfferDisplayedStatus:
        status, is_hidden, is_archived = self.get_base_displayed_status()

        if is_archived:
            return CollectiveOfferDisplayedStatus.ARCHIVED

        if is_hidden:
            return CollectiveOfferDisplayedStatus.HIDDEN

        return status

    def get_base_displayed_status(self) -> tuple[CollectiveOfferDisplayedStatus, bool, bool]:
        """
        Return tuple is (status, is_hidden, is_archived)
        status does not take into account the hiding and archiving of the offer
        """
        is_hidden = False
        is_archived = False

        if self.isArchived:
            is_archived = True

        status: CollectiveOfferDisplayedStatus | None = None
        match self.validation:
            case offer_mixin.OfferValidationStatus.DRAFT:
                status = CollectiveOfferDisplayedStatus.DRAFT
            case offer_mixin.OfferValidationStatus.PENDING:
                status = CollectiveOfferDisplayedStatus.UNDER_REVIEW
            case offer_mixin.OfferValidationStatus.REJECTED:
                status = CollectiveOfferDisplayedStatus.REJECTED
            case offer_mixin.OfferValidationStatus.APPROVED:
                if not self.isActive:
                    is_hidden = True

                last_booking = self.lastBooking
                last_booking_status = last_booking.status if last_booking else None
                has_booking_limit_passed = self.hasBookingLimitDatetimesPassed
                has_started = self.hasStartDatetimePassed
                has_ended = self.hasEndDatetimePassed

                match last_booking_status:
                    case None:
                        if has_started:
                            status = CollectiveOfferDisplayedStatus.CANCELLED
                        elif has_booking_limit_passed:
                            status = CollectiveOfferDisplayedStatus.EXPIRED
                        else:
                            status = CollectiveOfferDisplayedStatus.PUBLISHED

                    case CollectiveBookingStatus.PENDING:
                        if has_booking_limit_passed:
                            status = CollectiveOfferDisplayedStatus.EXPIRED
                        else:
                            status = CollectiveOfferDisplayedStatus.PREBOOKED

                    case CollectiveBookingStatus.CONFIRMED:
                        if has_ended:
                            status = CollectiveOfferDisplayedStatus.ENDED
                        else:
                            status = CollectiveOfferDisplayedStatus.BOOKED

                    case CollectiveBookingStatus.USED:
                        status = CollectiveOfferDisplayedStatus.ENDED

                    case CollectiveBookingStatus.REIMBURSED:
                        status = CollectiveOfferDisplayedStatus.REIMBURSED

                    case CollectiveBookingStatus.CANCELLED:
                        if (
                            self.lastBookingCancellationReason == CollectiveBookingCancellationReasons.EXPIRED
                            and not has_started
                        ):
                            # There is a script that set the booking status to CANCELLED with cancellation reason EXPIRED when the booking is expired.
                            # We need to distinguish between an expired booking and a cancelled booking.
                            status = CollectiveOfferDisplayedStatus.EXPIRED
                        else:
                            status = CollectiveOfferDisplayedStatus.CANCELLED

        if status is None:
            logger.error("Incorrect status: %s %s", self.validation, last_booking_status)
            status = CollectiveOfferDisplayedStatus.PUBLISHED

        return status, is_hidden, is_archived

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
    def lastBooking(self) -> "CollectiveBooking | None":
        stock = self.collectiveStock
        if stock is None:
            return None

        return stock.lastBooking

    @property
    def lastBookingCancellationReason(self) -> CollectiveBookingCancellationReasons | None:
        booking = self.lastBooking
        return booking.cancellationReason if booking else None

    def is_two_days_past_end(self) -> bool:
        if self.collectiveStock is None:
            return False

        return self.collectiveStock.is_two_days_past_end()

    @property
    def address(self) -> geography_models.Address | None:
        return self.offererAddress.address if self.offererAddress else None


class CollectiveOfferTemplateEducationalRedactor(PcObject, models.Model):
    """Allow adding to favorite the offer template for adage user"""

    __tablename__ = "collective_offer_template_educational_redactor"

    educationalRedactorId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("educational_redactor.id"), nullable=False
    )
    collectiveOfferTemplateId: sa_orm.Mapped[int] = sa_orm.mapped_column(
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
    HasImageMixin,
    models.Model,
):
    __tablename__ = "collective_offer_template"

    isActive: sa_orm.Mapped[bool] = sa_orm.mapped_column(
        sa.Boolean, nullable=False, server_default=sa.sql.expression.true(), default=True
    )

    authorId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(sa.BigInteger, sa.ForeignKey("user.id"), nullable=True)
    author: sa_orm.Mapped["User | None"] = sa_orm.relationship("User", foreign_keys=[authorId], uselist=False)

    venueId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("venue.id"), nullable=False, index=True
    )
    venue: sa_orm.Mapped["Venue"] = sa_orm.relationship(
        "Venue", foreign_keys=[venueId], back_populates="collectiveOfferTemplates"
    )

    name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(140), nullable=False)

    description: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False, server_default="", default="")

    durationMinutes: sa_orm.Mapped[int | None] = sa_orm.mapped_column(sa.Integer, nullable=True)

    dateCreated: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, default=date_utils.get_naive_utc_now
    )

    dateUpdated: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, default=date_utils.get_naive_utc_now, onupdate=date_utils.get_naive_utc_now
    )

    students: sa_orm.Mapped[list[StudentLevels]] = sa_orm.mapped_column(
        sa_mutable.MutableList.as_mutable(postgresql.ARRAY(sa.Enum(StudentLevels))),
        nullable=False,
        server_default="{}",
    )

    priceDetail: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)

    bookingEmails: sa_orm.Mapped[list[str]] = sa_orm.mapped_column(
        sa_mutable.MutableList.as_mutable(postgresql.ARRAY(sa.String)),
        nullable=False,
        server_default="{}",
    )

    interventionArea: sa_orm.Mapped[list[str]] = sa_orm.mapped_column(
        sa_mutable.MutableList.as_mutable(postgresql.ARRAY(sa.Text())), nullable=False, server_default="{}"
    )

    domains: sa_orm.Mapped[list["EducationalDomain"]] = sa_orm.relationship(
        "EducationalDomain",
        secondary=CollectiveOfferTemplateDomain.__table__,
        back_populates="collectiveOfferTemplates",
    )

    collectiveOffers: sa_orm.Mapped[list["CollectiveOffer"]] = sa_orm.relationship(
        "CollectiveOffer", foreign_keys="CollectiveOffer.templateId", back_populates="template"
    )

    flaggingValidationRules: sa_orm.Mapped[list["OfferValidationRule"]] = sa_orm.relationship(
        "OfferValidationRule",
        secondary=ValidationRuleCollectiveOfferTemplateLink.__table__,
        back_populates="collectiveOfferTemplates",
    )

    # does the collective offer belongs to a national program
    nationalProgramId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger,
        sa.ForeignKey("national_program.id"),
        nullable=True,
        index=True,
    )
    nationalProgram: sa_orm.Mapped["NationalProgram | None"] = sa_orm.relationship(
        "NationalProgram", foreign_keys=[nationalProgramId]
    )

    educationalRedactorsFavorite: sa_orm.Mapped[list["EducationalRedactor"]] = sa_orm.relationship(
        "EducationalRedactor",
        secondary=CollectiveOfferTemplateEducationalRedactor.__table__,
        back_populates="favoriteCollectiveOfferTemplates",
    )

    dateRange: sa_orm.Mapped[DateTimeRange | None] = sa_orm.mapped_column(postgresql.TSRANGE, nullable=True)

    formats: sa_orm.Mapped[list[EacFormat]] = sa_orm.mapped_column(
        postgresql.ARRAY(sa.Enum(EacFormat, create_constraint=False, native_enum=False)), nullable=False
    )

    collective_playlists: sa_orm.Mapped[list["CollectivePlaylist"]] = sa_orm.relationship(
        "CollectivePlaylist",
        foreign_keys="CollectivePlaylist.collectiveOfferTemplateId",
        back_populates="collective_offer_template",
    )

    contactEmail: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.String(120), nullable=True)
    contactPhone: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)
    contactUrl: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)
    contactForm: sa_orm.Mapped[OfferContactFormEnum | None] = sa_orm.mapped_column(
        db_utils.MagicEnum(OfferContactFormEnum),
        nullable=True,
        server_default=None,
        default=None,
    )

    rejectionReason: sa_orm.Mapped[CollectiveOfferRejectionReason | None] = sa_orm.mapped_column(
        db_utils.MagicEnum(CollectiveOfferRejectionReason), default=None
    )

    offererAddressId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offerer_address.id"), nullable=True, index=True
    )
    offererAddress: sa_orm.Mapped["OffererAddress | None"] = sa_orm.relationship(
        "OffererAddress", foreign_keys=[offererAddressId], uselist=False
    )

    locationType: sa_orm.Mapped[CollectiveLocationType] = sa_orm.mapped_column(
        db_utils.MagicEnum(CollectiveLocationType), nullable=False
    )

    locationComment: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text(), nullable=True)

    dateArchived: sa_orm.Mapped[datetime.datetime | None] = sa_orm.mapped_column(sa.DateTime, nullable=True)

    @sa_orm.declared_attr.directive
    def __table_args__(cls) -> tuple:
        parent_args: list = []
        # Retrieves indexes from parent mixins defined in __table_args__
        for base_class in cls.__mro__:
            try:
                parent_args += super(base_class, cls).__table_args__
            except (AttributeError, TypeError):
                pass
        parent_args += [
            sa.Index("ix_collective_offer_template_locationType_offererAddressId", "locationType", "offererAddressId"),
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
            sa.CheckConstraint(
                '("locationType" = \'ADDRESS\' AND "offererAddressId" IS NOT NULL) OR ("locationType" != \'ADDRESS\' AND "offererAddressId" IS NULL)',
                name="collective_offer_template_location_type_and_address_constraint",
            ),
            sa.CheckConstraint(
                '"locationType" = \'TO_BE_DEFINED\' OR "locationComment" IS NULL',
                name="collective_offer_template_location_type_and_comment_constraint",
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

    @displayedStatus.inplace.expression
    @classmethod
    def _displayedStatusExpression(cls) -> sa_elements.Case:
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

    @hybrid_property
    def hasEndDatePassed(self) -> bool:
        if not self.end:
            return False
        return self.end < date_utils.get_naive_utc_now()

    @hasEndDatePassed.inplace.expression
    @classmethod
    def _hasEndDatePassedExpression(cls) -> sa.ColumnElement[bool]:
        return sa.and_(
            cls.dateRange.is_not(None),
            sa.func.upper(cls.dateRange) < sa.func.now(),
        )

    @hybrid_property
    def isArchived(self) -> bool:
        return self.dateArchived is not None

    @isArchived.inplace.expression
    @classmethod
    def _isArchivedExpression(cls) -> sa.BinaryExpression[bool]:
        return cls.dateArchived.is_not(sa.null())

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
    def visibleText(self) -> str:  # used in validation rule, do not remove
        return f"{self.name} {self.description} {self.priceDetail}"

    @property
    def address(self) -> geography_models.Address | None:
        return self.offererAddress.address if self.offererAddress else None


class CollectiveStock(PcObject, models.Model):
    __tablename__ = "collective_stock"

    dateCreated: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, default=date_utils.get_naive_utc_now, server_default=sa.func.now()
    )

    dateModified: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, default=date_utils.get_naive_utc_now, onupdate=date_utils.get_naive_utc_now
    )

    startDatetime: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(sa.DateTime, nullable=False)
    endDatetime: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(sa.DateTime, nullable=False)

    collectiveOfferId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("collective_offer.id"), index=True, nullable=False, unique=True
    )

    collectiveOffer: sa_orm.Mapped["CollectiveOffer"] = sa_orm.relationship(
        "CollectiveOffer", foreign_keys=[collectiveOfferId], uselist=False, back_populates="collectiveStock"
    )

    collectiveBookings: sa_orm.Mapped[list["CollectiveBooking"]] = sa_orm.relationship(
        "CollectiveBooking", foreign_keys="CollectiveBooking.collectiveStockId", back_populates="collectiveStock"
    )

    price: sa_orm.Mapped[decimal.Decimal] = sa_orm.mapped_column(
        sa.Numeric(10, 2),
        sa.CheckConstraint("price >= 0", name="check_price_is_not_negative"),
        index=True,
        nullable=False,
    )

    bookingLimitDatetime: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(sa.DateTime, nullable=False)

    numberOfTickets: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.Integer, nullable=False)

    priceDetail: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)

    __table_args__ = (sa.Index("ix_collective_stock_startDatetime_endDatetime", startDatetime, endDatetime),)

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

    @hybrid_property
    def hasBookingLimitDatetimePassed(self) -> bool:
        return self.bookingLimitDatetime <= date_utils.get_naive_utc_now()

    @hasBookingLimitDatetimePassed.inplace.expression
    @classmethod
    def _hasBookingLimitDatetimePassedExpression(cls) -> sa.ColumnElement[bool]:
        return cls.bookingLimitDatetime <= sa.func.now()

    @hybrid_property
    def hasStartDatetimePassed(self) -> bool:
        return self.startDatetime <= date_utils.get_naive_utc_now()

    @hasStartDatetimePassed.inplace.expression
    @classmethod
    def _hasStartDatetimePassedExpression(cls) -> sa.ColumnElement[bool]:
        return cls.startDatetime <= sa.func.now()

    @hybrid_property
    def hasEndDatetimePassed(self) -> bool:
        return self.endDatetime <= date_utils.get_naive_utc_now()

    @hasEndDatetimePassed.inplace.expression
    @classmethod
    def _hasEndDatetimePassedExpression(cls) -> sa.ColumnElement[bool]:
        return cls.endDatetime <= sa.func.now()

    @hybrid_property
    def isEventExpired(self) -> bool:
        return self.startDatetime <= date_utils.get_naive_utc_now()

    @isEventExpired.inplace.expression
    @classmethod
    def _isEventExpiredExpression(cls) -> sa.ColumnElement[bool]:
        return cls.startDatetime <= sa.func.now()

    @property
    def isExpired(self) -> bool:
        return self.isEventExpired or self.hasBookingLimitDatetimePassed

    def get_non_cancelled_bookings(self) -> list["CollectiveBooking"]:
        return [booking for booking in self.collectiveBookings if booking.status != CollectiveBookingStatus.CANCELLED]

    def get_unique_non_cancelled_booking(self) -> "CollectiveBooking | None":
        non_cancelled_bookings = self.get_non_cancelled_bookings()
        if len(non_cancelled_bookings) > 1:
            raise exceptions.MultipleCollectiveBookingFound()
        return non_cancelled_bookings[0] if non_cancelled_bookings else None

    def is_two_days_past_end(self) -> bool:
        return self.endDatetime + datetime.timedelta(days=2) < date_utils.get_naive_utc_now()

    @property
    def isSoldOut(self) -> bool:
        non_cancelled_bookings = self.get_non_cancelled_bookings()
        return len(non_cancelled_bookings) > 0


class EducationalInstitution(PcObject, models.Model):
    __tablename__ = "educational_institution"

    # this institutionId corresponds to the UAI ("Unité Administrative Immatriculée") code
    institutionId: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(30), nullable=False, unique=True, index=True)

    institutionType: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(80), nullable=False)

    name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text(), nullable=False)

    city: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text(), nullable=False)

    postalCode: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(10), nullable=False)

    email: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text(), nullable=True)

    phoneNumber: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(30), nullable=False)

    collectiveOffers: sa_orm.Mapped[list["CollectiveOffer"]] = sa_orm.relationship(
        "CollectiveOffer", foreign_keys="CollectiveOffer.institutionId", back_populates="institution"
    )

    collectiveBookings: sa_orm.Mapped[list["CollectiveBooking"]] = sa_orm.relationship(
        "CollectiveBooking",
        foreign_keys="CollectiveBooking.educationalInstitutionId",
        back_populates="educationalInstitution",
    )

    isActive: sa_orm.Mapped[bool] = sa_orm.mapped_column(
        sa.Boolean, nullable=False, server_default=sa.sql.expression.true(), default=True
    )

    programAssociations: sa_orm.Mapped[list["EducationalInstitutionProgramAssociation"]] = sa_orm.relationship(
        "EducationalInstitutionProgramAssociation",
        foreign_keys="EducationalInstitutionProgramAssociation.institutionId",
        back_populates="institution",
    )

    ruralLevel: sa_orm.Mapped[InstitutionRuralLevel | None] = sa_orm.mapped_column(
        db_utils.MagicEnum(InstitutionRuralLevel), nullable=True, default=None
    )

    collective_playlists: sa_orm.Mapped[list["CollectivePlaylist"]] = sa_orm.relationship(
        "CollectivePlaylist", foreign_keys="CollectivePlaylist.institutionId", back_populates="institution"
    )

    deposits: sa_orm.Mapped[list["EducationalDeposit"]] = sa_orm.relationship(
        "EducationalDeposit",
        back_populates="educationalInstitution",
        foreign_keys="EducationalDeposit.educationalInstitutionId",
    )

    latitude: sa_orm.Mapped[decimal.Decimal | None] = sa_orm.mapped_column(sa.Numeric(8, 5), nullable=True)

    longitude: sa_orm.Mapped[decimal.Decimal | None] = sa_orm.mapped_column(sa.Numeric(8, 5), nullable=True)

    __table_args__ = (
        sa.Index(
            "ix_educational_institution_type_name_city",
            sa.text("""(((("institutionType"::text || ' '::text) || name) || ' '::text) || city)"""),
            postgresql_using="gin",
            postgresql_ops={
                "description": "gin_trgm_ops",
            },
        ),
        sa.Index(
            "ix_educational_institution_department_code",
            sa.func.postal_code_to_department_code(postalCode),
        ),
    )

    @property
    def full_name(self) -> str:
        return f"{self.institutionType} {self.name}".strip()

    def programs_at_date(self, date: datetime.datetime) -> list["EducationalInstitutionProgram"]:
        return [association.program for association in self.programAssociations if date in association.timespan]


class EducationalYear(PcObject, models.Model):
    __tablename__ = "educational_year"

    adageId: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(30), unique=True, nullable=False)

    # beginningDate and expirationDate are retrieved from Adage (/v1/annees-scolaires endpoint)
    # The values we get are in Paris timezone
    # As we store UTC, we have e.g beginningDate="2025-08-31 22:00:00" in DB (which corresponds to "2025-09-01 00:00:00" in Paris time)
    beginningDate: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(sa.DateTime, nullable=False)

    expirationDate: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(sa.DateTime, nullable=False)

    deposits: sa_orm.Mapped[list["EducationalDeposit"]] = sa_orm.relationship(
        "EducationalDeposit", back_populates="educationalYear", foreign_keys="EducationalDeposit.educationalYearId"
    )

    @hybrid_property
    def displayed_year(self) -> str:
        return f"{self.beginningDate.year}-{self.expirationDate.year}"

    @displayed_year.inplace.expression
    @classmethod
    def _displayed_year_expression(cls) -> sa.ColumnElement[str]:
        return (
            sa.func.extract("year", cls.beginningDate).cast(sa.String)
            + "-"
            + sa.func.extract("year", cls.expirationDate).cast(sa.String)
        )


class EducationalDeposit(PcObject, models.Model):
    __tablename__ = "educational_deposit"

    TEMPORARY_FUND_AVAILABLE_RATIO = 0.8

    educationalInstitutionId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("educational_institution.id"), index=True, nullable=False
    )
    educationalInstitution: sa_orm.Mapped[EducationalInstitution] = sa_orm.relationship(
        EducationalInstitution, foreign_keys=[educationalInstitutionId], back_populates="deposits"
    )

    educationalYearId: sa_orm.Mapped[str] = sa_orm.mapped_column(
        sa.String(30), sa.ForeignKey("educational_year.adageId"), index=True, nullable=False
    )
    educationalYear: sa_orm.Mapped["EducationalYear"] = sa_orm.relationship(
        EducationalYear, foreign_keys=[educationalYearId], back_populates="deposits"
    )

    amount: sa_orm.Mapped[decimal.Decimal] = sa_orm.mapped_column(sa.Numeric(10, 2), nullable=False)

    dateCreated: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, default=date_utils.get_naive_utc_now, server_default=sa.func.now()
    )

    isFinal: sa_orm.Mapped[bool] = sa_orm.mapped_column(sa.Boolean, nullable=False, default=True)

    ministry: sa_orm.Mapped[Ministry] = sa_orm.mapped_column(sa.Enum(Ministry), nullable=False)

    # when a collective booking is confirmed, we find the corresponding deposit depending on the institution, educational year and period
    # if the confirmation date is in the same educational year as the event, the period must contain the confirmation date
    # if the confirmation date is not in the same educational year as the event, the period must contain the start of the event educational year
    period: sa_orm.Mapped[DateTimeRange] = sa_orm.mapped_column(postgresql.TSRANGE, nullable=False)

    collectiveBookings: sa_orm.Mapped[list["CollectiveBooking"]] = sa_orm.relationship(
        "CollectiveBooking",
        foreign_keys="CollectiveBooking.educationalDepositId",
        back_populates="educationalDeposit",
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
                raise exceptions.InsufficientFund()
        else:
            ratio = decimal.Decimal(self.TEMPORARY_FUND_AVAILABLE_RATIO)
            temporary_fund = round(self.amount * ratio, 2)

            if temporary_fund < total_amount_after_booking:
                raise exceptions.InsufficientTemporaryFund()


class EducationalRedactor(PcObject, models.Model):
    __tablename__ = "educational_redactor"

    email: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(120), nullable=False, unique=True, index=True)

    firstName: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.String(128), nullable=True)

    lastName: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.String(128), nullable=True)

    civility: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.String(20), nullable=True)

    preferences: sa_orm.Mapped[dict] = sa_orm.mapped_column(
        postgresql.JSONB(), server_default="{}", default={}, nullable=False
    )

    collectiveBookings: sa_orm.Mapped[list["CollectiveBooking"]] = sa_orm.relationship(
        "CollectiveBooking",
        foreign_keys="CollectiveBooking.educationalRedactorId",
        back_populates="educationalRedactor",
    )

    collectiveOffers: sa_orm.Mapped[list["CollectiveOffer"]] = sa_orm.relationship(
        "CollectiveOffer", foreign_keys="CollectiveOffer.teacherId", back_populates="teacher"
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


class CollectiveBooking(PcObject, models.Model):
    __tablename__ = "collective_booking"

    dateCreated: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, default=date_utils.get_naive_utc_now
    )

    dateUsed: sa_orm.Mapped[datetime.datetime | None] = sa_orm.mapped_column(sa.DateTime, nullable=True, index=True)

    collectiveStockId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("collective_stock.id"), index=True, nullable=False
    )
    collectiveStock: sa_orm.Mapped["CollectiveStock"] = sa_orm.relationship(
        "CollectiveStock", foreign_keys=[collectiveStockId], back_populates="collectiveBookings"
    )

    venueId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("venue.id"), index=True, nullable=False
    )
    venue: sa_orm.Mapped["Venue"] = sa_orm.relationship(
        "Venue", foreign_keys=[venueId], back_populates="collectiveBookings"
    )

    offererId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offerer.id"), index=True, nullable=False
    )
    offerer: sa_orm.Mapped["Offerer"] = sa_orm.relationship(
        "Offerer", foreign_keys=[offererId], back_populates="collectiveBookings"
    )

    cancellationDate: sa_orm.Mapped[datetime.datetime | None] = sa_orm.mapped_column(sa.DateTime, nullable=True)

    cancellationUserId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("user.id"), nullable=True
    )
    cancellationUser: sa_orm.Mapped["User | None"] = sa_orm.relationship("User", foreign_keys=[cancellationUserId])

    cancellationLimitDate: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(sa.DateTime, nullable=False)

    cancellationReason: sa_orm.Mapped[CollectiveBookingCancellationReasons | None] = sa_orm.mapped_column(
        "cancellationReason",
        sa.Enum(
            CollectiveBookingCancellationReasons,
            values_callable=lambda x: [reason.value for reason in CollectiveBookingCancellationReasons],
        ),
        nullable=True,
    )

    status: sa_orm.Mapped[CollectiveBookingStatus] = sa_orm.mapped_column(
        sa.Enum(CollectiveBookingStatus), nullable=False, default=CollectiveBookingStatus.CONFIRMED
    )

    reimbursementDate: sa_orm.Mapped[datetime.datetime | None] = sa_orm.mapped_column(sa.DateTime, nullable=True)

    educationalInstitutionId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("educational_institution.id"), nullable=False
    )
    educationalInstitution: sa_orm.Mapped["EducationalInstitution"] = sa_orm.relationship(
        EducationalInstitution, foreign_keys=[educationalInstitutionId], back_populates="collectiveBookings"
    )

    educationalYearId: sa_orm.Mapped[str] = sa_orm.mapped_column(
        sa.String(30), sa.ForeignKey("educational_year.adageId"), nullable=False
    )
    educationalYear: sa_orm.Mapped["EducationalYear"] = sa_orm.relationship(
        EducationalYear, foreign_keys=[educationalYearId]
    )

    confirmationDate: sa_orm.Mapped[datetime.datetime | None] = sa_orm.mapped_column(sa.DateTime, nullable=True)
    confirmationLimitDate: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(sa.DateTime, nullable=False)

    educationalRedactorId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger,
        sa.ForeignKey("educational_redactor.id"),
        nullable=False,
        index=True,
    )
    educationalRedactor: sa_orm.Mapped["EducationalRedactor"] = sa_orm.relationship(
        EducationalRedactor,
        foreign_keys=[educationalRedactorId],
        back_populates="collectiveBookings",
        uselist=False,
    )

    educationalDepositId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("educational_deposit.id"), nullable=True, index=True
    )
    educationalDeposit: sa_orm.Mapped[EducationalDeposit | None] = sa_orm.relationship(
        EducationalDeposit, foreign_keys=[educationalDepositId], back_populates="collectiveBookings", uselist=False
    )

    finance_events: sa_orm.Mapped[list["finance_models.FinanceEvent"]] = sa_orm.relationship(
        "FinanceEvent", foreign_keys="FinanceEvent.collectiveBookingId", back_populates="collectiveBooking"
    )
    pricings: sa_orm.Mapped[list["finance_models.Pricing"]] = sa_orm.relationship(
        "Pricing", foreign_keys="Pricing.collectiveBookingId", back_populates="collectiveBooking"
    )
    incidents: sa_orm.Mapped[list["finance_models.BookingFinanceIncident"]] = sa_orm.relationship(
        "BookingFinanceIncident",
        foreign_keys="BookingFinanceIncident.collectiveBookingId",
        back_populates="collectiveBooking",
    )
    payments: sa_orm.Mapped[list["finance_models.Payment"]] = sa_orm.relationship(
        "Payment", foreign_keys="Payment.collectiveBookingId", back_populates="collectiveBooking"
    )

    __table_args__ = (
        sa.Index("ix_collective_booking_date_created", dateCreated),
        sa.Index("ix_collective_booking_status", status),
        sa.Index("ix_collective_booking_educationalYear_and_institution", educationalYearId, educationalInstitutionId),
    )

    def cancel_booking(
        self,
        reason: CollectiveBookingCancellationReasons,
        cancel_even_if_used: bool = False,
        cancel_even_if_reimbursed: bool = False,
        author_id: int | None = None,
    ) -> None:
        if self.status is CollectiveBookingStatus.CANCELLED:
            raise exceptions.CollectiveBookingAlreadyCancelled()
        if self.status is CollectiveBookingStatus.REIMBURSED and not cancel_even_if_reimbursed:
            raise exceptions.CollectiveBookingIsAlreadyUsed
        if self.status is CollectiveBookingStatus.USED and not cancel_even_if_used:
            raise exceptions.CollectiveBookingIsAlreadyUsed
        self.status = CollectiveBookingStatus.CANCELLED
        self.cancellationDate = date_utils.get_naive_utc_now()
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
                self.dateUsed = date_utils.get_naive_utc_now()
            else:
                self.status = CollectiveBookingStatus.CONFIRMED
        else:
            self.status = CollectiveBookingStatus.PENDING

    def mark_as_confirmed(self, confirmation_datetime: datetime.datetime) -> None:
        if self.confirmationLimitDate < confirmation_datetime:
            raise booking_exceptions.ConfirmationLimitDateHasPassed()

        self.status = CollectiveBookingStatus.CONFIRMED
        self.confirmationDate = confirmation_datetime

    @hybrid_property
    def isConfirmed(self) -> bool:
        return self.cancellationLimitDate <= date_utils.get_naive_utc_now()

    @isConfirmed.inplace.expression
    @classmethod
    def _isConfirmedExpression(cls) -> sa.ColumnElement[bool]:
        return cls.cancellationLimitDate <= date_utils.get_naive_utc_now()

    @hybrid_property
    def is_used_or_reimbursed(self) -> bool:
        return self.status in [CollectiveBookingStatus.USED, CollectiveBookingStatus.REIMBURSED]

    @is_used_or_reimbursed.inplace.expression
    @classmethod
    def _is_used_or_reimbursed_expression(cls) -> sa.ColumnElement[bool]:
        return cls.status.in_([CollectiveBookingStatus.USED, CollectiveBookingStatus.REIMBURSED])

    @hybrid_property
    def isReimbursed(self) -> bool:
        return self.status == CollectiveBookingStatus.REIMBURSED

    @isReimbursed.inplace.expression
    @classmethod
    def _isReimbursedExpression(cls) -> sa.ColumnElement[bool]:
        return cls.status == CollectiveBookingStatus.REIMBURSED

    @hybrid_property
    def isCancelled(self) -> bool:
        return self.status == CollectiveBookingStatus.CANCELLED

    @isCancelled.inplace.expression
    @classmethod
    def _isCancelledExpression(cls) -> sa.ColumnElement[bool]:
        return cls.status == CollectiveBookingStatus.CANCELLED

    @property
    def is_expired(self) -> bool:
        return self.isCancelled and self.cancellationReason == CollectiveBookingCancellationReasons.EXPIRED

    @property
    def userName(self) -> str | None:
        return f"{self.educationalRedactor.firstName} {self.educationalRedactor.lastName}"

    def mark_as_refused(self) -> None:
        if (
            self.status != CollectiveBookingStatus.PENDING
            and self.cancellationLimitDate <= date_utils.get_naive_utc_now()
        ):
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

    @hybrid_property
    def validated_incident_id(self) -> int | None:
        for booking_incident in self.incidents:
            if booking_incident.incident.status in (
                finance_models.IncidentStatus.VALIDATED,
                finance_models.IncidentStatus.INVOICED,
            ):
                return booking_incident.incident.id
        return None

    @validated_incident_id.inplace.expression
    @classmethod
    def _validated_incident_id_expression(cls) -> sa.ScalarSelect[int]:
        return (
            sa.select(finance_models.FinanceIncident.id)
            .select_from(finance_models.FinanceIncident)
            .join(finance_models.BookingFinanceIncident)
            .where(
                sa.and_(
                    finance_models.BookingFinanceIncident.collectiveBookingId == CollectiveBooking.id,
                    finance_models.FinanceIncident.status.in_(
                        (finance_models.IncidentStatus.VALIDATED, finance_models.IncidentStatus.INVOICED)
                    ),
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


class EducationalDomainVenue(PcObject, models.Model):
    __tablename__ = "educational_domain_venue"

    educationalDomainId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("educational_domain.id", ondelete="CASCADE"), index=True, nullable=False
    )
    venueId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("venue.id", ondelete="CASCADE"), nullable=False
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "educationalDomainId",
            "venueId",
            name="unique_educational_domain_venue",
        ),
    )


class DomainToNationalProgram(PcObject, models.Model):
    """Intermediate table that links `EducationalDomain`
    to `NationalProgram`. Links are unique: a domain can be linked to many
    programs but not twice the same.
    """

    __tablename__ = "domain_to_national_program"
    domainId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("educational_domain.id", ondelete="CASCADE"), index=True, nullable=False
    )
    nationalProgramId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("national_program.id", ondelete="CASCADE"), index=True, nullable=False
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "domainId",
            "nationalProgramId",
            name="unique_domain_to_national_program",
        ),
    )


class EducationalDomain(PcObject, models.Model):
    __tablename__ = "educational_domain"

    name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False)
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


class CollectiveDmsApplication(PcObject, models.Model):
    __tablename__ = "collective_dms_application"
    state: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(30), nullable=False)
    procedure: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.BigInteger, nullable=False)
    application: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.BigInteger, nullable=False, index=True)
    siret: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(14), nullable=False, index=True)
    lastChangeDate: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(sa.DateTime, nullable=False)
    depositDate: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(sa.DateTime, nullable=False)
    expirationDate: sa_orm.Mapped[datetime.datetime | None] = sa_orm.mapped_column(sa.DateTime, nullable=True)
    buildDate: sa_orm.Mapped[datetime.datetime | None] = sa_orm.mapped_column(sa.DateTime, nullable=True)
    instructionDate: sa_orm.Mapped[datetime.datetime | None] = sa_orm.mapped_column(sa.DateTime, nullable=True)
    processingDate: sa_orm.Mapped[datetime.datetime | None] = sa_orm.mapped_column(sa.DateTime, nullable=True)
    userDeletionDate: sa_orm.Mapped[datetime.datetime | None] = sa_orm.mapped_column(sa.DateTime, nullable=True)

    venue: sa_orm.Mapped["Venue"] = sa_orm.relationship(
        "Venue",
        back_populates="collectiveDmsApplications",
        primaryjoin="foreign(CollectiveDmsApplication.siret) == Venue.siret",
        uselist=False,
    )

    __table_args__ = (
        # Search application related to an offerer should use siren expression to use take benefit from the index
        # instead of "LIKE '123456782%'" which causes a sequential scan.
        sa.Index("ix_collective_dms_application_siren", sa.func.substr(siret, 1, SIREN_LENGTH)),
    )

    @hybrid_property
    def siren(self) -> str:
        return self.siret[:SIREN_LENGTH]

    @siren.inplace.expression
    @classmethod
    def _siren_expression(cls) -> sa.Function:
        return sa.func.substr(cls.siret, 1, SIREN_LENGTH)


trig_update_cancellationDate_on_isCancelled_ddl = sa.DDL(f"""
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
    """)

sa_event.listen(CollectiveBooking.__table__, "after_create", trig_update_cancellationDate_on_isCancelled_ddl)


class CollectiveOfferRequest(PcObject, models.Model):
    __tablename__ = "collective_offer_request"
    _phoneNumber: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.String(30), nullable=True, name="phoneNumber")

    requestedDate: sa_orm.Mapped[datetime.date | None] = sa_orm.mapped_column(sa.Date, nullable=True)

    totalStudents: sa_orm.Mapped[int | None] = sa_orm.mapped_column(sa.Integer, nullable=True)

    totalTeachers: sa_orm.Mapped[int | None] = sa_orm.mapped_column(sa.Integer, nullable=True)

    comment: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False)

    dateCreated: sa_orm.Mapped[datetime.date] = sa_orm.mapped_column(
        sa.Date, nullable=False, server_default=sa.func.current_date()
    )

    educationalRedactorId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("educational_redactor.id"), nullable=False
    )
    educationalRedactor: sa_orm.Mapped["EducationalRedactor"] = sa_orm.relationship(
        "EducationalRedactor", foreign_keys=[educationalRedactorId]
    )

    collectiveOfferTemplateId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("collective_offer_template.id"), index=True, nullable=False
    )
    collectiveOfferTemplate: sa_orm.Mapped["CollectiveOfferTemplate"] = sa_orm.relationship(
        "CollectiveOfferTemplate", foreign_keys=[collectiveOfferTemplateId]
    )

    educationalInstitutionId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("educational_institution.id"), index=True, nullable=False
    )
    educationalInstitution: sa_orm.Mapped["EducationalInstitution"] = sa_orm.relationship(
        "EducationalInstitution", foreign_keys=[educationalInstitutionId]
    )

    @hybrid_property
    def phoneNumber(self) -> str | None:
        return self._phoneNumber

    @phoneNumber.inplace.setter
    def phoneNumberSetter(self, value: str | None) -> None:
        if not value:
            self._phoneNumber = None
        else:
            self._phoneNumber = ParsedPhoneNumber(value).phone_number

    @phoneNumber.inplace.expression
    @classmethod
    def _phoneNumberExpression(cls) -> sa_orm.InstrumentedAttribute[str | None]:
        return cls._phoneNumber


class NationalProgram(PcObject, models.Model):
    """
    Keep a track of existing national program that are used to highlight
    collective offers (templates) within a coherent frame.
    """

    __tablename__ = "national_program"

    name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, unique=True, nullable=False)
    dateCreated: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, default=date_utils.get_naive_utc_now
    )
    domains: sa_orm.Mapped[list["EducationalDomain"]] = sa_orm.relationship(
        "EducationalDomain",
        back_populates="nationalPrograms",
        secondary=DomainToNationalProgram.__table__,
    )
    isActive: sa_orm.Mapped[bool] = sa_orm.mapped_column(
        sa.Boolean, nullable=False, server_default=sa.sql.expression.true(), default=True
    )
    collectiveOffers: sa_orm.Mapped[list["CollectiveOffer"]] = sa_orm.relationship(
        "CollectiveOffer", foreign_keys="CollectiveOffer.nationalProgramId", back_populates="nationalProgram"
    )


PROGRAM_MARSEILLE_EN_GRAND = "marseille_en_grand"


class EducationalInstitutionProgramAssociation(models.Model):
    """Association model between EducationalInstitution and
    EducationalInstitutionProgram (many-to-many)
    """

    __tablename__ = "educational_institution_program_association"
    institutionId: sa_orm.Mapped[int] = sa_orm.mapped_column(
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

    programId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger,
        sa.ForeignKey("educational_institution_program.id", ondelete="CASCADE"),
        index=True,
        primary_key=True,
    )
    program: sa_orm.Mapped["EducationalInstitutionProgram"] = sa_orm.relationship(
        "EducationalInstitutionProgram", foreign_keys=[programId]
    )

    timespan: sa_orm.Mapped[DateTimeRange] = sa_orm.mapped_column(
        # the date 2023-09-01 is the beginning of the MEG program. This will need to evolve if other programs are added
        "timespan",
        postgresql.TSRANGE(),
        server_default=sa.text("'[\"2023-09-01 00:00:00\",)'::tsrange"),
        nullable=False,
    )


class EducationalInstitutionProgram(PcObject, models.Model):
    __tablename__ = "educational_institution_program"
    # technical name
    name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False, unique=True)
    # public (printable) name - if something different from name is needed
    label: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)
    description: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)


class CollectivePlaylist(PcObject, models.Model):
    __tablename__ = "collective_playlist"
    type: sa_orm.Mapped[PlaylistType] = sa_orm.mapped_column(db_utils.MagicEnum(PlaylistType), nullable=False)
    distanceInKm: sa_orm.Mapped[float | None] = sa_orm.mapped_column(sa.Float, nullable=True)

    institutionId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("educational_institution.id"), index=True, nullable=False
    )
    institution: sa_orm.Mapped["EducationalInstitution"] = sa_orm.relationship(
        "EducationalInstitution", foreign_keys=[institutionId], back_populates="collective_playlists"
    )

    venueId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("venue.id"), index=True, nullable=True
    )
    venue: sa_orm.Mapped["Venue | None"] = sa_orm.relationship(
        "Venue", foreign_keys=[venueId], back_populates="collective_playlists"
    )

    collectiveOfferTemplateId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("collective_offer_template.id"), index=True, nullable=True
    )
    collective_offer_template: sa_orm.Mapped["CollectiveOfferTemplate | None"] = sa_orm.relationship(
        "CollectiveOfferTemplate", foreign_keys=[collectiveOfferTemplateId], back_populates="collective_playlists"
    )

    __table_args__ = (sa.Index("ix_collective_playlist_type_institutionId", type, institutionId),)
