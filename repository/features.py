from utils.config import IS_DEV, IS_STAGING


def feature_paid_offers_enabled():
    return IS_DEV

def feature_send_mail_to_users_enabled():
    return not (IS_DEV or IS_STAGING)
