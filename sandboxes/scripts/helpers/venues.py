from models import Offerer, Venue
from models.pc_object import PcObject
from utils.human_ids import dehumanize
from utils.logger import logger

def create_or_find_venue(venue_mock):
    offerer = Offerer.query.get(dehumanize(venue_mock['offererId']))

    logger.info("look venue " + venue_mock['name'] + " " + venue_mock.get('id'))

    if 'id' in venue_mock:
        venue = Venue.query.get(dehumanize(venue_mock['id']))
    else:
        venue = Venue.query.filter_by(
            managingOffererId=offerer.id,
            name=venue_mock['name']
        ).first()

    if venue is None:
        venue = Venue(from_dict=venue_mock)
        venue.managingOfferer = offerer
        if 'id' in venue_mock:
            venue.id = dehumanize(venue_mock['id'])
        PcObject.check_and_save(venue)
        logger.info("created venue " + str(venue))
    else:
        logger.info('--already here-- venue ' + str(venue))

    return venue
