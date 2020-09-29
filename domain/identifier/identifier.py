from base64 import b32encode

from utils.human_ids import dehumanize


class NonStricltyPositiveIdentifierException(Exception):
    def __init__(self):
        super().__init__('Identifier should be a strictly positive number')


class Identifier:
    def __init__(self, identifier: int):
        if identifier <= 0:
            raise NonStricltyPositiveIdentifierException()
        self._identifier: int = identifier

    @staticmethod
    def from_scrambled_id(scrambled_identifier: str):
        return Identifier(dehumanize(scrambled_identifier))

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
