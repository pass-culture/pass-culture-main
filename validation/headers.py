from utils.config import IS_DEV, IS_STAGING


def check_header_validity(header, endpoint):
    endpoint_exceptions = _get_endpoint_exceptions()
    if endpoint in endpoint_exceptions:
        return True
    white_list = _get_header_whitelist()
    return header in white_list


def _get_header_whitelist():
    if IS_DEV:
        return ['http://localhost:3000', 'https://localhost:3000', 'localhost:3000']
    if IS_STAGING:
        return ['pro.passculture-staging.beta.gouv.fr', 'app.passculture-staging.beta.gouv.fr',
                'http://pro.passculture-staging.beta.gouv.fr', 'http://app.passculture-staging.beta.gouv.fr',
                'https://pro.passculture-staging.beta.gouv.fr', 'https://app.passculture-staging.beta.gouv.fr']
    else:
        return ['app.passculture.beta.gouv.fr', 'pro.passculture.beta.gouv.fr', 'http://app.passculture.beta.gouv.fr',
                'http://pro.passculture.beta.gouv.fr', 'https://app.passculture.beta.gouv.fr',
                'https://pro.passculture.beta.gouv.fr']


def _get_endpoint_exceptions():
    return ['patch_booking_by_token', 'get_booking_by_token']
