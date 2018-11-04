from models import Offerer, Venue
from models.pc_object import PcObject
from utils.logger import logger

def create_or_find_venue(venue_mock, store=None):
    if store is None:
        store = {}
    offerer = store['offerers_by_key'][venue_mock['offererKey']]
    query = Venue.query.filter_by(
        managingOffererId=offerer.id,
        name=venue_mock['name']
    )
    if query.count() == 0:
        venue = Venue(from_dict=venue_mock)
        venue.managingOfferer = store['offerers_by_key'][venue_mock['offererKey']]
        PcObject.check_and_save(venue)
        logger.info("created venue " + venue_mock['offererKey'] + " " + venue_mock['name'])
    else:
        venue = query.first()
        logger.info('--already here-- venue' + str(venue))

    return venue

def create_or_find_venues(*venue_mocks, store=None):
    if store is None:
        store = {}
    venues_count = str(len(venue_mocks))
    logger.info("venue mocks " + venues_count)
    store['venues_by_key'] = {}
    for (venue_index, venue_mock) in enumerate(venue_mocks):
        logger.info("look venue " + venue_mock['offererKey'] + " " + venue_mock['name'] + " " + str(venue_index) + "/" + venues_count)
        venue = create_or_find_venue(venue_mock, store=store)
        store['venues_by_key'][venue_mock['key']] = venue
