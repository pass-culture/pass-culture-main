from repository import thing_queries


class InconsistentOffer(Exception):

    def __init__(self, message=''):
        self.message = message

    def __str__(self):
        return self.message


def check_digital_offer_consistency(offer, venue, find_thing=thing_queries.find_by_id):
    thing = find_thing(offer.thingId)

    if venue.isVirtual and not thing.url:
        raise InconsistentOffer('Offer.venue is virtual but Offer.thing does not have an URL')

    if not venue.isVirtual and thing.url:
        raise InconsistentOffer('Offer.venue is not virtual but Offer.thing has an URL')


def addStockAlertMessageToOffer(offer):

    offer_stocks = [stock for stock in offer.stocks if not stock.isSoftDeleted]

    stock_alert_message = ''
    total_number_stocks = len(offer_stocks)
    offre_au_singulier = "offre"
    offre_au_pluriel = "offres"

    if offer.thingId:
        thing_type = True
        stock_word = "stock"
        remaining_stock_word = "en stock"
        all_places_word = ''
    else:
        thing_type = False
        stock_word = "places"
        all_places_word = 'pour toutes les dates'
        remaining_stock_word = "place"
        pluralized_remaining_stock_word = "places"

    if total_number_stocks == 0:
        if thing_type:
            stock_alert_message = 'pas encore de stock'
        else:
            stock_alert_message = 'pas encore de places'

    if total_number_stocks > 0:
        stocks_with_illimited_places_or_stock = [stock for stock in offer_stocks if not stock.available]
        number_of_illimited_places_or_stock = len(stocks_with_illimited_places_or_stock)

        still_available_places_or_stock = 0
        total_remaining_places_or_stock_available_for_offer = 0
        number_of_empty_places_or_stock_in_stock_offer = 0

    for stock in offer_stocks:
        total_bookings_by_stock = 0
        valid_bookings = [booking for booking in stock.bookings if not booking.isCancelled]

        for valid_booking in valid_bookings:
            total_bookings_by_stock += valid_booking.quantity

        if stock.available:
            still_available_places_or_stock = stock.available - total_bookings_by_stock

            total_remaining_places_or_stock_available_for_offer += still_available_places_or_stock

            if still_available_places_or_stock == 0:
                number_of_empty_places_or_stock_in_stock_offer += 1

        if number_of_empty_places_or_stock_in_stock_offer >= 1:
            mot_offre = offre_au_singulier if number_of_empty_places_or_stock_in_stock_offer == 1 else offre_au_pluriel

            stock_alert_message = f'plus de {stock_word} pour {number_of_empty_places_or_stock_in_stock_offer} {mot_offre}'

        if number_of_illimited_places_or_stock == total_number_stocks:
            offer.stockAlertMessage = "illimité"
            return offer

        if number_of_empty_places_or_stock_in_stock_offer == total_number_stocks:
            offer.stockAlertMessage = f'plus de {stock_word} {all_places_word}'
            return offer


        if still_available_places_or_stock > 0 and number_of_empty_places_or_stock_in_stock_offer == 0:

            if total_remaining_places_or_stock_available_for_offer > 1 and not thing_type:
                remaining_stock_word = pluralized_remaining_stock_word

            stock_alert_message = f'encore {total_remaining_places_or_stock_available_for_offer} {remaining_stock_word}'

    offer.stockAlertMessage = stock_alert_message

    return offer
