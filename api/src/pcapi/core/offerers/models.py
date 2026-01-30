import decimal
import enum
import logging
import os
import re
import typing
from datetime import date
from datetime import datetime

import psycopg2.extras
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as sa_psql
import sqlalchemy.orm as sa_orm
import sqlalchemy.sql.functions as sa_func
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.ext import mutable as sa_mutable
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.sql import expression
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.sql.elements import Case
from sqlalchemy.sql.selectable import Exists
from sqlalchemy.sql.selectable import ScalarSelect
from sqlalchemy.sql.sqltypes import LargeBinary

import pcapi.core.finance.models as finance_models
import pcapi.utils.db as db_utils
from pcapi import settings
from pcapi.connectors.big_query.queries.offerer_stats import OffererViewsModel
from pcapi.connectors.big_query.queries.offerer_stats import TopOffersData
from pcapi.core.criteria.models import VenueCriterion
from pcapi.core.educational import models as educational_models
from pcapi.core.geography import models as geography_models
from pcapi.core.history.constants import ACTION_HISTORY_ORDER_BY
from pcapi.core.offerers import constants
from pcapi.core.offerers.schemas import BannerMetaModel
from pcapi.core.offerers.schemas import VenueImageCredit
from pcapi.core.offerers.schemas import VenueTypeCode
from pcapi.models import Model
from pcapi.models import db
from pcapi.models.accessibility_mixin import AccessibilityMixin
from pcapi.models.deactivable_mixin import DeactivableMixin
from pcapi.models.has_thumb_mixin import HasThumbMixin
from pcapi.models.pc_object import PcObject
from pcapi.models.soft_deletable_mixin import SoftDeletableMixin
from pcapi.models.validation_status_mixin import ValidationStatusMixin
from pcapi.utils import crypto
from pcapi.utils import date as date_utils
from pcapi.utils import siren as siren_utils
from pcapi.utils.date import numranges_to_timespan_str
from pcapi.utils.human_ids import humanize
from pcapi.utils.regions import NEW_CALEDONIA_DEPARTMENT_CODE


if typing.TYPE_CHECKING:
    import pcapi.core.bookings.models as bookings_models
    import pcapi.core.criteria.models as criteria_models
    import pcapi.core.history.models as history_models
    import pcapi.core.offers.models as offers_models
    import pcapi.core.providers.models as providers_models
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

VENUE_DEFAULTS_DIR = "assets/venue_default_images"
VENUE_TYPE_DEFAULT_BANNERS: dict[VenueTypeCode, tuple[str, ...]] = {
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
    NON_RECEIVED_DOCS = "NON_RECEIVED_DOCS"
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


class Activity(enum.Enum):
    """
    Venue's Activity is the main business activity of an ERP (open to public) structure
    For a non-ERP structure, the business is described through the Venue's list of EducationalDomain (venue.collectiveDomains)
    """

    ART_GALLERY = "ART_GALLERY"
    ART_SCHOOL = "ART_SCHOOL"
    ARTISTIC_COMPANY = "ARTISTIC_COMPANY"
    ARTS_CENTRE = "ARTS_CENTRE"
    ARTS_EDUCATION = "ARTS_EDUCATION"
    BOOKSTORE = "BOOKSTORE"
    CINEMA = "CINEMA"
    COMMUNITY_CENTRE = "COMMUNITY_CENTRE"
    CREATIVE_ARTS_STORE = "CREATIVE_ARTS_STORE"
    CULTURAL_CENTRE = "CULTURAL_CENTRE"
    CULTURAL_MEDIATION = "CULTURAL_MEDIATION"
    DISTRIBUTION_STORE = "DISTRIBUTION_STORE"
    FESTIVAL = "FESTIVAL"
    # 'GAMES_CENTRE' is used for archived structures and should not be available for cultural partners during onboarding
    GAMES_CENTRE = "GAMES_CENTRE"
    HERITAGE_SITE = "HERITAGE_SITE"
    LIBRARY = "LIBRARY"
    MUSEUM = "MUSEUM"
    MUSIC_INSTRUMENT_STORE = "MUSIC_INSTRUMENT_STORE"
    # TODO: (lmaubert 2026-01): Remove 'NOT_ASSIGNED' that was used for non-ERP structures (is_open_to_public=False) in a previous version
    NOT_ASSIGNED = "NOT_ASSIGNED"
    # TODO (lmaubert 2025-10): Remove 'OTHER' when not necessary anymore (temporary value to measure the adequacy of the new list of main activities)
    OTHER = "OTHER"
    PERFORMANCE_HALL = "PERFORMANCE_HALL"
    PRESS = "PRESS"
    PRODUCTION_OR_PROMOTION_COMPANY = "PRODUCTION_OR_PROMOTION_COMPANY"
    RECORD_STORE = "RECORD_STORE"
    SCIENCE_CENTRE = "SCIENCE_CENTRE"
    STREAMING_PLATFORM = "STREAMING_PLATFORM"
    TOURIST_INFORMATION_CENTRE = "TOURIST_INFORMATION_CENTRE"
    TRAVELLING_CINEMA = "TRAVELLING_CINEMA"


ActivityOpenToPublic: enum.EnumType = enum.Enum(  # type: ignore[misc]
    "ActivityOpenToPublic",
    {
        x.name: x.value
        for x in Activity
        if x.name
        in (
            "ART_GALLERY",
            "ART_SCHOOL",
            "ARTS_CENTRE",
            "BOOKSTORE",
            "CINEMA",
            "COMMUNITY_CENTRE",
            "CREATIVE_ARTS_STORE",
            "CULTURAL_CENTRE",
            "DISTRIBUTION_STORE",
            "FESTIVAL",
            "HERITAGE_SITE",
            "LIBRARY",
            "MUSEUM",
            "MUSIC_INSTRUMENT_STORE",
            "OTHER",
            "PERFORMANCE_HALL",
            "RECORD_STORE",
            "SCIENCE_CENTRE",
            "TOURIST_INFORMATION_CENTRE",
        )
    },
)


ActivityNotOpenToPublic: enum.EnumType = enum.Enum(  # type: ignore[misc]
    "ActivityNotOpenToPublic",
    {
        x.name: x.value
        for x in Activity
        if x.name
        in (
            "ARTISTIC_COMPANY",
            "ARTS_EDUCATION",
            "CULTURAL_MEDIATION",
            "FESTIVAL",
            "OTHER",
            "PRESS",
            "PRODUCTION_OR_PROMOTION_COMPANY",
            "STREAMING_PLATFORM",
            "TRAVELLING_CINEMA",
        )
    },
)


DisplayableActivity: enum.EnumType = enum.Enum(  # type: ignore[misc]
    "DisplayableActivity", {x.name: x.value for x in Activity if x.name != "NOT_ASSIGNED"}
)


class Venue(PcObject, Model, HasThumbMixin, AccessibilityMixin, SoftDeletableMixin):
    __tablename__ = "venue"
    thumb_path_component = "venues"

    name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(140), nullable=False)

    siret: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.String(14), nullable=True, unique=True)

    venueProviders: sa_orm.Mapped[list["providers_models.VenueProvider"]] = sa_orm.relationship(
        "VenueProvider", foreign_keys="VenueProvider.venueId", back_populates="venue"
    )

    managingOffererId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offerer.id"), nullable=False, index=True
    )
    managingOfferer: sa_orm.Mapped["Offerer"] = sa_orm.relationship(
        "Offerer", foreign_keys=[managingOffererId], back_populates="managedVenues"
    )

    bookingEmail: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.String(120), nullable=True)

    publicName: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(255), nullable=False)

    isVirtual: sa_orm.Mapped[bool] = sa_orm.mapped_column(
        sa.Boolean,
        nullable=False,
        default=False,
        server_default=expression.false(),
    )

    isPermanent: sa_orm.Mapped[bool] = sa_orm.mapped_column(sa.Boolean, nullable=False, default=False)

    isOpenToPublic: sa_orm.Mapped[bool] = sa_orm.mapped_column(sa.Boolean, nullable=False, default=False)

    comment: sa_orm.Mapped[str | None] = sa_orm.mapped_column(
        sa.TEXT,
        nullable=True,
    )

    collectiveOffers: sa_orm.Mapped[list[educational_models.CollectiveOffer]] = sa_orm.relationship(
        "CollectiveOffer", foreign_keys="CollectiveOffer.venueId", back_populates="venue"
    )

    collectiveBookings: sa_orm.Mapped[list[educational_models.CollectiveBooking]] = sa_orm.relationship(
        "CollectiveBooking", foreign_keys="CollectiveBooking.venueId", back_populates="venue"
    )

    collectiveOfferTemplates: sa_orm.Mapped[list[educational_models.CollectiveOfferTemplate]] = sa_orm.relationship(
        "CollectiveOfferTemplate", foreign_keys="CollectiveOfferTemplate.venueId", back_populates="venue"
    )

    venueTypeCode: sa_orm.Mapped[VenueTypeCode] = sa_orm.mapped_column(
        sa.Enum(VenueTypeCode, create_constraint=False), index=True, nullable=False, default=VenueTypeCode.OTHER
    )

    venueLabelId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("venue_label.id"), nullable=True
    )
    venueLabel: sa_orm.Mapped["VenueLabel"] = sa_orm.relationship("VenueLabel", foreign_keys=[venueLabelId])

    dateCreated: sa_orm.Mapped[datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, default=date_utils.get_naive_utc_now
    )

    withdrawalDetails: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)

    description: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)

    contact: sa_orm.Mapped["VenueContact | None"] = sa_orm.relationship(
        "VenueContact", foreign_keys="VenueContact.venueId", back_populates="venue", uselist=False
    )

    # _bannerUrl should provide a safe way to retrieve the banner,
    # whereas bannerMeta should provide extra information that might be
    # helpful like image type, author, etc. that can change over time.
    _bannerUrl: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True, name="bannerUrl")
    googlePlacesInfo: sa_orm.Mapped["GooglePlacesInfo | None"] = sa_orm.relationship(
        "GooglePlacesInfo", foreign_keys="GooglePlacesInfo.venueId", back_populates="venue", uselist=False
    )

    _bannerMeta: sa_orm.Mapped[dict | None] = sa_orm.mapped_column(
        MutableDict.as_mutable(JSONB), nullable=True, name="bannerMeta"
    )

    adageId: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)
    adageInscriptionDate: sa_orm.Mapped[datetime | None] = sa_orm.mapped_column(sa.DateTime, nullable=True)

    criteria: sa_orm.Mapped[list["criteria_models.Criterion"]] = sa_orm.relationship(
        "Criterion", back_populates="venue_criteria", secondary=VenueCriterion.__table__
    )

    dmsToken: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False, unique=True)

    venueEducationalStatusId = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("venue_educational_status.id"), nullable=True
    )
    venueEducationalStatus: sa_orm.Mapped["VenueEducationalStatus"] = sa_orm.relationship(
        "VenueEducationalStatus", back_populates="venues", foreign_keys=[venueEducationalStatusId]
    )

    pricing_point_links: sa_orm.Mapped[list["VenuePricingPointLink"]] = sa_orm.relationship(
        "VenuePricingPointLink",
        back_populates="venue",
        foreign_keys="VenuePricingPointLink.venueId",
        uselist=True,
    )

    collectiveDescription: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)
    collectiveStudents: sa_orm.Mapped[list[educational_models.StudentLevels] | None] = sa_orm.mapped_column(
        MutableList.as_mutable(sa.dialects.postgresql.ARRAY(sa.Enum(educational_models.StudentLevels))),
        nullable=True,
        server_default="{}",
    )
    collectiveWebsite: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)
    collectiveDomains: sa_orm.Mapped[list[educational_models.EducationalDomain]] = sa_orm.relationship(
        educational_models.EducationalDomain,
        back_populates="venues",
        secondary=educational_models.EducationalDomainVenue.__table__,
        uselist=True,
    )
    collectiveDmsApplications: sa_orm.Mapped[list[educational_models.CollectiveDmsApplication]] = sa_orm.relationship(
        educational_models.CollectiveDmsApplication,
        back_populates="venue",
        primaryjoin="foreign(CollectiveDmsApplication.siret) == Venue.siret",
        uselist=True,
    )
    collectiveInterventionArea: sa_orm.Mapped[list[str] | None] = sa_orm.mapped_column(
        MutableList.as_mutable(sa.dialects.postgresql.json.JSONB), nullable=True
    )
    collectiveNetwork: sa_orm.Mapped[list[str] | None] = sa_orm.mapped_column(
        MutableList.as_mutable(sa.dialects.postgresql.json.JSONB), nullable=True
    )
    collectiveAccessInformation: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)
    collectivePhone: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)
    collectiveEmail: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)

    collective_playlists: sa_orm.Mapped[list[educational_models.CollectivePlaylist]] = sa_orm.relationship(
        "CollectivePlaylist", foreign_keys="CollectivePlaylist.venueId", back_populates="venue"
    )

    priceCategoriesLabel: sa_orm.Mapped[list["offers_models.PriceCategoryLabel"]] = sa_orm.relationship(
        "PriceCategoryLabel", foreign_keys="PriceCategoryLabel.venueId", back_populates="venue"
    )

    registration: sa_orm.Mapped["VenueRegistration | None"] = sa_orm.relationship(
        "VenueRegistration", foreign_keys="VenueRegistration.venueId", back_populates="venue", uselist=False
    )

    bankAccountLinks: sa_orm.Mapped[list["VenueBankAccountLink"]] = sa_orm.relationship(
        "VenueBankAccountLink",
        foreign_keys="VenueBankAccountLink.venueId",
        back_populates="venue",
        passive_deletes=True,
    )

    accessibilityProvider: sa_orm.Mapped["AccessibilityProvider | None"] = sa_orm.relationship(
        "AccessibilityProvider", foreign_keys="AccessibilityProvider.venueId", back_populates="venue", uselist=False
    )

    openingHours: sa_orm.Mapped[list["OpeningHours"]] = sa_orm.relationship(
        "OpeningHours", foreign_keys="OpeningHours.venueId", back_populates="venue", passive_deletes=True
    )

    offererAddress: sa_orm.Mapped["OffererAddress"] = sa_orm.relationship(
        "OffererAddress",
        primaryjoin="and_(Venue.id==OffererAddress.venueId, OffererAddress.type=='VENUE_LOCATION')",
        back_populates="venue",
    )

    cinemaProviderPivot: sa_orm.Mapped["providers_models.CinemaProviderPivot | None"] = sa_orm.relationship(
        "CinemaProviderPivot", foreign_keys="CinemaProviderPivot.venueId", back_populates="venue", uselist=False
    )
    allocinePivot: sa_orm.Mapped["providers_models.AllocinePivot | None"] = sa_orm.relationship(
        "AllocinePivot", foreign_keys="AllocinePivot.venueId", back_populates="venue", uselist=False
    )

    headlineOffers: sa_orm.Mapped[list["offers_models.HeadlineOffer"]] = sa_orm.relationship(
        "HeadlineOffer", foreign_keys="HeadlineOffer.venueId", back_populates="venue"
    )
    finance_incidents: sa_orm.Mapped[list["finance_models.FinanceIncident"]] = sa_orm.relationship(
        "FinanceIncident", foreign_keys="FinanceIncident.venueId", back_populates="venue"
    )
    custom_reimbursement_rules: sa_orm.Mapped[list["finance_models.CustomReimbursementRule"]] = sa_orm.relationship(
        "CustomReimbursementRule", foreign_keys="CustomReimbursementRule.venueId", back_populates="venue"
    )

    bookings: sa_orm.Mapped[list["bookings_models.Booking"]] = sa_orm.relationship(
        "Booking", foreign_keys="Booking.venueId", back_populates="venue"
    )

    action_history: sa_orm.Mapped[list["history_models.ActionHistory"]] = sa_orm.relationship(
        "ActionHistory",
        foreign_keys="ActionHistory.venueId",
        back_populates="venue",
        order_by=ACTION_HISTORY_ORDER_BY,
        passive_deletes=True,
    )
    offers: sa_orm.Mapped[list["offers_models.Offer"]] = sa_orm.relationship(
        "Offer", foreign_keys="Offer.venueId", back_populates="venue"
    )

    confidenceRule: sa_orm.Mapped["OffererConfidenceRule | None"] = sa_orm.relationship(
        "OffererConfidenceRule", foreign_keys="OffererConfidenceRule.venueId", back_populates="venue", uselist=False
    )

    _has_partner_page: sa_orm.Mapped[bool] = sa_orm.query_expression()

    activity: sa_orm.Mapped[Activity | None] = sa_orm.mapped_column(
        db_utils.MagicEnum(Activity, use_values=False), nullable=True
    )

    __table_args__ = (
        sa.CheckConstraint("(siret IS NOT NULL) OR (comment IS NOT NULL)", name="check_has_siret_or_comment"),
        sa.Index(
            "ix_venue_trgm_unaccent_public_name",
            sa.func.immutable_unaccent("publicName"),
            postgresql_using="gin",
            postgresql_ops={
                "description": "gin_trgm_ops",
            },
        ),
        sa.Index(
            "ix_venue_trgm_unaccent_name",
            sa.func.immutable_unaccent("name"),
            postgresql_using="gin",
            postgresql_ops={
                "description": "gin_trgm_ops",
            },
        ),
        sa.Index("idx_venue_bookingEmail", bookingEmail),
    )

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

    @bannerUrl.inplace.setter
    def _bannerUrlSetter(self, value: str | None) -> None:
        self._bannerUrl = value

    @bannerUrl.inplace.expression
    @classmethod
    def _bannerUrlExpression(cls) -> sa_orm.InstrumentedAttribute[str | None]:
        return cls._bannerUrl

    @hybrid_property
    def bannerMeta(self) -> dict | None:
        if self._bannerMeta is not None:
            return self._bannerMeta
        if self.googlePlacesInfo and self.googlePlacesInfo.bannerMeta:
            # Google Places API returns a list of HTML attributions, formatted like this:
            # <a href="https://url-of-contributor">John D.</a>
            # Regex to extract URL and text
            regex = r'<a href="(.*?)">(.*?)</a>'

            # TODO: (lixxday 2024-04-25) handle multiple attributions
            html_attributions = self.googlePlacesInfo.bannerMeta.get("html_attributions")
            if not html_attributions:
                return None
            match = re.search(regex, html_attributions[0])
            if match:
                url, credit = match.groups()

                return typing.cast(
                    dict,
                    BannerMetaModel(image_credit=VenueImageCredit(credit), image_credit_url=url, is_from_google=True),
                )
        return None

    @bannerMeta.inplace.setter
    def _bannerMetaSetter(self, value: dict | None) -> None:
        self._bannerMeta = value

    @bannerMeta.inplace.expression
    @classmethod
    def _bannerMetaExpression(cls) -> sa_orm.InstrumentedAttribute[dict | None]:
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

    @hasOffers.inplace.expression
    @classmethod
    def _hasOffersExpression(cls) -> Exists:
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
                offers_models.Offer.isActive,
                Venue.id == self.id,
            )
            .exists()
        ).scalar()

    @property
    def hasAtLeastOneBookableOffer(self) -> bool:
        import pcapi.core.offers.models as offers_models

        return db.session.query(
            sa.select(1)
            .select_from(offers_models.Offer)
            .join(Venue, offers_models.Offer.venueId == Venue.id)
            .join(offers_models.Stock, offers_models.Stock.offerId == offers_models.Offer.id)
            .where(
                Venue.id == self.id,
                offers_models.Offer.is_released_and_bookable,
            )
            .exists()
        ).scalar()

    @property
    def is_eligible_for_search(self) -> bool:
        return (
            bool(self.isOpenToPublic)
            and self.managingOfferer.isActive
            and self.managingOfferer.isValidated
            and bool(self.hasAtLeastOneBookableOffer)
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

    @dms_adage_status.inplace.expression
    @classmethod
    def _dms_adage_status_expression(cls) -> ScalarSelect:
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
        now = date_utils.get_naive_utc_now()
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
        now = date_utils.get_naive_utc_now()

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
        now = date_utils.get_naive_utc_now()

        for link in self.bankAccountLinks:
            lower = link.timespan.lower
            upper = link.timespan.upper

            if lower <= now and (not upper or now <= upper):
                return link

        return None

    @property
    def current_bank_account(self) -> "finance_models.BankAccount | None":
        if current_bank_account_link := self.current_bank_account_link:
            return current_bank_account_link.bankAccount
        return None

    @hybrid_property
    def common_name(self) -> str:
        return self.publicName or self.name

    @common_name.inplace.expression
    @classmethod
    def _common_name_expression(cls) -> sa_func.coalesce:
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
        return siren_utils.is_ridet(self.siret) or (
            self.offererAddress and self.offererAddress.address.departmentCode == NEW_CALEDONIA_DEPARTMENT_CODE
        )

    @property
    def has_headline_offer(self) -> bool:
        return any(headline_offer.isActive for headline_offer in self.headlineOffers)

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
                sa.not_(Offerer.isClosed),
                Venue.isPermanent.is_(True),
                Venue.isVirtual.is_(False),
                Venue.id == self.id,
            )
            .exists()
        ).scalar()

    @has_partner_page.inplace.expression
    @classmethod
    def _has_partner_page_expression(cls) -> Exists:
        from pcapi.core.offers.models import Offer

        AliasedVenue = sa_orm.aliased(Venue)
        return (
            sa.select(1)
            .select_from(Offer)
            .join(AliasedVenue, Offer.venueId == AliasedVenue.id)
            .join(Offerer, Offerer.id == AliasedVenue.managingOffererId)
            .where(
                Offerer.isActive.is_(True),
                sa.not_(Offerer.isClosed),
                AliasedVenue.isPermanent.is_(True),
                AliasedVenue.isVirtual.is_(False),
                AliasedVenue.id == cls.id,
            )
            .exists()
        )

    @property
    def can_display_highlights(self) -> bool:
        import pcapi.core.offers.models as offers_models

        return db.session.query(
            sa.select(1)
            .select_from(offers_models.Offer)
            .where(
                sa.and_(
                    offers_models.Offer.venueId == self.id,
                    offers_models.Offer.isEvent,
                )
            )
            .exists()
        ).scalar()


class GooglePlacesInfo(PcObject, Model):
    __tablename__ = "google_places_info"
    venueId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("venue.id", ondelete="CASCADE"), nullable=False, index=True, unique=True
    )
    venue: sa_orm.Mapped[Venue] = sa_orm.relationship(
        "Venue", foreign_keys=[venueId], back_populates="googlePlacesInfo"
    )
    # Some venues are duplicated in our database. They are all linked to the same item on
    # Google Places, so this column cannot be unique.
    placeId: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True, unique=False)
    bannerUrl: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True, name="bannerUrl")
    bannerMeta: sa_orm.Mapped[dict | None] = sa_orm.mapped_column(MutableDict.as_mutable(JSONB), nullable=True)
    updateDate: sa_orm.Mapped[datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()
    )


class AccessibilityProvider(PcObject, Model):
    __tablename__ = "accessibility_provider"
    venueId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("venue.id", ondelete="CASCADE"), index=True, nullable=False, unique=True
    )
    venue: sa_orm.Mapped[Venue] = sa_orm.relationship(
        "Venue", foreign_keys=[venueId], back_populates="accessibilityProvider"
    )
    externalAccessibilityId: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False)
    externalAccessibilityUrl: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False)
    externalAccessibilityData: sa_orm.Mapped[dict | None] = sa_orm.mapped_column(
        MutableDict.as_mutable(JSONB), nullable=True
    )
    lastUpdateAtProvider: sa_orm.Mapped[datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, default=date_utils.get_naive_utc_now
    )


class OpeningHours(PcObject, Model):
    __tablename__ = "opening_hours"

    venueId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("venue.id", ondelete="CASCADE"), nullable=True, index=True
    )
    venue: sa_orm.Mapped[Venue | None] = sa_orm.relationship(
        "Venue", foreign_keys=[venueId], back_populates="openingHours"
    )

    offerId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offer.id", ondelete="CASCADE"), nullable=True, index=True
    )
    offer: sa_orm.Mapped["offers_models.Offer | None"] = sa_orm.relationship(
        "Offer", foreign_keys=[offerId], back_populates="openingHours"
    )

    weekday: sa_orm.Mapped[Weekday] = sa_orm.mapped_column(
        db_utils.MagicEnum(Weekday), nullable=False, default=Weekday.MONDAY
    )
    timespan: sa_orm.Mapped[list[psycopg2.extras.NumericRange] | None] = sa_orm.mapped_column(
        sa_psql.ARRAY(sa_psql.ranges.NUMRANGE), nullable=True
    )

    __table_args__ = (
        (sa.CheckConstraint(sa.func.cardinality(timespan) <= 2, name="max_timespan_is_2")),
        (
            sa.CheckConstraint(
                sa.text(
                    '("venueId" IS NULL AND "offerId" IS NOT NULL) OR ("venueId" IS NOT NULL AND "offerId" IS NULL)'
                )
            )
        ),
    )

    def field_exists_and_has_changed(self, field: str, value: typing.Any) -> typing.Any:
        if field not in type(self).__table__.columns:
            raise ValueError(f"Unknown field {field} for model {type(self)}")
        return getattr(self, field) != value


class VenueLabel(PcObject, Model):
    __tablename__ = "venue_label"
    label: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(100), nullable=False)


class VenueContact(PcObject, Model):
    __tablename__ = "venue_contact"

    venueId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("venue.id", ondelete="CASCADE"), nullable=False, index=True, unique=True
    )

    venue: sa_orm.Mapped[Venue] = sa_orm.relationship("Venue", foreign_keys=[venueId], back_populates="contact")

    email: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.String(256), nullable=True)

    website: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.String(256), nullable=True)

    phone_number: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.String(64), nullable=True)

    social_medias: sa_orm.Mapped[dict] = sa_orm.mapped_column(
        MutableDict.as_mutable(JSONB), nullable=False, default={}, server_default="{}"
    )

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


class VenuePricingPointLink(Model):
    """At any given time, the bookings of a venue are priced against a
    particular venue that we call the "pricing point" of the venue.
    There should only ever be one pricing point for each venue, but
    for flexibility's sake we store the link in a table with the
    period during which this link is active.
    """

    __tablename__ = "venue_pricing_point_link"
    id: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.BigInteger, primary_key=True, autoincrement=True)
    venueId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("venue.id"), index=True, nullable=False
    )
    venue: sa_orm.Mapped[Venue] = sa_orm.relationship(
        Venue, foreign_keys=[venueId], back_populates="pricing_point_links"
    )
    pricingPointId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("venue.id"), index=True, nullable=False
    )
    pricingPoint: sa_orm.Mapped[Venue] = sa_orm.relationship(Venue, foreign_keys=[pricingPointId])
    # The lower bound is inclusive and required. The upper bound is
    # exclusive and optional. If there is no upper bound, it means
    # that the venue is still linked to the pricing point. For links
    # that existed before this table was introduced, the lower bound
    # is set to the Epoch.
    timespan: sa_orm.Mapped[psycopg2.extras.DateTimeRange] = sa_orm.mapped_column(sa_psql.TSRANGE, nullable=False)

    __table_args__ = (
        # A venue cannot be linked to multiple pricing points at the
        # same time.
        sa_psql.ExcludeConstraint(("venueId", "="), ("timespan", "&&")),
    )

    def __init__(self, **kwargs: typing.Any) -> None:
        kwargs["timespan"] = db_utils.make_timerange(*kwargs["timespan"])
        super().__init__(**kwargs)


class VenueBankAccountLink(PcObject, Model):
    """
    Professional users can link as many venues as they want to a given bank account.
    However, we want to keep tracks of the history, hence that table.
    """

    __tablename__ = "venue_bank_account_link"
    venueId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("venue.id", ondelete="CASCADE"), index=True, nullable=False
    )
    venue: sa_orm.Mapped[Venue] = sa_orm.relationship(
        "Venue", foreign_keys=[venueId], back_populates="bankAccountLinks"
    )

    bankAccountId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("bank_account.id", ondelete="CASCADE"), index=True, nullable=False
    )
    bankAccount: sa_orm.Mapped[finance_models.BankAccount] = sa_orm.relationship(
        "BankAccount", foreign_keys=[bankAccountId], back_populates="venueLinks"
    )

    timespan: sa_orm.Mapped[psycopg2.extras.DateTimeRange] = sa_orm.mapped_column(sa_psql.TSRANGE, nullable=False)

    __table_args__ = (
        # For a given venue, there can only be one bank account at a time.
        sa_psql.ExcludeConstraint(("venueId", "="), ("timespan", "&&")),
    )

    def __init__(self, **kwargs: typing.Any) -> None:
        kwargs["timespan"] = db_utils.make_timerange(*kwargs["timespan"])
        super().__init__(**kwargs)


class VenueEducationalStatus(Model):
    __tablename__ = "venue_educational_status"
    id: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.BigInteger, primary_key=True, autoincrement=False, nullable=False)
    name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(256), nullable=False)
    venues: sa_orm.Mapped[list[Venue]] = sa_orm.relationship(
        Venue, foreign_keys="Venue.venueEducationalStatusId", back_populates="venueEducationalStatus", uselist=True
    )


class VenueRegistration(PcObject, Model):
    __tablename__ = "venue_registration"

    id: sa_orm.Mapped[int] = sa_orm.mapped_column("id", sa.BigInteger, sa.Identity(), primary_key=True)

    venueId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("venue.id", ondelete="CASCADE"), nullable=False, index=True, unique=True
    )
    venue: sa_orm.Mapped[Venue] = sa_orm.relationship("Venue", foreign_keys=[venueId], back_populates="registration")

    target: sa_orm.Mapped[Target] = sa_orm.mapped_column(db_utils.MagicEnum(Target), nullable=False)

    webPresence: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)


class OffererTagMapping(PcObject, Model):
    __tablename__ = "offerer_tag_mapping"

    offererId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offerer.id", ondelete="CASCADE"), index=True, nullable=False
    )
    tagId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offerer_tag.id", ondelete="CASCADE"), index=True, nullable=False
    )

    __table_args__ = (sa.UniqueConstraint("offererId", "tagId", name="unique_offerer_tag"),)


class Offerer(
    PcObject,
    Model,
    ValidationStatusMixin,
    DeactivableMixin,
):
    __tablename__ = "offerer"
    thumb_path_component = "offerers"

    dateCreated: sa_orm.Mapped[datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, default=date_utils.get_naive_utc_now
    )

    name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(140), nullable=False)

    UserOfferers: sa_orm.Mapped[list["UserOfferer"]] = sa_orm.relationship(
        "UserOfferer", foreign_keys="UserOfferer.offererId", order_by="UserOfferer.id", back_populates="offerer"
    )

    siren: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(9), nullable=False, unique=True)

    dateValidated: sa_orm.Mapped[datetime | None] = sa_orm.mapped_column(sa.DateTime, nullable=True, default=None)

    tags: sa_orm.Mapped[list["OffererTag"]] = sa_orm.relationship("OffererTag", secondary=OffererTagMapping.__table__)

    offererProviders: sa_orm.Mapped[list["OffererProvider"]] = sa_orm.relationship(
        "OffererProvider", foreign_keys="OffererProvider.offererId", back_populates="offerer"
    )

    bankAccounts: sa_orm.Mapped[list[finance_models.BankAccount]] = sa_orm.relationship(
        finance_models.BankAccount,
        foreign_keys="BankAccount.offererId",
        back_populates="offerer",
        passive_deletes=True,
    )

    individualSubscription: sa_orm.Mapped["IndividualOffererSubscription | None"] = sa_orm.relationship(
        "IndividualOffererSubscription",
        foreign_keys="IndividualOffererSubscription.offererId",
        back_populates="offerer",
        uselist=False,
    )

    allowedOnAdage: sa_orm.Mapped[bool] = sa_orm.mapped_column(
        sa.Boolean, nullable=False, default=False, server_default=sa.sql.expression.false()
    )

    action_history: sa_orm.Mapped[list["history_models.ActionHistory"]] = sa_orm.relationship(
        "ActionHistory",
        foreign_keys="ActionHistory.offererId",
        back_populates="offerer",
        order_by=ACTION_HISTORY_ORDER_BY,
        passive_deletes=True,
    )

    _street = sa_orm.mapped_column("street", sa.Text(), nullable=True)

    managedVenues: sa_orm.Mapped[list[Venue]] = sa_orm.relationship(
        "Venue", foreign_keys="Venue.managingOffererId", back_populates="managingOfferer"
    )

    bookings: sa_orm.Mapped[list["bookings_models.Booking"]] = sa_orm.relationship(
        "Booking", foreign_keys="Booking.offererId", back_populates="offerer"
    )

    collectiveBookings: sa_orm.Mapped[list["educational_models.CollectiveBooking"]] = sa_orm.relationship(
        "CollectiveBooking", foreign_keys="CollectiveBooking.offererId", back_populates="offerer"
    )

    confidenceRule: sa_orm.Mapped["OffererConfidenceRule | None"] = sa_orm.relationship(
        "OffererConfidenceRule", foreign_keys="OffererConfidenceRule.offererId", back_populates="offerer", uselist=False
    )

    custom_reimbursement_rules: sa_orm.Mapped[list["finance_models.CustomReimbursementRule"]] = sa_orm.relationship(
        "CustomReimbursementRule", foreign_keys="CustomReimbursementRule.offererId", back_populates="offerer"
    )

    # use an expression instead of joinedload(tags) to avoid multiple SQL rows returned
    isTopActeur: sa_orm.Mapped["bool"] = sa_orm.query_expression()

    __table_args__ = (
        sa.Index("ix_offerer_trgm_unaccent_name", sa.func.immutable_unaccent("name"), postgresql_using="gin"),
    )

    def __init__(self, street: str | None = None, **kwargs: typing.Any) -> None:
        if street:
            self.street = street
        super().__init__(**kwargs)

    @hybrid_property
    def is_top_acteur(self) -> bool:
        return any(tag.name == constants.TOP_ACTEUR_TAG_NAME for tag in self.tags)

    @is_top_acteur.inplace.expression
    @classmethod
    def _is_top_acteur_expression(cls) -> Exists:
        return (
            sa.select(1)
            .select_from(OffererTagMapping)
            .join(OffererTag, OffererTag.id == OffererTagMapping.tagId)
            .where(OffererTagMapping.offererId == cls.id, OffererTag.name == constants.TOP_ACTEUR_TAG_NAME)
            .limit(1)
            .exists()
        )

    @hybrid_property
    def rid7(self) -> str | None:
        if siren_utils.is_rid7(self.siren):
            return siren_utils.siren_to_rid7(self.siren)
        return None

    @rid7.inplace.expression
    @classmethod
    def _rid7_expression(cls) -> Case:
        return sa.case(
            (cls.siren.ilike(f"{siren_utils.NEW_CALEDONIA_SIREN_PREFIX}%"), sa.func.substring(cls.siren, 3, 7)),
            else_=None,
        )

    @hybrid_property
    def is_caledonian(self) -> bool:
        """
        Note that Caledonian offerers may be registered with their SIREN.
        However, all offerers imported in New Caledonia are registered with a RID7 => avoid complex requests with joins
        on venue, offerer_address and address to check department code.
        """
        return siren_utils.is_rid7(self.siren)

    @is_caledonian.inplace.expression
    @classmethod
    def _is_caledonian_expression(cls) -> sa.ColumnElement[bool]:
        return cls.siren.ilike(f"{siren_utils.NEW_CALEDONIA_SIREN_PREFIX}%")

    @property
    def identifier_name(self) -> str:
        return "RID7" if siren_utils.is_rid7(self.siren) else "SIREN"

    @property
    def identifier(self) -> str | None:
        return self.rid7 or self.siren

    department_codes: sa_orm.Mapped[list[str] | None] = sa_orm.query_expression()

    @classmethod
    def department_codes_expression(cls) -> ScalarSelect:
        return (
            sa.select(sa.func.array_agg(sa.distinct(geography_models.Address.departmentCode)))
            .select_from(Venue)
            # FIXME (prouzet, 2026-01-19) Why does the following exception occurs without explicit join conditions?
            # AttributeError: Neither 'InstrumentedAttribute' object nor 'Comparator' object associated with Venue.offererAddress has an attribute '_deannotate'
            .join(
                OffererAddress,
                sa.and_(Venue.id == OffererAddress.venueId, OffererAddress.type == LocationType.VENUE_LOCATION),
            )
            .join(geography_models.Address, OffererAddress.addressId == geography_models.Address.id)
            .filter(Venue.managingOffererId == Offerer.id)
            .filter(sa.not_(Venue.isSoftDeleted.is_(True)))
            .correlate(Offerer)
            .scalar_subquery()
        )

    cities: sa_orm.Mapped[list[str] | None] = sa_orm.query_expression()

    @classmethod
    def cities_expression(cls) -> ScalarSelect:
        return (
            sa.select(sa.func.array_agg(sa.distinct(geography_models.Address.city)))
            .select_from(Venue)
            # FIXME (prouzet, 2026-01-19) Why does the following exception occurs without explicit join conditions?
            # AttributeError: Neither 'InstrumentedAttribute' object nor 'Comparator' object associated with Venue.offererAddress has an attribute '_deannotate'
            .join(
                OffererAddress,
                sa.and_(Venue.id == OffererAddress.venueId, OffererAddress.type == LocationType.VENUE_LOCATION),
            )
            .join(geography_models.Address, OffererAddress.addressId == geography_models.Address.id)
            .filter(Venue.managingOffererId == Offerer.id)
            .filter(sa.not_(Venue.isSoftDeleted.is_(True)))
            .correlate(Offerer)
            .scalar_subquery()
        )

    @property
    def confidenceLevel(self) -> "OffererConfidenceLevel | None":
        if not self.confidenceRule:
            return None
        return self.confidenceRule.confidenceLevel


class UserOfferer(PcObject, Model, ValidationStatusMixin):
    __tablename__ = "user_offerer"
    userId: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.BigInteger, sa.ForeignKey("user.id"), primary_key=True)
    user: sa_orm.Mapped["users_models.User"] = sa_orm.relationship(
        "User", foreign_keys=[userId], back_populates="UserOfferers"
    )
    offererId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offerer.id"), index=True, primary_key=True, nullable=False
    )
    offerer: sa_orm.Mapped[Offerer] = sa_orm.relationship(
        Offerer, foreign_keys=[offererId], back_populates="UserOfferers"
    )

    # dateCreated will remain null for all rows already in this table before this field was added
    dateCreated: sa_orm.Mapped[datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=True, default=date_utils.get_naive_utc_now
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "userId",
            "offererId",
            name="unique_user_offerer",
        ),
    )


class ApiKey(PcObject, Model):
    __tablename__ = "api_key"
    providerId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("provider.id", ondelete="CASCADE"), index=True, nullable=False
    )
    provider: sa_orm.Mapped["providers_models.Provider"] = sa_orm.relationship(
        "Provider", foreign_keys=[providerId], back_populates="apiKeys"
    )
    dateCreated: sa_orm.Mapped[datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, default=date_utils.get_naive_utc_now, server_default=sa.func.now()
    )
    prefix: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True, unique=True)
    secret: sa_orm.Mapped[bytes] = sa_orm.mapped_column(LargeBinary, nullable=True)

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


class OffererTagCategoryMapping(PcObject, Model):
    __tablename__ = "offerer_tag_category_mapping"

    tagId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offerer_tag.id", ondelete="CASCADE"), index=True, nullable=False
    )
    categoryId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offerer_tag_category.id", ondelete="CASCADE"), index=True, nullable=False
    )

    __table_args__ = (sa.UniqueConstraint("tagId", "categoryId", name="unique_offerer_tag_category"),)


class OffererTag(PcObject, Model):
    """
    Tags on offerers are only used in backoffice, set to help for filtering and analytics in metabase.
    There is currently no display or impact in mobile and web apps.
    """

    __tablename__ = "offerer_tag"

    name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(140), nullable=False, unique=True)
    label: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.String(140), nullable=True)
    description: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)

    categories: sa_orm.Mapped[list["OffererTagCategory"]] = sa_orm.relationship(
        "OffererTagCategory", secondary=OffererTagCategoryMapping.__table__
    )

    def __str__(self) -> str:
        return self.label or self.name


class OffererTagCategory(PcObject, Model):
    """
    Tag categories can be considered as "tags on tags", which aims at filtering tags depending on the project:
    tags used for partners counting, tags used for offerer validation, etc.
    The same OffererTag can be used in one or several project.
    """

    __tablename__ = "offerer_tag_category"

    name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(140), nullable=False, unique=True)
    label: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.String(140), nullable=True)

    def __str__(self) -> str:
        return self.label or self.name


class OffererProvider(PcObject, Model):
    __tablename__ = "offerer_provider"
    offererId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offerer.id"), index=True, nullable=False
    )
    offerer: sa_orm.Mapped[Offerer] = sa_orm.relationship(
        "Offerer", foreign_keys=[offererId], back_populates="offererProviders"
    )
    providerId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("provider.id"), index=True, nullable=False
    )
    provider: sa_orm.Mapped["providers_models.Provider"] = sa_orm.relationship(
        "Provider", foreign_keys=[providerId], back_populates="offererProvider"
    )

    __table_args__ = (sa.UniqueConstraint("offererId", "providerId", name="unique_offerer_provider"),)


class OffererInvitation(PcObject, Model):
    __tablename__ = "offerer_invitation"
    offererId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offerer.id", ondelete="CASCADE"), index=True, nullable=False
    )
    offerer: sa_orm.Mapped[Offerer] = sa_orm.relationship("Offerer", foreign_keys=[offererId])
    email: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False)
    dateCreated: sa_orm.Mapped[datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, default=date_utils.get_naive_utc_now
    )
    userId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("user.id"), nullable=False, index=True
    )
    user: sa_orm.Mapped["users_models.User"] = sa_orm.relationship(
        "User", foreign_keys=[userId], back_populates="OffererInvitations"
    )
    status: sa_orm.Mapped[InvitationStatus] = sa_orm.mapped_column(db_utils.MagicEnum(InvitationStatus), nullable=False)

    __table_args__ = (sa.UniqueConstraint("offererId", "email", name="unique_offerer_invitation"),)


class IndividualOffererSubscription(PcObject, Model):
    __tablename__ = "individual_offerer_subscription"

    offererId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offerer.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    offerer: sa_orm.Mapped[Offerer] = sa_orm.relationship(
        "Offerer", foreign_keys=[offererId], back_populates="individualSubscription", uselist=False
    )

    isEmailSent: sa_orm.Mapped[bool] = sa_orm.mapped_column(
        sa.Boolean, nullable=False, server_default=sa.sql.expression.false(), default=False
    )
    dateEmailSent: sa_orm.Mapped[date | None] = sa_orm.mapped_column(sa.Date, nullable=True)
    dateReminderEmailSent: sa_orm.Mapped[date | None] = sa_orm.mapped_column(sa.Date, nullable=True)

    isCriminalRecordReceived: sa_orm.Mapped[bool] = sa_orm.mapped_column(
        sa.Boolean, nullable=False, server_default=sa.sql.expression.false(), default=False
    )
    dateCriminalRecordReceived: sa_orm.Mapped[date | None] = sa_orm.mapped_column(sa.Date, nullable=True)

    isCertificateReceived: sa_orm.Mapped[bool] = sa_orm.mapped_column(
        sa.Boolean, nullable=False, server_default=sa.sql.expression.false(), default=False
    )
    certificateDetails: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)
    isExperienceReceived: sa_orm.Mapped[bool] = sa_orm.mapped_column(
        sa.Boolean, nullable=False, server_default=sa.sql.expression.false(), default=False
    )
    experienceDetails: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)
    has1yrExperience: sa_orm.Mapped[bool] = sa_orm.mapped_column(
        sa.Boolean, nullable=False, server_default=sa.sql.expression.false(), default=False
    )
    has5yrExperience: sa_orm.Mapped[bool] = sa_orm.mapped_column(
        sa.Boolean, nullable=False, server_default=sa.sql.expression.false(), default=False
    )
    isCertificateValid: sa_orm.Mapped[bool] = sa_orm.mapped_column(
        sa.Boolean, nullable=False, server_default=sa.sql.expression.false(), default=False
    )

    @hybrid_property
    def isReminderEmailSent(self) -> bool:
        return self.dateReminderEmailSent is not None

    @isReminderEmailSent.inplace.expression
    @classmethod
    def _isReminderEmailSentExpression(cls) -> BinaryExpression[bool]:
        return cls.dateReminderEmailSent.is_not(sa.null())


class OffererStatsData(typing.TypedDict, total=False):
    daily_views: list[OffererViewsModel]
    top_offers: list[TopOffersData]
    total_views_last_30_days: int


class OffererStats(PcObject, Model):
    __tablename__ = "offerer_stats"

    offererId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offerer.id", ondelete="CASCADE"), nullable=False
    )
    offerer: sa_orm.Mapped[Offerer] = sa_orm.relationship("Offerer", foreign_keys=[offererId])

    syncDate: sa_orm.Mapped[datetime] = sa_orm.mapped_column(sa.DateTime, nullable=False)
    table: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(120), nullable=False)
    jsonData: sa_orm.Mapped[dict] = sa_orm.mapped_column(  # serialized from `OffererStatsData`
        "jsonData",
        sa_mutable.MutableDict.as_mutable(sa_psql.JSONB),
        default={},
        server_default="{}",
        nullable=False,
    )

    __table_args__ = (sa.Index("ix_offerer_stats_offererId", offererId),)


class LocationType(enum.Enum):
    VENUE_LOCATION = "VENUE_LOCATION"
    OFFER_LOCATION = "OFFER_LOCATION"


class OffererAddress(PcObject, Model):
    __tablename__ = "offerer_address"
    label: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text(), nullable=True)
    addressId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("address.id"), index=True, nullable=False
    )
    address: sa_orm.Mapped[geography_models.Address] = sa_orm.relationship("Address", foreign_keys=[addressId])
    offererId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offerer.id", ondelete="CASCADE"), index=True, nullable=False
    )
    offerer: sa_orm.Mapped["Offerer"] = sa_orm.relationship("Offerer", foreign_keys=[offererId])
    type: sa_orm.Mapped[LocationType | None] = sa_orm.mapped_column(db_utils.MagicEnum(LocationType), nullable=True)
    venueId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("venue.id", ondelete="CASCADE"), nullable=True
    )
    # Do not add back_populates="offererAddress" because it is not always the venue location
    venue: sa_orm.Mapped[Venue | None] = sa_orm.relationship("Venue", foreign_keys=[venueId])

    __table_args__ = (
        # TODO (prouzet, 2025-10-09) When type and venueId are declared as non-nullable, index should be:
        # sa.Index("ix_unique_offerer_address_per_label, "offererId", "addressId", "label", "type", "venueId", unique=True),
        # probably with postgresql_nulls_not_distinct=True, because duplicate empty label should be on different venues.
        #
        # But this would break unique checking during transition because null values in type and venueId are distinct.
        # Setting postgresql_nulls_not_distinct is not possible because :
        # - null values must be distinct on label
        # - null values should not be distinct on type and venueId
        # so several partial indexes are created temporarily to ensure integrity during transition.
        sa.Index(
            "ix_unique_offerer_address_per_label",
            "offererId",
            "addressId",
            "label",
            postgresql_where=sa.and_(type.is_(None), venueId.is_(None)),
            unique=True,
        ),
        # After label
        sa.Index(
            "ix_wip_unique_offerer_address_when_label_is_null",
            "offererId",
            "addressId",
            "type",
            "venueId",
            unique=True,
            postgresql_where=sa.and_(label.is_(None), venueId.is_not(None)),
            postgresql_nulls_not_distinct=True,
        ),
        sa.Index(
            "ix_wip_unique_offerer_address_when_label_is_not_null",
            "offererId",
            "addressId",
            "label",
            "type",
            "venueId",
            unique=True,
            postgresql_where=label.is_not(None),
            postgresql_nulls_not_distinct=True,
        ),
        sa.Index(
            "ix_offerer_address_unique_venue_location_per_venue_id",
            "venueId",
            unique=True,
            postgresql_where=(type == LocationType.VENUE_LOCATION),
        ),
        sa.Index(
            "ix_offerer_address_venueId_type",
            "venueId",
            "type",
        ),
    )


class OffererConfidenceLevel(enum.Enum):
    # No default value when offerer follows rules in offer_validation_rule table,
    # in which case there is no row in table below
    MANUAL_REVIEW = "MANUAL_REVIEW"
    WHITELIST = "WHITELIST"


class OffererConfidenceRule(PcObject, Model):
    __tablename__ = "offerer_confidence_rule"

    offererId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offerer.id", ondelete="CASCADE"), index=True, unique=True, nullable=True
    )
    offerer: sa_orm.Mapped["Offerer | None"] = sa_orm.relationship(
        "Offerer", foreign_keys=[offererId], back_populates="confidenceRule"
    )

    venueId = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("venue.id", ondelete="CASCADE"), index=True, unique=True, nullable=True
    )
    venue: sa_orm.Mapped["Venue | None"] = sa_orm.relationship(
        "Venue", foreign_keys=[venueId], back_populates="confidenceRule"
    )

    confidenceLevel: sa_orm.Mapped[OffererConfidenceLevel] = sa_orm.mapped_column(
        db_utils.MagicEnum(OffererConfidenceLevel), nullable=False
    )

    __table_args__ = (sa.CheckConstraint('num_nonnulls("offererId", "venueId") = 1'),)


class NoticeType(enum.Enum):
    UNPAID_AMOUNT_NOTICE = "UNPAID_AMOUNT_NOTICE"
    REMINDER_LETTER = "REMINDER_LETTER"
    BAILIFF = "BAILIFF"


class NoticeStatus(enum.Enum):
    CREATED = "CREATED"
    PENDING = "PENDING"
    WITHOUT_CONTINUATION = "WITHOUT_CONTINUATION"
    CLOSED = "CLOSED"


class NoticeStatusMotivation(enum.Enum):
    # status = PENDING
    OFFERER_NOT_FOUND = "OFFERER_NOT_FOUND"
    PRICE_NOT_FOUND = "PRICE_NOT_FOUND"
    # status = CLOSED
    ALREADY_PAID = "ALREADY_PAID"
    REJECTED = "REJECTED"
    NO_LINKED_BANK_ACCOUNT = "NO_LINKED_BANK_ACCOUNT"


class NonPaymentNoticeBatchAssociation(PcObject, Model):
    """Many-to-many association table"""

    __tablename__ = "non_payment_notice_batch_association"

    noticeId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("non_payment_notice.id", ondelete="CASCADE"), index=True, nullable=False
    )
    batchId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("cashflow_batch.id"), index=True, nullable=False
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "noticeId",
            "batchId",
            name="unique_non_payment_notice_batch_association",
        ),
    )


class NonPaymentNotice(PcObject, Model):
    __tablename__ = "non_payment_notice"

    amount: sa_orm.Mapped[decimal.Decimal] = sa_orm.mapped_column(sa.Numeric(10, 2), nullable=False)
    # TODO (prouzet, 2026-01-30) batchId is deprecated and should be removed when data is migrated
    batchId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("cashflow_batch.id"), nullable=True, index=True
    )
    dateReceived: sa_orm.Mapped[date] = sa_orm.mapped_column(
        sa.Date, nullable=False, server_default=sa.func.current_date()
    )
    dateCreated: sa_orm.Mapped[datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, default=date_utils.get_naive_utc_now
    )
    emitterName: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text(), nullable=False)
    emitterEmail: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text(), nullable=False)
    reference: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text(), nullable=False)
    noticeType: sa_orm.Mapped[NoticeType] = sa_orm.mapped_column(db_utils.MagicEnum(NoticeType), nullable=False)
    status: sa_orm.Mapped[NoticeStatus] = sa_orm.mapped_column(
        db_utils.MagicEnum(NoticeStatus),
        nullable=False,
        server_default=NoticeStatus.CREATED.value,
        default=NoticeStatus.CREATED,
    )
    motivation: sa_orm.Mapped[NoticeStatusMotivation | None] = sa_orm.mapped_column(
        db_utils.MagicEnum(NoticeStatusMotivation), nullable=True
    )
    venueId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("venue.id", ondelete="SET NULL"), nullable=True, index=True
    )
    venue: sa_orm.Mapped["Venue | None"] = sa_orm.relationship("Venue", foreign_keys=[venueId])
    offererId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offerer.id", ondelete="SET NULL"), nullable=True, index=True
    )
    offerer: sa_orm.Mapped["Offerer | None"] = sa_orm.relationship("Offerer", foreign_keys=[offererId])
    batches: sa_orm.Mapped[list["finance_models.CashflowBatch"]] = sa_orm.relationship(
        secondary=NonPaymentNoticeBatchAssociation.__tablename__
    )


class NoticeRecipientType(enum.Enum):
    SGC = "Service Gestion Comptable"
    PRO = "Partenaire Culturel"
