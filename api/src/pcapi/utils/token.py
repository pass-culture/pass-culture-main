import random
import string


# For historical reasons, use the alphabet of Base 32 (A-Z, 2-7), and
# remove letters O and I to avoid misreadings.
ALPHABET = string.ascii_uppercase + string.digits
ALPHABET = ALPHABET.translate(str.maketrans("", "", "0189IO"))


def random_token(length=6):
    return "".join(random.choices(ALPHABET, k=length))
