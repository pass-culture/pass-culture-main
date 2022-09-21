import re


MAINLAND_DEPARTEMENT_CODE_LENGTH = 2
OVERSEAS_DEPARTEMENT_CODE_LENGTH = 3
OVERSEAS_DEPARTEMENT_CODE_START = 97

POSTAL_CODE_REGEX = re.compile(r"^\d[AB0-9]\d{3,4}$")


class PostalCode:
    postalCode: str

    def __init__(self, postalCode: str):
        self.postalCode = postalCode

    def get_departement_code(self) -> str:
        return (
            self.postalCode[:OVERSEAS_DEPARTEMENT_CODE_LENGTH]
            if self._is_overseas_departement()
            else self.postalCode[:MAINLAND_DEPARTEMENT_CODE_LENGTH]
        )

    def _is_overseas_departement(self) -> bool:
        return int(self.postalCode[0:2]) >= OVERSEAS_DEPARTEMENT_CODE_START
