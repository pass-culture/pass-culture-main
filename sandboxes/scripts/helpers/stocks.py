from models import Stock
from models.pc_object import PcObject
from utils.logger import logger

def create_or_find_stock(stock_mock, store=None):
    if store is None:
        store = {}
    if 'eventOccurrenceKey' in stock_mock:
        event_occurrence = store['event_occurrences_by_key'][stock_mock['eventOccurrenceKey']]
        query = Stock.queryNotSoftDeleted().filter_by(eventOccurrenceId=event_occurrence.id)
    else:
        offer = store['offers_by_key'][stock_mock['offerKey']]
        query = Stock.queryNotSoftDeleted().filter_by(offerId=offer.id)

    if query.count() == 0:
        stock = Stock(from_dict=stock_mock)
        if 'eventOccurrenceKey' in stock_mock:
            stock.eventOccurrence = event_occurrence
        else:
            stock.offer = offer
        PcObject.check_and_save(stock)
        logger.info("created stock " + str(stock))
    else:
        stock = query.first()
        logger.info('--already here-- stock' + str(stock))
    return stock

def create_or_find_stocks(*stock_mocks, store=None):
    if store is None:
        store = {}
    stocks_count = str(len(stock_mocks))
    logger.info("stock mocks " + stocks_count)
    store['stocks_by_key'] = {}
    for (stock_index, stock_mock) in enumerate(stock_mocks):
        if 'eventOccurrenceKey' in stock_mock:
            logger.info("look stock " + store['event_occurrences_by_key'][stock_mock['eventOccurrenceKey']].offer.event.name + str(stock_index) + "/" + stocks_count)
        else:
            logger.info("look stock " + store['offers_by_key'][stock_mock['offerKey']].thing.name + " " + str(stock_index) + "/" + stocks_count)
        stock = create_or_find_stock(stock_mock, store=store)
        store['stocks_by_key'][stock_mock['key']] = stock
