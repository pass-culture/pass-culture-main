from models.mediation import Mediation
from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_recommendation

def create_handmade_recommendations(mediations_by_name, offers_by_name, users_by_name):
    logger.info('create_handmade_recommendations')

    recommendations_by_name = {}

    first_mediation = Mediation.query.filter_by(tutoIndex=0).one()
    second_mediation = Mediation.query.filter_by(tutoIndex=1).one()
    tuto_mediations = [first_mediation, second_mediation]
    for (user_name, user) in users_by_name.items():

        user_has_no_tuto_recommendations = \
            user.firstName != "PC Test Jeune"  or \
            "has-signed-up" in user_name

        if user_has_no_tuto_recommendations:
            continue

        for (tuto_index, tuto_mediation) in enumerate(tuto_mediations):
            recommendation_name = 'Tuto {} / {}'.format(
                tuto_index,
                user_name
            )
            recommendation = \
                create_recommendation(
                    mediation=tuto_mediation,
                    user=user
                )

            user_has_already_read_tuto = "has-signed-up" not in user_name
            if user_has_already_read_tuto:
                recommendation.dateRead = "2018-12-17T15:59:11.689Z"

            recommendations_by_name[recommendation_name] = recommendation

    mediation = mediations_by_name['Rencontre avec Franck Lepage / THEATRE LE GRAND REX PARIS']
    recommendations_by_name['Rencontre avec Franck Lepage / THEATRE LE GRAND REX PARIS / jeune93 has-booked-some'] = \
        create_recommendation(
            mediation=mediation,
            offer=mediation.offer,
            user=users_by_name['jeune93 has-booked-some']
        )

    mediation = mediations_by_name['Ravage / THEATRE DE L ODEON']
    recommendations_by_name['Ravage / THEATRE DE L ODEON / jeune93 has-booked-some'] = \
        create_recommendation(
            mediation=mediation,
            offer=mediation.offer,
            user=users_by_name['jeune93 has-booked-some']
        )

    PcObject.check_and_save(*recommendations_by_name.values())

    logger.info('created {} recommendations'.format(len(recommendations_by_name)))

    return recommendations_by_name
