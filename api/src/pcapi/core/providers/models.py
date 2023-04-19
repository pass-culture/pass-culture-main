from dataclasses import dataclass
import datetime
import decimal
import enum

from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import CheckConstraint
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import UniqueConstraint
from sqlalchemy import and_
from sqlalchemy import case
from sqlalchemy import exists
from sqlalchemy import select
from sqlalchemy import true
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as sa_orm
from sqlalchemy.orm import column_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from pcapi.core.offerers.models import Venue
import pcapi.core.providers.constants as provider_constants
from pcapi.domain.price_rule import PriceRule
from pcapi.infrastructure.repository.stock_provider.provider_api import ProviderAPI
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.deactivable_mixin import DeactivableMixin
from pcapi.models.pc_object import PcObject
from pcapi.models.providable_mixin import ProvidableMixin


class Provider(PcObject, Base, Model, DeactivableMixin):
    name: str = Column(String(90), index=True, nullable=False)

    localClass = Column(
        String(60),
        nullable=True,
        unique=True,
    )

    # Presence of this fields signify the provider implements pass Culture's provider API
    apiUrl = Column(String, nullable=True)

    authToken = Column(String, nullable=True)

    enabledForPro: bool = Column(Boolean, nullable=False, default=False, server_default=expression.false())

    enableParallelSynchronization: bool = Column(
        Boolean, nullable=False, default=False, server_default=expression.false()
    )

    logoUrl: str = Column(Text(), nullable=True)
    pricesInCents: bool = Column(Boolean, nullable=False, default=False, server_default=expression.false())

    @property
    def isAllocine(self) -> bool:
        from pcapi import local_providers  # avoid import loop

        return self.localClass == local_providers.AllocineStocks.__name__

    @property
    def isCinemaProvider(self) -> bool:
        return self.localClass in provider_constants.CINEMA_PROVIDER_NAMES

    @property
    def implements_provider_api(self) -> bool:
        return self.apiUrl != None

    def getProviderAPI(self) -> ProviderAPI:
        return ProviderAPI(
            api_url=self.apiUrl,  # type: ignore [arg-type]
            name=self.name,
            authentication_token=self.authToken,
        )


class VenueProvider(PcObject, Base, Model, ProvidableMixin, DeactivableMixin):
    """Stores specific sync settings for a Venue, and whether it is active"""

    venueId: int = Column(BigInteger, ForeignKey("venue.id"), nullable=False)

    venue: sa_orm.Mapped["Venue"] = relationship("Venue", foreign_keys=[venueId])

    providerId: int = Column(BigInteger, ForeignKey("provider.id"), index=True, nullable=False)

    provider: sa_orm.Mapped["Provider"] = relationship("Provider", foreign_keys=[providerId], backref="venueProviders")

    venueIdAtOfferProvider: str = Column(String(70), nullable=False)

    lastSyncDate = Column(DateTime, nullable=True)

    # describe if synchronised offers are available for duo booking or not
    isDuoOffers = Column(Boolean, nullable=True)

    isFromAllocineProvider = column_property(  # type: ignore [misc]
        exists(select([Provider.id]).where(and_(Provider.id == providerId, Provider.localClass == "AllocineStocks")))
    )

    isFromCinemaProvider = column_property(  # type: ignore [misc]
        exists(select(Provider.id)).where(
            and_(Provider.id == providerId, Provider.localClass.in_(provider_constants.CINEMA_PROVIDER_NAMES))
        )
    )

    __mapper_args__ = {
        "polymorphic_on": case(
            [
                (isFromAllocineProvider, "allocine_venue_provider"),
            ],
            else_="venue_provider",
        ),
        "polymorphic_identity": "venue_provider",
    }

    __table_args__ = (
        UniqueConstraint(
            "venueId",
            "providerId",
            "venueIdAtOfferProvider",
            name="unique_venue_provider",
        ),
    )

    @staticmethod
    def restize_integrity_error(error: sa_exc.IntegrityError) -> tuple[str, str]:
        if "unique_venue_provider" in str(error.orig):
            return ("global", "Votre lieu est déjà lié à cette source")
        return PcObject.restize_integrity_error(error)

    @property
    def nOffers(self):  # type: ignore [no-untyped-def]
        from pcapi.core.offers.models import Offer

        # pylint: disable=comparison-with-callable
        return (
            Offer.query.filter(Offer.venueId == self.venueId, Offer.isActive == True)
            .filter(Offer.lastProviderId == self.providerId)
            .count()
        )


class CinemaProviderPivot(PcObject, Base, Model):
    """Stores whether a Venue has requested to be synced with a Provider"""

    venueId = Column(BigInteger, ForeignKey("venue.id"), index=False, nullable=True, unique=True)

    venue: sa_orm.Mapped["Venue | None"] = relationship(Venue, foreign_keys=[venueId])

    providerId: int = Column(BigInteger, ForeignKey("provider.id"), nullable=False)

    provider: sa_orm.Mapped["Provider"] = relationship("Provider", foreign_keys=[providerId])

    idAtProvider: str = Column(Text, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "venueId",
            "providerId",
            name="unique_pivot_venue_provider",
        ),
        UniqueConstraint(
            "providerId",
            "idAtProvider",
            name="unique_provider_id_at_provider",
        ),
    )


class CDSCinemaDetails(PcObject, Base, Model):
    """Stores info on the specific login details of a cinema synced with CDS"""

    cinemaProviderPivotId = Column(
        BigInteger, ForeignKey("cinema_provider_pivot.id"), index=False, nullable=True, unique=True
    )

    cinemaProviderPivot: sa_orm.Mapped["CinemaProviderPivot | None"] = relationship(
        CinemaProviderPivot, foreign_keys=[cinemaProviderPivotId]
    )

    cinemaApiToken: str = Column(Text, nullable=False)

    accountId: str = Column(Text, nullable=False)


class AllocineVenueProvider(VenueProvider):
    __tablename__ = "allocine_venue_provider"

    id: int = Column(BigInteger, ForeignKey("venue_provider.id"), primary_key=True)

    isDuo: bool = Column(Boolean, default=True, server_default=true(), nullable=False)

    quantity = Column(Integer, nullable=True)

    internalId: str = Column(Text, nullable=False, unique=True)

    __mapper_args__ = {
        "polymorphic_identity": "allocine_venue_provider",
    }


class AllocineVenueProviderPriceRule(PcObject, Base, Model):
    priceRule: PriceRule = Column(Enum(PriceRule), nullable=False)

    allocineVenueProviderId: int = Column(
        BigInteger, ForeignKey("allocine_venue_provider.id"), index=True, nullable=False
    )

    allocineVenueProvider: sa_orm.Mapped["AllocineVenueProvider"] = relationship(
        "AllocineVenueProvider", foreign_keys=[allocineVenueProviderId], backref="priceRules"
    )

    price: decimal.Decimal = Column(
        Numeric(10, 2), CheckConstraint("price >= 0", name="check_price_is_not_negative"), nullable=False
    )

    UniqueConstraint(
        allocineVenueProviderId,
        priceRule,
        name="unique_allocine_venue_provider_price_rule",
    )

    @staticmethod
    def restize_integrity_error(error: sa_exc.IntegrityError) -> tuple[str, str]:
        if "unique_allocine_venue_provider_price_rule" in str(error.orig):
            return ("global", "Vous ne pouvez avoir qu''un seul prix par catégorie")
        if "check_price_is_not_negative" in str(error.orig):
            return ("global", "Vous ne pouvez renseigner un prix négatif")
        return PcObject.restize_integrity_error(error)

    @staticmethod
    def restize_data_error(data_error: sa_exc.DataError) -> tuple[str, str]:
        if "wrong_price" in str(data_error):
            return ("global", "Le prix doit être un nombre décimal")
        return PcObject.restize_data_error(data_error)


@dataclass
class VenueProviderCreationPayload:
    isDuo: bool | None = None
    price: str | None = None
    quantity: int | None = None
    venueIdAtOfferProvider: str | None = None


@dataclass
class StockDetail:
    products_provider_reference: str
    offers_provider_reference: str
    venue_reference: str
    stocks_provider_reference: str
    available_quantity: int
    price: decimal.Decimal


class AllocinePivot(PcObject, Base, Model):
    venueId: int = Column(BigInteger, ForeignKey("venue.id"), index=False, nullable=False, unique=True)

    venue: sa_orm.Mapped["Venue"] = relationship(Venue, foreign_keys=[venueId])

    theaterId: str = Column(String(20), nullable=False, unique=True)

    internalId: str = Column(Text, nullable=False, unique=True)


class AllocineTheater(PcObject, Base, Model):
    siret = Column(String(14), nullable=True, unique=True)

    theaterId: str = Column(String(20), nullable=False, unique=True)

    internalId: str = Column(Text, nullable=False, unique=True)


class LocalProviderEventType(enum.Enum):
    SyncError = "SyncError"

    SyncPartStart = "SyncPartStart"
    SyncPartEnd = "SyncPartEnd"

    SyncStart = "SyncStart"
    SyncEnd = "SyncEnd"


class LocalProviderEvent(PcObject, Base, Model):
    providerId: int = Column(BigInteger, ForeignKey("provider.id"), nullable=False)
    provider: sa_orm.Mapped["Provider"] = relationship("Provider", foreign_keys=[providerId])
    date: datetime.datetime = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    type: LocalProviderEventType = Column(Enum(LocalProviderEventType), nullable=False)
    payload = Column(String(50), nullable=True)


class BoostCinemaDetails(PcObject, Base, Model):
    """Stores info on the specific login details of a cinema synced with Boost"""

    cinemaProviderPivotId = Column(
        BigInteger, ForeignKey("cinema_provider_pivot.id"), index=False, nullable=True, unique=True
    )
    cinemaProviderPivot: sa_orm.Mapped["CinemaProviderPivot | None"] = relationship(
        CinemaProviderPivot, foreign_keys=[cinemaProviderPivotId]
    )
    cinemaUrl: str = Column(Text, nullable=False)  # including http:// or https:// and trailing /
    username: str = Column(Text, nullable=False)
    password: str = Column(Text, nullable=False)
    token: str | None = Column(Text, nullable=True)
    tokenExpirationDate: datetime.datetime | None = Column(DateTime, nullable=True)


class CGRCinemaDetails(PcObject, Base, Model):
    """Stores info on the specific login details of a cinema synced with CGR"""

    cinemaProviderPivotId = Column(
        BigInteger, ForeignKey("cinema_provider_pivot.id"), index=False, nullable=True, unique=True
    )
    cinemaProviderPivot: sa_orm.Mapped["CinemaProviderPivot | None"] = relationship(
        CinemaProviderPivot, foreign_keys=[cinemaProviderPivotId]
    )
    cinemaUrl: str = Column(Text, nullable=False)
    numCinema: int = Column(Integer, nullable=True)
    password: str = Column(
        Text, nullable=True
    )  # FIXME (yacine-pc) since we already have a row in production, make this column not nullable later
