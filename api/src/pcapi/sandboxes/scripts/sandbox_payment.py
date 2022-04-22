from datetime import datetime
from datetime import timedelta
import logging
import typing

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.categories import subcategories
from pcapi.core.offerers.models import Venue
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
import pcapi.core.payments.api as payments_api
from pcapi.core.users import factories as users_factories
from pcapi.core.users.models import EligibilityType
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_stock
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_event_occurrence
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.model_creators.specific_creators import create_stock_from_event_occurrence
from pcapi.repository import repository


logger = logging.getLogger(__name__)


now = datetime.utcnow()
three_days = timedelta(days=3)


def save_users_with_deposits() -> typing.Tuple[users_factories.UserFactory, ...]:
    user1 = users_factories.BeneficiaryGrant18Factory(email="user1@test.com")
    user2 = users_factories.BeneficiaryGrant18Factory(email="user2@test.com")
    user3 = users_factories.BeneficiaryGrant18Factory(email="user3@test.com")
    user4 = users_factories.BeneficiaryGrant18Factory(email="user4@test.com")
    user5 = users_factories.BeneficiaryGrant18Factory(email="user5@test.com")
    deposit1 = payments_api.create_deposit(user1, "sandbox", EligibilityType.AGE18)
    deposit2 = payments_api.create_deposit(user2, "sandbox", EligibilityType.AGE18)
    deposit3 = payments_api.create_deposit(user3, "sandbox", EligibilityType.AGE18)
    deposit4 = payments_api.create_deposit(user4, "sandbox", EligibilityType.AGE18)
    deposit5 = payments_api.create_deposit(user5, "sandbox", EligibilityType.AGE18)
    repository.save(deposit1, deposit2, deposit3, deposit4, deposit5)
    logger.info("created 5 users with deposits")
    return user1, user2, user3, user4, user5


def save_offerer_with_iban() -> typing.Tuple[Venue, ...]:
    offerer_with_iban = create_offerer(siren="180046021", name="Philarmonie")
    venue_with_siret = create_venue(offerer=offerer_with_iban, siret="18004602100026", is_virtual=False)
    venue_without_siret = create_venue(offerer=offerer_with_iban, siret=None, is_virtual=False, comment="pas de siret")
    venue_online = create_venue(offerer=offerer_with_iban, siret=None, is_virtual=True)
    offers_factories.BankInformationFactory(
        offerer=offerer_with_iban,
        bic="TRPUFRP1",
        iban="FR7610071750000000100420866",
        applicationId=1,
    )
    repository.save(venue_online, venue_with_siret, venue_without_siret)
    logger.info("created 1 offerer with iban and 1 virtual venue, 1 venue with siret and 1 venue without siret")
    return venue_online, venue_with_siret, venue_without_siret


def save_offerer_without_iban() -> typing.Tuple[Venue, ...]:
    offerer_without_iban = create_offerer(siren="213400328", name="Béziers")
    venue_with_siret_with_iban = create_venue(offerer=offerer_without_iban, siret="21340032800018", is_virtual=False)
    venue_with_siret_without_iban = create_venue(offerer=offerer_without_iban, siret="21340032800802", is_virtual=False)
    venue_online = create_venue(offerer=offerer_without_iban, siret=None, is_virtual=True)

    offers_factories.BankInformationFactory(
        venue=venue_with_siret_with_iban,
        bic="BDFEFRPPCCT",
        iban="FR733000100206C343000000066",
        application_id=2,
    )
    repository.save(venue_online, venue_with_siret_with_iban, venue_with_siret_without_iban)
    logger.info(
        "created 1 offerer without iban and 1 virtual venue, 1 venue with siret with iban and 1 venue with siret without iban"
    )
    return venue_online, venue_with_siret_with_iban, venue_with_siret_without_iban


def save_free_event_offer_with_stocks(venue: Venue) -> typing.Tuple[offers_models.Stock, ...]:
    free_event_offer = create_offer_with_event_product(
        venue,
        event_name="Free event",
        event_subcategory_id=subcategories.SPECTACLE_REPRESENTATION.id,
    )
    past_occurrence = create_event_occurrence(free_event_offer, beginning_datetime=now - three_days)
    future_occurrence = create_event_occurrence(free_event_offer, beginning_datetime=now + three_days)
    past_free_event_stock = create_stock_from_event_occurrence(past_occurrence, price=0)
    future_free_event_stock = create_stock_from_event_occurrence(future_occurrence, price=0)
    repository.save(past_free_event_stock, future_free_event_stock)
    logger.info("created 1 event offer with 1 past and 1 future occurrence with 1 free stock each")
    return past_free_event_stock, future_free_event_stock


def save_non_reimbursable_thing_offer(venue: Venue) -> offers_models.Stock:
    paid_non_reimbursable_offer = create_offer_with_thing_product(
        venue,
        thing_name="Concert en ligne",
        thing_subcategory_id=subcategories.JEU_SUPPORT_PHYSIQUE.id,
        url="http://my.game.fr",
    )
    non_reimbursable_stock = create_stock(offer=paid_non_reimbursable_offer, price=30)
    repository.save(non_reimbursable_stock)
    logger.info("created 1 non reimbursable thing offer with 1 paid stock of 30 €")
    return non_reimbursable_stock


def save_reimbursable_thing_offer(venue: Venue) -> offers_models.Stock:
    paid_reimbursable_offer = create_offer_with_thing_product(
        venue, thing_name="Roman cool", thing_subcategory_id=subcategories.LIVRE_PAPIER.id
    )
    reimbursable_stock = create_stock(offer=paid_reimbursable_offer, price=30)
    repository.save(reimbursable_stock)
    logger.info("created 1 reimbursable thing offer with 1 paid stock of 30 €")
    return reimbursable_stock


def save_paid_online_book_offer(venue: Venue) -> offers_models.Stock:
    paid_reimbursable_offer = create_offer_with_thing_product(
        venue, thing_name="Roman cool", thing_subcategory_id=subcategories.LIVRE_PAPIER.id, url="https://mycoolbook.fr"
    )
    reimbursable_stock = create_stock(offer=paid_reimbursable_offer, price=20)
    repository.save(reimbursable_stock)
    logger.info("created 1 online book offer with 1 paid stock of 20 €")
    return reimbursable_stock


def save_paid_reimbursable_event_offer(venue: Venue) -> typing.Tuple[offers_models.Stock, ...]:
    paid_reimbursable_event_offer = create_offer_with_event_product(
        venue,
        event_name="Paid event",
        event_subcategory_id=subcategories.SPECTACLE_REPRESENTATION.id,
    )
    past_occurrence = create_event_occurrence(paid_reimbursable_event_offer, beginning_datetime=now - three_days)
    future_occurrence = create_event_occurrence(paid_reimbursable_event_offer, beginning_datetime=now + three_days)
    past_event_stock = create_stock_from_event_occurrence(past_occurrence, price=10)
    future_event_stock = create_stock_from_event_occurrence(future_occurrence, price=10)
    repository.save(past_event_stock, future_event_stock)
    logger.info("created 1 event offer with 1 past and 1 future occurrence with 1 paid stock of 10 € each")
    return past_event_stock, future_event_stock


def save_sandbox() -> None:
    user1, user2, user3, user4, user5 = save_users_with_deposits()
    (
        venue_online_of_offerer_with_iban,
        venue_with_siret_of_offerer_with_iban,
        venue_without_siret_of_offerer_with_iban,
    ) = save_offerer_with_iban()
    (
        _venue_online_of_offerer_without_iban,
        venue_of_offerer_without_iban_with_siret_with_iban,
        venue_of_offerer_without_iban_with_siret_without_iban,
    ) = save_offerer_without_iban()
    past_free_event_stock, future_free_event_stock = save_free_event_offer_with_stocks(
        venue_with_siret_of_offerer_with_iban
    )
    non_reimbursable_stock_of_offerer_with_iban = save_non_reimbursable_thing_offer(venue_online_of_offerer_with_iban)
    reimbursable_stock_of_offerer_with_iban = save_reimbursable_thing_offer(venue_with_siret_of_offerer_with_iban)
    past_event_stock_of_offerer_with_iban, future_event_stock_of_offerer_with_iban = save_paid_reimbursable_event_offer(
        venue_without_siret_of_offerer_with_iban
    )

    (
        past_event_stock_of_offerer_without_iban,
        future_event_stock_of_offerer_without_iban,
    ) = save_paid_reimbursable_event_offer(venue_of_offerer_without_iban_with_siret_without_iban)

    reimbursable_stock_of_offerer_without_iban = save_reimbursable_thing_offer(
        venue_of_offerer_without_iban_with_siret_with_iban
    )
    online_book_stock_of_offerer_without_iban = save_paid_online_book_offer(venue_online_of_offerer_with_iban)

    bookings = [
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=user1,
            user=user1,
            stock=past_free_event_stock,
            token="TOKEN1",
        ),
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=user2,
            user=user2,
            stock=past_free_event_stock,
            token="TOKEN2",
        ),
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=user3,
            user=user3,
            stock=past_free_event_stock,
            token="TOKEN3",
        ),
        bookings_factories.UsedIndividualBookingFactory(
            individualBooking__user=user4,
            user=user4,
            stock=future_free_event_stock,
            token="TOKEN4",
        ),
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=user5,
            user=user5,
            stock=future_free_event_stock,
            token="TOKEN5",
        ),
        bookings_factories.UsedIndividualBookingFactory(
            individualBooking__user=user1,
            user=user1,
            stock=non_reimbursable_stock_of_offerer_with_iban,
            token="TOKEN6",
        ),
        bookings_factories.UsedIndividualBookingFactory(
            individualBooking__user=user2,
            user=user2,
            stock=non_reimbursable_stock_of_offerer_with_iban,
            token="TOKEN7",
        ),
        bookings_factories.UsedIndividualBookingFactory(
            individualBooking__user=user3,
            user=user3,
            stock=non_reimbursable_stock_of_offerer_with_iban,
            token="TOKEN8",
        ),
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=user4,
            user=user4,
            stock=non_reimbursable_stock_of_offerer_with_iban,
            token="TOKEN9",
        ),
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=user5,
            user=user5,
            stock=non_reimbursable_stock_of_offerer_with_iban,
            # Drop the "N" because the token has 6 characters.
            token="TOKE10",
        ),
        bookings_factories.UsedIndividualBookingFactory(
            individualBooking__user=user1,
            user=user1,
            stock=reimbursable_stock_of_offerer_with_iban,
            token="TOKE11",
        ),
        bookings_factories.UsedIndividualBookingFactory(
            individualBooking__user=user2,
            user=user2,
            stock=reimbursable_stock_of_offerer_with_iban,
            token="TOKE12",
        ),
        bookings_factories.UsedIndividualBookingFactory(
            individualBooking__user=user3,
            user=user3,
            stock=reimbursable_stock_of_offerer_with_iban,
            token="TOKE13",
        ),
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=user4,
            user=user4,
            stock=reimbursable_stock_of_offerer_with_iban,
            token="TOKE14",
        ),
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=user5,
            user=user5,
            stock=reimbursable_stock_of_offerer_with_iban,
            token="TOKE15",
        ),
        bookings_factories.UsedIndividualBookingFactory(
            individualBooking__user=user1,
            user=user1,
            stock=past_event_stock_of_offerer_with_iban,
            token="TOKE16",
        ),
        bookings_factories.UsedIndividualBookingFactory(
            individualBooking__user=user2,
            user=user2,
            stock=past_event_stock_of_offerer_with_iban,
            token="TOKE17",
        ),
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=user3,
            user=user3,
            stock=past_event_stock_of_offerer_with_iban,
            token="TOKE18",
        ),
        bookings_factories.UsedIndividualBookingFactory(
            individualBooking__user=user4,
            user=user4,
            stock=future_event_stock_of_offerer_with_iban,
            token="TOKE19",
        ),
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=user5,
            user=user5,
            stock=future_event_stock_of_offerer_with_iban,
            token="TOKE20",
        ),
        bookings_factories.UsedIndividualBookingFactory(
            individualBooking__user=user1,
            user=user1,
            stock=past_event_stock_of_offerer_without_iban,
            token="TOKE21",
        ),
        bookings_factories.UsedIndividualBookingFactory(
            individualBooking__user=user2,
            user=user2,
            stock=past_event_stock_of_offerer_without_iban,
            token="TOKE22",
        ),
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=user3,
            user=user3,
            stock=past_event_stock_of_offerer_without_iban,
            token="TOKE23",
        ),
        bookings_factories.UsedIndividualBookingFactory(
            individualBooking__user=user4,
            user=user4,
            stock=future_event_stock_of_offerer_without_iban,
            token="TOKE24",
        ),
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=user5,
            user=user5,
            stock=future_event_stock_of_offerer_without_iban,
            token="TOKE25",
        ),
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=user1,
            user=user1,
            stock=reimbursable_stock_of_offerer_without_iban,
            token="TOKE26",
        ),
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=user2,
            user=user2,
            stock=reimbursable_stock_of_offerer_without_iban,
            token="TOKE27",
        ),
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=user3,
            user=user3,
            stock=reimbursable_stock_of_offerer_without_iban,
            token="TOKE28",
        ),
        bookings_factories.UsedIndividualBookingFactory(
            individualBooking__user=user4,
            user=user4,
            stock=reimbursable_stock_of_offerer_without_iban,
            token="TOKE29",
        ),
        bookings_factories.UsedIndividualBookingFactory(
            individualBooking__user=user5,
            user=user5,
            stock=reimbursable_stock_of_offerer_without_iban,
            token="TOKE30",
        ),
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=user1,
            user=user1,
            stock=online_book_stock_of_offerer_without_iban,
            token="TOKE31",
        ),
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=user2,
            user=user2,
            stock=online_book_stock_of_offerer_without_iban,
            token="TOKE32",
        ),
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=user3,
            user=user3,
            stock=online_book_stock_of_offerer_without_iban,
            token="TOKE33",
        ),
        bookings_factories.UsedIndividualBookingFactory(
            individualBooking__user=user4,
            user=user4,
            stock=online_book_stock_of_offerer_without_iban,
            token="TOKE34",
        ),
        bookings_factories.UsedIndividualBookingFactory(
            individualBooking__user=user5,
            user=user5,
            stock=online_book_stock_of_offerer_without_iban,
            token="TOKE35",
        ),
    ]

    logger.info("created %s bookings", len(bookings))
    repository.save(*bookings)
