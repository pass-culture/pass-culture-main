from datetime import date
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
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import UniqueConstraint
from sqlalchemy import case
from sqlalchemy import cast
from sqlalchemy import func
import sqlalchemy.dialects.postgresql as sa_psql
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.event import listens_for
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext import mutable as sa_mutable
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import MutableDict
import sqlalchemy.orm as sa_orm
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.sql.elements import Case
from sqlalchemy.sql.sqltypes import LargeBinary

from pcapi.connectors.acceslibre import AccessibilityInfo
from pcapi.connectors.big_query.queries.offerer_stats import OffererViewsModel
from pcapi.connectors.big_query.queries.offerer_stats import TopOffersData
from pcapi.core.finance import models as finance_models
from pcapi.core.geography import models as geography_models
from pcapi.core.offerers.base_models import Target
from pcapi.core.offerers.base_models import Venue
from pcapi.core.offerers.base_models import VenuePricingPointLink  # pylint: disable=unused-import
from pcapi.core.offerers.schemas import VenueTypeCode
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models import db
from pcapi.models.deactivable_mixin import DeactivableMixin
from pcapi.models.feature import FeatureToggle
from pcapi.models.has_address_mixin import HasAddressMixin
from pcapi.models.pc_object import PcObject
from pcapi.models.validation_status_mixin import ValidationStatusMixin
from pcapi.utils import crypto
from pcapi.utils import regions as regions_utils
from pcapi.utils import siren as siren_utils
import pcapi.utils.db as db_utils
import pcapi.utils.postal_code as postal_code_utils


if typing.TYPE_CHECKING:
    import pcapi.core.criteria.models as criteria_models
    import pcapi.core.offers.models as offers_models
    import pcapi.core.providers.models as providers_models
    from pcapi.core.providers.models import Provider
    import pcapi.core.users.models as users_models

logger = logging.getLogger(__name__)

PERMENANT_VENUE_TYPES = [
    VenueTypeCode.CREATIVE_ARTS_STORE,
    VenueTypeCode.LIBRARY,
    VenueTypeCode.BOOKSTORE,
    VenueTypeCode.MUSEUM,
    VenueTypeCode.MOVIE,
    VenueTypeCode.MUSICAL_INSTRUMENT_STORE,
]


class OffererRejectionReason(enum.Enum):
    ELIGIBILITY = "ELIGIBILITY"
    ERROR = "ERROR"
    ADAGE_DECLINED = "ADAGE_DECLINED"
    OUT_OF_TIME = "OUT_OF_TIME"
    CLOSED_BUSINESS = "CLOSED_BUSINESS"
    OTHER = "OTHER"


class InvitationStatus(enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"


class Weekday(enum.Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


class GooglePlacesInfo(PcObject, Base, Model):
    __tablename__ = "google_places_info"
    venueId: int = Column(
        BigInteger, ForeignKey("venue.id", ondelete="CASCADE"), nullable=False, index=True, unique=True
    )
    venue: sa_orm.Mapped[Venue] = relationship("Venue", foreign_keys=[venueId], back_populates="googlePlacesInfo")
    # Some venues are duplicated in our database. They are all linked to the same item on
    # Google Places, so this column cannot be unique.
    placeId: str | None = Column(Text, nullable=True, unique=False)
    bannerUrl: str | None = Column(Text, nullable=True, name="bannerUrl")
    bannerMeta: dict | None = Column(MutableDict.as_mutable(JSONB), nullable=True)
    updateDate: datetime = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


class AccessibilityProvider(PcObject, Base, Model):
    venueId: int = Column(
        BigInteger, ForeignKey("venue.id", ondelete="CASCADE"), index=True, nullable=False, unique=True
    )
    venue: sa_orm.Mapped[Venue] = relationship("Venue", foreign_keys=[venueId], back_populates="accessibilityProvider")
    externalAccessibilityId: str = Column(Text, nullable=False)
    externalAccessibilityUrl: str = Column(Text, nullable=False)
    externalAccessibilityData: AccessibilityInfo | None = sa.Column(MutableDict.as_mutable(JSONB), nullable=True)
    lastUpdateAtProvider: datetime = Column(DateTime, nullable=False, default=datetime.utcnow)


class OpeningHours(PcObject, Base, Model):
    __tablename__ = "opening_hours"
    venueId: int = Column(BigInteger, ForeignKey("venue.id", ondelete="CASCADE"), nullable=False, index=True)
    venue: sa_orm.Mapped[Venue] = relationship("Venue", foreign_keys=[venueId], back_populates="openingHours")
    weekday: Weekday = Column(db_utils.MagicEnum(Weekday), nullable=False, default=Weekday.MONDAY)
    timespan: list[psycopg2.extras.NumericRange] = Column(sa_psql.ARRAY(sa_psql.ranges.NUMRANGE), nullable=True)

    __table_args__ = ((CheckConstraint(func.cardinality(timespan) <= 2, name="max_timespan_is_2")),)

    def field_exists_and_has_changed(self, field: str, value: typing.Any) -> typing.Any:
        if field not in type(self).__table__.columns:
            raise ValueError(f"Unknown field {field} for model {type(self)}")
        return getattr(self, field) != value


class VenueLabel(PcObject, Base, Model):
    __tablename__ = "venue_label"
    id: sa_orm.Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
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
    _fill_departement_code_and_timezone(venue)


@listens_for(Venue, "before_update")
def before_update(mapper: typing.Any, connect: typing.Any, venue: Venue) -> None:
    _fill_departement_code_and_timezone(venue)


def _fill_departement_code_and_timezone(venue: Venue) -> None:
    if not venue.isVirtual:
        if not venue.postalCode:
            raise IntegrityError(None, None, None)
        venue.store_departement_code()
    venue.store_timezone()


class VenueBankAccountLink(PcObject, Base, Model):
    """
    Professional users can link as many venues as they want to a given bank account.
    However, we want to keep tracks of the history, hence that table.
    """

    venueId: int = Column(BigInteger, ForeignKey("venue.id", ondelete="CASCADE"), index=True, nullable=False)
    venue: sa_orm.Mapped[Venue] = relationship("Venue", foreign_keys=[venueId], back_populates="bankAccountLinks")

    bankAccountId: int = Column(
        BigInteger, ForeignKey("bank_account.id", ondelete="CASCADE"), index=True, nullable=False
    )
    bankAccount: sa_orm.Mapped[finance_models.BankAccount] = relationship(
        "BankAccount", foreign_keys=[bankAccountId], back_populates="venueLinks"
    )

    timespan: psycopg2.extras.DateTimeRange = Column(sa_psql.TSRANGE, nullable=False)

    __table_args__ = (
        # For a given venue, there can only be one bank account at a time.
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


class VenueRegistration(PcObject, Base, Model):
    __tablename__ = "venue_registration"

    id: int = Column("id", BigInteger, sa.Identity(), primary_key=True)

    venueId: int = Column(
        BigInteger, ForeignKey("venue.id", ondelete="CASCADE"), nullable=False, index=True, unique=True
    )

    venue: sa_orm.Mapped[Venue] = relationship("Venue", foreign_keys=[venueId], back_populates="registration")

    target: Target = Column(db_utils.MagicEnum(Target), nullable=False)

    webPresence: str | None = sa.Column(sa.Text, nullable=True)


class Offerer(
    PcObject,
    Base,
    Model,
    HasAddressMixin,
    ValidationStatusMixin,
    DeactivableMixin,
):
    dateCreated: datetime = Column(DateTime, nullable=False, default=datetime.utcnow)

    name: str = Column(String(140), nullable=False)
    sa.Index("ix_offerer_trgm_unaccent_name", sa.func.immutable_unaccent("name"), postgresql_using="gin")

    sa.Index("ix_offerer_trgm_unaccent_city", sa.func.immutable_unaccent("city"), postgresql_using="gin")

    UserOfferers: list["UserOfferer"] = sa_orm.relationship(
        "UserOfferer", order_by="UserOfferer.id", back_populates="offerer"
    )

    siren = Column(
        String(9), nullable=True, unique=True
    )  # FIXME: should not be nullable, is until we have all SIRENs filled in the DB

    dateValidated = Column(DateTime, nullable=True, default=None)

    tags: list["OffererTag"] = sa_orm.relationship("OffererTag", secondary="offerer_tag_mapping")

    # use an expression instead of joinedload(tags) to avoid multiple SQL rows returned
    isTopActeur: sa_orm.Mapped["bool"] = sa_orm.query_expression()

    @hybrid_property
    def is_top_acteur(self) -> bool:
        return any(tag.name == "top-acteur" for tag in self.tags)

    @is_top_acteur.expression  # type: ignore[no-redef]
    def is_top_acteur(cls) -> sa.sql.elements.BooleanClauseList:  # pylint: disable=no-self-argument
        return (
            sa.select(1)
            .select_from(OffererTagMapping)
            .join(OffererTag, OffererTag.id == OffererTagMapping.c.tagId)
            .where(OffererTagMapping.c.offererId == cls.id, OffererTag.name == "top-acteur")
            .limit(1)
            .exists()
        )

    offererProviders: list["OffererProvider"] = sa_orm.relationship("OffererProvider", back_populates="offerer")
    thumb_path_component = "offerers"

    bankAccounts: list[finance_models.BankAccount] = sa_orm.relationship(
        finance_models.BankAccount,
        back_populates="offerer",
        passive_deletes=True,
    )

    individualSubscription: Mapped["IndividualOffererSubscription | None"] = sa_orm.relationship(
        "IndividualOffererSubscription", back_populates="offerer", uselist=False
    )

    allowedOnAdage: bool = Column(Boolean, nullable=False, default=False, server_default=sa.sql.expression.false())

    _street = Column("street", Text(), nullable=True)

    def __init__(self, street: str | None = None, **kwargs: typing.Any) -> None:
        if street:
            self.street = street  # type: ignore[method-assign]
        super().__init__(**kwargs)

    @hybrid_property
    def street(self) -> str | None:
        return self._address

    @street.setter  # type: ignore[no-redef]
    def street(self, value: str | None) -> None:
        self._address = value
        self._street = value

    @street.expression  # type: ignore[no-redef]
    def street(cls):  # pylint: disable=no-self-argument
        return cls._address

    @hybrid_property
    def departementCode(self) -> str:
        return postal_code_utils.PostalCode(self.postalCode).get_departement_code()

    @departementCode.expression  # type: ignore[no-redef]
    def departementCode(cls) -> Case:  # pylint: disable=no-self-argument
        return case(
            (
                cls.postalCode == postal_code_utils.SAINT_MARTIN_POSTAL_CODE,
                postal_code_utils.SAINT_MARTIN_DEPARTEMENT_CODE,
            ),
            (
                cast(func.substring(cls.postalCode, 1, postal_code_utils.MAINLAND_DEPARTEMENT_CODE_LENGTH), Integer)
                >= postal_code_utils.OVERSEAS_DEPARTEMENT_CODE_START,
                func.substring(cls.postalCode, 1, postal_code_utils.OVERSEAS_DEPARTEMENT_CODE_LENGTH),
            ),
            else_=func.substring(cls.postalCode, 1, postal_code_utils.MAINLAND_DEPARTEMENT_CODE_LENGTH),
        )

    @hybrid_property
    def rid7(self) -> str | None:
        if self.siren and siren_utils.is_rid7(self.siren):
            return siren_utils.siren_to_rid7(self.siren)
        return None

    @rid7.expression  # type: ignore[no-redef]
    def rid7(cls) -> Case:  # pylint: disable=no-self-argument
        return sa.case(
            (cls.siren.ilike(f"{siren_utils.NEW_CALEDONIA_SIREN_PREFIX}%"), func.substring(cls.siren, 3, 7)), else_=None
        )

    @hybrid_property
    def is_caledonian(self) -> bool:
        """
        Note that caledonian offerers may have a SIREN and be registered with their SIREN.
        Caledonian offerers with SIREN can be checked on "Annuaire des Entreprises" or Sirene API, but cannot create
        collective offers or apply on Adage. Check `rid7` or `is_caledonian` property depending on purpose.
        """
        if self.siren and siren_utils.is_rid7(self.siren):
            return True
        if self.postalCode.startswith(regions_utils.NEW_CALEDONIA_DEPARTMENT_CODE):
            return True
        return False

    @is_caledonian.expression  # type: ignore[no-redef]
    def is_caledonian(cls) -> BinaryExpression:  # pylint: disable=no-self-argument
        return sa.or_(
            cls.siren.ilike(f"{siren_utils.NEW_CALEDONIA_SIREN_PREFIX}%"),
            cls.postalCode.ilike(f"{regions_utils.NEW_CALEDONIA_DEPARTMENT_CODE}%"),
        )

    @property
    def identifier_name(self) -> str:
        return "RID7" if siren_utils.is_rid7(self.siren) else "SIREN"

    @property
    def identifier(self) -> str | None:
        return self.rid7 or self.siren

    @property
    def confidenceLevel(self) -> "OffererConfidenceLevel | None":
        if not self.confidenceRule:
            return None
        return self.confidenceRule.confidenceLevel


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
    providerId: int = Column(BigInteger, ForeignKey("provider.id", ondelete="CASCADE"), index=True)
    provider: sa_orm.Mapped["providers_models.Provider"] = relationship(
        "Provider", foreign_keys=[providerId], back_populates="apiKeys"
    )
    dateCreated: datetime = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=func.now())
    prefix = Column(Text, nullable=True, unique=True)
    secret: bytes = Column(LargeBinary, nullable=True)

    def check_secret(self, clear_text: str) -> bool:
        if self.secret.decode("utf-8").startswith("$sha3_512$"):
            return crypto.check_public_api_key(clear_text, self.secret)
        if crypto.check_password(clear_text, self.secret):
            if FeatureToggle.WIP_ENABLE_NEW_HASHING_ALGORITHM.is_active():
                self.secret = crypto.hash_public_api_key(clear_text)
                db.session.commit()
                logger.info("Switched hash of API key from bcrypt to SHA3-512", extra={"key_id": self.id})
            return True
        return False


class OffererTag(PcObject, Base, Model):
    """
    Tags on offerers are only used in backoffice, set to help for filtering and analytics in metabase.
    There is currently no display or impact in mobile and web apps.
    """

    __tablename__ = "offerer_tag"

    name: str = Column(String(140), nullable=False, unique=True)
    label: str = Column(String(140))
    description: str = Column(Text)

    categories: list["OffererTagCategory"] = sa_orm.relationship(
        "OffererTagCategory", secondary="offerer_tag_category_mapping"
    )

    def __str__(self) -> str:
        return self.label or self.name


class OffererTagCategory(PcObject, Base, Model):
    """
    Tag categories can be considered as "tags on tags", which aims at filtering tags depending on the project:
    tags used for partners counting, tags used for offerer validation, etc.
    The same OffererTag can be used in one or several project.
    """

    __tablename__ = "offerer_tag_category"

    name: str = Column(String(140), nullable=False, unique=True)
    label: str = Column(String(140))

    def __str__(self) -> str:
        return self.label or self.name


OffererTagCategoryMapping = sa.Table(
    "offerer_tag_category_mapping",
    Base.metadata,
    sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
    sa.Column("tagId", sa.ForeignKey(OffererTag.id, ondelete="CASCADE"), index=True, nullable=False),
    sa.Column("categoryId", sa.ForeignKey(OffererTagCategory.id, ondelete="CASCADE"), index=True, nullable=False),
    sa.UniqueConstraint("tagId", "categoryId", name="unique_offerer_tag_category"),
)


OffererTagMapping = sa.Table(
    "offerer_tag_mapping",
    Base.metadata,
    sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
    sa.Column("offererId", sa.ForeignKey(Offerer.id, ondelete="CASCADE"), index=True, nullable=False),
    sa.Column("tagId", sa.ForeignKey(OffererTag.id, ondelete="CASCADE"), index=True, nullable=False),
    sa.UniqueConstraint("offererId", "tagId", name="unique_offerer_tag"),
)


class OffererProvider(PcObject, Base, Model):
    __tablename__ = "offerer_provider"
    offererId: int = Column(BigInteger, ForeignKey("offerer.id", ondelete="CASCADE"), index=True, nullable=False)
    offerer: Offerer = relationship("Offerer", foreign_keys=[offererId], back_populates="offererProviders")
    providerId: int = Column(BigInteger, ForeignKey("provider.id"), index=True, nullable=False)
    provider: sa_orm.Mapped["providers_models.Provider"] = relationship(
        "Provider", foreign_keys=[providerId], back_populates="offererProvider"
    )

    __table_args__ = (UniqueConstraint("offererId", "providerId", name="unique_offerer_provider"),)


class OffererInvitation(PcObject, Base, Model):
    __tablename__ = "offerer_invitation"
    offererId: int = Column(BigInteger, ForeignKey("offerer.id", ondelete="CASCADE"), index=True, nullable=False)
    offerer: Offerer = relationship("Offerer", foreign_keys=[offererId])
    email: str = Column(Text, nullable=False)
    dateCreated: datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    userId: int = Column(BigInteger, ForeignKey("user.id"), nullable=False, index=True)
    user: sa_orm.Mapped["users_models.User"] = relationship("User", foreign_keys=[userId], backref="OffererInvitations")
    status: InvitationStatus = Column(db_utils.MagicEnum(InvitationStatus), nullable=False)

    __table_args__ = (UniqueConstraint("offererId", "email", name="unique_offerer_invitation"),)


class IndividualOffererSubscription(PcObject, Base, Model):
    __tablename__ = "individual_offerer_subscription"

    offererId: int = Column(BigInteger, ForeignKey("offerer.id", ondelete="CASCADE"), unique=True, nullable=False)
    offerer: Mapped[Offerer] = relationship(
        "Offerer", foreign_keys=[offererId], back_populates="individualSubscription", uselist=False
    )

    isEmailSent: bool = sa.Column(sa.Boolean, nullable=False, server_default=sa.sql.expression.false(), default=False)
    dateEmailSent: date | None = sa.Column(sa.Date, nullable=True)
    dateReminderEmailSent: date | None = sa.Column(sa.Date, nullable=True)

    isCriminalRecordReceived: bool = sa.Column(
        sa.Boolean, nullable=False, server_default=sa.sql.expression.false(), default=False
    )
    dateCriminalRecordReceived: date | None = sa.Column(sa.Date, nullable=True)

    isCertificateReceived: bool = sa.Column(
        sa.Boolean, nullable=False, server_default=sa.sql.expression.false(), default=False
    )
    certificateDetails: str | None = sa.Column(sa.Text, nullable=True)
    isExperienceReceived: bool = sa.Column(
        sa.Boolean, nullable=False, server_default=sa.sql.expression.false(), default=False
    )
    experienceDetails: str | None = sa.Column(sa.Text, nullable=True)
    has1yrExperience: bool = sa.Column(
        sa.Boolean, nullable=False, server_default=sa.sql.expression.false(), default=False
    )
    has5yrExperience: bool = sa.Column(
        sa.Boolean, nullable=False, server_default=sa.sql.expression.false(), default=False
    )
    isCertificateValid: bool = sa.Column(
        sa.Boolean, nullable=False, server_default=sa.sql.expression.false(), default=False
    )

    @hybrid_property
    def isReminderEmailSent(self) -> bool:
        return self.dateReminderEmailSent is not None

    @isReminderEmailSent.expression  # type: ignore[no-redef]
    def isReminderEmailSent(cls) -> Boolean:  # pylint: disable=no-self-argument
        return cls.dateReminderEmailSent.is_not(sa.null())


class OffererStatsData(typing.TypedDict, total=False):
    daily_views: list[OffererViewsModel]
    top_offers: list[TopOffersData]
    total_views_last_30_days: int


class OffererStats(PcObject, Base, Model):
    __tablename__ = "offerer_stats"

    offererId: int = Column(BigInteger, ForeignKey("offerer.id", ondelete="CASCADE"), nullable=False)
    sa.Index("ix_offerer_stats_offererId", offererId)
    offerer: Offerer = relationship("Offerer", foreign_keys=[offererId])

    syncDate: datetime = Column(DateTime, nullable=False)
    table: str = Column(String(120), nullable=False)
    jsonData: dict = sa.Column(  # serialized from `OffererStatsData`
        "jsonData",
        sa_mutable.MutableDict.as_mutable(sa_psql.JSONB),
        default={},
        server_default="{}",
        nullable=False,
    )


class OffererAddress(PcObject, Base, Model):
    __tablename__ = "offerer_address"
    label: str | None = sa.Column(sa.Text(), nullable=True)
    addressId = sa.Column(sa.BigInteger, sa.ForeignKey("address.id"), index=True)
    address: sa_orm.Mapped[geography_models.Address] = sa_orm.relationship("Address", foreign_keys=[addressId])
    offererId = sa.Column(sa.BigInteger, sa.ForeignKey("offerer.id", ondelete="CASCADE"), index=True)
    offerer: sa_orm.Mapped["Offerer"] = sa_orm.relationship("Offerer", foreign_keys=[offererId])
    venues: sa_orm.Mapped[typing.Sequence["Venue"]] = sa.orm.relationship("Venue", back_populates="offererAddress")

    __table_args__ = (sa.Index("ix_unique_offerer_address_per_label", "offererId", "addressId", "label", unique=True),)

    _isLinkedToVenue: sa_orm.Mapped["bool|None"] = sa_orm.query_expression()

    @hybrid_property
    def isLinkedToVenue(self) -> bool:
        return db.session.query(sa.select(1).exists().where(Venue.offererAddressId == self.id)).scalar()

    @isLinkedToVenue.expression  # type: ignore[no-redef]
    def isLinkedToVenue(cls) -> sa.sql.elements.BooleanClauseList:  # pylint: disable=no-self-argument
        return sa.select(1).where(Venue.offererAddressId == cls.id).exists()


class OffererConfidenceLevel(enum.Enum):
    # No default value when offerer follows rules in offer_validation_rule table,
    # in which case there is no row in table below
    MANUAL_REVIEW = "MANUAL_REVIEW"
    WHITELIST = "WHITELIST"


class OffererConfidenceRule(PcObject, Base, Model):
    __tablename__ = "offerer_confidence_rule"

    offererId = sa.Column(
        sa.BigInteger, sa.ForeignKey("offerer.id", ondelete="CASCADE"), index=True, unique=True, nullable=True
    )
    offerer: sa_orm.Mapped["Offerer | None"] = sa_orm.relationship(
        "Offerer", foreign_keys=[offererId], backref=sa_orm.backref("confidenceRule", uselist=False)
    )

    venueId = sa.Column(
        sa.BigInteger, sa.ForeignKey("venue.id", ondelete="CASCADE"), index=True, unique=True, nullable=True
    )
    venue: sa_orm.Mapped["Venue | None"] = sa_orm.relationship(
        "Venue", foreign_keys=[venueId], backref=sa_orm.backref("confidenceRule", uselist=False)
    )

    confidenceLevel: OffererConfidenceLevel = sa.Column(db_utils.MagicEnum(OffererConfidenceLevel), nullable=False)

    __table_args__ = (sa.CheckConstraint('num_nonnulls("offererId", "venueId") = 1'),)
