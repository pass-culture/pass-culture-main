from models.offer_type import EventType
from models.pc_object import PcObject
from sandboxes.scripts.utils.select import remove_every
from utils.logger import logger
from utils.test_utils import create_booking

RECOMMENDATIONS_WITH_BOOKINGS_REMOVE_RATIO = 3
RECOMMENDATIONS_WITH_SEVERAL_STOCKS_REMOVE_MODULO = 2
BOOKINGS_USED_REMOVE_MODULO = 3

def create_industrial_bookings(
    recommendations_by_name,
    stocks_by_name
):
    logger.info('create_industrial_bookings')

    bookings_by_name = {}

    token = 100000

    stocks = stocks_by_name.values()

    recommendation_items = recommendations_by_name.items()

    recommendation_items_with_booking = remove_every(
        recommendation_items,
        RECOMMENDATIONS_WITH_BOOKINGS_REMOVE_RATIO
    )

    for (recommendation_index, (recommendation_name, recommendation)) in enumerate(recommendation_items_with_booking):

        offer = recommendation.offer
        user = recommendation.user

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

        is_activation_offer = offer.eventOrThing.offerType['value'] == str(EventType.ACTIVATION)

        if user_has_only_activation_booked and not is_activation_offer:
            continue

        recommendation_stocks = [
            stock for stock in stocks
            if stock.offer == offer or\
            stock.eventOccurrence in offer.eventOccurrences
        ]

        for (index, stock) in enumerate(recommendation_stocks):

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

            booking = create_booking(
                user,
                is_used=is_used,
                recommendation=recommendation,
                stock=stock,
                token=str(token),
                venue=recommendation.offer.venue
            )

            token += 1

            bookings_by_name[booking_name] = booking


    PcObject.check_and_save(*bookings_by_name.values())

    logger.info('created {} bookings'.format(len(bookings_by_name)))

    return bookings_by_name
