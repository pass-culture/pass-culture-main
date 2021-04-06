from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import CheckConstraint
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy import and_
from sqlalchemy import case
from sqlalchemy import exists
from sqlalchemy import select
from sqlalchemy.orm import column_property
from sqlalchemy.orm import relationship

from pcapi.core.offers.models import Offer
from pcapi.infrastructure.repository.stock_provider.provider_api import ProviderAPI
from pcapi.models.db import Model
from pcapi.models.deactivable_mixin import DeactivableMixin
from pcapi.models.pc_object import PcObject
from pcapi.models.providable_mixin import ProvidableMixin


class Provider(PcObject, Model, DeactivableMixin):
    id = Column(BigInteger, primary_key=True)

    name = Column(String(90), index=True, nullable=False)

    localClass = Column(
        String(60),
        CheckConstraint(
            '("localClass" IS NOT NULsrc/pcapi/core/offerers/factories.pyL AND "apiUrl" IS NULL) OR ("localClass" IS NULL AND "apiUrl" IS NOT NULL)',
            name="check_provider_has_localclass_or_apiUrl",
        ),
        nullable=True,
        unique=True,
    )

    # Presence of this fields signify the provider implements pass Culture's provider API
    apiUrl = Column(String, nullable=True)

    authToken = Column(String, nullable=True)

    enabledForPro = Column(Boolean, nullable=False, default=False)

    requireProviderIdentifier = Column(Boolean, nullable=False, default=True)

    @property
    def isAllocine(self) -> bool:
        from pcapi import local_providers  # avoid import loop

        return self.localClass == local_providers.AllocineStocks.__name__

    @property
    def implements_provider_api(self) -> bool:
        return self.apiUrl != None

    def getProviderAPI(self) -> ProviderAPI:
        return ProviderAPI(
            api_url=self.apiUrl,
            name=self.name,
            authentication_token=self.authToken,
        )


class VenueProvider(PcObject, Model, ProvidableMixin, DeactivableMixin):
    venueId = Column(BigInteger, ForeignKey("venue.id"), nullable=False)

    venue = relationship("Venue", foreign_keys=[venueId])

    providerId = Column(BigInteger, ForeignKey("provider.id"), index=True, nullable=False)

    provider = relationship("Provider", foreign_keys=[providerId])

    venueIdAtOfferProvider = Column(String(70))

    lastSyncDate = Column(DateTime, nullable=True)

    syncWorkerId = Column(String(24), nullable=True)

    isFromAllocineProvider = column_property(
        exists(select([Provider.id]).where(and_(Provider.id == providerId, Provider.localClass == "AllocineStocks")))
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
    def restize_integrity_error(internal_error):
        if "unique_venue_provider" in str(internal_error.orig):
            return ["global", "Votre lieu est déjà lié à cette source"]
        return PcObject.restize_integrity_error(internal_error)

    @property
    def nOffers(self):
        # pylint: disable=comparison-with-callable
        return Offer.query.filter(Offer.venueId == self.venueId).filter(Offer.lastProviderId == self.providerId).count()
