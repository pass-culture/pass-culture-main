from schwifty import IBAN, BIC
from sqlalchemy import Column, String, CheckConstraint

from models import ApiErrors


class HasBankInformationMixin(object):
    iban = Column(
        String(27),
        nullable=True)

    bic = Column(String(11),
                 CheckConstraint('(iban IS NULL AND bic IS NULL) OR (iban IS NOT NULL AND bic IS NOT NULL)',
                                 name='check_iban_and_bic_xor_not_iban_and_not_bic'),
                 nullable=True)

    def check_bank_account_information(self, api_errors: ApiErrors) -> ApiErrors:
        if self.iban and self.bic:

            try:
                IBAN(self.iban)
            except ValueError:
                api_errors.addError('iban', "L'IBAN saisi est invalide")

            try:
                BIC(self.bic)
            except ValueError:
                api_errors.addError('bic', "Le BIC saisi est invalide")

        if not self.bic and self.iban:
            api_errors.addError('bic', "Le BIC es manquant")
        if not self.iban and self.bic:
            api_errors.addError('iban', "L'IBAN es manquant")
