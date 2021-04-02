from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import CheckConstraint
from sqlalchemy import Column
from sqlalchemy import String

from pcapi.infrastructure.repository.stock_provider.provider_api import ProviderAPI
from pcapi.models.db import Model
from pcapi.models.deactivable_mixin import DeactivableMixin
from pcapi.models.pc_object import PcObject


class Provider(PcObject, Model, DeactivableMixin):
    id = Column(BigInteger, primary_key=True)

    name = Column(String(90), index=True, nullable=False)

    localClass = Column(
        String(60),
        CheckConstraint(
            '("localClass" IS NOT NULL AND "apiUrl" IS NULL) OR ("localClass" IS NULL AND "apiUrl" IS NOT NULL)',
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
