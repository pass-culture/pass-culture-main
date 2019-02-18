import os

from utils.config import IS_PROD


def feature_paid_offers_enabled():
    return True


def feature_send_mail_to_users_enabled():
    return IS_PROD


def feature_cron_send_final_booking_recaps_enabled():
    return os.environ.get('CRON_SEND_FINAL_BOOKING', False)


def feature_cron_generate_and_send_payments():
    return os.environ.get('CRON_GENERATE_AND_SEND_PAYMENTS', False)


def feature_cron_send_wallet_balances():
    return os.environ.get('CRON_SEND_WALLET_BALANCES', False)


def feature_cron_retrieve_offerers_bank_information():
    return os.environ.get('CRON_RETRIEVE_OFFERERS_BANK_INFORMATION', False)
