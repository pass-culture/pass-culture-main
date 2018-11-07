from models import Event, Thing, Mediation, Offer
from models.pc_object import PcObject
from sandboxes.scripts.utils.storage_utils import store_public_object_from_sandbox_assets
from utils.human_ids import dehumanize
from utils.logger import logger

def create_or_find_mediation(mediation_mock):
    offer = Offer.query.get(dehumanize(mediation_mock['offerId']))

    logger.info("look mediation " + mediation_mock.get('id'))

    if 'id' in mediation_mock:
        mediation = Mediation.query.get(dehumanize(mediation_mock['id']))
    else:
        mediation = Mediation.query.filter_by(offerId=offer.id).first()

    if mediation is None:
        mediation = Mediation(from_dict=mediation_mock)
        mediation.offer = offer
        if 'id' in mediation_mock:
            mediation.id = dehumanize(mediation_mock['id'])
        PcObject.check_and_save(mediation)
        logger.info("created mediation " + str(mediation))
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
    else:
        logger.info('--already here-- mediation' + str(mediation))

    return mediation
