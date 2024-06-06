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
from sqlalchemy.ext import mutable as sa_mutable
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.ext.mutable import MutableList
import sqlalchemy.orm as sa_orm
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression
from sqlalchemy.sql.elements import Case
import sqlalchemy.sql.functions as sqla_func
from sqlalchemy.sql.sqltypes import LargeBinary

from pcapi import settings
from pcapi.connectors.acceslibre import AccessibilityInfo
from pcapi.connectors.big_query.queries.offerer_stats import OffererViewsModel
from pcapi.connectors.big_query.queries.offerer_stats import TopOffersData
from pcapi.core.educational import models as educational_models
import pcapi.core.finance.models as finance_models
from pcapi.core.geography import models as geography_models
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models import db
from pcapi.models.accessibility_mixin import AccessibilityMixin
from pcapi.models.deactivable_mixin import DeactivableMixin
from pcapi.models.feature import FeatureToggle
from pcapi.models.has_address_mixin import HasAddressMixin
from pcapi.models.has_thumb_mixin import HasThumbMixin
from pcapi.models.pc_object import PcObject
from pcapi.models.validation_status_mixin import ValidationStatusMixin
from pcapi.routes.native.v1.serialization.offerers import BannerMetaModel
from pcapi.routes.native.v1.serialization.offerers import VenueTypeCode
from pcapi.utils import crypto
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
    from pcapi.core.providers.models import Provider
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


class Venue(PcObject, Base, Model, HasThumbMixin, AccessibilityMixin):
    __tablename__ = "venue"

    name: str = Column(String(140), nullable=False)
    sa.Index("ix_venue_trgm_unaccent_name", sa.func.immutable_unaccent("name"), postgresql_using="gin")

    siret = Column(String(14), nullable=True, unique=True)

    departementCode = Column(String(3), nullable=True, index=True)

    latitude = Column(Numeric(8, 5), nullable=True)

    longitude = Column(Numeric(8, 5), nullable=True)

    venueProviders: list["providers_models.VenueProvider"] = relationship("VenueProvider", back_populates="venue")

    managingOffererId: int = Column(BigInteger, ForeignKey("offerer.id"), nullable=False, index=True)

    managingOfferer: sa_orm.Mapped["Offerer"] = relationship(
        "Offerer", foreign_keys=[managingOffererId], backref="managedVenues"
    )

    bookingEmail = Column(String(120), nullable=True)
    sa.Index("idx_venue_bookingEmail", bookingEmail)

    _address = Column("address", String(200), nullable=True)

    _street = Column("street", Text(), nullable=True)

    postalCode = Column(String(6), nullable=True)

    city = Column(String(50), nullable=True)

    # banId is a unique interoperability key for French addresses registered in the
    # Base Adresse Nationale. See "cle_interop" here:
    # https://doc.adresse.data.gouv.fr/mettre-a-jour-sa-base-adresse-locale/le-format-base-adresse-locale
    banId = Column(Text(), nullable=True)

    timezone = Column(String(50), nullable=False, default=METROPOLE_TIMEZONE, server_default=METROPOLE_TIMEZONE)

    publicName = Column(String(255), nullable=True)
    sa.Index("ix_venue_trgm_unaccent_public_name", sa.func.immutable_unaccent("name"), postgresql_using="gin")

    isVisibleInApp = Column(Boolean, nullable=False, default=True, server_default=sa.sql.expression.true())

    isVirtual: bool = Column(
        Boolean,
        CheckConstraint(CONSTRAINT_CHECK_IS_VIRTUAL_XOR_HAS_ADDRESS, name="check_is_virtual_xor_has_address"),
        nullable=False,
        default=False,
        server_default=expression.false(),
    )

    isPermanent = Column(Boolean, nullable=False, default=False)

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

    venueTypeCode: VenueTypeCode = Column(
        sa.Enum(VenueTypeCode, create_constraint=False), nullable=False, default=VenueTypeCode.OTHER
    )

    venueLabelId = Column(Integer, ForeignKey("venue_label.id"), nullable=True)

    venueLabel: sa_orm.Mapped["VenueLabel"] = relationship("VenueLabel", foreign_keys=[venueLabelId])

    dateCreated: datetime = Column(DateTime, nullable=False, default=datetime.utcnow)

    withdrawalDetails = Column(Text, nullable=True)

    description = Column(Text, nullable=True)

    contact: sa_orm.Mapped["VenueContact | None"] = relationship("VenueContact", back_populates="venue", uselist=False)

    # _bannerUrl should provide a safe way to retrieve the banner,
    # whereas bannerMeta should provide extra information that might be
    # helpful like image type, author, etc. that can change over time.
    _bannerUrl = Column(Text, nullable=True, name="bannerUrl")
    googlePlacesInfo: sa_orm.Mapped["GooglePlacesInfo | None"] = relationship(
        "GooglePlacesInfo", back_populates="venue", uselist=False
    )

    _bannerMeta: dict | None = Column(MutableDict.as_mutable(JSONB), nullable=True, name="bannerMeta")

    adageId = Column(Text, nullable=True)
    adageInscriptionDate = Column(DateTime, nullable=True)

    thumb_path_component = "venues"

    criteria: list["criteria_models.Criterion"] = sa.orm.relationship(
        "Criterion", backref=db.backref("venue_criteria", lazy="dynamic"), secondary="venue_criterion"
    )

    dmsToken: str = Column(Text, nullable=False, unique=True)

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
    collectiveDmsApplications: Mapped[list[educational_models.CollectiveDmsApplication]] = relationship(
        educational_models.CollectiveDmsApplication,
        backref=backref("venue"),
        primaryjoin="foreign(CollectiveDmsApplication.siret) == Venue.siret",
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

    collective_playlists: list[educational_models.CollectivePlaylist] = relationship(
        "CollectivePlaylist", back_populates="venue"
    )

    bankInformation: finance_models.BankInformation | None = relationship(
        "BankInformation", back_populates="venue", uselist=False
    )

    priceCategoriesLabel: sa_orm.Mapped[list["offers_models.PriceCategoryLabel"]] = relationship(
        "PriceCategoryLabel", back_populates="venue"
    )

    collectiveSubCategoryId = sa.Column(sa.Text, nullable=True)

    registration: sa_orm.Mapped["VenueRegistration | None"] = relationship(
        "VenueRegistration", back_populates="venue", uselist=False
    )

    bankAccountLinks: list["VenueBankAccountLink"] = relationship(
        "VenueBankAccountLink", back_populates="venue", passive_deletes=True
    )

    accessibilityProvider: sa_orm.Mapped["AccessibilityProvider | None"] = relationship(
        "AccessibilityProvider", back_populates="venue", uselist=False
    )

    adage_addresses: sa_orm.Mapped[typing.Sequence[educational_models.AdageVenueAddress]] = sa.orm.relationship(
        "AdageVenueAddress", back_populates="venue"
    )

    openingHours: Mapped[list["OpeningHours | None"]] = relationship(
        "OpeningHours", back_populates="venue", passive_deletes=True
    )

    offererAddressId: int = Column(BigInteger, ForeignKey("offerer_address.id"), nullable=True, index=True)
    offererAddress: Mapped["OffererAddress | None"] = relationship("OffererAddress", foreign_keys=[offererAddressId])

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
        if (
            self.googlePlacesInfo
            and self.googlePlacesInfo.bannerUrl
            and FeatureToggle.WIP_GOOGLE_MAPS_VENUE_IMAGES.is_active()
        ):
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
        if (
            self.googlePlacesInfo
            and self.googlePlacesInfo.bannerMeta
            and FeatureToggle.WIP_GOOGLE_MAPS_VENUE_IMAGES.is_active()
        ):
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
    def dms_adage_status(cls) -> str | None:  # pylint: disable=no-self-argument
        return (
            db.session.query(educational_models.CollectiveDmsApplication.state)
            .select_from(educational_models.CollectiveDmsApplication)
            .filter(educational_models.CollectiveDmsApplication.siret == cls.siret)
            .order_by(educational_models.CollectiveDmsApplication.lastChangeDate.desc())
            .limit(1)
            .scalar_subquery()
        )

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
    def common_name(cls) -> str:  # pylint: disable=no-self-argument
        return sqla_func.coalesce(func.nullif(cls.publicName, ""), cls.name)

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
    externalAccessibilityId: str | None = Column(
        Text,
        nullable=True,
    )
    externalAccessibilityUrl: str | None = Column(
        Text,
        nullable=True,
    )
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

    UserOfferers: list["UserOfferer"] = sa.orm.relationship(
        "UserOfferer", order_by="UserOfferer.id", back_populates="offerer"
    )

    siren = Column(
        String(9), nullable=True, unique=True
    )  # FIXME: should not be nullable, is until we have all SIRENs filled in the DB

    dateValidated = Column(DateTime, nullable=True, default=None)

    tags: list["OffererTag"] = sa.orm.relationship("OffererTag", secondary="offerer_tag_mapping")

    offererProviders: list["OffererProvider"] = sa.orm.relationship("OffererProvider", back_populates="offerer")
    thumb_path_component = "offerers"

    bankAccounts: list[finance_models.BankAccount] = sa.orm.relationship(
        finance_models.BankAccount,
        back_populates="offerer",
        passive_deletes=True,
    )

    individualSubscription: Mapped["IndividualOffererSubscription | None"] = sa.orm.relationship(
        "IndividualOffererSubscription", back_populates="offerer", uselist=False
    )

    allowedOnAdage: bool = Column(Boolean, nullable=False, default=False, server_default=sa.sql.expression.false())

    _street = Column("street", Text(), nullable=True)

    hasNewNavUsers: sa_orm.Mapped["bool | None"] = sa.orm.query_expression()
    hasOldNavUsers: sa_orm.Mapped["bool | None"] = sa.orm.query_expression()

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

    @departementCode.expression  # type: ignore[no-redef]
    def departementCode(cls) -> Case:  # pylint: disable=no-self-argument
        return case(
            (
                cast(func.substring(cls.postalCode, 1, 2), Integer)
                >= postal_code_utils.OVERSEAS_DEPARTEMENT_CODE_START,
                func.substring(cls.postalCode, 1, 3),
            ),
            else_=func.substring(cls.postalCode, 1, 2),
        )

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
                db.session.flush()  # it may not be committed but the hash recompute cost is low
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

    categories: list["OffererTagCategory"] = sa.orm.relationship(
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
    address: sa.orm.Mapped[geography_models.Address] = sa.orm.relationship("Address", foreign_keys=[addressId])
    offererId = sa.Column(sa.BigInteger, sa.ForeignKey("offerer.id", ondelete="CASCADE"), index=True)
    offerer: sa.orm.Mapped["Offerer"] = sa.orm.relationship("Offerer", foreign_keys=[offererId])

    __table_args__ = (sa.Index("ix_unique_offerer_address_per_label", "offererId", "addressId", "label", unique=True),)

    _isEditable: sa.orm.Mapped["bool|None"] = sa.orm.query_expression()

    @hybrid_property
    def isEditable(self) -> bool:
        return db.session.query(~sa.select(1).exists().where(Venue.offererAddressId == self.id)).scalar()

    @isEditable.expression  # type: ignore[no-redef]
    def isEditable(cls) -> sa.sql.elements.BooleanClauseList:  # pylint: disable=no-self-argument
        return ~sa.select(1).where(Venue.offererAddressId == cls.id).exists()


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
    offerer: sa.orm.Mapped["Offerer | None"] = sa.orm.relationship(
        "Offerer", foreign_keys=[offererId], backref=sa_orm.backref("confidenceRule", uselist=False)
    )

    venueId = sa.Column(
        sa.BigInteger, sa.ForeignKey("venue.id", ondelete="CASCADE"), index=True, unique=True, nullable=True
    )
    venue: sa.orm.Mapped["Venue | None"] = sa.orm.relationship(
        "Venue", foreign_keys=[venueId], backref=sa_orm.backref("confidenceRule", uselist=False)
    )

    confidenceLevel: OffererConfidenceLevel = sa.Column(db_utils.MagicEnum(OffererConfidenceLevel), nullable=False)

    __table_args__ = (sa.CheckConstraint('num_nonnulls("offererId", "venueId") = 1'),)
