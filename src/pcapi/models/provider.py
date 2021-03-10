""" provider """
from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import String

from pcapi.models.db import Model
from pcapi.models.deactivable_mixin import DeactivableMixin
from pcapi.models.pc_object import PcObject


class Provider(PcObject, Model, DeactivableMixin):
    id = Column(BigInteger, primary_key=True)

    name = Column(String(90), index=True, nullable=False)

    localClass = Column(
        String(60),
        nullable=True,
        unique=True,
    )

    enabledForPro = Column(Boolean, nullable=False, default=False)

    requireProviderIdentifier = Column(Boolean, nullable=False, default=True)

    @property
    def isAllocine(self) -> bool:
        from pcapi import local_providers  # avoid import loop

        return self.localClass == local_providers.AllocineStocks.__name__
