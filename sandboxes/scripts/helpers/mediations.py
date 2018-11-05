from models import Event, Thing, Mediation
from models.pc_object import PcObject
from sandboxes.utils import store_public_object_from_sandbox_assets
from utils.logger import logger

def create_or_find_mediation(mediation_mock, offer=None, store=None):
    if offer is None:
        offer = store['offers_by_key'][mediation_mock['offerKey']]

    mediation = Mediation.query.filter_by(offerId=offer.id).first()
    if mediation is None:
        mediation = Mediation(from_dict=mediation_mock)
        mediation.offer = offer
        PcObject.check_and_save(mediation)
        logger.info("created mediation " + str(mediation))
    else:
        logger.info('--already here-- mediation' + str(mediation))

    if 'thumbName' not in mediation_mock:
        if offer.event:
            event = Event.query.filter_by(id=offer.event.id).first()
            thumb_name = event.type
        else:
            thing = Thing.query.filter_by(id=offer.thing.id).first()
            thumb_name = thing.type
    else:
        thumb_name = mediation_mock['thumbName']

    store_public_object_from_sandbox_assets("thumbs", mediation, thumb_name)

    return mediation

def create_or_find_mediations(*mediation_mocks, store=None):
    if store is None:
        store = {}
    mediations_count = str(len(mediation_mocks))
    logger.info("mediation mocks " + mediations_count)
    store['mediations_by_key'] = {}
    for (mediation_index, mediation_mock) in enumerate(mediation_mocks):
        logger.info("look mediation " + mediation_mock['offerKey'] + " " + str(mediation_index) + "/" + mediations_count)
        mediation = create_or_find_mediation(mediation_mock, store=store)
        store['mediations_by_key'][mediation_mock['key']] = mediation
