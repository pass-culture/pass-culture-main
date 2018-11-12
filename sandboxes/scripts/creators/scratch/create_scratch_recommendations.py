from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_recommendation

def create_scratch_recommendations(mediations_by_name, offers_by_name, users_by_name):
    logger.info('create_scratch_recommendations')

    recommendations_by_name = {}

    recommendations_by_name['Rencontre avec Franck Lepage / LE GRAND REX PARIS / jeune 93'] = create_recommendation(
        mediation=mediations_by_name['Rencontre avec Franck Lepage / LE GRAND REX PARIS'],
        offer=offers_by_name['Rencontre avec Franck Lepage / LE GRAND REX PARIS'],
        user=users_by_name['jeune 93']
    ),

    recommendations_by_name['Ravage / THEATRE DE L ODEON / jeune 93'] = create_recommendation(
        mediation=mediations_by_name['Ravage / THEATRE DE L ODEON'],
        offer=offers_by_name['Ravage / THEATRE DE L ODEON'],
        user=users_by_name['jeune 93']
    )

    PcObject.check_and_save(*recommendations_by_name.values())

    return recommendations_by_name
