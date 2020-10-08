from pcapi.models import ApiKey


def find_api_key_by_value(key: str) -> ApiKey:
    return ApiKey.query.filter_by(value=key).first()
