from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_event_offer

def create_scratch_event_offers(events_by_name, venues_by_name):
    logger.info("create_scratch_event_offers")

    event_offers_by_name = {}

    event_offers_by_name["Rencontre avec Franck Lepage / LE GRAND REX PARIS"] = create_event_offer(
        event=events_by_name["Rencontre avec Franck Lepage"],
        venue=venues_by_name['LE GRAND REX PARIS']
    )

    event_offers_by_name["Concert de Gael Faye / THEATRE DE L ODEON"] = create_event_offer(
        event=events_by_name['Concert de Gael Faye'],
        venue=venues_by_name['THEATRE DE L ODEON']
    )

    event_offers_by_name["PNL chante Marx / THEATRE DE L ODEON"] = create_event_offer(
        event=events_by_name['PNL chante Marx'],
        venue=venues_by_name['THEATRE DE L ODEON']
    )

    PcObject.check_and_save(*event_offers_by_name.values())

    return event_offers_by_name
