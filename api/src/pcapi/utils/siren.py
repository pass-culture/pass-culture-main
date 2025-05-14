import re


SIREN_LENGTH = 9
SIRET_LENGTH = 14

# New Caledonia
RID7_LENGTH = 7
RIDET_LENGTH = 10
# In order to write RID7/RIDET in SIREN/SIRET columns, choice has been made to prefix ISEE identifiers with "NC" in the
# database. So the model is not changed with registrer management. Detection is made with this pattern.
NEW_CALEDONIA_SIREN_PREFIX = "NC"
NEW_CALEDONIA_SIREN_PREFIX_LEN = len(NEW_CALEDONIA_SIREN_PREFIX)
NEW_CALEDONIA_SIRET_PADDING_CHAR = "X"
NEW_CALEDONIA_SIREN_RE = r"^NC\d{7}$"
NEW_CALEDONIA_SIRET_RE = r"^NC\d{10}XX$"
SIRET_OR_RIDET_RE = r"^(\d{14}|NC\d{10}XX)$"


def _compute_luhn_sum(digits: str, total_length: int) -> int:
    """
    Last digit in a SIREN or SIRET code is a check digit calculated using the Luhn formula:
    https://fr.wikipedia.org/wiki/Syst%C3%A8me_d%27identification_du_r%C3%A9pertoire_des_entreprises
    https://fr.wikipedia.org/wiki/Formule_de_Luhn
    """
    parity = total_length % 2
    result = 0
    for i, digit in enumerate(digits):
        value = int(digit)
        if (i + 1) % 2 == parity:
            result += value
        elif value > 4:
            result += 2 * value - 9
        else:
            result += 2 * value
    return result % 10


def complete_siren_or_siret(digits: str) -> str:
    if len(digits) not in (SIREN_LENGTH - 1, SIRET_LENGTH - 1):
        raise ValueError("Unexpected length")

    return digits + str((10 - _compute_luhn_sum(digits, len(digits) + 1)) % 10)


def is_valid_siren(digits: str) -> bool:
    if len(digits) != SIREN_LENGTH or not digits.isnumeric():
        return False

    return _compute_luhn_sum(digits, SIREN_LENGTH) == 0


def is_valid_siret(digits: str) -> bool:
    if len(digits) != SIRET_LENGTH or not digits.isnumeric():
        return False

    if _compute_luhn_sum(digits, SIRET_LENGTH) == 0:
        return True

    if digits[:9] == "356000000":
        # La Poste, special case described here:
        # https://fr.wikipedia.org/wiki/Syst%C3%A8me_d%27identification_du_r%C3%A9pertoire_des_%C3%A9tablissements
        return sum(int(digit) for digit in digits) % 5 == 0

    return False


def is_rid7(siren: str) -> bool:
    return bool(re.match(NEW_CALEDONIA_SIREN_RE, siren))


def is_ridet(siret: str | None) -> bool:
    return bool(siret and re.match(NEW_CALEDONIA_SIRET_RE, siret))


def is_siret_or_ridet(data: str) -> bool:
    return bool(re.match(SIRET_OR_RIDET_RE, data))


def siren_to_rid7(siren: str) -> str:
    return siren[NEW_CALEDONIA_SIREN_PREFIX_LEN:]


def rid7_to_siren(rid7: str) -> str:
    return NEW_CALEDONIA_SIREN_PREFIX + rid7


def siret_to_ridet(siret: str) -> str:
    return siret[NEW_CALEDONIA_SIREN_PREFIX_LEN:].strip(NEW_CALEDONIA_SIRET_PADDING_CHAR)


def ridet_to_siret(ridet: str) -> str:
    return (NEW_CALEDONIA_SIREN_PREFIX + ridet).ljust(SIRET_LENGTH, NEW_CALEDONIA_SIRET_PADDING_CHAR)
