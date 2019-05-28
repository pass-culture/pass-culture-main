import os

from utils.config import IS_PROD, IS_INTEGRATION


def feature_paid_offers_enabled() -> bool:
    return True


def feature_send_mail_to_users_enabled() -> bool:
    return IS_PROD or IS_INTEGRATION


def feature_cron_send_final_booking_recaps_enabled() -> bool:
    return os.environ.get('CRON_SEND_FINAL_BOOKING', False)


def feature_cron_generate_and_send_payments() -> bool:
    return os.environ.get('CRON_GENERATE_AND_SEND_PAYMENTS', False)


def feature_cron_send_wallet_balances() -> bool:
    return os.environ.get('CRON_SEND_WALLET_BALANCES', False)


def feature_cron_retrieve_offerers_bank_information() -> bool:
    return os.environ.get('CRON_RETRIEVE_OFFERERS_BANK_INFORMATION', False)


def feature_cron_synchronize_titelive_things() -> bool:
    return os.environ.get('CRON_SYNCHRONIZE_TITELIVE_THINGS', False)


def feature_cron_synchronize_titelive_descriptions() -> bool:
    return os.environ.get('CRON_SYNCHRONIZE_TITELIVE_DESCRIPTIONS', False)


def feature_cron_synchronize_titelive_thumbs() -> bool:
    return os.environ.get('CRON_SYNCHRONIZE_TITELIVE_THUMBS', False)


def feature_cron_send_remedial_emails() -> bool:
    return os.environ.get('CRON_SEND_REMEDIAL_EMAILS', False)


def feature_request_profiling_enabled() -> bool:
    return os.environ.get('PROFILE_REQUESTS', False)


def feature_import_beneficiaries_enabled():
    return os.environ.get('CRON_BENEFICIARIES_ENROLLMENT', False)
