""" content """
from random import randint

def get_mediation (recommendation):
    return recommendation.get('mediation')

def get_stock (stock_id, recommendation):
    return [o for o in recommendation.get('recommendationStocks', []) if o['id'] == stock_id][0]

def get_source(mediation, stock):
    return stock.get('eventOccurrence', {"event": None}).get('event') or\
           stock.get('thing') or\
           mediation.get('event') or\
           mediation.get('thing')

def get_thumb_url(mediation, source, stock):
    source_plural_model_name = (stock.get('eventOccurrence') and 'events') or\
        (stock.get('thing') and 'things') or\
        (mediation.get('event') and 'events') or\
        (mediation.get('thing') and 'things') or ''
    if mediation and mediation.get('thumbCount') > 0:
        return '/mediations/'+ mediation['id']
    elif source and source.get('thumbCount') > 0:
        return source_plural_model_name + '/' + source['id']

def get_venue(stock, source):
    return stock.get('eventOccurrence', {'venue': None}).get('venue') or\
    stock.get('venue') or\
    source.get('eventOccurrence', {'venue': None}).get('venue') or\
    source.get('venue')

def get_content(recommendation):
    content = {}
    mediation = recommendation.get('mediation')
    recommendation_stocks = recommendation['recommendationStocks']
    stock_index = randint(0, len(recommendation_stocks) - 1)
    stock_id = recommendation_stocks[stock_index]['id']
    mediation = get_mediation(recommendation)
    stock = get_stock(stock_id, recommendation)
    source = get_source(mediation, stock)
    venue = get_venue(stock, source)
    content['thumbUrl'] = get_thumb_url(mediation, source, stock)
    content.update({
        "stock": stock,
        "mediation": mediation,
        "source": source,
        "venue": venue
    })
    return content
