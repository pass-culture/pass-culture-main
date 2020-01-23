from models.offer_type import EventType
from repository import repository
from sandboxes.scripts.utils.select import remove_every
from tests.model_creators.generic_creators import create_booking
from utils.logger import logger

RECOMMENDATIONS_WITH_BOOKINGS_REMOVE_RATIO = 3
RECOMMENDATIONS_WITH_SEVERAL_STOCKS_REMOVE_MODULO = 2
BOOKINGS_USED_REMOVE_MODULO = 3

def create_industrial_bookings(
    recommendations_by_name,
    stocks_by_name
):
    logger.info('create_industrial_bookings')

    bookings_by_name = {}

    list_of_users_with_no_more_money = []

    token = 100000

    recommendation_items = recommendations_by_name.items()

    recommendation_items_with_booking = remove_every(
        recommendation_items,
        RECOMMENDATIONS_WITH_BOOKINGS_REMOVE_RATIO
    )

    for (recommendation_index, (recommendation_name, recommendation)) in enumerate(recommendation_items_with_booking):

        offer = recommendation.offer
        user = recommendation.user

        user_should_have_no_more_money = "has-no-more-money" in user.email

        not_bookable_recommendation = offer is None
        if not_bookable_recommendation:
            continue

        user_has_no_booking = \
            user.firstName != "PC Test Jeune" or \
            "has-signed-up" in user.email

        if user_has_no_booking:
            continue

        user_has_only_activation_booked = \
            "has-booked-activation" in user.email or \
            "has-confirmed-activation" in user.email

        is_activation_offer = offer.product.offerType['value'] == str(EventType.ACTIVATION)

        if user_has_only_activation_booked and not is_activation_offer:
            continue

        for (index, stock) in enumerate(offer.stocks):

            # every STOCK_MODULO RECO will have several stocks
            if index > 0 and recommendation_index%(RECOMMENDATIONS_WITH_SEVERAL_STOCKS_REMOVE_MODULO + index):
                continue

            booking_name = "{} / {}".format(recommendation_name, str(token))

            is_used = False
            if is_activation_offer:
                is_used = True if "has-confirmed-activation" in user.email or \
                                  "has-booked-some" in user.email or \
                                  "has-no-more-money" in user.email else False
            else:
                # (BOOKINGS_USED_REMOVE_MODULO-1)/BOOKINGS_USED_REMOVE_MODULO are used
                is_used = recommendation_index%BOOKINGS_USED_REMOVE_MODULO != 0

            if user_should_have_no_more_money and user not in list_of_users_with_no_more_money:
                booking_amount = 500
                list_of_users_with_no_more_money.append(user)
            elif user_should_have_no_more_money and user in list_of_users_with_no_more_money:
                booking_amount = 0
            else:
                booking_amount = None

            booking = create_booking(user=user, amount=booking_amount, is_used=is_used, recommendation=recommendation,
                                     stock=stock, token=str(token), venue=recommendation.offer.venue)

            token += 1

            bookings_by_name[booking_name] = booking

    bookings = bookings_by_name.values()

    repository.save(*bookings)

    used_bookings = [b for b in bookings if b.isUsed]
    for used_booking in used_bookings:
        used_booking.isUsed = False
    repository.save(*used_bookings)
    for used_booking in used_bookings:
        used_booking.isUsed = True
    repository.save(*used_bookings)

    logger.info('created {} bookings'.format(len(bookings_by_name)))

    return bookings_by_name
