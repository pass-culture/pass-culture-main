""" providable mixin """
from datetime import datetime

from bs4 import element
from sqlalchemy import BigInteger, \
    CheckConstraint, \
    Column, \
    DateTime, \
    ForeignKey, \
    String, JSON
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from models.api_errors import ApiErrors


class ProvidableMixin:

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
                           unique=True,
                           index=True)

    dateModifiedAtLastProvider = Column(DateTime,
                                        nullable=True,
                                        default=datetime.utcnow)

    fieldsUpdated = Column(ARRAY(String),
                           default=[])

    def ensure_can_be_updated(self):
        if self.lastProvider:
            errors = ApiErrors()
            errors.add_error(
                'global',
                'not allowed because data come from provider ' + element.lastProvider.name
            )
            raise errors
