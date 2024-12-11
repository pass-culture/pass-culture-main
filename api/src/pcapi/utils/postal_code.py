import re


MAINLAND_DEPARTEMENT_CODE_LENGTH = 2
OVERSEAS_DEPARTEMENT_CODE_LENGTH = 3
OVERSEAS_DEPARTEMENT_CODE_START = 97

SAINT_BARTHELEMY_POSTAL_CODE = "97133"
SAINT_BARTHELEMY_DEPARTEMENT_CODE = "977"
SAINT_MARTIN_POSTAL_CODE = "97150"
SAINT_MARTIN_DEPARTEMENT_CODE = "978"

POSTAL_CODE_REGEX = re.compile(r"^\d[AB0-9]\d{3,4}$")


class PostalCode:
    postalCode: str

    def __init__(self, postalCode: str):
        self.postalCode = postalCode

    def get_departement_code(self) -> str:
        if self._is_overseas_departement():
            if self.postalCode == SAINT_BARTHELEMY_POSTAL_CODE:
                return SAINT_BARTHELEMY_DEPARTEMENT_CODE
            if self.postalCode == SAINT_MARTIN_POSTAL_CODE:
                return SAINT_MARTIN_DEPARTEMENT_CODE
            return self.postalCode[:OVERSEAS_DEPARTEMENT_CODE_LENGTH]
        return self.postalCode[:MAINLAND_DEPARTEMENT_CODE_LENGTH]

    def _is_overseas_departement(self) -> bool:
        return int(self.postalCode[0:2]) >= OVERSEAS_DEPARTEMENT_CODE_START
