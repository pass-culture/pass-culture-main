from sqlalchemy import Column, Enum, BigInteger, ForeignKey, Numeric, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship

from local_providers.price_rule import PriceRule
from models import PcObject
from models.db import Model


class AllocineVenueProviderPriceRule(PcObject, Model):
    priceRule = Column(Enum(PriceRule), nullable=False)

    allocineVenueProviderId = Column(BigInteger,
                                     ForeignKey('allocine_venue_provider.id'),
                                     index=True,
                                     nullable=False)

    allocineVenueProvider = relationship('AllocineVenueProvider',
                                         foreign_keys=[allocineVenueProviderId],
                                         backref='priceRules')

    price = Column(Numeric(10, 2),
                   CheckConstraint('price >= 0', name='check_price_is_not_negative'),
                   nullable=False)

    __table_args__ = (
        UniqueConstraint(
            'allocineVenueProviderId',
            'priceRule',
            name='unique_venue_provider_price_rule',
        ),
    )

    @staticmethod
    def restize_integrity_error(internal_error):
        if 'unique_venue_provider_price_rule' in str(internal_error.orig):
            return ['global', "Vous ne pouvez avoir qu''un seul prix par catégorie"]
        if 'check_price_is_not_negative' in str(internal_error.orig):
            return ['global', "Vous ne pouvez renseigner un prix négatif"]
        return PcObject.restize_integrity_error(internal_error)

    @staticmethod
    def restize_data_error(data_error):
        if 'wrong_price' in str(data_error):
            return ['global', 'Le prix doit être un nombre décimal']
        return PcObject.restize_integrity_error(data_error)
