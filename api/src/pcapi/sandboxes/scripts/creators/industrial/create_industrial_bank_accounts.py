import logging

from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.sandboxes.scripts.utils.helpers import log_func_duration


logger = logging.getLogger(__name__)


@log_func_duration
def create_industrial_bank_accounts() -> None:
    logger.info("create_industrial_bank_accounts")
    create_offerer_without_bank_accounts()
    create_offerer_with_various_bank_accounts_state()
    create_offerer_with_all_his_venue_linked()
    create_offerer_at_least_one_venue_linked()
    create_offerer_with_none_venue_linked()
    create_offerer_with_all_his_venue_linked_to_one_bank_account()
    create_offerer_with_only_one_venue_linked()


def create_offerer_without_bank_accounts() -> None:
    logger.info("create_offerer_without_bank_accounts")
    offerer_without_bank_accounts = offerers_factories.OffererFactory.create(
        name="1 - [CB] Structure sans coordonnées bancaires"
    )
    offerers_factories.UserOffererFactory.create(
        offerer=offerer_without_bank_accounts, user__email="activation@example.com"
    )
    venue = offerers_factories.VenueFactory.create(managingOfferer=offerer_without_bank_accounts, pricing_point="self")
    offer = offers_factories.OfferFactory.create(venue=venue)
    offers_factories.StockFactory.create(offer=offer)


def create_offerer_with_various_bank_accounts_state() -> None:
    logger.info("create_offerer_with_various_bank_accounts_state")
    offerer_with_various_bank_accounts_status = offerers_factories.OffererFactory.create(
        name="1 - [CB] Structure avec des coordonnées bancaires dans différents états"
    )
    offerers_factories.UserOffererFactory.create(
        offerer=offerer_with_various_bank_accounts_status, user__email="activation@example.com"
    )
    finance_factories.BankAccountFactory.create(
        status=finance_models.BankAccountApplicationStatus.ACCEPTED, offerer=offerer_with_various_bank_accounts_status
    )
    finance_factories.BankAccountFactory.create(
        status=finance_models.BankAccountApplicationStatus.DRAFT, offerer=offerer_with_various_bank_accounts_status
    )
    finance_factories.BankAccountFactory.create(
        status=finance_models.BankAccountApplicationStatus.ON_GOING, offerer=offerer_with_various_bank_accounts_status
    )
    finance_factories.BankAccountFactory.create(
        status=finance_models.BankAccountApplicationStatus.REFUSED, offerer=offerer_with_various_bank_accounts_status
    )
    finance_factories.BankAccountFactory.create(
        status=finance_models.BankAccountApplicationStatus.WITHOUT_CONTINUATION,
        offerer=offerer_with_various_bank_accounts_status,
    )
    finance_factories.BankAccountFactory.create(
        status=finance_models.BankAccountApplicationStatus.WITH_PENDING_CORRECTIONS,
        offerer=offerer_with_various_bank_accounts_status,
    )
    venue = offerers_factories.VenueFactory.create(
        managingOfferer=offerer_with_various_bank_accounts_status, pricing_point="self"
    )
    offer = offers_factories.OfferFactory.create(venue=venue)
    offers_factories.StockFactory.create(offer=offer)


def create_offerer_with_all_his_venue_linked() -> None:
    logger.info("create_offerer_with_all_his_venue_linked")

    offerer_with_all_venues_linked = offerers_factories.OffererFactory.create(
        name="1 - [CB] Structure avec tous ses lieux liés à des coordonnées bancaires"
    )
    offerers_factories.UserOffererFactory.create(
        offerer=offerer_with_all_venues_linked, user__email="activation@example.com"
    )
    first_venue_with_non_free_offer = offerers_factories.VenueFactory.create(
        managingOfferer=offerer_with_all_venues_linked, pricing_point="self"
    )
    offers_factories.StockFactory.create(offer__venue=first_venue_with_non_free_offer)
    second_venue_with_non_free_offer = offerers_factories.VenueFactory.create(
        managingOfferer=offerer_with_all_venues_linked, pricing_point="self"
    )
    offers_factories.StockFactory.create(offer__venue=second_venue_with_non_free_offer)

    bank_account = finance_factories.BankAccountFactory.create(offerer=offerer_with_all_venues_linked)
    offerers_factories.VenueBankAccountLinkFactory.create(
        venue=first_venue_with_non_free_offer, bankAccount=bank_account
    )
    offerers_factories.VenueBankAccountLinkFactory.create(
        venue=second_venue_with_non_free_offer, bankAccount=bank_account
    )


def create_offerer_at_least_one_venue_linked() -> None:
    logger.info("create_offerer_at_least_one_venue_linked")
    offerer_with_one_venue_linked = offerers_factories.OffererFactory.create(
        name="1 - [CB] Structure avec un de ses lieux non rattachés à des coordonnées bancaires"
    )
    offerers_factories.UserOffererFactory.create(
        offerer=offerer_with_one_venue_linked, user__email="activation@example.com"
    )
    first_venue_with_non_free_offer = offerers_factories.VenueFactory.create(
        managingOfferer=offerer_with_one_venue_linked, pricing_point="self"
    )
    offers_factories.StockFactory.create(offer__venue=first_venue_with_non_free_offer)
    second_venue_with_non_free_offer = offerers_factories.VenueFactory.create(
        managingOfferer=offerer_with_one_venue_linked, pricing_point="self"
    )
    offers_factories.StockFactory.create(offer__venue=second_venue_with_non_free_offer)

    bank_account = finance_factories.BankAccountFactory.create(offerer=offerer_with_one_venue_linked)
    offerers_factories.VenueBankAccountLinkFactory.create(
        venue=first_venue_with_non_free_offer, bankAccount=bank_account
    )


def create_offerer_with_none_venue_linked() -> None:
    logger.info("create_offerer_with_none_venue_linked")
    offerer_with_none_venue_linked = offerers_factories.OffererFactory.create(
        name="1 - [CB] Structure avec aucun de ses lieux liés à des coordonnées bancaires"
    )
    offerers_factories.UserOffererFactory.create(
        offerer=offerer_with_none_venue_linked, user__email="activation@example.com"
    )
    first_venue_with_non_free_offer = offerers_factories.VenueFactory.create(
        managingOfferer=offerer_with_none_venue_linked, pricing_point="self"
    )
    offers_factories.StockFactory.create(offer__venue=first_venue_with_non_free_offer)
    second_venue_with_non_free_offer = offerers_factories.VenueFactory.create(
        managingOfferer=offerer_with_none_venue_linked, pricing_point="self"
    )
    offers_factories.StockFactory.create(offer__venue=second_venue_with_non_free_offer)

    finance_factories.BankAccountFactory.create(offerer=offerer_with_none_venue_linked)


def create_offerer_with_all_his_venue_linked_to_one_bank_account() -> None:
    logger.info("create_offerer_with_all_his_venue_linked_to_one_bank_account")

    offerer_with_all_venues_linked = offerers_factories.OffererFactory.create(
        name="1 - [CB] Structure avec deux coordonnées bancaires dont tous les lieux sont liés à l’une d’entre elles."
    )
    offerers_factories.UserOffererFactory.create(
        offerer=offerer_with_all_venues_linked, user__email="activation@example.com"
    )
    first_venue_with_non_free_offer = offerers_factories.VenueFactory.create(
        managingOfferer=offerer_with_all_venues_linked, pricing_point="self"
    )
    offers_factories.StockFactory.create(offer__venue=first_venue_with_non_free_offer)
    second_venue_with_non_free_offer = offerers_factories.VenueFactory.create(
        managingOfferer=offerer_with_all_venues_linked, pricing_point="self"
    )
    offers_factories.StockFactory.create(offer__venue=second_venue_with_non_free_offer)

    bank_account = finance_factories.BankAccountFactory.create(offerer=offerer_with_all_venues_linked)
    finance_factories.BankAccountFactory.create(offerer=offerer_with_all_venues_linked)
    offerers_factories.VenueBankAccountLinkFactory.create(
        venue=first_venue_with_non_free_offer, bankAccount=bank_account
    )
    offerers_factories.VenueBankAccountLinkFactory.create(
        venue=second_venue_with_non_free_offer, bankAccount=bank_account
    )


def create_offerer_with_only_one_venue_linked() -> None:
    logger.info("create_offerer_with_only_one_venue_linked")
    offerer_with_only_one_venue_linked = offerers_factories.OffererFactory.create(
        name="1 - [CB] Structure avec plusieurs de ses lieux non rattachés à des coordonnées bancaires"
    )
    offerers_factories.UserOffererFactory.create(
        offerer=offerer_with_only_one_venue_linked, user__email="activation@example.com"
    )
    first_venue_with_non_free_offer = offerers_factories.VenueFactory.create(
        managingOfferer=offerer_with_only_one_venue_linked, pricing_point="self"
    )
    offers_factories.StockFactory.create(offer__venue=first_venue_with_non_free_offer)
    second_venue_with_non_free_offer = offerers_factories.VenueFactory.create(
        managingOfferer=offerer_with_only_one_venue_linked
    )
    offers_factories.StockFactory.create(offer__venue=second_venue_with_non_free_offer)
    third_venue_with_non_free_offer = offerers_factories.VenueFactory.create(
        managingOfferer=offerer_with_only_one_venue_linked
    )

    bank_account = finance_factories.BankAccountFactory.create(offerer=offerer_with_only_one_venue_linked)

    offerers_factories.VenueBankAccountLinkFactory.create(
        venue=third_venue_with_non_free_offer, bankAccount=bank_account
    )
