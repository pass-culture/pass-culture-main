""" providable mixin """
from datetime import datetime

from sqlalchemy import BigInteger
from sqlalchemy import CheckConstraint
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship


class ProvidableMixin:
    @declared_attr
    def lastProviderId(cls):  # type: ignore [no-untyped-def] # pylint: disable=no-self-argument
        return Column(BigInteger, ForeignKey("provider.id"), nullable=True)

    @declared_attr
    def lastProvider(cls):  # type: ignore [no-untyped-def] # pylint: disable=no-self-argument
        return relationship("Provider", foreign_keys=[cls.lastProviderId])

    idAtProviders = Column(
        String(70),
        CheckConstraint(
            '"lastProviderId" IS NULL OR "idAtProviders" IS NOT NULL',
            name="check_providable_with_provider_has_idatproviders",
        ),
        nullable=True,
        unique=True,
    )

    dateModifiedAtLastProvider = Column(DateTime, nullable=True, default=datetime.utcnow)

    fieldsUpdated = Column(ARRAY(String(100)), nullable=False, default=[], server_default="{}")
