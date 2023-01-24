from datetime import datetime
import enum
import logging
import typing

import psycopg2.extras
import sqlalchemy as sa
from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import CheckConstraint
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy import TEXT
from sqlalchemy import Text
from sqlalchemy import UniqueConstraint
from sqlalchemy import case
from sqlalchemy import cast
from sqlalchemy import func
import sqlalchemy.dialects.postgresql as sa_psql
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.event import listens_for
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.ext.mutable import MutableList
import sqlalchemy.orm as sa_orm
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import aliased
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression
from sqlalchemy.sql.elements import Case
import sqlalchemy.sql.functions as sqla_func
from sqlalchemy.sql.sqltypes import LargeBinary
from werkzeug.utils import cached_property

from pcapi.connectors import sirene
from pcapi.core.educational import models as educational_models
import pcapi.core.finance.models as finance_models
from pcapi.domain.ts_vector import create_ts_vector_and_table_args
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models import db
from pcapi.models.accessibility_mixin import AccessibilityMixin
from pcapi.models.deactivable_mixin import DeactivableMixin
from pcapi.models.has_address_mixin import HasAddressMixin
from pcapi.models.has_thumb_mixin import HasThumbMixin
from pcapi.models.pc_object import PcObject
from pcapi.models.providable_mixin import ProvidableMixin
from pcapi.models.validation_status_mixin import ValidationStatusMixin
from pcapi.utils import crypto
from pcapi.utils.date import CUSTOM_TIMEZONES
from pcapi.utils.date import METROPOLE_TIMEZONE
from pcapi.utils.date import get_department_timezone
from pcapi.utils.date import get_postal_code_timezone
import pcapi.utils.db as db_utils
from pcapi.utils.human_ids import humanize
import pcapi.utils.postal_code as postal_code_utils

from . import constants


if typing.TYPE_CHECKING:
    import pcapi.core.criteria.models as criteria_models
    import pcapi.core.providers.models as providers_models
    import pcapi.core.users.models as users_models


logger = logging.getLogger(__name__)

CONSTRAINT_CHECK_IS_VIRTUAL_XOR_HAS_ADDRESS = """
(
    "isVirtual" IS TRUE
    AND (address IS NULL AND "postalCode" IS NULL AND city IS NULL AND "departementCode" IS NULL)
)
OR
(
    "isVirtual" IS FALSE
    AND siret is NOT NULL
    AND ("postalCode" IS NOT NULL AND city IS NOT NULL AND "departementCode" IS NOT NULL)
)
OR
(
    "isVirtual" IS FALSE
    AND (siret is NULL and comment is NOT NULL)
    AND (address IS NOT NULL AND "postalCode" IS NOT NULL AND city IS NOT NULL AND "departementCode" IS NOT NULL)
)

"""

CONSTRAINT_CHECK_HAS_SIRET_XOR_HAS_COMMENT_XOR_IS_VIRTUAL = """
    (siret IS NULL AND comment IS NULL AND "isVirtual" IS TRUE)
    OR (siret IS NULL AND comment IS NOT NULL AND "isVirtual" IS FALSE)
    OR (siret IS NOT NULL AND "isVirtual" IS FALSE)
"""


class VenueTypeCode(enum.Enum):
    VISUAL_ARTS = "Arts visuels, arts plastiques et galeries"
    CULTURAL_CENTRE = "Centre culturel"
    TRAVELING_CINEMA = "Cinéma itinérant"
    MOVIE = "Cinéma - Salle de projections"
    ARTISTIC_COURSE = "Cours et pratique artistiques"
    SCIENTIFIC_CULTURE = "Culture scientifique"
    FESTIVAL = "Festival"
    GAMES = "Jeux / Jeux vidéos"
    BOOKSTORE = "Librairie"
    LIBRARY = "Bibliothèque ou médiathèque"
    MUSEUM = "Musée"
    RECORD_STORE = "Musique - Disquaire"
    MUSICAL_INSTRUMENT_STORE = "Musique - Magasin d’instruments"
    CONCERT_HALL = "Musique - Salle de concerts"
    DIGITAL = "Offre numérique"
    PATRIMONY_TOURISM = "Patrimoine et tourisme"
    PERFORMING_ARTS = "Spectacle vivant"
    CREATIVE_ARTS_STORE = "Magasin arts créatifs"
    ADMINISTRATIVE = "Lieu administratif"
    OTHER = "Autre"

    # These methods are used by Pydantic in order to return the enum name and validate the value
    # instead of returning the enum directly.
    @classmethod
    def __get_validators__(cls) -> typing.Iterator[typing.Callable]:
        yield cls.validate

    @classmethod
    def validate(cls, value: str | enum.Enum) -> str:
        if isinstance(value, enum.Enum):
            value = value.name

        if not hasattr(cls, value):
            raise ValueError(f"{value}: invalide")

        return value


VenueTypeCodeKey = enum.Enum(  # type: ignore [misc]
    "VenueTypeCodeKey",
    {code.name: code.name for code in VenueTypeCode},
)


class Venue(PcObject, Base, Model, HasThumbMixin, ProvidableMixin, AccessibilityMixin):
    __tablename__ = "venue"

    name: str = Column(String(140), nullable=False)
    sa.Index("idx_venue_trgm_name", name, postgresql_using="gin")

    siret = Column(String(14), nullable=True, unique=True)

    departementCode = Column(String(3), nullable=True)

    latitude = Column(Numeric(8, 5), nullable=True)

    longitude = Column(Numeric(8, 5), nullable=True)

    venueProviders: list["providers_models.VenueProvider"] = relationship("VenueProvider", back_populates="venue")

    managingOffererId: int = Column(BigInteger, ForeignKey("offerer.id"), nullable=False, index=True)

    managingOfferer: sa_orm.Mapped["Offerer"] = relationship(
        "Offerer", foreign_keys=[managingOffererId], backref="managedVenues"
    )

    bookingEmail = Column(String(120), nullable=True)

    address = Column(String(200), nullable=True)

    postalCode = Column(String(6), nullable=True)

    city = Column(String(50), nullable=True)

    publicName = Column(String(255), nullable=True)
    sa.Index("idx_venue_trgm_public_name", publicName, postgresql_using="gin")

    isVirtual: bool = Column(
        Boolean,
        CheckConstraint(CONSTRAINT_CHECK_IS_VIRTUAL_XOR_HAS_ADDRESS, name="check_is_virtual_xor_has_address"),
        nullable=False,
        default=False,
        server_default=expression.false(),
    )

    isPermanent = Column(
        Boolean,
        nullable=True,
        default=False,
    )

    comment = Column(
        TEXT,
        CheckConstraint(
            CONSTRAINT_CHECK_HAS_SIRET_XOR_HAS_COMMENT_XOR_IS_VIRTUAL, name="check_has_siret_xor_comment_xor_isVirtual"
        ),
        nullable=True,
    )

    collectiveOffers: list[educational_models.CollectiveOffer] = relationship("CollectiveOffer", back_populates="venue")

    collectiveOfferTemplates: list[educational_models.CollectiveOfferTemplate] = relationship(
        "CollectiveOfferTemplate", back_populates="venue"
    )

    venueTypeId = Column(Integer, ForeignKey("venue_type.id"), nullable=True)

    venueType: sa_orm.Mapped["VenueType"] = relationship("VenueType", foreign_keys=[venueTypeId])

    venueTypeCode = Column(sa.Enum(VenueTypeCode, create_constraint=False), nullable=True, default=VenueTypeCode.OTHER)

    venueLabelId = Column(Integer, ForeignKey("venue_label.id"), nullable=True)

    venueLabel: sa_orm.Mapped["VenueLabel"] = relationship("VenueLabel", foreign_keys=[venueLabelId])

    dateCreated: datetime = Column(DateTime, nullable=False, default=datetime.utcnow)

    withdrawalDetails = Column(Text, nullable=True)

    description = Column(Text, nullable=True)

    contact: sa_orm.Mapped["VenueContact | None"] = relationship("VenueContact", back_populates="venue", uselist=False)

    businessUnitId = Column(Integer, ForeignKey("business_unit.id"), nullable=True)
    businessUnit: sa_orm.Mapped["finance_models.BusinessUnit"] = relationship(
        "BusinessUnit", foreign_keys=[businessUnitId], backref="venues"
    )

    # bannerUrl should provide a safe way to retrieve the banner,
    # whereas bannerMeta should provide extra information that might be
    # helpful like image type, author, etc. that can change over time.
    bannerUrl = Column(Text, nullable=True)

    bannerMeta: dict | None = Column(MutableDict.as_mutable(JSONB), nullable=True)

    adageId = Column(Text, nullable=True)

    thumb_path_component = "venues"

    criteria: list["criteria_models.Criterion"] = sa.orm.relationship(
        "Criterion", backref=db.backref("venue_criteria", lazy="dynamic"), secondary="venue_criterion"
    )

    # TODO(fseguin,2022-06-20): Make column non-nullable when column is populated on all envs
    dmsToken = Column(Text, nullable=True, unique=True)

    venueEducationalStatusId = Column(BigInteger, ForeignKey("venue_educational_status.id"), nullable=True)
    venueEducationalStatus: Mapped["VenueEducationalStatus"] = relationship(
        "VenueEducationalStatus", back_populates="venues", foreign_keys=[venueEducationalStatusId]
    )
    reimbursement_point_links: Mapped[list["VenueReimbursementPointLink"]] = relationship(
        "VenueReimbursementPointLink",
        back_populates="venue",
        foreign_keys="VenueReimbursementPointLink.venueId",
        uselist=True,
    )

    pricing_point_links: Mapped[list["VenuePricingPointLink"]] = relationship(
        "VenuePricingPointLink",
        back_populates="venue",
        foreign_keys="VenuePricingPointLink.venueId",
        uselist=True,
    )

    collectiveDescription = Column(Text, nullable=True)
    collectiveStudents: list[educational_models.StudentLevels] | None = sa.Column(
        MutableList.as_mutable(sa.dialects.postgresql.ARRAY(sa.Enum(educational_models.StudentLevels))),
        nullable=True,
        server_default="{}",
    )
    collectiveWebsite = Column(Text, nullable=True)
    collectiveDomains: Mapped[list[educational_models.EducationalDomain]] = relationship(
        educational_models.EducationalDomain,
        back_populates="venues",
        secondary="educational_domain_venue",
        uselist=True,
    )
    collectiveInterventionArea: list[str] | None = sa.Column(
        MutableList.as_mutable(sa.dialects.postgresql.json.JSONB), nullable=True
    )
    collectiveNetwork: list[str] | None = sa.Column(
        MutableList.as_mutable(sa.dialects.postgresql.json.JSONB), nullable=True
    )
    collectiveAccessInformation = Column(Text, nullable=True)
    collectivePhone = Column(Text, nullable=True)
    collectiveEmail = Column(Text, nullable=True)
    bankInformation: finance_models.BankInformation | None = relationship(
        "BankInformation", back_populates="venue", uselist=False
    )

    @property
    def is_eligible_for_search(self) -> bool:
        not_administrative = self.venueTypeCode != VenueTypeCode.ADMINISTRATIVE
        return bool(self.isPermanent) and self.managingOfferer.isActive and not_administrative

    def store_departement_code(self) -> None:
        if not self.postalCode:
            return
        self.departementCode = postal_code_utils.PostalCode(self.postalCode).get_departement_code()

    @property
    def bic(self) -> str | None:
        return self.bankInformation.bic if self.bankInformation else None

    @property
    def iban(self) -> str | None:
        return self.bankInformation.iban if self.bankInformation else None

    @property
    def demarchesSimplifieesApplicationId(self) -> int | None:
        if not self.bankInformation:
            return None

        if self.bankInformation.status not in (
            finance_models.BankInformationStatus.DRAFT,
            finance_models.BankInformationStatus.ACCEPTED,
        ):
            return None

        return self.bankInformation.applicationId

    @property
    def hasPendingBankInformationApplication(self) -> bool:
        if not self.bankInformation:
            return False
        return self.bankInformation.status == finance_models.BankInformationStatus.DRAFT

    @property
    def demarchesSimplifieesIsAccepted(self) -> bool:
        if not self.bankInformation:
            return False
        return self.bankInformation.status == finance_models.BankInformationStatus.ACCEPTED

    @property
    def has_individual_offers(self) -> bool:
        from pcapi.core.offers.models import Offer

        return db.session.query(Offer.query.filter(Offer.venueId == self.id).exists()).scalar()

    @property
    def has_collective_offers(self) -> bool:
        from pcapi.core.educational.models import CollectiveOffer

        return db.session.query(CollectiveOffer.query.filter(CollectiveOffer.venueId == self.id).exists()).scalar()

    @property
    def has_approved_offers(self) -> bool:
        """Better performance than nApprovedOffers when we only want to check if there is at least one offer"""
        from pcapi.core.educational.models import CollectiveOffer
        from pcapi.core.offers.models import Offer
        from pcapi.core.offers.models import OfferValidationStatus

        query_offer = db.session.query(
            Offer.query.filter(Offer.validation == OfferValidationStatus.APPROVED, Offer.venueId == self.id).exists()
        )
        query_collective = db.session.query(
            CollectiveOffer.query.filter(
                CollectiveOffer.validation == OfferValidationStatus.APPROVED, CollectiveOffer.venueId == self.id
            ).exists()
        )
        results = query_offer.union(query_collective).all()

        return any(result for result, in results)

    @property
    def nApprovedOffers(self) -> int:  # used in validation rule, do not remove
        from pcapi.core.educational.models import CollectiveOffer
        from pcapi.core.offers.models import Offer
        from pcapi.core.offers.models import OfferValidationStatus

        query_offer = db.session.query(func.count(Offer.id)).filter(
            Offer.validation == OfferValidationStatus.APPROVED, Offer.venueId == self.id
        )
        query_collective = db.session.query(func.count(CollectiveOffer.id)).filter(
            CollectiveOffer.validation == OfferValidationStatus.APPROVED, CollectiveOffer.venueId == self.id
        )
        results = query_offer.union(query_collective).all()

        return sum(result for result, in results)

    @property
    def thumbUrl(self) -> str:
        """
        Override to discard the thumbCount column: not used by Venues
        which have at most one banner (thumb).
        """
        return "{}/{}/{}".format(self.thumb_base_url, self.thumb_path_component, humanize(self.id))

    @property
    def isReleased(self) -> bool:
        return self.managingOfferer.isActive and self.managingOfferer.isValidated

    @hybrid_property
    def timezone(self) -> str:
        if self.departementCode is None:
            return get_postal_code_timezone(self.managingOfferer.postalCode)
        return get_department_timezone(self.departementCode)

    @timezone.expression  # type: ignore [no-redef]
    def timezone(cls) -> Case:  # pylint: disable=no-self-argument
        offerer_alias = aliased(Offerer)
        return case(
            [
                (
                    cls.departementCode.is_(None),
                    case(
                        CUSTOM_TIMEZONES,
                        value=db.session.query(offerer_alias.departementCode)
                        .filter(cls.managingOffererId == offerer_alias.id)
                        .as_scalar(),
                        else_=METROPOLE_TIMEZONE,
                    ),
                )
            ],
            else_=case(CUSTOM_TIMEZONES, value=cls.departementCode, else_=METROPOLE_TIMEZONE),
        )

    def field_exists_and_has_changed(self, field: str, value: typing.Any) -> typing.Any:
        if field not in type(self).__table__.columns:
            raise ValueError(f"Unknown field {field} for model {type(self)}")
        return getattr(self, field) != value

    @property
    def current_pricing_point_id(self) -> int | None:
        now = datetime.utcnow()
        return (
            db.session.query(VenuePricingPointLink.pricingPointId)
            .filter(
                VenuePricingPointLink.venueId == self.id,
                VenuePricingPointLink.timespan.contains(now),
            )
            .scalar()
        )

    @property
    def current_reimbursement_point_id(self) -> int | None:
        now = datetime.utcnow()
        return (
            db.session.query(VenueReimbursementPointLink.reimbursementPointId)
            .filter(
                VenueReimbursementPointLink.venueId == self.id,
                VenueReimbursementPointLink.timespan.contains(now),
            )
            .scalar()
        )

    @hybrid_property
    def common_name(self) -> str:
        return self.publicName or self.name

    @common_name.expression  # type: ignore [no-redef]
    def common_name(self) -> str:
        return sqla_func.coalesce(func.nullif(self.publicName, ""), self.name)


class VenueLabel(PcObject, Base, Model):
    __tablename__ = "venue_label"
    label: str = Column(String(100), nullable=False)


class VenueType(PcObject, Base, Model):
    __tablename__ = "venue_type"
    label: str = Column(String(100), nullable=False)


class VenueContact(PcObject, Base, Model):
    __tablename__ = "venue_contact"

    venueId: int = Column(
        BigInteger, ForeignKey("venue.id", ondelete="CASCADE"), nullable=False, index=True, unique=True
    )

    venue: sa_orm.Mapped[Venue] = relationship("Venue", foreign_keys=[venueId], back_populates="contact")

    email = Column(String(256), nullable=True)

    website = Column(String(256), nullable=True)

    phone_number = Column(String(64), nullable=True)

    social_medias: dict = Column(MutableDict.as_mutable(JSONB), nullable=False, default={}, server_default="{}")

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(venueid={self.venueId!r}, "
            f"email={self.email!r}, "
            f"phone_number={self.phone_number!r}, "
            f"social_medias={self.social_medias!r})"
        )

    def field_exists_and_has_changed(self, field: str, value: typing.Any) -> typing.Any:
        if field not in type(self).__table__.columns:
            raise ValueError(f"Unknown field {field} for model {type(self)}")
        return getattr(self, field) != value


@listens_for(Venue, "before_insert")
def before_insert(mapper: typing.Any, connect: typing.Any, venue: Venue) -> None:
    _fill_departement_code_from_postal_code(venue)


@listens_for(Venue, "before_update")
def before_update(mapper: typing.Any, connect: typing.Any, venue: Venue) -> None:
    _fill_departement_code_from_postal_code(venue)


def _fill_departement_code_from_postal_code(venue: Venue) -> None:
    if not venue.isVirtual:
        if not venue.postalCode:
            raise IntegrityError(None, None, None)
        venue.store_departement_code()


ts_indexes = [
    ("idx_venue_fts_name", Venue.name),
    (
        "idx_venue_fts_publicName",
        Venue.publicName,
    ),
    ("idx_venue_fts_address", Venue.address),
    ("idx_venue_fts_siret", Venue.siret),
    ("idx_venue_fts_city", Venue.city),
]

(Venue.__ts_vectors__, Venue.__table_args__) = create_ts_vector_and_table_args(ts_indexes)


class VenuePricingPointLink(Base, Model):
    """At any given time, the bookings of a venue are priced against a
    particular venue that we call the "pricing point" of the venue.
    There should only ever be one pricing point for each venue, but
    for flexibility's sake we store the link in a table with the
    period during which this link is active.
    """

    id: int = Column(BigInteger, primary_key=True, autoincrement=True)
    venueId: int = Column(BigInteger, ForeignKey("venue.id"), index=True, nullable=False)
    venue: sa_orm.Mapped[Venue] = relationship(Venue, foreign_keys=[venueId], back_populates="pricing_point_links")
    pricingPointId: int = Column(BigInteger, ForeignKey("venue.id"), index=True, nullable=False)
    pricingPoint: sa_orm.Mapped[Venue] = relationship(Venue, foreign_keys=[pricingPointId])
    # The lower bound is inclusive and required. The upper bound is
    # exclusive and optional. If there is no upper bound, it means
    # that the venue is still linked to the pricing point. For links
    # that existed before this table was introduced, the lower bound
    # is set to the Epoch.
    timespan: psycopg2.extras.DateTimeRange = Column(sa_psql.TSRANGE, nullable=False)

    __table_args__ = (
        # A venue cannot be linked to multiple pricing points at the
        # same time.
        sa_psql.ExcludeConstraint(("venueId", "="), ("timespan", "&&")),
    )

    def __init__(self, **kwargs: typing.Any) -> None:
        kwargs["timespan"] = db_utils.make_timerange(*kwargs["timespan"])
        super().__init__(**kwargs)


class VenueReimbursementPointLink(Base, Model):
    """At any given time, all bookings of a venue are reimbursed to a bank
    account that is attached to a particular venue that we call the
    "reimbursement point" of the venue. It may be the venue itself or
    any other venue (that has a related bank account) of the same offerer.
    """

    id: int = Column(BigInteger, primary_key=True, autoincrement=True)
    venueId: int = Column(BigInteger, ForeignKey("venue.id"), index=True, nullable=False)
    venue: sa_orm.Mapped[Venue] = relationship(
        Venue, foreign_keys=[venueId], back_populates="reimbursement_point_links"
    )
    reimbursementPointId: int = Column(BigInteger, ForeignKey("venue.id"), index=True, nullable=False)
    reimbursementPoint: sa_orm.Mapped[Venue] = relationship(Venue, foreign_keys=[reimbursementPointId])
    # The lower bound is inclusive and required. The upper bound is
    # exclusive and optional. If there is no upper bound, it means
    # that the venue is still linked to the reimbursement point. For links
    # that existed before this table was introduced, the lower bound
    # is set to the Epoch.
    timespan: psycopg2.extras.DateTimeRange = Column(sa_psql.TSRANGE, nullable=False)

    __table_args__ = (
        # A venue cannot be linked to multiple reimbursement points at
        # the same time.
        sa_psql.ExcludeConstraint(("venueId", "="), ("timespan", "&&")),
    )

    def __init__(self, **kwargs: typing.Any) -> None:
        kwargs["timespan"] = db_utils.make_timerange(*kwargs["timespan"])
        super().__init__(**kwargs)


class VenueEducationalStatus(Base, Model):
    __tablename__ = "venue_educational_status"
    id: int = Column(BigInteger, primary_key=True, autoincrement=False, nullable=False)
    name: str = Column(String(256), nullable=False)
    venues = relationship(Venue, back_populates="venueEducationalStatus", uselist=True)


class Offerer(
    PcObject,
    Base,
    Model,
    HasThumbMixin,
    HasAddressMixin,
    ProvidableMixin,
    ValidationStatusMixin,
    DeactivableMixin,
):
    dateCreated: datetime = Column(DateTime, nullable=False, default=datetime.utcnow)

    name: str = Column(String(140), nullable=False)
    sa.Index("idx_offerer_trgm_name", name, postgresql_using="gin")

    UserOfferers: list["UserOfferer"] = sa.orm.relationship(
        "UserOfferer", order_by="UserOfferer.id", back_populates="offerer"
    )

    siren = Column(
        String(9), nullable=True, unique=True
    )  # FIXME: should not be nullable, is until we have all SIRENs filled in the DB

    dateValidated = Column(DateTime, nullable=True, default=None)

    tags: list["OffererTag"] = sa.orm.relationship("OffererTag", secondary="offerer_tag_mapping")

    thumb_path_component = "offerers"

    @property
    def bic(self) -> str | None:
        return self.bankInformation.bic if self.bankInformation else None

    @property
    def iban(self) -> str | None:
        return self.bankInformation.iban if self.bankInformation else None

    @property
    def demarchesSimplifieesApplicationId(self) -> str | None:
        if not self.bankInformation:
            return None

        if self.bankInformation.status not in (
            finance_models.BankInformationStatus.DRAFT,
            finance_models.BankInformationStatus.ACCEPTED,
        ):
            return None

        return self.bankInformation.applicationId

    @hybrid_property
    def departementCode(self) -> str:
        return postal_code_utils.PostalCode(self.postalCode).get_departement_code()

    @departementCode.expression  # type: ignore [no-redef]
    def departementCode(cls) -> Case:  # pylint: disable=no-self-argument
        return case(
            [
                (
                    cast(func.substring(cls.postalCode, 1, 2), Integer)
                    >= postal_code_utils.OVERSEAS_DEPARTEMENT_CODE_START,
                    func.substring(cls.postalCode, 1, 3),
                )
            ],
            else_=func.substring(cls.postalCode, 1, 2),
        )

    @cached_property
    def legal_category(self) -> dict:
        code = None
        if self.siren:
            try:
                code = sirene.get_legal_category_code(self.siren)
            except sirene.SireneException as exc:
                logger.warning(
                    "Error on Sirene API when retrieving legal category",
                    extra={"exc": exc, "siren": self.siren},
                )
        if code:
            label = constants.CODE_TO_CATEGORY_MAPPING.get(int(code), "")
        else:
            code = label = "Donnée indisponible"
        return {"code": code, "label": label}

    @property
    def first_user(self) -> "users_models.User | None":
        # Currently there is no way to mark a UserOfferer as the owner/creator, so we consider that this first user
        # is the oldest entry in the table. When creator leaves the offerer, next registered user becomes the "first".
        if not self.UserOfferers:
            return None
        return self.UserOfferers[0].user


offerer_ts_indexes = [
    ("idx_offerer_fts_name", Offerer.name),
    ("idx_offerer_fts_address", Offerer.address),
    ("idx_offerer_fts_siret", Offerer.siren),
]

(Offerer.__ts_vectors__, Offerer.__table_args__) = create_ts_vector_and_table_args(offerer_ts_indexes)


class UserOfferer(PcObject, Base, Model, ValidationStatusMixin):
    __table_name__ = "user_offerer"
    userId: int = Column(BigInteger, ForeignKey("user.id"), primary_key=True)
    user: sa_orm.Mapped["users_models.User"] = relationship(
        "User", foreign_keys=[userId], back_populates="UserOfferers"
    )
    offererId: int = Column(BigInteger, ForeignKey("offerer.id"), index=True, primary_key=True, nullable=False)
    offerer: Offerer = relationship(Offerer, foreign_keys=[offererId], back_populates="UserOfferers")

    __table_args__ = (
        UniqueConstraint(
            "userId",
            "offererId",
            name="unique_user_offerer",
        ),
    )

    # dateCreated will remain null for all rows already in this table before this field was added
    dateCreated: datetime = Column(DateTime, nullable=True, default=datetime.utcnow)


class ApiKey(PcObject, Base, Model):
    offererId: int = Column(BigInteger, ForeignKey("offerer.id"), index=True, nullable=False)

    offerer: sa_orm.Mapped[Offerer] = relationship("Offerer", foreign_keys=[offererId], backref=backref("apiKeys"))

    dateCreated: datetime = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=func.now())

    prefix = Column(Text, nullable=True, unique=True)

    secret: bytes = Column(LargeBinary, nullable=True)

    def check_secret(self, clear_text: str) -> bool:
        return crypto.check_password(clear_text, self.secret)


class OffererTag(PcObject, Base, Model):
    """
    Tags on offerers are only used in backoffice, set to help for filtering and analytics in metabase.
    There is currently no display or impact in mobile and web apps.
    """

    __tablename__ = "offerer_tag"

    name: str = Column(String(140), nullable=False, unique=True)
    label: str = Column(String(140))
    description: str = Column(Text)

    categories: list["OffererTagCategory"] = sa.orm.relationship(
        "OffererTagCategory", secondary="offerer_tag_category_mapping"
    )

    def __str__(self) -> str:
        return self.label or self.name


class OffererTagCategory(PcObject, Base, Model):
    """
    Tag categories can be considered as "tags on tags", which aims at filtering tags depending on the projet:
    tags used for partners counting, tags used for offerer validation, etc.
    The same OffererTag can be used in one or several project.
    """

    __tablename__ = "offerer_tag_category"

    name: str = Column(String(140), nullable=False, unique=True)
    label: str = Column(String(140))

    def __str__(self) -> str:
        return self.label or self.name


class OffererTagCategoryMapping(PcObject, Base, Model):
    __tablename__ = "offerer_tag_category_mapping"

    tagId: int = Column(BigInteger, ForeignKey("offerer_tag.id", ondelete="CASCADE"), index=True, nullable=False)
    categoryId: int = Column(
        BigInteger, ForeignKey("offerer_tag_category.id", ondelete="CASCADE"), index=True, nullable=False
    )

    __table_args__ = (UniqueConstraint("tagId", "categoryId", name="unique_offerer_tag_category"),)


class OffererTagMapping(PcObject, Base, Model):
    __tablename__ = "offerer_tag_mapping"

    offererId: int = Column(BigInteger, ForeignKey("offerer.id", ondelete="CASCADE"), index=True, nullable=False)
    tagId: int = Column(BigInteger, ForeignKey("offerer_tag.id", ondelete="CASCADE"), index=True, nullable=False)

    __table_args__ = (UniqueConstraint("offererId", "tagId", name="unique_offerer_tag"),)
