from utils.config import IS_DEV, IS_PROD


def feature_paid_offers_enabled():
    return True

def feature_send_mail_to_users_enabled():
    return IS_PROD
