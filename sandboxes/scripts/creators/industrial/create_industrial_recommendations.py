from models.pc_object import PcObject
from sandboxes.scripts.creators.industrial.create_industrial_events import MOCK_ACTIVATION_NAME
from utils.logger import logger
from utils.test_utils import create_recommendation


def create_industrial_recommendations(mediations_by_name, offers_by_name, users_by_name):
    logger.info('create_industrial_recommendations')

    recommendations_by_name = {}

    activation_offers = [
        o
        for o in offers_by_name.values()
        ['{} / {}'.format(MOCK_ACTIVATION_NAME, )]

    for (user_name, user) in users_by_name.items():

        if user.firstName != "PC Test Jeune" or\
           "has-signed-up" in user_name or\
           "has-confirmed-activation" in user_name:
            continue



            Rencontre avec Franck Lepage / THEATRE LE GRAND REX PARIS / jeune93 0
        recommendations_by_name['{} / public / 500'.format(user_name)] = create_deposit(
            user,
            None,
            amount=500
        )


    PcObject.check_and_save(*recommendations_by_name.values())

    logger.info('created {} recommendations'.format(len(recommendations_by_name)))

    return recommendations_by_name
