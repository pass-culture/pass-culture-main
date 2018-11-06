from models import EventOccurrence, Offer, Stock
from models.pc_object import PcObject
from utils.human_ids import dehumanize
from utils.logger import logger

def create_or_find_stock(stock_mock, event_occurrence=None, offer=None):
    if 'eventOccurrenceId' in stock_mock:
        if event_occurrence is None:
            event_occurrence = EventOccurrence.query.get(dehumanize(stock_mock['eventOccurrenceId']))
            query = Stock.queryNotSoftDeleted().filter_by(eventOccurrenceId=event_occurrence.id)
            logger.info("look stock " + event_occurrence.offer.eventOrThing.name)
    else:
        if offer is None:
            offer = Offer.query.get(dehumanize(stock_mock['offerId']))
            logger.info("look stock " + offer.eventOrThing.name)
        query = Stock.queryNotSoftDeleted().filter_by(offerId=offer.id)

    stock = query.first()

    if stock is None:
        stock = Stock(from_dict=stock_mock)
        if 'eventOccurrenceId' in stock_mock:
            stock.eventOccurrence = event_occurrence
        else:
            stock.offer = offer
        if 'id' in stock_mock:
            stock.id = dehumanize(stock_mock['id'])
        PcObject.check_and_save(stock)
        logger.info("created stock " + str(stock))
    else:
        logger.info('--already here-- stock' + str(stock))

    return stock

def create_or_find_stocks(*stock_mocks):
    stocks_count = str(len(stock_mocks))
    logger.info("stock mocks " + stocks_count)

    stocks = []
    for (stock_index, stock_mock) in enumerate(stock_mocks):
        logger.info(str(stock_index) + "/" + stocks_count)
        stock = create_or_find_stock(stock_mock)
        stocks.append(stock)

    return stocks
