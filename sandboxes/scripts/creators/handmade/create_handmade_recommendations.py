from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_recommendation

def create_handmade_recommendations(mediations_by_name, offers_by_name, users_by_name):
    logger.info('create_handmade_recommendations')

    recommendations_by_name = {}

    mediation = mediations_by_name['Rencontre avec Franck Lepage / THEATRE LE GRAND REX PARIS']
    recommendations_by_name['Rencontre avec Franck Lepage / THEATRE LE GRAND REX PARIS / jeune93 0'] = \
        create_recommendation(
            mediation=mediation,
            offer=mediation.offer,
            user=users_by_name['jeune93 0']
        )

    mediation = mediations_by_name['Ravage / THEATRE DE L ODEON']
    recommendations_by_name['Ravage / THEATRE DE L ODEON / jeune93 0'] = \
        create_recommendation(
            mediation=mediation,
            offer=mediation.offer,
            user=users_by_name['jeune93 0']
        )

    PcObject.check_and_save(*recommendations_by_name.values())

    logger.info('created {} recommendations'.format(len(recommendations_by_name)))

    return recommendations_by_name
