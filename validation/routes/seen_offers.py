from models import ApiErrors


class PayloadMissing(ApiErrors):
    pass


def check_payload_is_valid(payload: dict):
    if ("offerId" not in payload) or ("userId" not in payload):
        raise PayloadMissing({'global': ['Données manquantes']})
