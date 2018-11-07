from models import EventOccurrence, Offer, Stock
from models.pc_object import PcObject
from utils.human_ids import dehumanize
from utils.logger import logger

def create_or_find_stock(stock_mock):
    if 'eventOccurrenceId' in stock_mock:
        event_occurrence = EventOccurrence.query.get(dehumanize(stock_mock['eventOccurrenceId']))
        query = Stock.queryNotSoftDeleted().filter_by(eventOccurrenceId=event_occurrence.id)
        logger.info("look stock " + event_occurrence.offer.eventOrThing.name + " " + stock_mock.get('id'))
    else:
        offer = Offer.query.get(dehumanize(stock_mock['offerId']))
        logger.info("look stock " + offer.eventOrThing.name + " " + stock_mock.get('id'))
        query = Stock.queryNotSoftDeleted().filter_by(offerId=offer.id)

    if 'id' in stock_mock:
        stock = Stock.query.get(dehumanize(stock_mock['id']))
    else:
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
