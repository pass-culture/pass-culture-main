import logging
from typing import List
from typing import Set

from pcapi.core.offers.models import Offer
from pcapi.core.users.api import suspend_account
from pcapi.core.users.constants import SuspensionReason
from pcapi.core.users.models import User
from pcapi.repository.booking_queries import find_offers_booked_by_beneficiary_by_stocks
from pcapi.repository.booking_queries import find_stocks_booked_by_beneficiary
from pcapi.repository.user_queries import find_beneficiary_users_by_email_provider


def suspend_fraudulent_beneficiary_users_by_email_providers(
    fraudulent_email_providers: List[str], admin_user: User, dry_run: bool = True
) -> None:
    fraudulent_users: List[User] = []
    logging.info("[Suspend fraudulent beneficiaries script] START")
    for email_provider in fraudulent_email_providers:
        fraudulent_users_for_provider = find_beneficiary_users_by_email_provider(email_provider)
        suspend_fraudulent_beneficiary_user(fraudulent_users_for_provider, admin_user, dry_run)
        fraudulent_users = fraudulent_users + fraudulent_users_for_provider
        logging.info("[Suspend fraudulent beneficiaries script] fraudulent users for provider %s", email_provider)

    logging.info("[Suspend fraudulent beneficiaries script] fraudulent users %s", fraudulent_users)
    offers = get_offers_booked_by_users(fraudulent_users)
    logging.info("[Suspend fraudulent beneficiaries script] offers %s", offers)
    logging.info("[Suspend fraudulent beneficiaries script] END")


def suspend_fraudulent_beneficiary_user(fraudulent_users: List[User], admin_user: User, dry_run: bool = True) -> None:
    for fraudulent_user in fraudulent_users:
        if not dry_run:
            suspend_account(fraudulent_user, SuspensionReason.FRAUD, admin_user)


def get_offers_booked_by_users(users: List[User]) -> Set[Offer]:
    offers: List[Offer] = []
    for user in users:
        offers = offers + find_offers_booked_by_fraudulent_users(user)
    return set(offers)


def find_offers_booked_by_fraudulent_users(user: User) -> List[Offer]:
    stocks = find_stocks_booked_by_beneficiary(user)
    return find_offers_booked_by_beneficiary_by_stocks(stocks)
