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
        if 'thumbName' in mediation_mock:
            store_public_object_from_sandbox_assets("thumbs", mediation, mediation_mock['thumbName'])
    else:
        logger.info('--already here-- mediation' + str(mediation))

    return mediation
