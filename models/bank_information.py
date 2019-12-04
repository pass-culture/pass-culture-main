from schwifty import IBAN, BIC
from sqlalchemy import Column, BigInteger, ForeignKey, String, Integer
from sqlalchemy.orm import relationship, backref

from models.versioned_mixin import VersionedMixin
from models.db import Model
from models.pc_object import PcObject
from models.providable_mixin import ProvidableMixin


class BankInformation(PcObject, Model, ProvidableMixin, VersionedMixin):
    offererId = Column(BigInteger,
                       ForeignKey("offerer.id"),
                       index=True,
                       nullable=True)

    offerer = relationship('Offerer',
                           foreign_keys=[offererId],
                           backref=backref('bankInformation', uselist=False))

    venueId = Column(BigInteger,
                     ForeignKey("venue.id"),
                     index=True,
                     nullable=True)

    venue = relationship('Venue',
                         foreign_keys=[venueId],
                         backref=backref('bankInformation', uselist=False))

    iban = Column(String(27),
                  nullable=False)

    bic = Column(String(11),
                 nullable=False)

    applicationId = Column(Integer,
                           nullable=False)

    def errors(self):
        api_errors = super(BankInformation, self).errors()
        if api_errors.errors:
            return api_errors
        try:
            IBAN(self.iban)
        except (ValueError, TypeError):
            api_errors.add_error('iban', f"L'IBAN renseigné (\"{self.iban}\") est invalide")

        try:
            BIC(self.bic)
        except (ValueError, TypeError):
            api_errors.add_error('bic', f"Le BIC renseigné (\"{self.bic}\") est invalide")

        return api_errors
