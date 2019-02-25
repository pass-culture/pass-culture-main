from schwifty import IBAN, BIC
from sqlalchemy import Column, BigInteger, ForeignKey, String, Integer
from sqlalchemy.orm import relationship

from models.api_errors import ApiErrors
from models.offerer import Offerer
from models.db import Model
from models.pc_object import PcObject
from models.providable_mixin import ProvidableMixin


class BankInformation(PcObject,
                      Model,
                      ProvidableMixin):
    offererId = Column(BigInteger,
                       ForeignKey("offerer.id"),
                       index=True,
                       nullable=True)

    offerer = relationship('Offerer',
                           foreign_keys=[offererId],
                           uselist=False,
                           backref='bankInformation')

    venueId = Column(BigInteger,
                     ForeignKey("venue.id"),
                     index=True,
                     nullable=True)

    venue = relationship('Venue',
                         foreign_keys=[venueId],
                         uselist=False,
                         backref='bankInformation')

    iban = Column(String(27),
                  nullable=False)

    bic = Column(String(11),
                 nullable=False)

    applicationId = Column(Integer,
                           nullable=False)

    def check_bank_account_information(self, api_errors: ApiErrors) -> ApiErrors:
        try:
            IBAN(self.iban)
        except (ValueError, TypeError):
            api_errors.addError('iban', f"L'IBAN renseigné (\"{self.iban}\") est invalide")

        try:
            BIC(self.bic)
        except (ValueError, TypeError):
            api_errors.addError('bic', f"Le BIC renseigné (\"{self.bic}\") est invalide")


    def errors(self):
        api_errors = super(BankInformation, self).errors()
        self.check_bank_account_information(api_errors)

        return api_errors