from datetime import date
from datetime import datetime
import decimal
import enum
import logging
import os
import re
import typing

import psycopg2.extras
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as sa_psql
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.event import listens_for
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext import mutable as sa_mutable
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.ext.mutable import MutableList
import sqlalchemy.orm as sa_orm
from sqlalchemy.sql import expression
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.sql.elements import Case
import sqlalchemy.sql.functions as sa_func
from sqlalchemy.sql.selectable import Exists
from sqlalchemy.sql.sqltypes import LargeBinary

from pcapi import settings
from pcapi.connectors.acceslibre import AccessibilityInfo
from pcapi.connectors.big_query.queries.offerer_stats import OffererViewsModel
from pcapi.connectors.big_query.queries.offerer_stats import TopOffersData
from pcapi.core.criteria.models import VenueCriterion
from pcapi.core.educational import models as educational_models
import pcapi.core.finance.models as finance_models
from pcapi.core.geography import models as geography_models
from pcapi.core.offerers.schemas import BannerMetaModel
from pcapi.core.offerers.schemas import VenueTypeCode
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models import db
from pcapi.models.accessibility_mixin import AccessibilityMixin
from pcapi.models.deactivable_mixin import DeactivableMixin
from pcapi.models.feature import FeatureToggle
from pcapi.models.has_address_mixin import HasAddressMixin
from pcapi.models.has_thumb_mixin import HasThumbMixin
from pcapi.models.pc_object import PcObject
from pcapi.models.soft_deletable_mixin import SoftDeletableMixin
from pcapi.models.validation_status_mixin import ValidationStatusMixin
from pcapi.utils import crypto
from pcapi.utils import regions as regions_utils
from pcapi.utils import siren as siren_utils
from pcapi.utils.date import METROPOLE_TIMEZONE
from pcapi.utils.date import get_department_timezone
from pcapi.utils.date import get_postal_code_timezone
from pcapi.utils.date import numranges_to_timespan_str
import pcapi.utils.db as db_utils
from pcapi.utils.human_ids import humanize
import pcapi.utils.postal_code as postal_code_utils


if typing.TYPE_CHECKING:
    import pcapi.core.criteria.models as criteria_models
    import pcapi.core.offers.models as offers_models
    import pcapi.core.providers.models as providers_models
    import pcapi.core.users.models as users_models

logger = logging.getLogger(__name__)

CONSTRAINT_CHECK_HAS_SIRET_XOR_HAS_COMMENT_XOR_IS_VIRTUAL = """
    (siret IS NULL AND comment IS NULL AND "isVirtual" IS TRUE)
    OR (siret IS NULL AND comment IS NOT NULL AND "isVirtual" IS FALSE)
    OR (siret IS NOT NULL AND "isVirtual" IS FALSE)
"""


PERMENANT_VENUE_TYPES = [
    VenueTypeCode.CREATIVE_ARTS_STORE,
    VenueTypeCode.LIBRARY,
    VenueTypeCode.BOOKSTORE,
    VenueTypeCode.MUSEUM,
    VenueTypeCode.MOVIE,
    VenueTypeCode.MUSICAL_INSTRUMENT_STORE,
]

VENUE_DEFAULTS_DIR = "assets/venue_default_images"
VENUE_TYPE_DEFAULT_BANNERS: dict[VenueTypeCode, tuple[str, ...]] = {
    VenueTypeCode.ADMINISTRATIVE: (),
    VenueTypeCode.ARTISTIC_COURSE: (
        "AdobeStock_254377106_1.png",
        "the-climate-reality-project-Hb6uWq0i4MI-unsplash_1.png",
    ),
    VenueTypeCode.BOOKSTORE: (
        "becca-tapert-GnY_mW1Q6Xc-unsplash.png",
        "chuttersnap-m3ewYVannII-unsplash.png",
    ),
    VenueTypeCode.CONCERT_HALL: (
        "aleksandr-popov-hTv8aaPziOQ-unsplash.png",
        "nick-moore-5zWN8DTNeVA-unsplash.png",
    ),
    VenueTypeCode.CREATIVE_ARTS_STORE: (
        "jack-b-pliYdZJNma0-unsplash.png",
        "jacqueline-brandwayn-XJEeS5qSFAs-unsplash_1.png",
    ),
    VenueTypeCode.CULTURAL_CENTRE: (
        "jan-antonin-kolar-hN_zCni3ILg-unsplash_1.png",
        "noriely-fernandez-oJ1qnM6BYZo-unsplash.png",
    ),
    VenueTypeCode.DIGITAL: (
        "glenn-carstens-peters-npxXWgQ33ZQ-unsplash.png",
        "rodion-kutsaiev-0VGG7cqTwCo-unsplash.png",
    ),
    VenueTypeCode.DISTRIBUTION_STORE: (),
    VenueTypeCode.FESTIVAL: (
        "cody-board-C7DWZcxFCNY-unsplash.png",
        "colin-lloyd-W6_txbgkkeU-unsplash.png",
    ),
    VenueTypeCode.GAMES: (
        "AdobeStock_152386393_1.png",
        "kdwk-leung-3oqHaTT_j8o-unsplash_1.png",
    ),
    VenueTypeCode.LIBRARY: (
        "priscilla-du-preez-ggeZ9oyI-PE-unsplash_1.png",
        "trnava-university-sd8uJsf4XM4-unsplash_1.png",
    ),
    VenueTypeCode.MOVIE: (
        "denise-jans-OaVJQZ-nFD0-unsplash.png",
        "krists-luhaers-AtPWnYNDJnM-unsplash.png",
    ),
    VenueTypeCode.MUSEUM: (
        "amy-leigh-barnard-H3APOiYLyzk-unsplashed.png",
        "musee1.png",
    ),
    VenueTypeCode.MUSICAL_INSTRUMENT_STORE: (
        "sandie-clarke-Ga6TvlrtTrE-unsplash.png",
        "viktor-forgacs-nuRL2Wveb6w-unsplash.png",
    ),
    VenueTypeCode.OTHER: (),
    VenueTypeCode.PATRIMONY_TOURISM: (
        "daniel-chekalov-JAMX7iNjXnU-unsplash.png",
        "henri-lajarrige-lombard-OFDD2Jg1RCA-unsplash_1.png",
    ),
    VenueTypeCode.PERFORMING_ARTS: (
        "erik-mclean-PFfA3xlHFbQ-unsplash_(1).png",
        "mark-williams-9bNmhMKQM1Q-unsplash_1.png",
    ),
    VenueTypeCode.RECORD_STORE: (
        "clem-onojeghuo-pTeZKi29EYE-unsplash.png",
        "ilya-blagoderov-t4csj4KilnE-unsplash.png",
    ),
    VenueTypeCode.SCIENTIFIC_CULTURE: (
        "edd_Medium-Shot_avec_un_Canon_R5_50_mm_DSLR_Science_class_with__0251a3c2-c494-4b61-8116-a22c61848947%20(1).png",
        "uxuipc_High_angle_avec_un_Canon_R5_50_mm_DSLR_planetarium_with__f16e10f2-eb38-4314-b5f2-784819f04c05%20(1).png",
    ),
    VenueTypeCode.TRAVELING_CINEMA: (),
    VenueTypeCode.VISUAL_ARTS: (
        "dannie-jing-3GZlhROZIQg-unsplash_(1).jpg",
        "darya-tryfanava-UCNaGWn4EfU-unsplash.jpg",
    ),
}


class OffererRejectionReason(enum.Enum):
    ELIGIBILITY = "ELIGIBILITY"
    ERROR = "ERROR"
    ADAGE_DECLINED = "ADAGE_DECLINED"
    OUT_OF_TIME = "OUT_OF_TIME"
    CLOSED_BUSINESS = "CLOSED_BUSINESS"
    OTHER = "OTHER"


class Target(enum.Enum):
    EDUCATIONAL = "EDUCATIONAL"
    INDIVIDUAL_AND_EDUCATIONAL = "INDIVIDUAL_AND_EDUCATIONAL"
    INDIVIDUAL = "INDIVIDUAL"


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


class Venue(PcObject, Base, Model, HasThumbMixin, AccessibilityMixin, SoftDeletableMixin):
    __tablename__ = "venue"

    name: str = sa.Column(sa.String(140), nullable=False)
    sa.Index("ix_venue_trgm_unaccent_name", sa.func.immutable_unaccent("name"), postgresql_using="gin")

    siret = sa.Column(sa.String(14), nullable=True, unique=True)

    departementCode = sa.Column(sa.String(3), nullable=True, index=True)

    latitude: decimal.Decimal | None = sa.Column(sa.Numeric(8, 5), nullable=True)

    longitude: decimal.Decimal | None = sa.Column(sa.Numeric(8, 5), nullable=True)

    venueProviders: sa_orm.Mapped[list["providers_models.VenueProvider"]] = sa_orm.relationship(
        "VenueProvider", back_populates="venue"
    )

    managingOffererId: int = sa.Column(sa.BigInteger, sa.ForeignKey("offerer.id"), nullable=False, index=True)

    managingOfferer: sa_orm.Mapped["Offerer"] = sa_orm.relationship(
        "Offerer", foreign_keys=[managingOffererId], backref="managedVenues"
    )

    bookingEmail = sa.Column(sa.String(120), nullable=True)
    sa.Index("idx_venue_bookingEmail", bookingEmail)

    _address = sa.Column("address", sa.String(200), nullable=True)

    _street = sa.Column("street", sa.Text(), nullable=True)

    postalCode = sa.Column(sa.String(6), nullable=True)

    city = sa.Column(sa.String(50), nullable=True)

    # banId is a unique interoperability key for French addresses registered in the
    # Base Adresse Nationale. See "cle_interop" here:
    # https://doc.adresse.data.gouv.fr/mettre-a-jour-sa-base-adresse-locale/le-format-base-adresse-locale
    banId = sa.Column(sa.Text(), nullable=True)

    timezone: str = sa.Column(
        sa.String(50), nullable=False, default=METROPOLE_TIMEZONE, server_default=METROPOLE_TIMEZONE
    )

    publicName = sa.Column(sa.String(255), nullable=True)
    sa.Index("ix_venue_trgm_unaccent_public_name", sa.func.immutable_unaccent("name"), postgresql_using="gin")

    isVisibleInApp = sa.Column(sa.Boolean, nullable=False, default=True, server_default=sa.sql.expression.true())

    isVirtual: bool = sa.Column(
        sa.Boolean,
        nullable=False,
        default=False,
        server_default=expression.false(),
    )

    isPermanent = sa.Column(sa.Boolean, nullable=False, default=False)

    isOpenToPublic = sa.Column(sa.Boolean, nullable=False, default=False)

    comment = sa.Column(
        sa.TEXT,
        sa.CheckConstraint(
            CONSTRAINT_CHECK_HAS_SIRET_XOR_HAS_COMMENT_XOR_IS_VIRTUAL, name="check_has_siret_xor_comment_xor_isVirtual"
        ),
        nullable=True,
    )

    collectiveOffers: sa_orm.Mapped[list[educational_models.CollectiveOffer]] = sa_orm.relationship(
        "CollectiveOffer", back_populates="venue"
    )

    collectiveOfferTemplates: sa_orm.Mapped[list[educational_models.CollectiveOfferTemplate]] = sa_orm.relationship(
        "CollectiveOfferTemplate", back_populates="venue"
    )

    venueTypeCode: VenueTypeCode = sa.Column(
        sa.Enum(VenueTypeCode, create_constraint=False), nullable=False, default=VenueTypeCode.OTHER
    )

    venueLabelId = sa.Column(sa.Integer, sa.ForeignKey("venue_label.id"), nullable=True)

    venueLabel: sa_orm.Mapped["VenueLabel"] = sa_orm.relationship("VenueLabel", foreign_keys=[venueLabelId])

    dateCreated: datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)

    withdrawalDetails = sa.Column(sa.Text, nullable=True)

    description = sa.Column(sa.Text, nullable=True)

    contact: sa_orm.Mapped["VenueContact | None"] = sa_orm.relationship(
        "VenueContact", back_populates="venue", uselist=False
    )

    # _bannerUrl should provide a safe way to retrieve the banner,
    # whereas bannerMeta should provide extra information that might be
    # helpful like image type, author, etc. that can change over time.
    _bannerUrl = sa.Column(sa.Text, nullable=True, name="bannerUrl")
    googlePlacesInfo: sa_orm.Mapped["GooglePlacesInfo | None"] = sa_orm.relationship(
        "GooglePlacesInfo", back_populates="venue", uselist=False
    )

    _bannerMeta: dict | None = sa.Column(MutableDict.as_mutable(JSONB), nullable=True, name="bannerMeta")

    adageId = sa.Column(sa.Text, nullable=True)
    adageInscriptionDate = sa.Column(sa.DateTime, nullable=True)

    thumb_path_component = "venues"

    criteria: sa_orm.Mapped[list["criteria_models.Criterion"]] = sa_orm.relationship(
        "Criterion", backref=db.backref("venue_criteria", lazy="dynamic"), secondary=VenueCriterion.__table__
    )

    dmsToken: str = sa.Column(sa.Text, nullable=False, unique=True)

    venueEducationalStatusId = sa.Column(sa.BigInteger, sa.ForeignKey("venue_educational_status.id"), nullable=True)
    venueEducationalStatus: sa_orm.Mapped["VenueEducationalStatus"] = sa_orm.relationship(
        "VenueEducationalStatus", back_populates="venues", foreign_keys=[venueEducationalStatusId]
    )

    pricing_point_links: sa_orm.Mapped[list["VenuePricingPointLink"]] = sa_orm.relationship(
        "VenuePricingPointLink",
        back_populates="venue",
        foreign_keys="VenuePricingPointLink.venueId",
        uselist=True,
    )

    collectiveDescription = sa.Column(sa.Text, nullable=True)
    collectiveStudents: list[educational_models.StudentLevels] | None = sa.Column(
        MutableList.as_mutable(sa.dialects.postgresql.ARRAY(sa.Enum(educational_models.StudentLevels))),
        nullable=True,
        server_default="{}",
    )
    collectiveWebsite = sa.Column(sa.Text, nullable=True)
    collectiveDomains: sa_orm.Mapped[list[educational_models.EducationalDomain]] = sa_orm.relationship(
        educational_models.EducationalDomain,
        back_populates="venues",
        secondary=educational_models.EducationalDomainVenue.__table__,
        uselist=True,
    )
    collectiveDmsApplications: sa_orm.Mapped[list[educational_models.CollectiveDmsApplication]] = sa_orm.relationship(
        educational_models.CollectiveDmsApplication,
        backref="venue",
        primaryjoin="foreign(CollectiveDmsApplication.siret) == Venue.siret",
        uselist=True,
    )
    collectiveInterventionArea: list[str] | None = sa.Column(
        MutableList.as_mutable(sa.dialects.postgresql.json.JSONB), nullable=True
    )
    collectiveNetwork: list[str] | None = sa.Column(
        MutableList.as_mutable(sa.dialects.postgresql.json.JSONB), nullable=True
    )
    collectiveAccessInformation = sa.Column(sa.Text, nullable=True)
    collectivePhone = sa.Column(sa.Text, nullable=True)
    collectiveEmail = sa.Column(sa.Text, nullable=True)

    collective_playlists: sa_orm.Mapped[list[educational_models.CollectivePlaylist]] = sa_orm.relationship(
        "CollectivePlaylist", back_populates="venue"
    )

    priceCategoriesLabel: sa_orm.Mapped[list["offers_models.PriceCategoryLabel"]] = sa_orm.relationship(
        "PriceCategoryLabel", back_populates="venue"
    )

    registration: sa_orm.Mapped["VenueRegistration | None"] = sa_orm.relationship(
        "VenueRegistration", back_populates="venue", uselist=False
    )

    bankAccountLinks: sa_orm.Mapped[list["VenueBankAccountLink"]] = sa_orm.relationship(
        "VenueBankAccountLink", back_populates="venue", passive_deletes=True
    )

    accessibilityProvider: sa_orm.Mapped["AccessibilityProvider | None"] = sa_orm.relationship(
        "AccessibilityProvider", back_populates="venue", uselist=False
    )

    adage_addresses: sa_orm.Mapped[list[educational_models.AdageVenueAddress]] = sa_orm.relationship(
        "AdageVenueAddress", back_populates="venue"
    )

    openingHours: sa_orm.Mapped[list["OpeningHours"]] = sa_orm.relationship(
        "OpeningHours", back_populates="venue", passive_deletes=True
    )

    offererAddressId: int = sa.Column(sa.BigInteger, sa.ForeignKey("offerer_address.id"), nullable=True, index=True)
    offererAddress: sa_orm.Mapped["OffererAddress | None"] = sa_orm.relationship(
        "OffererAddress", foreign_keys=[offererAddressId], back_populates="venues"
    )

    headlineOffers: sa_orm.Mapped[list["offers_models.HeadlineOffer"]] = sa_orm.relationship(
        "HeadlineOffer", back_populates="venue"
    )

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
    def street(cls):
        return cls._address

    def _get_type_banner_url(self) -> str | None:
        elligible_banners: tuple[str, ...] = VENUE_TYPE_DEFAULT_BANNERS.get(self.venueTypeCode, tuple())
        try:
            default_banner = elligible_banners[self.id % 2]
        except IndexError:
            return None
        return os.path.join(settings.OBJECT_STORAGE_URL, VENUE_DEFAULTS_DIR, default_banner)

    @hybrid_property
    def bannerUrl(self) -> str | None:
        if self._bannerUrl:
            return self._bannerUrl
        if self.googlePlacesInfo and self.googlePlacesInfo.bannerUrl:
            return self.googlePlacesInfo.bannerUrl
        return self._get_type_banner_url()

    @bannerUrl.setter  # type: ignore[no-redef]
    def bannerUrl(self, value: str | None) -> None:
        self._bannerUrl = value

    @bannerUrl.expression  # type: ignore[no-redef]
    def bannerUrl(cls):
        return cls._bannerUrl

    @hybrid_property
    def bannerMeta(self) -> str | None:
        if self._bannerMeta is not None:
            return self._bannerMeta
        if self.googlePlacesInfo and self.googlePlacesInfo.bannerMeta:
            # Google Places API returns a list of HTML attributions, formatted like this:
            # <a href="https://url-of-contributor">John D.</a>
            # Regex to extract URL and text
            regex = r'<a href="(.*?)">(.*?)</a>'

            # TODO: (lixxday 2024-04-25) handle multiple attributions
            first_attribution = self.googlePlacesInfo.bannerMeta.get("html_attributions")[0]
            match = re.search(regex, first_attribution)
            if match:
                url, credit = match.groups()

                return BannerMetaModel(image_credit=credit, image_credit_url=url, is_from_google=True)
        return None

    @bannerMeta.setter  # type: ignore[no-redef]
    def bannerMeta(self, value: str | None) -> None:
        self._bannerMeta = value

    @bannerMeta.expression  # type: ignore[no-redef]
    def bannerMeta(cls):
        return cls._bannerMeta

    @hybrid_property
    def hasOffers(self) -> bool:
        # Don't use Python properties as high offer count venues will timeout
        import pcapi.core.offers.models as offers_models

        return bool(
            db.session.query(offers_models.Offer)
            .filter(offers_models.Offer.venueId == self.id)
            .limit(1)
            .with_entities(offers_models.Offer.venueId)
            .all()
        )

    @hasOffers.expression  # type: ignore[no-redef]
    def hasOffers(cls) -> Exists:
        import pcapi.core.offers.models as offers_models

        return sa.exists().where(offers_models.Offer.venueId == cls.id)

    @property
    def hasActiveIndividualOffer(self) -> bool:
        import pcapi.core.offers.models as offers_models

        return db.session.query(
            sa.select(1)
            .select_from(offers_models.Offer)
            .join(Venue, offers_models.Offer.venueId == Venue.id)
            .join(offers_models.Stock, offers_models.Stock.offerId == offers_models.Offer.id)
            .where(
                offers_models.Stock.offerId == offers_models.Offer.id,
                offers_models.Stock.isSoftDeleted.is_(False),
                offers_models.Offer.isActive.is_(True),
                Venue.id == self.id,
            )
            .exists()
        ).scalar()

    @property
    def is_eligible_for_search(self) -> bool:
        not_administrative = self.venueTypeCode != VenueTypeCode.ADMINISTRATIVE
        can_be_searched = bool(self.isPermanent)
        if FeatureToggle.WIP_IS_OPEN_TO_PUBLIC.is_active():
            can_be_searched = bool(self.isOpenToPublic)
        return (
            can_be_searched
            and self.managingOfferer.isActive
            and self.managingOfferer.isValidated
            and self.hasOffers
            and not_administrative
        )

    def store_departement_code(self) -> None:
        if not self.postalCode:
            return
        self.departementCode = postal_code_utils.PostalCode(self.postalCode).get_departement_code()

    def store_timezone(self) -> None:
        self.timezone = (
            get_department_timezone(self.departementCode)
            if self.departementCode
            else get_postal_code_timezone(self.managingOfferer.postalCode)
        )

    @property
    def last_collective_dms_application(self) -> educational_models.CollectiveDmsApplication | None:
        if self.collectiveDmsApplications:
            return sorted(
                self.collectiveDmsApplications, key=lambda application: application.lastChangeDate, reverse=True
            )[0]
        return None

    @hybrid_property
    def dms_adage_status(self) -> str | None:
        return self.last_collective_dms_application.state if self.last_collective_dms_application else None

    @dms_adage_status.expression  # type: ignore[no-redef]
    def dms_adage_status(cls) -> str | None:
        return (
            db.session.query(educational_models.CollectiveDmsApplication.state)
            .select_from(educational_models.CollectiveDmsApplication)
            .filter(educational_models.CollectiveDmsApplication.siret == cls.siret)
            .order_by(educational_models.CollectiveDmsApplication.lastChangeDate.desc())
            .limit(1)
            .scalar_subquery()
        )

    @property
    def hasPendingBankAccountApplication(self) -> bool:
        if not self.current_bank_account:
            return False
        return self.current_bank_account.status == finance_models.BankAccountApplicationStatus.DRAFT

    @property
    def hasAcceptedBankAccountApplication(self) -> bool:
        if not self.current_bank_account:
            return False
        return self.current_bank_account.status == finance_models.BankAccountApplicationStatus.ACCEPTED

    @property
    def has_individual_offers(self) -> bool:
        from pcapi.core.offers.models import Offer

        return db.session.query(db.session.query(Offer).filter(Offer.venueId == self.id).exists()).scalar()

    @property
    def has_collective_offers(self) -> bool:
        from pcapi.core.educational.models import CollectiveOffer

        return db.session.query(
            db.session.query(CollectiveOffer).filter(CollectiveOffer.venueId == self.id).exists()
        ).scalar()

    @property
    def has_approved_offers(self) -> bool:
        """Better performance than nApprovedOffers when we only want to check if there is at least one offer"""
        from pcapi.core.educational.models import CollectiveOffer
        from pcapi.core.offers.models import Offer
        from pcapi.core.offers.models import OfferValidationStatus

        query_offer = db.session.query(
            db.session.query(Offer)
            .filter(Offer.validation == OfferValidationStatus.APPROVED, Offer.venueId == self.id)
            .exists()
        )
        query_collective = db.session.query(
            db.session.query(CollectiveOffer)
            .filter(CollectiveOffer.validation == OfferValidationStatus.APPROVED, CollectiveOffer.venueId == self.id)
            .exists()
        )
        results = query_offer.union(query_collective).all()

        return any(result for (result,) in results)

    @property
    def nApprovedOffers(self) -> int:  # used in validation rule, do not remove
        from pcapi.core.educational.models import CollectiveOffer
        from pcapi.core.offers.models import Offer
        from pcapi.core.offers.models import OfferValidationStatus

        query_offer = db.session.query(sa_func.count(Offer.id)).filter(
            Offer.validation == OfferValidationStatus.APPROVED, Offer.venueId == self.id
        )
        query_collective = db.session.query(sa_func.count(CollectiveOffer.id)).filter(
            CollectiveOffer.validation == OfferValidationStatus.APPROVED, CollectiveOffer.venueId == self.id
        )
        results = query_offer.union(query_collective).all()

        return sum(result for (result,) in results)

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

    def field_exists_and_has_changed(self, field: str, value: typing.Any) -> typing.Any:
        if field not in type(self).__table__.columns:
            raise ValueError(f"Unknown field {field} for model {type(self)}")
        if isinstance(getattr(self, field), decimal.Decimal):
            return str(getattr(self, field)) != value
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
    def current_pricing_point_link(self) -> "VenuePricingPointLink | None":
        # Unlike current_pricing_point_id, this property uses pricing_point_links joinedloaded with the venue, which
        # avoids additional SQL query
        now = datetime.utcnow()

        for link in self.pricing_point_links:
            lower = link.timespan.lower
            upper = link.timespan.upper

            if lower <= now and (not upper or now <= upper):
                return link

        return None

    @property
    def current_pricing_point(self) -> "Venue | None":
        # Unlike current_pricing_point_id, this property uses pricing_point_links joinedloaded with the venue, which
        # avoids additional SQL query
        link = self.current_pricing_point_link
        return link.pricingPoint if link else None

    @property
    def current_bank_account_link(self) -> "VenueBankAccountLink | None":
        now = datetime.utcnow()

        for link in self.bankAccountLinks:
            lower = link.timespan.lower
            upper = link.timespan.upper

            if lower <= now and (not upper or now <= upper):
                return link

        return None

    @property
    def current_bank_account(self) -> "finance_models.BankAccount | None":
        if self.current_bank_account_link:
            return self.current_bank_account_link.bankAccount
        return None

    @hybrid_property
    def common_name(self) -> str:
        return self.publicName or self.name

    @common_name.expression  # type: ignore[no-redef]
    def common_name(cls) -> str:
        return sa_func.coalesce(sa.func.nullif(cls.publicName, ""), cls.name)

    @property
    def web_presence(self) -> str | None:
        return self.registration.webPresence if self.registration else None

    @property
    def target(self) -> Target | None:
        return self.registration.target if self.registration else None

    @property
    def opening_hours(self) -> dict | None:
        if not self.openingHours:
            return None

        opening_hours = {}
        for daily_opening_hours in self.openingHours:
            if not daily_opening_hours.timespan:
                timespan_list = None
            else:
                timespan_str = numranges_to_timespan_str(sorted(daily_opening_hours.timespan, key=lambda x: x.lower))
                timespan_list = [{"open": start, "close": end} for start, end in timespan_str]
            opening_hours[daily_opening_hours.weekday.value] = timespan_list

        return opening_hours

    @property
    def external_accessibility_id(self) -> str | None:
        if not self.accessibilityProvider:
            return None
        return self.accessibilityProvider.externalAccessibilityId

    @property
    def external_accessibility_url(self) -> str | None:
        if not self.accessibilityProvider:
            return None
        return self.accessibilityProvider.externalAccessibilityUrl

    @property
    def confidenceLevel(self) -> "OffererConfidenceLevel | None":
        if not self.confidenceRule:
            return None
        return self.confidenceRule.confidenceLevel

    __table_args__ = (
        sa.CheckConstraint(
            '("isVirtual" IS FALSE AND "offererAddressId" IS NOT NULL) OR "isVirtual" IS TRUE',
            name="check_physical_venue_has_offerer_address",
        ),
    )

    @property
    def ridet(self) -> str | None:
        if self.siret and siren_utils.is_ridet(self.siret):
            return siren_utils.siret_to_ridet(self.siret)
        return None

    @property
    def identifier_name(self) -> str:
        return "RIDET" if siren_utils.is_ridet(self.siret) else "SIRET"

    @property
    def identifier(self) -> str | None:
        return self.ridet or self.siret

    @property
    def is_caledonian(self) -> bool:
        return self.managingOfferer.is_caledonian

    @property
    def has_headline_offer(self) -> bool:
        return any(headline_offer.isActive for headline_offer in self.headlineOffers)

    _has_partner_page: sa_orm.Mapped["bool|None"] = sa_orm.query_expression()

    @hybrid_property
    def has_partner_page(self) -> bool:
        from pcapi.core.offers.models import Offer

        return db.session.query(
            sa.select(1)
            .select_from(Offer)
            .join(Venue, Offer.venueId == Venue.id)
            .join(Offerer, Offerer.id == Venue.managingOffererId)
            .where(
                Offerer.isActive.is_(True),
                Venue.isPermanent.is_(True),
                Venue.isVirtual.is_(False),
                Venue.id == self.id,
            )
            .exists()
        ).scalar()

    @has_partner_page.expression  # type: ignore[no-redef]
    def has_partner_page(cls):
        from pcapi.core.offers.models import Offer

        AliasedVenue = sa_orm.aliased(Venue)
        return (
            sa.select(1)
            .select_from(Offer)
            .join(AliasedVenue, Offer.venueId == AliasedVenue.id)
            .join(Offerer, Offerer.id == AliasedVenue.managingOffererId)
            .where(
                Offerer.isActive.is_(True),
                AliasedVenue.isPermanent.is_(True),
                AliasedVenue.isVirtual.is_(False),
                AliasedVenue.id == cls.id,
            )
            .exists()
        )


class GooglePlacesInfo(PcObject, Base, Model):
    __tablename__ = "google_places_info"
    venueId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("venue.id", ondelete="CASCADE"), nullable=False, index=True, unique=True
    )
    venue: sa_orm.Mapped[Venue] = sa_orm.relationship(
        "Venue", foreign_keys=[venueId], back_populates="googlePlacesInfo"
    )
    # Some venues are duplicated in our database. They are all linked to the same item on
    # Google Places, so this column cannot be unique.
    placeId: str | None = sa.Column(sa.Text, nullable=True, unique=False)
    bannerUrl: str | None = sa.Column(sa.Text, nullable=True, name="bannerUrl")
    bannerMeta: dict | None = sa.Column(MutableDict.as_mutable(JSONB), nullable=True)
    updateDate: datetime = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now())


class AccessibilityProvider(PcObject, Base, Model):
    venueId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("venue.id", ondelete="CASCADE"), index=True, nullable=False, unique=True
    )
    venue: sa_orm.Mapped[Venue] = sa_orm.relationship(
        "Venue", foreign_keys=[venueId], back_populates="accessibilityProvider"
    )
    externalAccessibilityId: str = sa.Column(sa.Text, nullable=False)
    externalAccessibilityUrl: str = sa.Column(sa.Text, nullable=False)
    externalAccessibilityData: AccessibilityInfo | None = sa.Column(MutableDict.as_mutable(JSONB), nullable=True)
    lastUpdateAtProvider: datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)


class OpeningHours(PcObject, Base, Model):
    __tablename__ = "opening_hours"
    venueId: int = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id", ondelete="CASCADE"), nullable=False, index=True)
    venue: sa_orm.Mapped[Venue] = sa_orm.relationship("Venue", foreign_keys=[venueId], back_populates="openingHours")
    weekday: Weekday = sa.Column(db_utils.MagicEnum(Weekday), nullable=False, default=Weekday.MONDAY)
    timespan: list[psycopg2.extras.NumericRange] = sa.Column(sa_psql.ARRAY(sa_psql.ranges.NUMRANGE), nullable=True)

    __table_args__ = ((sa.CheckConstraint(sa.func.cardinality(timespan) <= 2, name="max_timespan_is_2")),)

    def field_exists_and_has_changed(self, field: str, value: typing.Any) -> typing.Any:
        if field not in type(self).__table__.columns:
            raise ValueError(f"Unknown field {field} for model {type(self)}")
        return getattr(self, field) != value


class VenueLabel(PcObject, Base, Model):
    __tablename__ = "venue_label"
    id: sa_orm.Mapped[int] = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    label: str = sa.Column(sa.String(100), nullable=False)


class VenueContact(PcObject, Base, Model):
    __tablename__ = "venue_contact"

    venueId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("venue.id", ondelete="CASCADE"), nullable=False, index=True, unique=True
    )

    venue: sa_orm.Mapped[Venue] = sa_orm.relationship("Venue", foreign_keys=[venueId], back_populates="contact")

    email = sa.Column(sa.String(256), nullable=True)

    website = sa.Column(sa.String(256), nullable=True)

    phone_number = sa.Column(sa.String(64), nullable=True)

    social_medias: dict = sa.Column(MutableDict.as_mutable(JSONB), nullable=False, default={}, server_default="{}")

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


class VenuePricingPointLink(Base, Model):
    """At any given time, the bookings of a venue are priced against a
    particular venue that we call the "pricing point" of the venue.
    There should only ever be one pricing point for each venue, but
    for flexibility's sake we store the link in a table with the
    period during which this link is active.
    """

    id: int = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    venueId: int = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id"), index=True, nullable=False)
    venue: sa_orm.Mapped[Venue] = sa_orm.relationship(
        Venue, foreign_keys=[venueId], back_populates="pricing_point_links"
    )
    pricingPointId: int = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id"), index=True, nullable=False)
    pricingPoint: sa_orm.Mapped[Venue] = sa_orm.relationship(Venue, foreign_keys=[pricingPointId])
    # The lower bound is inclusive and required. The upper bound is
    # exclusive and optional. If there is no upper bound, it means
    # that the venue is still linked to the pricing point. For links
    # that existed before this table was introduced, the lower bound
    # is set to the Epoch.
    timespan: psycopg2.extras.DateTimeRange = sa.Column(sa_psql.TSRANGE, nullable=False)

    __table_args__ = (
        # A venue cannot be linked to multiple pricing points at the
        # same time.
        sa_psql.ExcludeConstraint(("venueId", "="), ("timespan", "&&")),
    )

    def __init__(self, **kwargs: typing.Any) -> None:
        kwargs["timespan"] = db_utils.make_timerange(*kwargs["timespan"])
        super().__init__(**kwargs)


class VenueBankAccountLink(PcObject, Base, Model):
    """
    Professional users can link as many venues as they want to a given bank account.
    However, we want to keep tracks of the history, hence that table.
    """

    venueId: int = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id", ondelete="CASCADE"), index=True, nullable=False)
    venue: sa_orm.Mapped[Venue] = sa_orm.relationship(
        "Venue", foreign_keys=[venueId], back_populates="bankAccountLinks"
    )

    bankAccountId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("bank_account.id", ondelete="CASCADE"), index=True, nullable=False
    )
    bankAccount: sa_orm.Mapped[finance_models.BankAccount] = sa_orm.relationship(
        "BankAccount", foreign_keys=[bankAccountId], back_populates="venueLinks"
    )

    timespan: psycopg2.extras.DateTimeRange = sa.Column(sa_psql.TSRANGE, nullable=False)

    __table_args__ = (
        # For a given venue, there can only be one bank account at a time.
        sa_psql.ExcludeConstraint(("venueId", "="), ("timespan", "&&")),
    )

    def __init__(self, **kwargs: typing.Any) -> None:
        kwargs["timespan"] = db_utils.make_timerange(*kwargs["timespan"])
        super().__init__(**kwargs)


class VenueEducationalStatus(Base, Model):
    __tablename__ = "venue_educational_status"
    id: int = sa.Column(sa.BigInteger, primary_key=True, autoincrement=False, nullable=False)
    name: str = sa.Column(sa.String(256), nullable=False)
    venues: sa_orm.Mapped[list[Venue]] = sa_orm.relationship(
        Venue, back_populates="venueEducationalStatus", uselist=True
    )


class VenueRegistration(PcObject, Base, Model):
    __tablename__ = "venue_registration"

    id: int = sa.Column("id", sa.BigInteger, sa.Identity(), primary_key=True)

    venueId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("venue.id", ondelete="CASCADE"), nullable=False, index=True, unique=True
    )

    venue: sa_orm.Mapped[Venue] = sa_orm.relationship("Venue", foreign_keys=[venueId], back_populates="registration")

    target: Target = sa.Column(db_utils.MagicEnum(Target), nullable=False)

    webPresence: str | None = sa.Column(sa.Text, nullable=True)


class OffererTagMapping(PcObject, Base, Model):
    __tablename__ = "offerer_tag_mapping"

    offererId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("offerer.id", ondelete="CASCADE"), index=True, nullable=False
    )
    tagId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("offerer_tag.id", ondelete="CASCADE"), index=True, nullable=False
    )

    __table_args__ = (sa.UniqueConstraint("offererId", "tagId", name="unique_offerer_tag"),)


class Offerer(
    PcObject,
    Base,
    Model,
    HasAddressMixin,
    ValidationStatusMixin,
    DeactivableMixin,
):
    dateCreated: datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)

    name: str = sa.Column(sa.String(140), nullable=False)
    sa.Index("ix_offerer_trgm_unaccent_name", sa.func.immutable_unaccent("name"), postgresql_using="gin")

    sa.Index("ix_offerer_trgm_unaccent_city", sa.func.immutable_unaccent("city"), postgresql_using="gin")

    UserOfferers: sa_orm.Mapped[list["UserOfferer"]] = sa_orm.relationship(
        "UserOfferer", order_by="UserOfferer.id", back_populates="offerer"
    )

    siren = sa.Column(
        sa.String(9), nullable=True, unique=True
    )  # FIXME: should not be nullable, is until we have all SIRENs filled in the DB

    dateValidated = sa.Column(sa.DateTime, nullable=True, default=None)

    tags: sa_orm.Mapped[list["OffererTag"]] = sa_orm.relationship("OffererTag", secondary=OffererTagMapping.__table__)

    # use an expression instead of joinedload(tags) to avoid multiple SQL rows returned
    isTopActeur: sa_orm.Mapped["bool"] = sa_orm.query_expression()

    @hybrid_property
    def is_top_acteur(self) -> bool:
        return any(tag.name == "top-acteur" for tag in self.tags)

    @is_top_acteur.expression  # type: ignore[no-redef]
    def is_top_acteur(cls) -> sa.sql.elements.BooleanClauseList:
        return (
            sa.select(1)
            .select_from(OffererTagMapping)
            .join(OffererTag, OffererTag.id == OffererTagMapping.tagId)
            .where(OffererTagMapping.offererId == cls.id, OffererTag.name == "top-acteur")
            .limit(1)
            .exists()
        )

    offererProviders: sa_orm.Mapped[list["OffererProvider"]] = sa_orm.relationship(
        "OffererProvider", back_populates="offerer"
    )
    thumb_path_component = "offerers"

    bankAccounts: sa_orm.Mapped[list[finance_models.BankAccount]] = sa_orm.relationship(
        finance_models.BankAccount,
        back_populates="offerer",
        passive_deletes=True,
    )

    individualSubscription: sa_orm.Mapped["IndividualOffererSubscription | None"] = sa_orm.relationship(
        "IndividualOffererSubscription", back_populates="offerer", uselist=False
    )

    allowedOnAdage: bool = sa.Column(
        sa.Boolean, nullable=False, default=False, server_default=sa.sql.expression.false()
    )

    _street = sa.Column("street", sa.Text(), nullable=True)

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
    def street(cls):
        return cls._address

    @hybrid_property
    def departementCode(self) -> str:
        return postal_code_utils.PostalCode(self.postalCode).get_departement_code()

    @departementCode.expression  # type: ignore[no-redef]
    def departementCode(cls) -> Case:
        return sa.func.postal_code_to_department_code(cls.postalCode)

    @hybrid_property
    def rid7(self) -> str | None:
        if self.siren and siren_utils.is_rid7(self.siren):
            return siren_utils.siren_to_rid7(self.siren)
        return None

    @rid7.expression  # type: ignore[no-redef]
    def rid7(cls) -> Case:
        return sa.case(
            (cls.siren.ilike(f"{siren_utils.NEW_CALEDONIA_SIREN_PREFIX}%"), sa.func.substring(cls.siren, 3, 7)),
            else_=None,
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
    def is_caledonian(cls) -> BinaryExpression:
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
    userId: int = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), primary_key=True)
    user: sa_orm.Mapped["users_models.User"] = sa_orm.relationship(
        "User", foreign_keys=[userId], back_populates="UserOfferers"
    )
    offererId: int = sa.Column(sa.BigInteger, sa.ForeignKey("offerer.id"), index=True, primary_key=True, nullable=False)
    offerer: sa_orm.Mapped[Offerer] = sa_orm.relationship(
        Offerer, foreign_keys=[offererId], back_populates="UserOfferers"
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "userId",
            "offererId",
            name="unique_user_offerer",
        ),
    )

    # dateCreated will remain null for all rows already in this table before this field was added
    dateCreated: datetime = sa.Column(sa.DateTime, nullable=True, default=datetime.utcnow)


class ApiKey(PcObject, Base, Model):
    offererId: int = sa.Column(sa.BigInteger, sa.ForeignKey("offerer.id"), index=True, nullable=False)
    offerer: sa_orm.Mapped[Offerer] = sa_orm.relationship("Offerer", foreign_keys=[offererId], backref="apiKeys")
    providerId: int = sa.Column(sa.BigInteger, sa.ForeignKey("provider.id", ondelete="CASCADE"), index=True)
    provider: sa_orm.Mapped["providers_models.Provider"] = sa_orm.relationship(
        "Provider", foreign_keys=[providerId], back_populates="apiKeys"
    )
    dateCreated: datetime = sa.Column(
        sa.DateTime, nullable=False, default=datetime.utcnow, server_default=sa.func.now()
    )
    prefix = sa.Column(sa.Text, nullable=True, unique=True)
    secret: bytes = sa.Column(LargeBinary, nullable=True)

    def check_secret(self, clear_text: str) -> bool:
        if settings.USE_FAST_AND_INSECURE_PASSWORD_HASHING_ALGORITHM and crypto.check_password(clear_text, self.secret):
            return True
        if self.secret.decode("utf-8").startswith("$sha3_512$"):
            return crypto.check_public_api_key(clear_text, self.secret)
        if crypto.check_password(clear_text, self.secret):
            self.secret = crypto.hash_public_api_key(clear_text)
            db.session.commit()
            logger.info("Switched hash of API key from bcrypt to SHA3-512", extra={"key_id": self.id})
            return True
        return False


class OffererTagCategoryMapping(PcObject, Base, Model):
    __tablename__ = "offerer_tag_category_mapping"

    tagId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("offerer_tag.id", ondelete="CASCADE"), index=True, nullable=False
    )
    categoryId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("offerer_tag_category.id", ondelete="CASCADE"), index=True, nullable=False
    )

    __table_args__ = (sa.UniqueConstraint("tagId", "categoryId", name="unique_offerer_tag_category"),)


class OffererTag(PcObject, Base, Model):
    """
    Tags on offerers are only used in backoffice, set to help for filtering and analytics in metabase.
    There is currently no display or impact in mobile and web apps.
    """

    __tablename__ = "offerer_tag"

    name: str = sa.Column(sa.String(140), nullable=False, unique=True)
    label: str = sa.Column(sa.String(140))
    description: str = sa.Column(sa.Text)

    categories: sa_orm.Mapped[list["OffererTagCategory"]] = sa_orm.relationship(
        "OffererTagCategory", secondary=OffererTagCategoryMapping.__table__
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

    name: str = sa.Column(sa.String(140), nullable=False, unique=True)
    label: str = sa.Column(sa.String(140))

    def __str__(self) -> str:
        return self.label or self.name


class OffererProvider(PcObject, Base, Model):
    __tablename__ = "offerer_provider"
    offererId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("offerer.id", ondelete="CASCADE"), index=True, nullable=False
    )
    offerer: sa_orm.Mapped[Offerer] = sa_orm.relationship(
        "Offerer", foreign_keys=[offererId], back_populates="offererProviders"
    )
    providerId: int = sa.Column(sa.BigInteger, sa.ForeignKey("provider.id"), index=True, nullable=False)
    provider: sa_orm.Mapped["providers_models.Provider"] = sa_orm.relationship(
        "Provider", foreign_keys=[providerId], back_populates="offererProvider"
    )

    __table_args__ = (sa.UniqueConstraint("offererId", "providerId", name="unique_offerer_provider"),)


class OffererInvitation(PcObject, Base, Model):
    __tablename__ = "offerer_invitation"
    offererId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("offerer.id", ondelete="CASCADE"), index=True, nullable=False
    )
    offerer: sa_orm.Mapped[Offerer] = sa_orm.relationship("Offerer", foreign_keys=[offererId])
    email: str = sa.Column(sa.Text, nullable=False)
    dateCreated: datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)
    userId: int = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), nullable=False, index=True)
    user: sa_orm.Mapped["users_models.User"] = sa_orm.relationship(
        "User", foreign_keys=[userId], backref="OffererInvitations"
    )
    status: InvitationStatus = sa.Column(db_utils.MagicEnum(InvitationStatus), nullable=False)

    __table_args__ = (sa.UniqueConstraint("offererId", "email", name="unique_offerer_invitation"),)


class IndividualOffererSubscription(PcObject, Base, Model):
    __tablename__ = "individual_offerer_subscription"

    offererId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("offerer.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    offerer: sa_orm.Mapped[Offerer] = sa_orm.relationship(
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
    def isReminderEmailSent(cls) -> sa.Boolean:
        return cls.dateReminderEmailSent.is_not(sa.null())


class OffererStatsData(typing.TypedDict, total=False):
    daily_views: list[OffererViewsModel]
    top_offers: list[TopOffersData]
    total_views_last_30_days: int


class OffererStats(PcObject, Base, Model):
    __tablename__ = "offerer_stats"

    offererId: int = sa.Column(sa.BigInteger, sa.ForeignKey("offerer.id", ondelete="CASCADE"), nullable=False)
    sa.Index("ix_offerer_stats_offererId", offererId)
    offerer: sa_orm.Mapped[Offerer] = sa_orm.relationship("Offerer", foreign_keys=[offererId])

    syncDate: datetime = sa.Column(sa.DateTime, nullable=False)
    table: str = sa.Column(sa.String(120), nullable=False)
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
    addressId: sa_orm.Mapped[int] = sa.Column(sa.BigInteger, sa.ForeignKey("address.id"), index=True, nullable=False)
    address: sa_orm.Mapped[geography_models.Address] = sa_orm.relationship("Address", foreign_keys=[addressId])
    offererId: sa_orm.Mapped[int] = sa.Column(
        sa.BigInteger, sa.ForeignKey("offerer.id", ondelete="CASCADE"), index=True, nullable=False
    )
    offerer: sa_orm.Mapped["Offerer"] = sa_orm.relationship("Offerer", foreign_keys=[offererId])
    venues: sa_orm.Mapped[list["Venue"]] = sa_orm.relationship("Venue", back_populates="offererAddress")

    __table_args__ = (sa.Index("ix_unique_offerer_address_per_label", "offererId", "addressId", "label", unique=True),)

    _isLinkedToVenue: sa_orm.Mapped["bool|None"] = sa_orm.query_expression()

    @hybrid_property
    def isLinkedToVenue(self) -> bool:
        return db.session.query(sa.select(1).exists().where(Venue.offererAddressId == self.id)).scalar()

    @isLinkedToVenue.expression  # type: ignore[no-redef]
    def isLinkedToVenue(cls) -> sa.sql.elements.BooleanClauseList:
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
