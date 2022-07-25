import secrets
import string


# For historical reasons, use the alphabet of Base 32 (A-Z, 2-7), and
# remove letters O and I to avoid misreadings.
ALPHABET = string.ascii_uppercase + string.digits
ALPHABET = ALPHABET.translate(str.maketrans("", "", "0189IO"))


def random_token(length: int = 6) -> str:
    """Generate a token.

    This function uses a limited set of characters. If you want to
    generate a secret, you should rather use the ``secrets`` module.
    """
    return "".join([secrets.choice(ALPHABET) for i in range(length)])
