from utils.config import IS_DEV, IS_STAGING


def check_header_validity(header, wh):
    white_list = get_header_whitelist()
    return header in white_list


def get_header_whitelist():
    if IS_DEV:
        return ['localhost']
    if IS_STAGING:
        return ['pro.passculture-staging.beta.gouv.fr', 'app.passculture-staging.beta.gouv.fr']
    else:
        return ['app.passculture.beta.gouv.fr', 'pro.passculture.beta.gouv.fr']