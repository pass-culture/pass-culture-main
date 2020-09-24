from base64 import b32encode


class Identifier:
    def __init__(self, identifier: int):
        self.identifier: int = identifier

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Identifier):
            return False

        return self.identifier == other.identifier

    def humanize(self) -> str:
        identifier_in_bytes = self.identifier.to_bytes((self.identifier.bit_length() + 7) // 8, 'big')
        identifier_in_base32 = b32encode(identifier_in_bytes)

        return identifier_in_base32.decode('ascii') \
            .replace('O', '8') \
            .replace('I', '9') \
            .rstrip('=')
