from pcapi.core import search
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.repository import repository


OFFER_IDS = [
    41267139,
    41267181,
    41268827,
    41272935,
    42718308,
    42718387,
    42718391,
    42718396,
    42718402,
    44058809,
    44058836,
    44135791,
    44136429,
    44321497,
    44669967,
    44893870,
    45672629,
    45672944,
    45673289,
    45677809,
    45817045,
    45817051,
    45817219,
    45817227,
    45817238,
    46903442,
    47071795,
    47404494,
    47547952,
    47611729,
    47611786,
    47751688,
    48192274,
    48193120,
    48325290,
    48325330,
    48325358,
    48535282,
    48761098,
    48965349,
    48971797,
    49087626,
    49113415,
    49200866,
    49430725,
    49431398,
    49523224,
    49524213,
    49606668,
    49606796,
    49606831,
    49606861,
    49606887,
    49606941,
    49620248,
    49620437,
    49620724,
    49656063,
    49684311,
    49711142,
    49711402,
    49727977,
    49727984,
    49727993,
    49728108,
    49728124,
    49728252,
    49728262,
    49728296,
    49728308,
    49729219,
    49729414,
    49729559,
    50462322,
    50488461,
]


def fix_stocks_from_educational_offers() -> None:
    """
    Select the first stock of the first educational offer with multiple stocks
    """
    offers = Offer.query.filter(Offer.id.in_(OFFER_IDS)).all()

    for offer in offers:
        stocks: list[Stock] = offer.stocks
        if len(stocks) == 1:
            _fix_offer_with_one_stock_many_quantity(offer)
            continue

        if len(stocks) > 1:
            # Handle offers where one stock has one booking and the rest does not
            stocks_with_at_least_one_booking = list(filter(lambda stock: stock.dnBookedQuantity >= 1, stocks))
            if len(stocks_with_at_least_one_booking) >= 1:
                if len(stocks_with_at_least_one_booking) > 1:
                    print("This offer should not have len(stocks_with_at_least_one_booking) > 1 (l59)", offer.id)
                    continue

                for stock in stocks:
                    if stock.dnBookedQuantity > 1:
                        print("This stock should not have dnBookedQuantity > 1 (l64)", stock.id)
                        continue

                    if stock.dnBookedQuantity == 1:
                        stock.quantity = 1
                        repository.save(stock)

                    if stock.dnBookedQuantity == 0:
                        stock.isSoftDeleted = True
                        repository.save(stock)
                # We skip this offer as we treated it
                continue

            for (index, stock) in enumerate(stocks):
                if index == 0:
                    stock.quantity = 1
                    repository.save(stock)
                    continue
                stock.isSoftDeleted = True
                repository.save(stock)
        search.async_index_offer_ids([offer.id])


def _fix_offer_with_one_stock_many_quantity(offer: Offer) -> None:
    stocks = offer.stocks

    if len(stocks) == 1:
        stock = stocks[0]

        if stock.dnBookedQuantity > 1:
            print("This stock should not have dnBookedQuantity > 1 (l96)", stock.id)
            return

        stock.quantity = 1
        repository.save(stock)
