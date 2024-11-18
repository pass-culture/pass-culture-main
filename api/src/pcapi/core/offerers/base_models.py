import datetime
import decimal
import enum
import os
import re
import typing

import psycopg2.extras
import sqlalchemy as sa
from sqlalchemy import func
import sqlalchemy.dialects.postgresql as sa_psql
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.ext.mutable import MutableList
import sqlalchemy.orm as sa_orm
import sqlalchemy.sql.functions as sqla_func
from sqlalchemy.sql.selectable import Exists

from pcapi import settings
from pcapi.core.educational import enum as educational_enum
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models import db
from pcapi.models.accessibility_mixin import AccessibilityMixin
from pcapi.models.has_thumb_mixin import HasThumbMixin
from pcapi.models.pc_object import PcObject
from pcapi.routes.native.v1.serialization.offerers import BannerMetaModel
from pcapi.routes.native.v1.serialization.offerers import VenueTypeCode
from pcapi.utils import db as db_utils
from pcapi.utils import postal_code as postal_code_utils
from pcapi.utils import siren as siren_utils
from pcapi.utils.date import METROPOLE_TIMEZONE
from pcapi.utils.date import get_department_timezone
from pcapi.utils.date import get_postal_code_timezone
from pcapi.utils.date import numranges_to_timespan_str
from pcapi.utils.human_ids import humanize


if typing.TYPE_CHECKING:
    from pcapi.core.educational import models as educational_models
    from pcapi.core.offers import models as offers_models


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

CONSTRAINT_CHECK_HAS_SIRET_XOR_HAS_COMMENT_XOR_IS_VIRTUAL = """
    (siret IS NULL AND comment IS NULL AND "isVirtual" IS TRUE)
    OR (siret IS NULL AND comment IS NOT NULL AND "isVirtual" IS FALSE)
    OR (siret IS NOT NULL AND "isVirtual" IS FALSE)
"""


class Target(enum.Enum):
    EDUCATIONAL = "EDUCATIONAL"
    INDIVIDUAL_AND_EDUCATIONAL = "INDIVIDUAL_AND_EDUCATIONAL"
    INDIVIDUAL = "INDIVIDUAL"


class Venue(PcObject, Base, Model, HasThumbMixin, AccessibilityMixin):
    __tablename__ = "venue"

    name: str = sa.Column(sa.String(140), nullable=False)
    sa.Index("ix_venue_trgm_unaccent_name", sa.func.immutable_unaccent("name"), postgresql_using="gin")

    siret = sa.Column(sa.String(14), nullable=True, unique=True)

    departementCode = sa.Column(sa.String(3), nullable=True, index=True)

    latitude: decimal.Decimal | None = sa.Column(sa.Numeric(8, 5), nullable=True)

    longitude: decimal.Decimal | None = sa.Column(sa.Numeric(8, 5), nullable=True)

    venueProviders: list["providers_models.VenueProvider"] = sa_orm.relationship(
        "VenueProvider", back_populates="venue"
    )

    managingOffererId: int = sa.Column(sa.BigInteger, sa.ForeignKey("offerer.id"), nullable=False, index=True)

    managingOfferer: sa.orm.Mapped["Offerer"] = sa_orm.relationship(
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
        server_default=sa.sql.expression.false(),
    )

    isPermanent = sa.Column(sa.Boolean, nullable=False, default=False)

    isOpenToPublic = sa.Column(sa.Boolean, nullable=True, default=None)

    comment = sa.Column(
        sa.TEXT,
        sa.CheckConstraint(
            CONSTRAINT_CHECK_HAS_SIRET_XOR_HAS_COMMENT_XOR_IS_VIRTUAL, name="check_has_siret_xor_comment_xor_isVirtual"
        ),
        nullable=True,
    )

    collectiveOffers: list["educational_models.CollectiveOffer"] = sa_orm.relationship(
        "CollectiveOffer", back_populates="venue"
    )

    collectiveOfferTemplates: list["educational_models.CollectiveOfferTemplate"] = sa_orm.relationship(
        "CollectiveOfferTemplate", back_populates="venue"
    )

    venueTypeCode: VenueTypeCode = sa.Column(
        sa.Enum(VenueTypeCode, create_constraint=False), nullable=False, default=VenueTypeCode.OTHER
    )

    venueLabelId = sa.Column(sa.Integer, sa.ForeignKey("venue_label.id"), nullable=True)

    venueLabel: sa_orm.Mapped["VenueLabel"] = sa_orm.relationship("VenueLabel", foreign_keys=[venueLabelId])

    dateCreated: datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)

    withdrawalDetails = sa.Column(sa.Text, nullable=True)

    description = sa.Column(sa.Text, nullable=True)

    contact: sa.orm.Mapped["VenueContact | None"] = sa_orm.relationship(
        "VenueContact", back_populates="venue", uselist=False
    )

    # _bannerUrl should provide a safe way to retrieve the banner,
    # whereas bannerMeta should provide extra information that might be
    # helpful like image type, author, etc. that can change over time.
    _bannerUrl = sa.Column(sa.Text, nullable=True, name="bannerUrl")
    googlePlacesInfo: sa.orm.Mapped["GooglePlacesInfo | None"] = sa_orm.relationship(
        "GooglePlacesInfo", back_populates="venue", uselist=False
    )

    _bannerMeta: dict | None = sa.Column(MutableDict.as_mutable(JSONB), nullable=True, name="bannerMeta")

    adageId = sa.Column(sa.Text, nullable=True)
    adageInscriptionDate = sa.Column(sa.DateTime, nullable=True)

    thumb_path_component = "venues"

    criteria: list["criteria_models.Criterion"] = sa_orm.relationship(
        "Criterion", backref=db.backref("venue_criteria", lazy="dynamic"), secondary="venue_criterion"
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
    collectiveStudents: list["educational_models.StudentLevels"] | None = sa.Column(
        MutableList.as_mutable(sa.dialects.postgresql.ARRAY(sa.Enum(educational_enum.StudentLevels))),
        nullable=True,
        server_default="{}",
    )
    collectiveWebsite = sa.Column(sa.Text, nullable=True)
    collectiveDomains: sa_orm.Mapped[list["educational_models.EducationalDomain"]] = sa_orm.relationship(
        # educational_models.EducationalDomain,
        "EducationalDomain",
        back_populates="venues",
        secondary="educational_domain_venue",
        uselist=True,
    )
    collectiveDmsApplications: sa_orm.Mapped[list["educational_models.CollectiveDmsApplication"]] = sa_orm.relationship(
        "CollectiveDmsApplication",
        backref=db.backref("venue"),
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

    collective_playlists: list["educational_models.CollectivePlaylist"] = sa_orm.relationship(
        "CollectivePlaylist", back_populates="venue"
    )

    priceCategoriesLabel: sa_orm.Mapped[list["offers_models.PriceCategoryLabel"]] = sa_orm.relationship(
        "PriceCategoryLabel", back_populates="venue"
    )

    collectiveSubCategoryId = sa.Column(sa.Text, nullable=True)

    registration: sa_orm.Mapped["VenueRegistration | None"] = sa_orm.relationship(
        "VenueRegistration", back_populates="venue", uselist=False
    )

    bankAccountLinks: list["VenueBankAccountLink"] = sa_orm.relationship(
        "VenueBankAccountLink", back_populates="venue", passive_deletes=True
    )

    accessibilityProvider: sa_orm.Mapped["AccessibilityProvider | None"] = sa_orm.relationship(
        "AccessibilityProvider", back_populates="venue", uselist=False
    )

    adage_addresses: sa_orm.Mapped[typing.Sequence["educational_models.AdageVenueAddress"]] = sa_orm.relationship(
        "AdageVenueAddress", back_populates="venue"
    )

    openingHours: sa_orm.Mapped[list["OpeningHours"]] = sa_orm.relationship(
        "OpeningHours", back_populates="venue", passive_deletes=True
    )

    offererAddressId: int = sa.Column(sa.BigInteger, sa.ForeignKey("offerer_address.id"), nullable=True, index=True)
    offererAddress: sa_orm.Mapped["OffererAddress | None"] = sa_orm.relationship(
        "OffererAddress", foreign_keys=[offererAddressId], back_populates="venues"
    )

    headlineOffers: list["offers_models.HeadlineOffer"] = sa_orm.relationship("HeadlineOffer", back_populates="venue")

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
    def bannerUrl(cls):  # pylint: disable=no-self-argument
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
    def bannerMeta(cls):  # pylint: disable=no-self-argument
        return cls._bannerMeta

    @hybrid_property
    def hasOffers(self) -> bool:
        # Don't use Python properties as high offer count venues will timeout
        import pcapi.core.offers.models as offers_models

        return bool(
            offers_models.Offer.query.filter(offers_models.Offer.venueId == self.id)
            .limit(1)
            .with_entities(offers_models.Offer.venueId)
            .all()
        )

    @hasOffers.expression  # type: ignore[no-redef]
    def hasOffers(cls) -> Exists:  # pylint: disable=no-self-argument
        import pcapi.core.offers.models as offers_models

        return sa.exists().where(offers_models.Offer.venueId == cls.id)

    @property
    def is_eligible_for_search(self) -> bool:
        not_administrative = self.venueTypeCode != VenueTypeCode.ADMINISTRATIVE
        return bool(self.isPermanent) and self.managingOfferer.isActive and not_administrative

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
    def last_collective_dms_application(self) -> "educational_models.CollectiveDmsApplication | None":
        if self.collectiveDmsApplications:
            return sorted(
                self.collectiveDmsApplications, key=lambda application: application.lastChangeDate, reverse=True
            )[0]
        return None

    @hybrid_property
    def dms_adage_status(self) -> str | None:
        return self.last_collective_dms_application.state if self.last_collective_dms_application else None

    @dms_adage_status.expression  # type: ignore[no-redef]
    def dms_adage_status(cls) -> str | None:  # pylint: disable=no-self-argument
        from pcapi.core.educational import models as educational_models

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
        from pcapi.core.finance.models import BankAccountApplicationStatus

        if not self.current_bank_account:
            return False
        return self.current_bank_account.status == BankAccountApplicationStatus.DRAFT

    @property
    def hasAcceptedBankAccountApplication(self) -> bool:
        from pcapi.core.finance.models import BankAccountApplicationStatus

        if not self.current_bank_account:
            return False
        return self.current_bank_account.status == BankAccountApplicationStatus.ACCEPTED

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

    def field_exists_and_has_changed(self, field: str, value: typing.Any) -> typing.Any:
        if field not in type(self).__table__.columns:
            raise ValueError(f"Unknown field {field} for model {type(self)}")
        if isinstance(getattr(self, field), decimal.Decimal):
            return str(getattr(self, field)) != value
        return getattr(self, field) != value

    @property
    def current_pricing_point_id(self) -> int | None:
        now = datetime.datetime.utcnow()
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
        now = datetime.datetime.utcnow()

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
        now = datetime.datetime.utcnow()

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
    def common_name(cls) -> str:  # pylint: disable=no-self-argument
        return sqla_func.coalesce(sa.func.nullif(cls.publicName, ""), cls.name)

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
        return bool(self.headlineOffers)


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
