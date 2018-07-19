""" providable mixin """
from datetime import datetime
from sqlalchemy import BigInteger,\
                       CheckConstraint,\
                       Column,\
                       DateTime,\
                       ForeignKey,\
                       String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr

from models.versioned_mixin import VersionedMixin


class ProvidableMixin(VersionedMixin):

    @declared_attr
    def lastProviderId(cls):
        return Column(BigInteger,
                      ForeignKey("provider.id"),
                      nullable=True)

    @declared_attr
    def lastProvider(cls):
        return relationship('Provider',
                            foreign_keys=[cls.lastProviderId])

    idAtProviders = Column(String(70),
                           CheckConstraint('"lastProviderId" IS NULL OR "idAtProviders" IS NOT NULL',
                                                 name='check_providable_with_provider_has_idatproviders'),
                           nullable=True,
                           unique=True)

    dateModifiedAtLastProvider = Column(DateTime,
                                        nullable=True,
                                        default=datetime.utcnow)
