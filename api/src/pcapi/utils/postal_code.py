import re


MAINLAND_DEPARTEMENT_CODE_LENGTH = 2
OVERSEAS_DEPARTEMENT_CODE_LENGTH = 3
OVERSEAS_DEPARTEMENT_CODE_START = 97

SAINT_BARTHELEMY_POSTAL_CODE = "97133"
SAINT_BARTHELEMY_DEPARTEMENT_CODE = "977"
SAINT_MARTIN_POSTAL_CODE = "97150"
SAINT_MARTIN_DEPARTEMENT_CODE = "978"

POSTAL_CODE_REGEX = re.compile(r"^\d[AB0-9]\d{3,4}$")

NORTH_CALEDONIAN_POSTAL_CODES = [
    "98811",  # Bélep
    "98813",  # Canala
    "98815",  # Hienghène
    "98816",  # Houaïlou
    "98817",  # Kaala-Gomen
    "98818",  # Kouaoua
    "98821",  # Ouégoa
    "98822",  # Poindimié
    "98823",  # Ponérihouen
    "98824",  # Pouébo
    "98825",  # Pouembout
    "98826",  # Poum
    "98831",  # Touho
    "98833",  # Voh
    "98850",  # Koumac
    "98860",  # Koné
]
LOYALTY_ISLANDS_POSTAL_CODES = [
    "98814",  # Fayaoué
    "98820",  # Wé
    "98828",  # Tadine
    "98878",  # La Roche
    "98884",  # Chépénéhé
    "98885",  # Mou
]
INELIGIBLE_POSTAL_CODES = NORTH_CALEDONIAN_POSTAL_CODES + LOYALTY_ISLANDS_POSTAL_CODES


class PostalCode:
    postalCode: str

    def __init__(self, postalCode: str):
        self.postalCode = postalCode

    def get_departement_code(self) -> str:
        # This method must be kept aligned with SQL function postal_code_to_department_code
        if self._is_overseas_departement():
            if self.postalCode == SAINT_BARTHELEMY_POSTAL_CODE:
                return SAINT_BARTHELEMY_DEPARTEMENT_CODE
            if self.postalCode == SAINT_MARTIN_POSTAL_CODE:
                return SAINT_MARTIN_DEPARTEMENT_CODE
            return self.postalCode[:OVERSEAS_DEPARTEMENT_CODE_LENGTH]
        return self.postalCode[:MAINLAND_DEPARTEMENT_CODE_LENGTH]

    def _is_overseas_departement(self) -> bool:
        return int(self.postalCode[0:2]) >= OVERSEAS_DEPARTEMENT_CODE_START
