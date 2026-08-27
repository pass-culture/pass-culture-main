import hmac
import typing
from datetime import datetime
from datetime import timedelta
from decimal import Decimal
from hashlib import sha256

from cryptography.hazmat.primitives import serialization
from dateutil import tz

import pcapi.utils.date as date_utils
from pcapi import settings
from pcapi.core.categories import subcategories


if typing.TYPE_CHECKING:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    from pcapi.core.bookings import schemas

QR_CODE_PASS_CULTURE_VERSION = "v3"

SUBCATEGORY_IDS_WITH_REACTION_AVAILABLE = [
    subcategories.SEANCE_CINE.id,
    subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
    subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id,
    subcategories.LIVRE_PAPIER.id,
]

SUGGEST_REACTION_COOLDOWN_IN_SECONDS = {
    subcategories.SEANCE_CINE.id: settings.SUGGEST_REACTION_SHORT_COOLDOWN_IN_SECONDS,
    subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id: settings.SUGGEST_REACTION_LONG_COOLDOWN_IN_SECONDS,
    subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id: settings.SUGGEST_REACTION_LONG_COOLDOWN_IN_SECONDS,
    subcategories.LIVRE_PAPIER.id: settings.SUGGEST_REACTION_LONG_COOLDOWN_IN_SECONDS,
}


def get_qr_code_data(booking_token: str) -> str:
    return f"PASSCULTURE:{QR_CODE_PASS_CULTURE_VERSION};TOKEN:{booking_token}"


def generate_hmac_signature(
    hmac_key: str,
    data: str,
) -> str:
    """
    Generate the signature of the notification data using the hmac_key.
    """
    return hmac.new(hmac_key.encode(), data.encode(), sha256).hexdigest()


def generate_ed25519_signature(data: str, private_key: str, password: str | None = None) -> str:
    """
    Generate the signature of the notification data using the the given ed25519 private key.

    private_key must be provided as a PEM encoded PKCS8 format.
    """
    if not private_key:
        return ""
    deserialized_key = serialization.load_pem_private_key(
        data=private_key.encode("utf-8"),
        password=password.encode("utf-8") if password else None,
    )
    # cannot use isinstance due to binding problems
    if not type(deserialized_key).__name__ == "Ed25519PrivateKey":
        raise ValueError("the provided key is not a valid ed25519 private key")
    deserialized_key = typing.cast("Ed25519PrivateKey", deserialized_key)

    return deserialized_key.sign(data.encode("utf-8")).hex()


def _apply_departement_timezone(naive_datetime: datetime | None, departement_code: str | None) -> datetime | None:
    if naive_datetime is None or departement_code is None:
        return None
    departement_tz = tz.gettz(date_utils.get_department_timezone(departement_code))
    return naive_datetime.astimezone(departement_tz)


def convert_booking_dates_utc_to_venue_timezone(
    date_without_timezone: datetime | None,
    booking: "schemas.ExportBookingsQueryResult | schemas.GetBookingsQueryResult",
) -> datetime | None:
    if booking.offerDepartmentCode:
        department_code = booking.offerDepartmentCode
        return _apply_departement_timezone(naive_datetime=date_without_timezone, departement_code=department_code)
    return _apply_departement_timezone(
        naive_datetime=date_without_timezone, departement_code=booking.venueDepartmentCode
    )


def get_cooldown_datetime_by_subcategories(sub_category_id: str) -> datetime:
    return date_utils.get_naive_utc_now() - timedelta(
        seconds=SUGGEST_REACTION_COOLDOWN_IN_SECONDS.get(sub_category_id, 0)
    )


DEFAULT_PACIFIC_FRANC_TO_EURO_RATE = 0.00838


def convert_euro_to_pacific_franc(price_in_euro: Decimal) -> Decimal:
    """
    Convertit un montant en euros en francs pacifiques (CFP) avec arrondi par tranche de 5 CFP.
    """
    result = float(price_in_euro) / DEFAULT_PACIFIC_FRANC_TO_EURO_RATE
    result = round(result / 5) * 5
    return Decimal(result)
