import binascii
from base64 import b32encode, b32decode


class NonStricltyPositiveIdentifierException(Exception):
    def __init__(self):
        super().__init__('Identifier should be a strictly positive number')


class NonProperlyFormattedScrambledId(Exception):
    def __init__(self, faulty_id):
        super().__init__(f'Scrambled identifier "{faulty_id}" is not properly formatted')


class Identifier:
    def __init__(self, identifier: int):
        if identifier <= 0:
            raise NonStricltyPositiveIdentifierException()
        self._identifier: int = identifier

    @staticmethod
    def from_scrambled_id(scrambled_identifier: str):
        if scrambled_identifier is None:
            return None
        missing_padding = len(scrambled_identifier) % 8
        if missing_padding != 0:
            scrambled_identifier += '=' * (8 - missing_padding)
        try:
            xbytes = b32decode(scrambled_identifier.replace('8', 'O').replace('9', 'I'))
            return Identifier(int.from_bytes(xbytes, 'big'))
        except binascii.Error:
            raise NonProperlyFormattedScrambledId(scrambled_identifier)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Identifier):
            return False

        return self._identifier == other._identifier

    def persisted(self) -> int:
        return self._identifier

    def scrambled(self) -> str:
        identifier_in_bytes = self._identifier.to_bytes((self._identifier.bit_length() + 7) // 8, 'big')
        identifier_in_base32 = b32encode(identifier_in_bytes)

        return identifier_in_base32.decode('ascii') \
            .replace('O', '8') \
            .replace('I', '9') \
            .rstrip('=')
