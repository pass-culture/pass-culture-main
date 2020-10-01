# encoding: utf-8

from functools import partial
import re
import string

from schwifty.bic import BIC
from schwifty.common import Base
from schwifty import registry


_spec_to_re = {
    'n': r'\d',
    'a': r'[A-Z]',
    'c': r'[A-Za-z0-9]',
    'e': r' '
}

_alphabet = string.digits + string.ascii_uppercase


def _get_iban_spec(country_code):
    try:
        return registry.get('iban')[country_code]
    except KeyError:
        raise ValueError("Unknown country-code '{}'".format(country_code))


def numerify(string):
    return int(''.join(str(_alphabet.index(c)) for c in string))


def code_length(spec, code_type):
    start, end = spec['positions'][code_type]
    return end - start


class IBAN(Base):
    """The IBAN object.

    Examples:

        You create a new IBAN object by supplying an IBAN code in text form. The IBAN
        is validated behind the scenes and you can then access all relevant components
        as properties::

            >>> iban = IBAN('DE89 3704 0044 0532 0130 00')
            >>> iban.account_code
            '0532013000'
            >>> iban.bank_code
            '37040044'
            >>> iban.country_code
            'DE'
            >>> iban.checksum_digits
            '89'


    Args:
        iban (str): The IBAN code.
        allow_invalid (bool): If set to `True` IBAN validation is skipped on instantiation.
    """

    def __init__(self, iban, allow_invalid=False):
        super(IBAN, self).__init__(iban)
        if self.checksum_digits == '??':
            self._code = self.country_code + self._calc_checksum_digits() + self.bban

        if not allow_invalid:
            self.validate()

    def _calc_checksum_digits(self):
        return '{:02d}'.format(98 - (numerify(self.bban + self.country_code) * 100) % 97)

    @classmethod
    def generate(cls, country_code, bank_code, account_code):
        """Generate an IBAN from it's components.

        If the bank-code and/or account-number have less digits than required by their
        country specific representation, the respective component is padded with zeros.

        Examples:

            To generate an IBAN do the following::

                >>> bank_code = '37040044'
                >>> account_code = '532013000'
                >>> iban = IBAN.generate('DE', bank_code, account_code)
                >>> iban.formatted
                'DE89 3704 0044 0532 0130 00'

        Args:
            country_code (str): The ISO 3166 alpha-2 country code.
            bank_code (str): The country specific bank-code.
            account_code (str): The customer specific account-code.
        """
        spec = _get_iban_spec(country_code)
        bank_code_length = code_length(spec, 'bank_code')
        branch_code_length = code_length(spec, 'branch_code')
        bank_and_branch_code_length = bank_code_length + branch_code_length
        account_code_length = code_length(spec, 'account_code')

        if len(bank_code) > bank_and_branch_code_length:
            raise ValueError(
                "Bank code exceeds maximum size {}".format(bank_and_branch_code_length))

        if len(account_code) > account_code_length:
            raise ValueError(
                "Account code exceeds maximum size {}".format(account_code_length))

        bank_code = bank_code.rjust(bank_and_branch_code_length, '0')
        account_code = account_code.rjust(account_code_length, '0')
        iban = country_code + '??' + bank_code + account_code
        return cls(iban)

    def validate(self):
        self._validate_characters()
        self._validate_length()
        self._validate_format()
        self._validate_checksum()
        return True

    def _validate_characters(self):
        if not re.match(r'[A-Z]{2}\d{2}[A-Z]*', self.compact):
            raise ValueError("Invalid characters in IBAN {}".format(self.compact))

    def _validate_checksum(self):
        if self.numeric % 97 != 1:
            raise ValueError("Invalid checksum digits")

    def _validate_length(self):
        if self.spec['iban_length'] != self.length:
            raise ValueError("Invalid IBAN length")

    def _validate_format(self):
        if not self.spec['regex'].match(self.bban):
            raise ValueError("Invalid BBAN structure: '{}' doesn't match '{}''".format(
                self.bban, self.spec['bban_spec']))

    @property
    def numeric(self):
        """int: A numeric represenation of the IBAN."""
        return numerify(self.bban + self.compact[:4])

    @property
    def formatted(self):
        """str: The IBAN formatted in blocks of 4 digits."""
        return ' '.join(self.compact[i:i + 4] for i in range(0, len(self.compact), 4))

    @property
    def spec(self):
        """dict: The country specific IBAN specification."""
        return _get_iban_spec(self.country_code)

    @property
    def bic(self):
        """BIC: The BIC associated to the IBAN´s bank-code."""
        return BIC.from_bank_code(self.country_code, self.bank_code)

    def _get_code(self, code_type):
        start, end = self.spec['positions'][code_type]
        return self.bban[start:end]

    bban = property(partial(Base._get_component, start=4),
                    doc="str: The BBAN part of the IBAN.")
    country_code = property(partial(Base._get_component, start=0, end=2),
                            doc="str: ISO 3166 alpha-2 country code.")
    checksum_digits = property(partial(Base._get_component, start=2, end=4),
                               doc="str: Two digit checksum of the IBAN.")
    bank_code = property(partial(_get_code, code_type='bank_code'),
                         doc="str: The country specific bank-code.")
    branch_code = property(partial(_get_code, code_type='branch_code'),
                           doc="str or None: The branch-code of the bank if available.")
    account_code = property(partial(_get_code, code_type='account_code'),
                            doc="str: The customer specific account-code")


def add_bban_regex(country, spec):
    bban_spec = spec['bban_spec']
    spec_re = r'(\d+)(!)?([{}])'.format(''.join(_spec_to_re.keys()))

    def convert(match):
        quantifier = ('{%s}' if match.group(2) else '{1,%s}') % match.group(1)
        return _spec_to_re[match.group(3)] + quantifier
    spec['regex'] = re.compile('^{}$'.format(re.sub(spec_re, convert, bban_spec)))
    return spec


registry.manipulate('iban', add_bban_regex)
