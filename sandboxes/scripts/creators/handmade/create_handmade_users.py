from models.pc_object import PcObject
from utils.logger import logger
from tests.test_utils import create_user,\
                             USER_TEST_ADMIN_EMAIL,\
                             USER_TEST_ADMIN_PASSWORD

def create_handmade_users():
    logger.info('create_handmade_users')

    users_by_name = {}

    ######################################
    # ADMINS
    ######################################

    users_by_name['admin93 0'] = create_user(public_name="PC Test Admin93 0", first_name="PC Test Admin",
                                             last_name="93 0", postal_code="93100", departement_code="93",
                                             email=USER_TEST_ADMIN_EMAIL, can_book_free_offers=False, is_admin=True)

    ######################################
    # PRO
    ######################################

    users_by_name['pro93 has-signed-up'] = create_user(public_name="PC Test Pro93 HSU", first_name="PC Test Pro",
                                                       last_name="93 HSU", postal_code="93100", departement_code="93",
                                                       email="pctest.pro93.has-signed-up@btmx.fr",
                                                       validation_token='AZERTY123')

    users_by_name['pro93 has-validated-unregistered-offerer'] = create_user(public_name="PC Test Pro93 HVUO",
                                                                            first_name="PC Test Pro",
                                                                            last_name="93 HVUO", postal_code="93100",
                                                                            departement_code="93",
                                                                            email="pctest.pro93.has-validated-unregistered-offerer@btmx.fr")

    users_by_name['pro93 has-validated-registered-offerer'] = create_user(public_name="PC Test Pro93 HVRO",
                                                                          first_name="PC Test Pro", last_name="93 HVRO",
                                                                          postal_code="93100", departement_code="93",
                                                                          email="pctest.pro93.has-validated-registered-offerer@btmx.fr")

    users_by_name['pro97 has-validated-unregistered-offerer'] = create_user(public_name="PC Test Pro97 HVUO",
                                                                            first_name="PC Test Pro",
                                                                            last_name="97 HVUO", postal_code="97351",
                                                                            departement_code="97",
                                                                            email="pctest.pro97.has-validated-unregistered-offerer@btmx.fr")

    ######################################
    # JEUNES
    ######################################

    users_by_name['jeune34 has-signed-up'] = create_user(public_name="PC Test Jeune34 HSU", first_name="PC Test Jeune",
                                                         last_name="34 has-signed-up", postal_code="34080",
                                                         departement_code="34",
                                                         email="pctest.jeune34.has-signed-up@btmx.fr",
                                                         reset_password_token='AZERTY124')

    users_by_name['jeune93 has-signed-up'] = create_user(public_name="PC Test Jeune93 HSU", first_name="PC Test Jeune",
                                                         last_name="93 HSU", postal_code="93100", departement_code="93",
                                                         email="pctest.jeune93.has-signed-up@btmx.fr",
                                                         reset_password_token='AZERTY125')

    users_by_name['jeune97 has-signed-up'] = create_user(public_name="PC Test Jeune93 HSU", first_name="PC Test Jeune",
                                                         last_name="97 HSU", postal_code="97100", departement_code="97",
                                                         email="pctest.jeune97.has-signed-up@btmx.fr",
                                                         reset_password_token='AZERTY126')

    users_by_name['jeune93 has-booked-some'] = create_user(public_name="PC Test Jeune93 HBS",
                                                           first_name="PC Test Jeune", last_name="93 HBS",
                                                           postal_code="93100", departement_code="93",
                                                           email="pctest.jeune93.has-booked-some@btmx.fr")

    users_by_name['jeune97 has-booked-some'] = create_user(public_name="PC Test Jeune97 HBS",
                                                           first_name="PC Test Jeune", last_name="97 HBS",
                                                           postal_code="97351", departement_code="97",
                                                           email="pctest.jeune97.has-booked-some@btmx.fr")

    PcObject.check_and_save(*users_by_name.values())

    logger.info('created {} users'.format(len(users_by_name)))

    return users_by_name
