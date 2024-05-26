from hashlib import sha256
import hmac


QR_CODE_PASS_CULTURE_VERSION = "v3"


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
